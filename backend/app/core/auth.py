"""Supabase Auth JWT verification and user identity dependency."""

from typing import Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.profile import Profile


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
    Cryptographically verify Supabase JWT token using HS256 and SUPABASE_JWT_SECRET.
    Rejects tampered, invalid, or expired tokens.
    """
    secret = settings.supabase_jwt_secret
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "error", "message": "Authentication service unconfigured"},
        )

    try:
        # Decode and verify HMAC signature and expiration
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": False,  # Allow varied client audiences if present
            },
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status": "error", "message": "Token has expired"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
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

    return AuthenticatedUser(
        id=user_id,
        email=email,
        name=name,
        role=role,
    )
