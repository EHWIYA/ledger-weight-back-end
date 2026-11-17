"""
Smoke tests: root and health endpoints.
"""

from fastapi.testclient import TestClient


def test_root(client: TestClient) -> None:
    """GET / returns server info and status."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data.get("status") == "running"


def test_health(client: TestClient) -> None:
    """GET /health returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
