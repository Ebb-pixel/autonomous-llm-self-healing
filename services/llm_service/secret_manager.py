import os
from typing import Any

import hvac
import requests


class SecretManagerError(RuntimeError):
    """Raised when required Vault configuration or secret retrieval fails."""


class SecretManager:
    # We centralize Vault access so route and model code never handles authentication directly.
    def __init__(self) -> None:
        self.vault_addr = self._require_env(
            "VAULT_ADDR",
        )  # → Sprint 1: http://vault:8200 inside Docker; production Vault address later

        self.vault_token = self._require_env(
            "VAULT_TOKEN",
        )  # → Sprint 1: disposable dev token; Kubernetes or IAM authentication later

        self.vault_secret_path = self._require_env(
            "VAULT_SECRET_PATH",
        )  # → Sprint 1: self-healing/dev; environment-specific application path later

        self.vault_mount_point = self._require_env(
            "VAULT_MOUNT_POINT",
        )  # → Sprint 1: secret KV v2 mount; policy-controlled mount later

        self.client = hvac.Client(
            url=self.vault_addr,
            token=self.vault_token,
        )  # → Sprint 1: authenticated local Vault client; workload-authenticated client later

        if not self.client.is_authenticated():
            raise SecretManagerError("Vault authentication failed")

    def get_secret(self, key: str) -> str:
        # We translate infrastructure failures into one stable application-level exception.
        try:
            response: dict[str, Any] = (
                self.client.secrets.kv.v2.read_secret_version(
                    path=self.vault_secret_path,
                    mount_point=self.vault_mount_point,
                )
            )  # → Sprint 1: KV v2 response containing the local development secret payload
        except (hvac.exceptions.VaultError, requests.RequestException) as exc:
            raise SecretManagerError("Unable to read secrets from Vault") from exc

        secret_data = response.get("data", {}).get(
            "data",
            {},
        )  # → Sprint 1: application key-value dictionary returned by Vault

        value = secret_data.get(
            key,
        )  # → Sprint 2: Mistral, Hugging Face, MLflow, or service credential value

        if not isinstance(value, str) or not value:
            raise SecretManagerError(f"Missing required Vault secret: {key}")

        return value

    @staticmethod
    def _require_env(name: str) -> str:
        # Required configuration prevents unsafe deployments from silently using fallback credentials.
        value = os.getenv(
            name,
        )  # → Sprint 1: runtime configuration injected by Docker Compose

        if not value:
            raise SecretManagerError(
                f"Missing required environment variable: {name}",
            )

        return value
