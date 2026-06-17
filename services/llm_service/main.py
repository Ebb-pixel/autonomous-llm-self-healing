from fastapi import FastAPI

SERVICE_NAME = "llm_service"  # → Sprint 2: service identifier used in logs, metrics, and API responses

app = FastAPI(
    title="Self-Healing LLM Service",  # → Sprint 2: OpenAPI title for the model inference service
    version="0.1.0",                   # → Sprint 1: local-dev foundation version
)


@app.get("/health")
def health_check() -> dict[str, str]:
    # We keep health dependency-free so Docker can prove the API boots before Redis/Mistral are wired.
    return {
        "status": "healthy",      # → Sprint 1: readiness signal for Docker Compose and CI
        "service": SERVICE_NAME,  # → Sprint 2: Prometheus service label value
    }
