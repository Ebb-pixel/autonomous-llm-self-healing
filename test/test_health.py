from fastapi.testclient import TestClient

from services.llm_service.main import app

client = TestClient(app)  # → Sprint 1: local test client that calls FastAPI without starting Uvicorn


def test_health_check_returns_healthy_status() -> None:
    # We test the smallest production signal first because CI needs a cheap proof the API imports.
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "llm_service",
    }
