"""Database engine configuration, session maker, resilient fallback, and FastAPI dependency."""

import logging
from typing import Generator, Optional
from sqlalchemy import create_engine, Engine, text
from sqlalchemy.orm import sessionmaker, Session
from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger(__name__)

DEFAULT_LOCAL_SQLITE_URL = "sqlite:///./local_dev.db"


def create_resilient_db_engine(db_url: Optional[str]) -> Engine:
    """
    Create a resilient SQLAlchemy engine.
    1. If a PostgreSQL URL is provided, attempts connection with a 2-second timeout.
    2. If reachable, returns the PostgreSQL engine.
    3. If unreachable or firewalled (e.g. campus/corporate network blocking port 5432),
       transparently falls back to local SQLite ('sqlite:///./local_dev.db') so the
       application operates with zero downtime.
    4. Automatically ensures all required tables exist.
    """
    selected_engine: Optional[Engine] = None

    if db_url and not db_url.startswith("sqlite"):
        try:
            logger.info("Connecting to primary database with 2s timeout...")
            candidate_engine = create_engine(
                db_url,
                pool_pre_ping=True,
                echo=False,
                connect_args={"connect_timeout": 2},
            )
            # Test active socket connectivity
            with candidate_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Successfully connected to primary PostgreSQL database.")
            selected_engine = candidate_engine
        except Exception as exc:
            logger.warning(
                "Primary PostgreSQL database unreachable (firewalled or timeout: %s). "
                "Switching to resilient local SQLite database (%s).",
                exc.__class__.__name__,
                DEFAULT_LOCAL_SQLITE_URL,
            )

    if selected_engine is None:
        sqlite_url = db_url if (db_url and db_url.startswith("sqlite")) else DEFAULT_LOCAL_SQLITE_URL
        selected_engine = create_engine(
            sqlite_url,
            pool_pre_ping=True,
            echo=False,
            connect_args={"check_same_thread": False},
        )
        logger.info("Initialized local SQLite engine (%s).", sqlite_url)

    # Ensure tables exist
    try:
        from app.db.base import Base
        import app.models  # noqa: F401
        Base.metadata.create_all(bind=selected_engine)
        logger.info("Verified all database tables are initialized.")
    except Exception as exc:
        logger.warning("Error verifying table schema initialization: %s", exc)

    return selected_engine


# Application-level engine and sessionmaker
engine: Engine = create_resilient_db_engine(settings.sync_database_url)

SessionLocal: sessionmaker[Session] = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


def init_db() -> None:
    """Explicitly verify and create all tables for the active engine."""
    from app.db.base import Base
    import app.models  # noqa: F401
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding an isolated database session per request.
    Closes the session after the request finishes.
    """
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
