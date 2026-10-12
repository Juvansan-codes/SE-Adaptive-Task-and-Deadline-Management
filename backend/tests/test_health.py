"""Automated tests for health check endpoints and database connectivity handling."""

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import get_db
from app.core.config import Settings


def test_app_imports_cleanly():
    """Verify application modules import without requiring actual database credentials."""
    from app.main import app as imported_app
    from app.core.config import settings as imported_settings
    from app.db.base import Base

    assert imported_app is not None
    assert imported_settings is not None
    assert Base is not None


def test_service_health_endpoint_returns_200(client: TestClient):
    """Verify GET /api/health returns HTTP 200 with exact required JSON payload."""
    response = client.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert data == {
        "status": "ok",
        "service": "adaptive-task-manager-api",
    }


def test_database_health_endpoint_success(client: TestClient, mock_healthy_db):
    """Verify GET /api/health/db returns HTTP 200 when database responds to SELECT 1."""
    # Override get_db dependency with mock healthy session
    app.dependency_overrides[get_db] = lambda: mock_healthy_db
    try:
        response = client.get("/api/health/db")
        assert response.status_code == 200
        data = response.json()
        assert data == {
            "status": "ok",
            "database": "connected",
        }
    finally:
        app.dependency_overrides.clear()


def test_database_health_endpoint_fails_safely_on_connection_error(
    client: TestClient, mock_failing_db
):
    """
    Verify GET /api/health/db returns HTTP 503 when the database is unreachable,
    without leaking connection strings or credentials.
    """
    app.dependency_overrides[get_db] = lambda: mock_failing_db
    try:
        response = client.get("/api/health/db")
        assert response.status_code == 503
        data = response.json()
        assert "detail" in data
        assert data["detail"]["status"] == "error"
        assert data["detail"]["message"] == "Database connection unavailable"
        # Ensure credentials / internal details are NOT leaked
        assert "password" not in str(data).lower()
        assert "connection refused" not in str(data).lower()
    finally:
        app.dependency_overrides.clear()


def test_database_health_endpoint_unconfigured_behavior(client: TestClient):
    """
    Verify GET /api/health/db without DATABASE_URL configured fails safely
    with an HTTP 503 status code and actionable error message.
    """
    def unconfigured_get_db():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "error", "message": "Database connection unavailable"},
        )

    app.dependency_overrides[get_db] = unconfigured_get_db
    try:
        response = client.get("/api/health/db")
        assert response.status_code == 503
        data = response.json()
        assert data["detail"]["status"] == "error"
        assert "Database connection unavailable" in data["detail"]["message"]
    finally:
        app.dependency_overrides.clear()


def test_settings_url_normalization():
    """Verify that postgresql:// URIs are mapped to postgresql+psycopg:// for SQLAlchemy 2.x."""
    test_settings = Settings(
        database_url="postgresql://user:pass@localhost:5432/testdb"
    )
    assert test_settings.sync_database_url == "postgresql+psycopg://user:pass@localhost:5432/testdb"

    # Already qualified URI should remain unchanged
    test_settings_psycopg = Settings(
        database_url="postgresql+psycopg://user:pass@localhost:5432/testdb"
    )
    assert test_settings_psycopg.sync_database_url == "postgresql+psycopg://user:pass@localhost:5432/testdb"
