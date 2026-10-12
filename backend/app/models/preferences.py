"""SQLAlchemy 2.x User Preferences model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import (
    String,
    Boolean,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    CheckConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.profile import Profile


class UserPreferences(Base):
    """
    User-specific notification, focus limit, and scheduling buffer preferences.
    """

    __tablename__ = "user_preferences"

    __table_args__ = (
        CheckConstraint(
            "buffer_strategy IN ('tight', 'moderate', 'relaxed')",
            name="chk_preference_buffer_strategy",
        ),
        CheckConstraint(
            "default_task_duration_minutes > 0 AND default_task_duration_minutes <= 1440",
            name="chk_preference_default_duration",
        ),
        CheckConstraint(
            "daily_focus_hours_limit > 0 AND daily_focus_hours_limit <= 24",
            name="chk_preference_focus_limit",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="Preferences record UUID",
    )
    user_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    enable_deadline_reminders: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    enable_schedule_updates: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    default_task_duration_minutes: Mapped[int] = mapped_column(
        Integer, default=60, nullable=False
    )
    daily_focus_hours_limit: Mapped[float] = mapped_column(
        Float, default=8.0, nullable=False
    )
    buffer_strategy: Mapped[str] = mapped_column(
        String(20), default="moderate", nullable=False
    )

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
    user: Mapped["Profile"] = relationship("Profile", back_populates="preferences")

    def __repr__(self) -> str:
        return f"<UserPreferences user_id={self.user_id} buffer={self.buffer_strategy}>"
