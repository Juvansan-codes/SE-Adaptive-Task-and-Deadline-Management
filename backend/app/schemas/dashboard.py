"""Pydantic schemas for Dashboard REST endpoints."""

from typing import List, Optional, Literal
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.schemas.task import TaskResponse
from app.services.scheduling.schemas import RiskLevel


class DashboardOverviewResponse(BaseModel):
    """High-level metrics for dashboard cards."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    available_time_hours: float
    scheduled_workload_hours: float
    overall_progress: int
    pending_tasks_count: int
    at_risk_tasks_count: int
    completed_today_count: int


class RecommendedTaskResponse(BaseModel):
    """Next-task recommendation payload."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    task: TaskResponse
    recommendation_reason: str
    urgency_label: Optional[str] = None


class AtRiskTaskResponse(BaseModel):
    """Deadline risk item."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    task: TaskResponse
    risk_level: RiskLevel
    risk_reason: str


class ScheduleBlockResponse(BaseModel):
    """Chronological schedule block for today."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    id: str
    start_time: str
    end_time: str
    title: str
    category: str
    task_id: Optional[str] = None
    status: Literal["completed", "current", "upcoming"]
    duration_minutes: int
