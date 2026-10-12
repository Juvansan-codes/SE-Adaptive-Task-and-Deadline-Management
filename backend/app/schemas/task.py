"""Pydantic schemas for Task requests, updates, responses, and filters."""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel

TaskPriority = Literal["low", "medium", "high", "critical"]
TaskDifficulty = Literal["easy", "medium", "hard"]
TaskStatus = Literal["pending", "in_progress", "completed", "overdue"]
TaskSortBy = Literal["deadline", "priority", "title", "status", "progress", "updatedAt", "updated_at"]
SortDirection = Literal["asc", "desc"]


class TaskBase(BaseModel):
    """Shared task attributes."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    title: str = Field(min_length=1, max_length=120)
    description: Optional[str] = Field(default="", max_length=1000)
    category: str = Field(min_length=1, max_length=50)
    deadline: datetime
    priority: TaskPriority = "medium"
    difficulty: TaskDifficulty = "medium"
    estimated_duration: float = Field(gt=0, le=500)
    completed_duration: Optional[float] = Field(default=0.0, ge=0)
    status: Optional[TaskStatus] = "pending"

    @field_validator("title", "category", mode="before")
    @classmethod
    def strip_required_strings(cls, v: str) -> str:
        if isinstance(v, str):
            stripped = v.strip()
            if not stripped:
                raise ValueError("String must not be empty or whitespace only")
            return stripped
        return v

    @field_validator("description", mode="before")
    @classmethod
    def strip_description(cls, v: Optional[str]) -> str:
        if isinstance(v, str):
            return v.strip()
        return "" if v is None else v


class CreateTaskRequest(TaskBase):
    """Payload to create a new task."""
    pass


class UpdateTaskRequest(BaseModel):
    """Partial update payload for existing task."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    title: Optional[str] = Field(default=None, min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=1000)
    category: Optional[str] = Field(default=None, min_length=1, max_length=50)
    deadline: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    difficulty: Optional[TaskDifficulty] = None
    estimated_duration: Optional[float] = Field(default=None, gt=0, le=500)
    completed_duration: Optional[float] = Field(default=None, ge=0)
    status: Optional[TaskStatus] = None

    @field_validator("title", "category", mode="before")
    @classmethod
    def strip_optional_strings(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and isinstance(v, str):
            stripped = v.strip()
            if not stripped:
                raise ValueError("String must not be empty or whitespace only")
            return stripped
        return v

    @field_validator("description", mode="before")
    @classmethod
    def strip_optional_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and isinstance(v, str):
            return v.strip()
        return v


class TaskResponse(BaseModel):
    """
    Task representation returned to frontend clients.
    Uses camelCase serialization to match existing TypeScript contracts.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    id: str
    title: str
    description: str
    category: str
    deadline: datetime
    priority: TaskPriority
    difficulty: TaskDifficulty
    estimated_duration: float
    completed_duration: float
    remaining_duration: float
    progress: int
    status: TaskStatus
    created_at: datetime
    updated_at: datetime


class TaskFilterParams(BaseModel):
    """Query parameters for task filtering and sorting."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    search: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    sort_by: Optional[str] = None
    sort_direction: Optional[SortDirection] = "asc"
