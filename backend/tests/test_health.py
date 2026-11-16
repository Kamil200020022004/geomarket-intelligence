"""Testy szkieletu: stan serwisu, CORS i jednolity format błędów."""

import pytest

from app.api import health
from app.db.session import check_database


def test_liveness_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_returns_503_when_database_is_down(client, monkeypatch):
    monkeypatch.setattr(health, "check_database", lambda: False)
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable", "database": "unavailable"}


@pytest.mark.integration
def test_readiness_returns_ok_with_running_mysql(client):
    if not check_database():
        pytest.skip("MySQL nie działa — uruchom docker compose up -d")
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_cors_allows_frontend_origin(client):
    response = client.get("/health", headers={"Origin": "http://localhost:5173"})
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_cors_rejects_unknown_origin(client):
    response = client.get("/health", headers={"Origin": "http://evil.example"})
    assert "access-control-allow-origin" not in response.headers


def test_unhandled_error_returns_json_without_internal_details(client):
    def broken():
        raise RuntimeError("tajny szczegół wewnętrzny")

    client.app.add_api_route("/test-error", broken)
    response = client.get("/test-error")
    assert response.status_code == 500
    assert response.json() == {"detail": "Wewnętrzny błąd serwera."}
    assert "tajny" not in response.text
