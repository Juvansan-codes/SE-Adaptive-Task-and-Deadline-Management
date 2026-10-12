"""SQLAlchemy 2.x Declarative Base for domain models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.
    Domain models implemented in subsequent phases will inherit from this Base.
    """
    pass
