"""Smoke tests for liveness/readiness endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root() -> None:
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["phase"] == "2"
    assert "database_url" not in payload
    assert "password" not in str(payload).lower()


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["phase"] == 2
    assert "database_url" not in payload
    assert "DATABASE_URL" not in payload


def test_ready_shape_hides_secrets() -> None:
    response = client.get("/api/ready")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in {"ready", "not_ready"}
    assert payload["database"] in {"connected", "unavailable"}
    assert "database_url" not in payload
    assert "password" not in payload
    assert "postgresql" not in str(payload).lower()
