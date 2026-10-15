"""Schemas package exports."""

from app.schemas.task import (
    TaskPriority,
    TaskDifficulty,
    TaskStatus,
    CreateTaskRequest,
    UpdateTaskRequest,
    TaskResponse,
    TaskFilterParams,
)
from app.schemas.dashboard import (
    DashboardOverviewResponse,
    RecommendedTaskResponse,
    AtRiskTaskResponse,
    ScheduleBlockResponse,
)
from app.schemas.schedule import (
    ScheduleItemResponse,
    DayScheduleResponse,
    ScheduleUpdateResponse,
    RegenerateScheduleRequest,
)
from app.schemas.settings import (
    DayAvailabilitySchema,
    UserProfileSchema,
    UserPreferencesSchema,
    SettingsStateResponse,
    UpdateProfileRequest,
    UpdatePreferencesRequest,
    UpdateSettingsRequest,
)

__all__ = [
    "TaskPriority",
    "TaskDifficulty",
    "TaskStatus",
    "CreateTaskRequest",
    "UpdateTaskRequest",
    "TaskResponse",
    "TaskFilterParams",
    "DashboardOverviewResponse",
    "RecommendedTaskResponse",
    "AtRiskTaskResponse",
    "ScheduleBlockResponse",
    "ScheduleItemResponse",
    "DayScheduleResponse",
    "ScheduleUpdateResponse",
    "RegenerateScheduleRequest",
    "DayAvailabilitySchema",
    "UserProfileSchema",
    "UserPreferencesSchema",
    "SettingsStateResponse",
    "UpdateProfileRequest",
    "UpdatePreferencesRequest",
    "UpdateSettingsRequest",
]

