
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["application"] == "NEXUS AI"
    assert response.json()["status"] == "operational"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["service"] == "NEXUS AI Backend"


def test_database_health_endpoint():
    response = client.get("/api/v1/database/health")

    assert response.status_code == 200
    assert response.json()["status"] == "connected"
    assert response.json()["database"] == "nexus_ai"
