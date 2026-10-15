"""Pydantic schemas for Schedule REST endpoints."""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.services.scheduling.schemas import ScheduleItemStatus


class ScheduleItemResponse(BaseModel):
    """Timeline item representing an allocated task block."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    id: str
    task_id: Optional[str] = None
    title: str
    category: str
    start_time: str
    end_time: str
    duration_minutes: int
    status: ScheduleItemStatus
    is_recommended: Optional[bool] = False
    recommendation_reason: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None


class DayScheduleResponse(BaseModel):
    """Daily schedule response matching frontend DaySchedule interface."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    date: str
    day_of_week: str
    formatted_date: str
    is_today: bool
    items: List[ScheduleItemResponse]
    total_scheduled_hours: float
    available_hours: float


class ScheduleUpdateResponse(BaseModel):
    """Banner notification indicating adaptive schedule adjustment."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    id: str
    title: str
    timestamp: str
    summary: Optional[str] = None
    changes: List[str]
    recommended_action: Optional[str] = None


class RegenerateScheduleRequest(BaseModel):
    """Payload to trigger schedule recalculation."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    date: Optional[str] = None
