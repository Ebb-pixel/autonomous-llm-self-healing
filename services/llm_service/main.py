from fastapi import FastAPI, HTTPException, status

from services.llm_service.secret_manager import SecretManager, SecretManagerError

SERVICE_NAME = "llm_service"  # → Sprint 2: service identifier used in metrics, logs, and API responses
SECRET_PROOF_KEY = "MISTRAL_API_KEY"  # → Sprint 2: model credential key retrieved from Vault

app = FastAPI(
    title="Self-Healing LLM Service",  # → Sprint 1: service title displayed in generated OpenAPI documentation
    version="0.1.0",  # → Sprint 1: baseline service version used by Docker and CI validation
)


@app.get("/health")
def health_check() -> dict[str, str]:
    # Liveness remains dependency-free so orchestration can distinguish app failure from Vault failure.
    return {
        "status": "healthy",  # → Sprint 1: liveness result consumed by developers and CI
        "service": SERVICE_NAME,  # → Sprint 2: service identity consumed by monitoring
    }


@app.get("/internal/readiness/secrets")
def secret_readiness() -> dict[str, str]:
    # We prove the secret exists without returning its value or length.
    try:
        secret_manager = SecretManager()  # → Sprint 1: centralized Vault-backed secret accessor
        secret_manager.get_secret(SECRET_PROOF_KEY)
    except SecretManagerError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return {
        "status": "ready",  # → Sprint 1: confirms the required secret was loaded successfully
        "source": "vault",  # → Sprint 1: confirms centralized Vault is the configured source
    }
