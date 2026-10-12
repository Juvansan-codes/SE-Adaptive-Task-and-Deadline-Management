"""SQLAlchemy 2.x User Availability model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.profile import Profile


class UserAvailability(Base):
    """
    Weekly schedule focus hour availability by day.
    """

    __tablename__ = "user_availability"

    __table_args__ = (
        CheckConstraint(
            "day IN ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')",
            name="chk_availability_day",
        ),
        UniqueConstraint("user_id", "day", name="uq_user_availability_day"),
    )

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="Availability record UUID",
    )
    user_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    day: Mapped[str] = mapped_column(String(20), nullable=False)
    label: Mapped[str] = mapped_column(String(30), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    start_time: Mapped[str] = mapped_column(String(10), default="09:00", nullable=False)
    end_time: Mapped[str] = mapped_column(String(10), default="17:00", nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped["Profile"] = relationship("Profile", back_populates="availability")

    def __repr__(self) -> str:
        return f"<UserAvailability user_id={self.user_id} day={self.day} enabled={self.enabled}>"
