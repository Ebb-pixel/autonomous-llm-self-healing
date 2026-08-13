import os

import ldclient
from ldclient import Context
from ldclient.config import Config


class FeatureFlagError(RuntimeError):
    """Raised when feature flag configuration fails."""


class FeatureFlagManager:
    # We isolate LaunchDarkly access so application code does not depend directly on the SDK.
    def __init__(self) -> None:

        self.sdk_key = self._require_env(
            "LD_SDK_KEY",
        )  # → Sprint 1: LaunchDarkly server SDK key from Vault/runtime injection

        self.environment = os.getenv(
            "LD_ENVIRONMENT",
            "development",
        )  # → Sprint 1: LaunchDarkly environment identifier

        ldclient.set_config(
            Config(
                self.sdk_key,
            )
        )  # → Sprint 1: initializes LaunchDarkly SDK client

        self.client = ldclient.get()

        if not self.client.is_initialized():
            raise FeatureFlagError(
                "LaunchDarkly client failed to initialize",
            )


    def is_enabled(
        self,
        flag_key: str,
        default: bool = False,
    ) -> bool:
        # Default values keep the service safe if LaunchDarkly temporarily becomes unavailable.
        context=Context.create("system")
         # → Sprint 1: evaluation identity; future becomes authenticated user/service identity

        return self.client.variation(
            flag_key,
            context,
            default,
        )


    @staticmethod
    def _require_env(
        name: str,
    ) -> str:
        value = os.getenv(
            name,
        )  # → Sprint 1: runtime configuration injected through secrets/config management

        if not value:
            raise FeatureFlagError(
                f"Missing required configuration: {name}",
            )

        return value
