"""Settings service managing user profile, weekly availability, and preferences."""

from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.profile import Profile
from app.models.availability import UserAvailability
from app.models.preferences import UserPreferences
from app.schemas.settings import (
    DayAvailabilitySchema,
    UserProfileSchema,
    UserPreferencesSchema,
    SettingsStateResponse,
    UpdateProfileRequest,
    UpdatePreferencesRequest,
    UpdateSettingsRequest,
)
from app.services.scheduling.capacity import parse_time_string, WEEKDAY_NAMES

DEFAULT_AVAILABILITY_CONFIG = [
    ("monday", "Monday", True, "09:00", "17:00"),
    ("tuesday", "Tuesday", True, "09:00", "17:00"),
    ("wednesday", "Wednesday", True, "09:00", "17:00"),
    ("thursday", "Thursday", True, "09:00", "17:00"),
    ("friday", "Friday", True, "09:00", "16:00"),
    ("saturday", "Saturday", True, "10:00", "14:00"),
    ("sunday", "Sunday", False, "10:00", "14:00"),
]


class SettingsService:
    """Encapsulates profile, preference, and weekly availability operations."""

    @staticmethod
    def get_or_create_availability(
        db: Session, user_id: str
    ) -> List[UserAvailability]:
        """Retrieve weekly availability for user, auto-seeding defaults if not yet created."""
        existing = (
            db.query(UserAvailability)
            .filter(UserAvailability.user_id == user_id)
            .all()
        )

        if not existing:
            created_records = []
            for day, label, enabled, start_t, end_t in DEFAULT_AVAILABILITY_CONFIG:
                record = UserAvailability(
                    user_id=user_id,
                    day=day,
                    label=label,
                    enabled=enabled,
                    start_time=start_t,
                    end_time=end_t,
                )
                db.add(record)
                created_records.append(record)
            try:
                db.commit()
                for r in created_records:
                    db.refresh(r)
                existing = created_records
            except Exception:
                db.rollback()
                existing = (
                    db.query(UserAvailability)
                    .filter(UserAvailability.user_id == user_id)
                    .all()
                )

        # Return strictly in Monday -> Sunday order
        day_order = {name: i for i, name in enumerate(WEEKDAY_NAMES)}
        return sorted(existing, key=lambda a: day_order.get(a.day.lower(), 99))

    @staticmethod
    def get_or_create_preferences(
        db: Session, user_id: str
    ) -> UserPreferences:
        """Retrieve user preferences, auto-seeding defaults if not yet created."""
        prefs = (
            db.query(UserPreferences)
            .filter(UserPreferences.user_id == user_id)
            .first()
        )
        if not prefs:
            prefs = UserPreferences(
                user_id=user_id,
                enable_deadline_reminders=True,
                enable_schedule_updates=True,
                default_task_duration_minutes=60,
                daily_focus_hours_limit=6.5,
                buffer_strategy="moderate",
            )
            db.add(prefs)
            try:
                db.commit()
                db.refresh(prefs)
            except Exception:
                db.rollback()
                prefs = (
                    db.query(UserPreferences)
                    .filter(UserPreferences.user_id == user_id)
                    .first()
                )
        return prefs

    @staticmethod
    def get_profile(db: Session, user_id: str) -> Profile:
        """Retrieve user profile, auto-creating a standard profile if not present."""
        profile = db.query(Profile).filter(Profile.id == user_id).first()
        if not profile:
            profile = Profile(
                id=user_id,
                email=f"{user_id}@supabase.user",
                name="Student",
                timezone="UTC",
                role="student",
            )
            db.add(profile)
            try:
                db.commit()
                db.refresh(profile)
            except Exception:
                db.rollback()
                profile = db.query(Profile).filter(Profile.id == user_id).first()
        return profile

    @staticmethod
    def get_settings_state(db: Session, user_id: str) -> SettingsStateResponse:
        """Return the complete unified settings state."""
        profile = SettingsService.get_profile(db, user_id)
        preferences = SettingsService.get_or_create_preferences(db, user_id)
        availability = SettingsService.get_or_create_availability(db, user_id)

        return SettingsStateResponse(
            profile=UserProfileSchema.model_validate(profile),
            preferences=UserPreferencesSchema.model_validate(preferences),
            availability=[
                DayAvailabilitySchema.model_validate(a) for a in availability
            ],
        )

    @staticmethod
    def update_profile(
        db: Session, user_id: str, payload: UpdateProfileRequest
    ) -> Profile:
        """Update profile fields."""
        profile = SettingsService.get_profile(db, user_id)
        if payload.name is not None:
            profile.name = payload.name
        if payload.timezone is not None:
            profile.timezone = payload.timezone
        if payload.role is not None:
            profile.role = payload.role

        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def update_preferences(
        db: Session, user_id: str, payload: UpdatePreferencesRequest
    ) -> UserPreferences:
        """Update preference fields."""
        prefs = SettingsService.get_or_create_preferences(db, user_id)
        if payload.enable_deadline_reminders is not None:
            prefs.enable_deadline_reminders = payload.enable_deadline_reminders
        if payload.enable_schedule_updates is not None:
            prefs.enable_schedule_updates = payload.enable_schedule_updates
        if payload.default_task_duration_minutes is not None:
            prefs.default_task_duration_minutes = payload.default_task_duration_minutes
        if payload.daily_focus_hours_limit is not None:
            prefs.daily_focus_hours_limit = payload.daily_focus_hours_limit
        if payload.buffer_strategy is not None:
            prefs.buffer_strategy = payload.buffer_strategy

        db.commit()
        db.refresh(prefs)
        return prefs

    @staticmethod
    def update_weekly_availability(
        db: Session, user_id: str, new_avail: List[DayAvailabilitySchema]
    ) -> List[UserAvailability]:
        """Update weekly availability, validating time windows and uniqueness."""
        seen_days = set()
        for item in new_avail:
            day_lower = item.day.lower()
            if day_lower in seen_days:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "status": "error",
                        "message": f"Duplicate entry for day '{item.day}'",
                    },
                )
            seen_days.add(day_lower)

            if item.enabled:
                t_start = parse_time_string(item.start_time)
                t_end = parse_time_string(item.end_time)
                if not t_start or not t_end or t_end <= t_start:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "status": "error",
                            "message": f"Invalid time window for {item.day}: start_time ({item.start_time}) must precede end_time ({item.end_time})",
                        },
                    )

        # Retrieve or seed existing records
        existing = SettingsService.get_or_create_availability(db, user_id)
        existing_map = {a.day.lower(): a for a in existing}

        for item in new_avail:
            day_lower = item.day.lower()
            if day_lower in existing_map:
                record = existing_map[day_lower]
                record.label = item.label
                record.enabled = item.enabled
                record.start_time = item.start_time
                record.end_time = item.end_time
            else:
                new_record = UserAvailability(
                    user_id=user_id,
                    day=day_lower,
                    label=item.label,
                    enabled=item.enabled,
                    start_time=item.start_time,
                    end_time=item.end_time,
                )
                db.add(new_record)

        db.commit()
        return SettingsService.get_or_create_availability(db, user_id)

    @staticmethod
    def reset_weekly_availability(
        db: Session, user_id: str
    ) -> List[UserAvailability]:
        """Reset weekly availability to standard defaults."""
        existing = SettingsService.get_or_create_availability(db, user_id)
        existing_map = {a.day.lower(): a for a in existing}

        for day, label, enabled, start_t, end_t in DEFAULT_AVAILABILITY_CONFIG:
            if day in existing_map:
                r = existing_map[day]
                r.label = label
                r.enabled = enabled
                r.start_time = start_t
                r.end_time = end_t
            else:
                db.add(
                    UserAvailability(
                        user_id=user_id,
                        day=day,
                        label=label,
                        enabled=enabled,
                        start_time=start_t,
                        end_time=end_t,
                    )
                )

        db.commit()
        return SettingsService.get_or_create_availability(db, user_id)

    @staticmethod
    def update_settings(
        db: Session, user_id: str, payload: UpdateSettingsRequest
    ) -> SettingsStateResponse:
        """Perform partial or full settings update across profile, preferences, and availability."""
        if payload.profile is not None:
            SettingsService.update_profile(db, user_id, payload.profile)
        if payload.preferences is not None:
            SettingsService.update_preferences(db, user_id, payload.preferences)
        if payload.availability is not None:
            SettingsService.update_weekly_availability(
                db, user_id, payload.availability
            )

        return SettingsService.get_settings_state(db, user_id)
