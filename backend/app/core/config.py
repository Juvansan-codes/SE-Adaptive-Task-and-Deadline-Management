"""Application settings and environment configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Application Metadata
    app_env: str = Field(default="development", description="Runtime environment")
    app_title: str = Field(
        default="Adaptive Task & Deadline Management API",
        description="FastAPI application title",
    )
    app_version: str = Field(default="0.1.0", description="API version")
    api_prefix: str = Field(default="/api", description="Root API router prefix")

    # CORS Configuration
    frontend_origin: str = Field(
        default="http://localhost:3000",
        description="Allowed frontend origin for CORS",
    )

    # Database Configuration
    database_url: Optional[str] = Field(
        default=None,
        description="PostgreSQL / Supabase connection URI",
    )

    # Supabase Authentication Configuration
    supabase_url: Optional[str] = Field(
        default=None,
        description="Supabase project URL",
    )
    supabase_jwt_secret: Optional[str] = Field(
        default=None,
        description="Supabase JWT secret for token verification",
    )
    supabase_anon_key: Optional[str] = Field(
        default=None,
        description="Supabase publishable anon key",
    )

    @property
    def is_database_configured(self) -> bool:
        """Check whether a non-empty database URL is provided."""
        return bool(self.database_url and self.database_url.strip())

    @property
    def sync_database_url(self) -> Optional[str]:
        """
        Normalize database URL for SQLAlchemy 2.x with psycopg (v3) driver.
        Supabase URIs beginning with 'postgresql://' or 'postgres://' are
        mapped to 'postgresql+psycopg://'.
        """
        if not self.is_database_configured:
            return None

        url = self.database_url.strip()
        if url.startswith("postgres://"):
            return "postgresql+psycopg://" + url[len("postgres://"):]
        if url.startswith("postgresql://") and not url.startswith("postgresql+"):
            return "postgresql+psycopg://" + url[len("postgresql://"):]
        return url


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings instance."""
    return Settings()


settings = get_settings()
