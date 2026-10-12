"""Pytest configuration, fixtures, and FastAPI TestClient setup."""

import time
import pytest
import jwt
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import OperationalError
from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.config import settings


@pytest.fixture
def client() -> TestClient:
    """Return a FastAPI TestClient instance without dependency overrides."""
    return TestClient(app)


@pytest.fixture
def mock_healthy_db():
    """Simulate an active, responsive PostgreSQL database session."""
    mock_session = MagicMock()
    mock_result = MagicMock()
    mock_result.scalar.return_value = 1
    mock_session.execute.return_value = mock_result
    return mock_session


@pytest.fixture
def mock_failing_db():
    """Simulate an unreachable or failing database connection."""
    mock_session = MagicMock()
    mock_session.execute.side_effect = OperationalError(
        statement="SELECT 1",
        params={},
        orig=Exception("could not connect to server: Connection refused"),
    )
    return mock_session


# ------------------------------------------------------------------------------
# In-Memory SQLite Database and Auth Fixtures for Phase 2 Tests
# ------------------------------------------------------------------------------

TEST_JWT_SECRET = "test-supabase-jwt-secret-very-long-32-chars-ok"

test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def configure_test_jwt_secret():
    """Ensure test environment uses predictable test JWT secret."""
    original_secret = settings.supabase_jwt_secret
    settings.supabase_jwt_secret = TEST_JWT_SECRET
    yield
    settings.supabase_jwt_secret = original_secret


@pytest.fixture
def db_session():
    """Yield an isolated, clean in-memory database session."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def authed_client(db_session) -> TestClient:
    """Return a TestClient bound to the isolated in-memory test database."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def make_test_token(
    user_id: str,
    email: str = "student@example.com",
    name: str = "Test Student",
    expires_in: int = 3600,
    secret: str = TEST_JWT_SECRET,
) -> str:
    """Generate a cryptographically valid Supabase JWT for test isolation."""
    now = int(time.time())
    payload = {
        "sub": user_id,
        "email": email,
        "role": "authenticated",
        "aud": "authenticated",
        "iat": now,
        "exp": now + expires_in,
        "user_metadata": {"name": name, "full_name": name},
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def make_auth_headers(
    user_id: str,
    email: str = "student@example.com",
    name: str = "Test Student",
) -> dict:
    """Return Authorization header dictionary for given user."""
    token = make_test_token(user_id=user_id, email=email, name=name)
    return {"Authorization": f"Bearer {token}"}

