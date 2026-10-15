"""Data transfer objects and internal schemas for the Adaptive Scheduling Engine."""

from datetime import date, datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

RiskLevel = Literal["critical", "high", "moderate"]
ScheduleItemStatus = Literal["pending", "in_progress", "completed", "overdue"]
BufferStrategy = Literal["tight", "moderate", "relaxed"]


class DayCapacity(BaseModel):
    """Calculated capacity metrics for a single calendar day."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    date: date
    day_of_week: str
    enabled: bool
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    raw_window_hours: float = 0.0
    focus_limit_hours: float = 0.0
    available_hours: float = 0.0
    buffer_hours: float = 0.0
    allocatable_hours: float = 0.0


class TaskScoreBreakdown(BaseModel):
    """Detailed scoring components for ranking transparency."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    task_id: str
    total_score: float
    priority_score: float
    urgency_score: float
    difficulty_score: float
    in_progress_bonus: float
    feasibility_score: float
    reason: str


class RankedTask(BaseModel):
    """Task paired with its deterministic ranking score and breakdown."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    task_id: str
    rank: int
    score: float
    score_breakdown: TaskScoreBreakdown


class ScheduleBlockItem(BaseModel):
    """Individual scheduled work block on the daily timeline."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: str
    task_id: Optional[str] = None
    title: str
    category: str
    start_time: str
    end_time: str
    duration_minutes: int
    status: ScheduleItemStatus
    is_recommended: bool = False
    recommendation_reason: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None


class DailyScheduleResult(BaseModel):
    """Complete generated daily schedule timeline matching frontend contracts."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    date: str
    day_of_week: str
    formatted_date: str
    is_today: bool
    items: List[ScheduleBlockItem] = Field(default_factory=list)
    total_scheduled_hours: float = 0.0
    available_hours: float = 0.0
    unscheduled_tasks_count: int = 0


class TaskRiskAssessment(BaseModel):
    """Deadline risk classification for a task."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    task_id: str
    risk_level: RiskLevel
    risk_reason: str
    hours_until_deadline: float
    remaining_duration_hours: float
    available_capacity_before_deadline: float
    is_overdue: bool = False


class TaskRecommendation(BaseModel):
    """Recommendation for the next task the user should focus on."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    task_id: str
    title: str
    category: str
    recommendation_reason: str
    urgency_label: str
    priority: str
    remaining_duration: float
    progress: int
    status: str


class ScheduleRegenerationTrigger(BaseModel):
    """Assessment of whether the active schedule requires adaptive regeneration."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    needs_regeneration: bool
    reasons: List[str] = Field(default_factory=list)
    changes: List[str] = Field(default_factory=list)
    recommended_action: Optional[str] = None
