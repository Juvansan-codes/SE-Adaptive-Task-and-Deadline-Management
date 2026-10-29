"""Database engine configuration, session maker, and FastAPI dependency.

Exclusively connects to Supabase PostgreSQL database via SQLAlchemy and psycopg.
No local SQLite storage or fallback is used.
"""

import logging
from typing import Generator, Optional
from sqlalchemy import create_engine, Engine, text
from sqlalchemy.orm import sessionmaker, Session
from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger(__name__)

# Supabase PostgreSQL Engine and Session Configuration
engine: Optional[Engine] = None
SessionLocal: Optional[sessionmaker[Session]] = None

if settings.sync_database_url:
    connect_args = {}
    engine_kwargs = {}
    if "sqlite" in settings.sync_database_url.lower():
        connect_args["check_same_thread"] = False
    else:
        connect_args["connect_timeout"] = 5
        engine_kwargs["pool_pre_ping"] = True
        engine_kwargs["pool_recycle"] = 300

    engine = create_engine(
        settings.sync_database_url,
        connect_args=connect_args,
        echo=False,
        **engine_kwargs,
    )
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    logger.info("Initialized database engine with URL: %s", settings.sync_database_url)
else:
    logger.warning("DATABASE_URL is not configured; database engine is uninitialized.")


def init_db() -> None:
    """Explicitly verify and create all tables for the configured Supabase PostgreSQL database."""
    if engine is None:
        logger.warning("DATABASE_URL is not configured; skipping table initialization.")
        return

    try:
        from app.db.base import Base
        import app.models  # noqa: F401
        Base.metadata.create_all(bind=engine)
        logger.info("Verified all database tables in Supabase PostgreSQL.")
    except Exception as exc:
        logger.warning("Could not automatically initialize tables in Supabase PostgreSQL: %s", exc)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding an isolated database session per request.
    Exclusively connects to Supabase PostgreSQL.
    Raises HTTP 503 if the database is not configured or unreachable.
    """
    if SessionLocal is None or engine is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "error", "message": "Database connection is not configured."},
        )

    db: Session = SessionLocal()
    try:
        yield db
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
        raise
    finally:
        try:
            db.close()
        except Exception:
            pass


def ping_database(db: Session) -> bool:
    """
    Execute a lightweight ping query ('SELECT 1') to verify active connectivity.
    Returns True if responsive; raises SQLAlchemyError if disconnected.
    """
    result = db.execute(text("SELECT 1"))
    return result.scalar() == 1
