from services.api.app.main import app
from fastapi.testclient import TestClient

client=TestClient(app)

def test_health_check_returns_ok()->None:
    response=client.get("/health")

    assert response.status_code==200
    assert response.json()["status"]=="ok"
    assert response.json()["services"]=="Self-Healing LLM API"
