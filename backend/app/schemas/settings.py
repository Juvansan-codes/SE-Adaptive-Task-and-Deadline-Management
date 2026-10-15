"""Pydantic schemas for Settings and User Preferences REST endpoints."""

from typing import List, Optional, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel

DayOfWeek = Literal[
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]
BufferStrategy = Literal["tight", "moderate", "relaxed"]


class DayAvailabilitySchema(BaseModel):
    """Configuration for a single day's study window."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    day: DayOfWeek
    label: str
    enabled: bool
    start_time: str = Field(pattern=r"^\d{2}:\d{2}$")
    end_time: str = Field(pattern=r"^\d{2}:\d{2}$")

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        parts = v.strip().split(":")
        if len(parts) != 2:
            raise ValueError("Time must be in HH:MM 24-hour format")
        h, m = int(parts[0]), int(parts[1])
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError("Hours must be 00-23 and minutes 00-59")
        return f"{h:02d}:{m:02d}"


class UserProfileSchema(BaseModel):
    """User profile response."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    id: str
    name: str
    email: str
    timezone: str
    role: Optional[str] = "student"


class UserPreferencesSchema(BaseModel):
    """User scheduling and notification preferences response."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    enable_deadline_reminders: bool
    enable_schedule_updates: bool
    default_task_duration_minutes: int
    daily_focus_hours_limit: float
    buffer_strategy: BufferStrategy


class SettingsStateResponse(BaseModel):
    """Unified settings payload matching frontend SettingsState interface."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    profile: UserProfileSchema
    preferences: UserPreferencesSchema
    availability: List[DayAvailabilitySchema]


class UpdateProfileRequest(BaseModel):
    """Payload to update profile information."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    timezone: Optional[str] = Field(default=None, max_length=50)
    role: Optional[str] = Field(default=None, max_length=30)

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and isinstance(v, str):
            stripped = v.strip()
            if not stripped:
                raise ValueError("Name cannot be empty or whitespace only")
            return stripped
        return v


class UpdatePreferencesRequest(BaseModel):
    """Payload to update user preferences."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    enable_deadline_reminders: Optional[bool] = None
    enable_schedule_updates: Optional[bool] = None
    default_task_duration_minutes: Optional[int] = Field(default=None, gt=0, le=1440)
    daily_focus_hours_limit: Optional[float] = Field(default=None, gt=0, le=24)
    buffer_strategy: Optional[BufferStrategy] = None


class UpdateSettingsRequest(BaseModel):
    """Partial update payload across settings domains."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    profile: Optional[UpdateProfileRequest] = None
    preferences: Optional[UpdatePreferencesRequest] = None
    availability: Optional[List[DayAvailabilitySchema]] = None
