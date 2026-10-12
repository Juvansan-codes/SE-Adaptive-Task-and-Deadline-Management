"""SQLAlchemy 2.x Task model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import (
    String,
    Float,
    Integer,
    DateTime,
    ForeignKey,
    Index,
    CheckConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.profile import Profile


class Task(Base):
    """
    Task entity tracking deadlines, workloads, priorities, and progress.
    Fully aligned with the frontend domain model.
    """

    __tablename__ = "tasks"

    __table_args__ = (
        CheckConstraint(
            "priority IN ('low', 'medium', 'high', 'critical')",
            name="chk_task_priority",
        ),
        CheckConstraint(
            "difficulty IN ('easy', 'medium', 'hard')",
            name="chk_task_difficulty",
        ),
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed', 'overdue')",
            name="chk_task_status",
        ),
        CheckConstraint(
            "estimated_duration > 0 AND estimated_duration <= 500",
            name="chk_task_estimated_duration",
        ),
        CheckConstraint(
            "completed_duration >= 0",
            name="chk_task_completed_duration",
        ),
        CheckConstraint(
            "progress >= 0 AND progress <= 100",
            name="chk_task_progress",
        ),
        Index("ix_tasks_user_id_status", "user_id", "status"),
        Index("ix_tasks_user_id_deadline", "user_id", "deadline"),
        Index("ix_tasks_user_id_category", "user_id", "category"),
    )

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: f"task-{uuid.uuid4().hex[:8]}",
        comment="Unique task identifier",
    )
    user_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Owner user ID",
    )
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), default="", nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    deadline: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    priority: Mapped[str] = mapped_column(
        String(20), default="medium", nullable=False, index=True
    )
    difficulty: Mapped[str] = mapped_column(
        String(20), default="medium", nullable=False
    )
    estimated_duration: Mapped[float] = mapped_column(
        Float, nullable=False, comment="Duration in decimal hours"
    )
    completed_duration: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False, comment="Completed duration in decimal hours"
    )
    remaining_duration: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False, comment="Remaining duration in decimal hours"
    )
    progress: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="Completion percentage 0-100"
    )
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False, index=True
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
    user: Mapped["Profile"] = relationship("Profile", back_populates="tasks")

    def __repr__(self) -> str:
        return f"<Task id={self.id} title={self.title} status={self.status}>"
