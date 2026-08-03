from unittest.mock import MagicMock, patch

import pytest

from services.llm_service.secret_manager import SecretManager, SecretManagerError

VAULT_ADDR = "http://vault:8200"  # → Sprint 1: test Vault address injected without contacting a server
VAULT_TOKEN = "test-token"  # → Sprint 1: non-sensitive unit-test authentication value
VAULT_SECRET_PATH = "self-healing/test"  # → Sprint 1: isolated KV path used by unit tests
VAULT_MOUNT_POINT = "secret"  # → Sprint 1: KV v2 mount represented in unit tests
SECRET_KEY = "MISTRAL_API_KEY"  # → Sprint 2: required model credential key
SECRET_VALUE = "test-secret-value"  # → Sprint 1: non-sensitive value proving retrieval behaviour


def configure_vault_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("VAULT_ADDR", VAULT_ADDR)
    monkeypatch.setenv("VAULT_TOKEN", VAULT_TOKEN)
    monkeypatch.setenv("VAULT_SECRET_PATH", VAULT_SECRET_PATH)
    monkeypatch.setenv("VAULT_MOUNT_POINT", VAULT_MOUNT_POINT)


def test_get_secret_returns_vault_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_vault_environment(monkeypatch)

    mock_client = MagicMock()  # → Sprint 1: isolated Vault client replacing the real network dependency
    mock_client.is_authenticated.return_value = True
    mock_client.secrets.kv.v2.read_secret_version.return_value = {
        "data": {
            "data": {
                SECRET_KEY: SECRET_VALUE,
            },
        },
    }

    with patch(
        "services.llm_service.secret_manager.hvac.Client",
        return_value=mock_client,
    ):
        secret_manager = SecretManager()  # → Sprint 1: system under test using mocked Vault
        actual_value = secret_manager.get_secret(
            SECRET_KEY,
        )  # → Sprint 1: value returned by centralized secret retrieval

    assert actual_value == SECRET_VALUE


def test_missing_environment_configuration_fails_fast(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("VAULT_ADDR", raising=False)

    with pytest.raises(
        SecretManagerError,
        match="Missing required environment variable: VAULT_ADDR",
    ):
        SecretManager()
