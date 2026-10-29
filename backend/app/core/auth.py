import logging
from typing import Optional
import jwt
from jwt import PyJWKClient, PyJWKClientError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.profile import Profile

logger = logging.getLogger(__name__)

_jwks_client: Optional[PyJWKClient] = None


def get_jwks_client() -> Optional[PyJWKClient]:
    """Return a cached PyJWKClient instance for Supabase JWKS verification."""
    global _jwks_client
    if _jwks_client is None and settings.supabase_url:
        jwks_url = f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
        _jwks_client = PyJWKClient(jwks_url, cache_jwk_set=True, lifespan=3600)
    return _jwks_client


class AuthenticatedUser(BaseModel):
    """Authenticated user context extracted from verified Supabase JWT."""

    id: str
    email: str
    name: str = ""
    role: str = "authenticated"


# HTTP Bearer authentication scheme (auto_error=False allows returning custom 401 details)
http_bearer = HTTPBearer(auto_error=False)


def verify_supabase_jwt(token: str) -> dict:
    """
    Cryptographically verify Supabase JWT token.
    Supports:
    1. Asymmetric algorithms (ES256, RS256, EdDSA) via Supabase JWKS endpoint.
    2. Symmetric HS256 tokens using SUPABASE_JWT_SECRET (for test environments and fallback).
    Rejects tampered, invalid, or expired tokens.
    """
    try:
        unverified_header = jwt.get_unverified_header(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status": "error", "message": "Invalid authentication token"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    alg = unverified_header.get("alg", "HS256")

    # If token is signed with an asymmetric algorithm (standard in modern Supabase)
    if alg in ("ES256", "RS256", "EdDSA"):
        jwks_client = get_jwks_client()
        if jwks_client:
            try:
                signing_key = jwks_client.get_signing_key_from_jwt(token)
                payload = jwt.decode(
                    token,
                    signing_key.key,
                    algorithms=[alg],
                    leeway=60,
                    options={
                        "verify_signature": True,
                        "verify_exp": True,
                        "verify_aud": False,
                    },
                )
                return payload
            except jwt.ExpiredSignatureError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={"status": "error", "message": "Token has expired"},
                    headers={"WWW-Authenticate": "Bearer"},
                )
            except (jwt.InvalidTokenError, PyJWKClientError) as exc:
                logger.warning("JWKS verification failed for asymmetric token: %s", exc)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={"status": "error", "message": "Invalid authentication token"},
                    headers={"WWW-Authenticate": "Bearer"},
                )

    # For HS256 tokens (or tests/fallback)
    secret = settings.supabase_jwt_secret
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "error", "message": "Authentication service unconfigured"},
        )

    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            leeway=60,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": False,
            },
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status": "error", "message": "Token has expired"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status": "error", "message": "Invalid authentication token"},
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    db: Session = Depends(get_db),
) -> AuthenticatedUser:
    """
    FastAPI dependency that:
    1. Extracts Bearer token from Authorization header.
    2. Verifies cryptographic signature using Supabase secret.
    3. Rejects missing, invalid, or expired tokens.
    4. Auto-provisions a matching Profile record if not present.
    5. Returns AuthenticatedUser domain context.
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status": "error", "message": "Missing authorization token"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = verify_supabase_jwt(token)

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status": "error", "message": "Malformed token: missing subject (sub)"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = payload.get("email") or f"{user_id}@supabase.user"
    user_metadata = payload.get("user_metadata") or {}
    name = user_metadata.get("name") or user_metadata.get("full_name") or ""
    role = payload.get("role") or "authenticated"

    # Ensure profile row exists in local DB for foreign key consistency
    profile = db.query(Profile).filter(Profile.id == user_id).first()
    if profile is None:
        profile = Profile(
            id=user_id,
            email=email,
            name=name,
            role=role,
        )
        db.add(profile)
        try:
            db.commit()
            db.refresh(profile)
        except Exception:
            db.rollback()
            # If concurrent creation occurred, retrieve existing
            profile = db.query(Profile).filter(Profile.id == user_id).first()

    # Automatically ensure starter data for demo user
    if email == "demo@example.com":
        from app.services.seed_service import ensure_user_seeded
        ensure_user_seeded(db, user_id=user_id, email=email, name=name)

    return AuthenticatedUser(
        id=user_id,
        email=email,
        name=name,
        role=role,
    )
