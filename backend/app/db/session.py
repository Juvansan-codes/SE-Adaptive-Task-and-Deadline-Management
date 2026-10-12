"""Database engine configuration, session maker, and FastAPI dependency."""

from typing import Generator, Optional
from sqlalchemy import create_engine, Engine, text
from sqlalchemy.orm import sessionmaker, Session
from fastapi import HTTPException, status
from app.core.config import settings


def create_db_engine(db_url: Optional[str]) -> Optional[Engine]:
    """
    Create a SQLAlchemy engine if a valid database URL is configured.
    Configures pool_pre_ping for resilient connections with PostgreSQL poolers.
    """
    if not db_url:
        return None

    # Connect args for SQLite if used in test overrides; otherwise PostgreSQL defaults
    connect_args = {}
    if db_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    return create_engine(
        db_url,
        pool_pre_ping=True,
        echo=False,
        connect_args=connect_args,
    )


# Application-level engine and sessionmaker
engine: Optional[Engine] = create_db_engine(settings.sync_database_url)

SessionLocal: Optional[sessionmaker[Session]] = (
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
    if engine is not None
    else None
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding an isolated database session per request.
    Closes the session after the request finishes.
    Raises HTTPException 503 if the database connection string is not configured.
    """
    if SessionLocal is None or not settings.is_database_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "error", "message": "Database connection unavailable"},
        )

    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ping_database(db: Session) -> bool:
    """
    Execute a lightweight ping query ('SELECT 1') to verify active connectivity.
    Returns True if responsive; raises SQLAlchemyError if disconnected.
    """
    result = db.execute(text("SELECT 1"))
    return result.scalar() == 1
