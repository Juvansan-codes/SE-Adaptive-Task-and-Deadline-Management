"""Tests for Supabase JWT verification, expiration, invalid signatures, and profile auto-provisioning."""

import time
import jwt
from fastapi.testclient import TestClient

from tests.conftest import TEST_JWT_SECRET, make_test_token, make_auth_headers
from app.models.profile import Profile


def test_missing_authorization_header_returns_401(authed_client: TestClient):
    """Endpoints require Bearer token; missing header returns 401."""
    response = authed_client.get("/api/tasks")
    assert response.status_code == 401
    assert "Missing authorization token" in response.json()["detail"]["message"]


def test_malformed_authorization_header_returns_401(authed_client: TestClient):
    """Invalid token string returns 401."""
    response = authed_client.get(
        "/api/tasks",
        headers={"Authorization": "Bearer not-a-valid-jwt-token"},
    )
    assert response.status_code == 401
    assert "Invalid authentication token" in response.json()["detail"]["message"]


def test_expired_token_returns_401(authed_client: TestClient):
    """Expired Supabase JWT returns 401 with informative message."""
    expired_token = make_test_token(
        user_id="user-expired-123",
        expires_in=-300,  # Expired 5 minutes ago
    )
    response = authed_client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401
    assert "Token has expired" in response.json()["detail"]["message"]


def test_token_with_wrong_secret_signature_returns_401(authed_client: TestClient):
    """Token signed with forged secret is cryptographically rejected."""
    forged_token = make_test_token(
        user_id="user-forged-123",
        secret="wrong-forged-secret-key-1234567890",
    )
    response = authed_client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {forged_token}"},
    )
    assert response.status_code == 401
    assert "Invalid authentication token" in response.json()["detail"]["message"]


def test_valid_token_auto_provisions_user_profile(authed_client: TestClient, db_session):
    """First request with valid Supabase token auto-creates a Profile row."""
    user_id = "user-profile-auto-456"
    headers = make_auth_headers(
        user_id=user_id,
        email="newstudent@karunya.edu",
        name="New Student",
    )

    response = authed_client.get("/api/tasks", headers=headers)
    assert response.status_code == 200
    assert response.json() == []

    # Verify profile was inserted into database
    profile = db_session.query(Profile).filter(Profile.id == user_id).first()
    assert profile is not None
    assert profile.email == "newstudent@karunya.edu"
    assert profile.name == "New Student"


def test_valid_asymmetric_token_verifies(authed_client: TestClient, monkeypatch, db_session):
    """Asymmetric ES256 Supabase token verified via JWKS public key."""
    from cryptography.hazmat.primitives.asymmetric import ec
    from unittest.mock import MagicMock
    from app.core import auth

    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    token = jwt.encode(
        {"sub": "user-asym-123", "email": "asym@example.com", "exp": int(time.time() + 3600)},
        private_key,
        algorithm="ES256",
        headers={"kid": "test-key-id"},
    )

    mock_jwks = MagicMock()
    mock_signing_key = MagicMock()
    mock_signing_key.key = public_key
    mock_jwks.get_signing_key_from_jwt.return_value = mock_signing_key

    monkeypatch.setattr(auth, "get_jwks_client", lambda: mock_jwks)

    response = authed_client.get("/api/tasks", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    profile = db_session.query(Profile).filter(Profile.id == "user-asym-123").first()
    assert profile is not None
    assert profile.email == "asym@example.com"
