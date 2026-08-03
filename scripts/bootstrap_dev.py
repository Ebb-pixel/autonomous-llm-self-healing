import subprocess
import time

VAULT_CONTAINER = "self_healing_vault"  # → Sprint 1: Docker container hosting local Vault
VAULT_SECRET_PATH = "secret/self-healing/dev"  # → Sprint 1: complete CLI path for local KV v2 secrets
VAULT_PROOF_KEY = "MISTRAL_API_KEY"  # → Sprint 2: required model credential name
VAULT_PROOF_VALUE = "local-dev-placeholder"  # → Sprint 1: non-sensitive local integration-test value
MAX_ATTEMPTS = 15  # → Sprint 1: maximum Vault readiness attempts before bootstrap stops
RETRY_SECONDS = 2  # → Sprint 1: delay between Vault readiness attempts


class BootstrapError(RuntimeError):
    """Raised when the local Vault bootstrap cannot complete safely."""


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    # Captured output gives developers an actionable failure instead of silent bootstrap errors.
    result = subprocess.run(
        command,
        capture_output=True,
        check=False,
        text=True,
    )  # → Sprint 1: completed Docker or Vault command including exit code and output

    return result


def wait_for_vault() -> None:
    status_command = [
        "docker",
        "exec",
        VAULT_CONTAINER,
        "vault",
        "status",
    ]  # → Sprint 1: command checking whether local Vault is initialized and unsealed

    for attempt in range(1, MAX_ATTEMPTS + 1):
        result = run_command(
            status_command,
        )  # → Sprint 1: current Vault readiness result

        if result.returncode == 0:
            print("Vault is ready.")
            return

        print(f"Waiting for Vault ({attempt}/{MAX_ATTEMPTS})...")
        time.sleep(RETRY_SECONDS)

    raise BootstrapError(
        "Vault did not become ready. Run: docker compose logs vault",
    )


def seed_development_secret() -> None:
    seed_command = [
        "docker",
        "exec",
        VAULT_CONTAINER,
        "vault",
        "kv",
        "put",
        VAULT_SECRET_PATH,
        f"{VAULT_PROOF_KEY}={VAULT_PROOF_VALUE}",
    ]  # → Sprint 1: idempotent command writing the non-sensitive local proof secret

    result = run_command(
        seed_command,
    )  # → Sprint 1: Vault write result used to validate bootstrap success

    if result.returncode != 0:
        error_message = (
            result.stderr.strip() or result.stdout.strip()
        )  # → Sprint 1: actionable Vault CLI error returned to the developer

        raise BootstrapError(
            f"Vault development bootstrap failed:\n{error_message}",
        )

    print(f"Development secret written to {VAULT_SECRET_PATH}.")


def main() -> None:
    # One entry point gives every developer the same repeatable local setup.
    wait_for_vault()
    seed_development_secret()
    print("Local Vault bootstrap completed successfully.")


if __name__ == "__main__":
    main()
