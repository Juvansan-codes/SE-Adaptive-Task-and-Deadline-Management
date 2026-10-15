"""Schedule service coordinating timeline generation and adaptive rescheduling."""

from datetime import date, datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.task import Task
from app.schemas.schedule import (
    DayScheduleResponse,
    ScheduleItemResponse,
    ScheduleUpdateResponse,
)
from app.services.settings_service import SettingsService
from app.services.scheduling.capacity import resolve_timezone
from app.services.scheduling.engine import (
    generate_daily_schedule,
    detect_schedule_regeneration_triggers,
)


class ScheduleService:
    """Manages schedule timeline calculation and adaptive updates."""

    @staticmethod
    def get_daily_schedule(
        db: Session,
        user_id: str,
        date_str: Optional[str] = None,
        reference_time: Optional[datetime] = None,
    ) -> DayScheduleResponse:
        """
        Generate schedule for requested ISO calendar date (or today in user timezone).
        Fully dynamic, conflict-free, and idempotent.
        """
        profile = SettingsService.get_profile(db, user_id)
        user_tz = resolve_timezone(profile.timezone)

        now_user = reference_time or datetime.now(user_tz)
        if now_user.tzinfo is None:
            now_user = now_user.replace(tzinfo=user_tz)
        else:
            now_user = now_user.astimezone(user_tz)

        if date_str and date_str.strip():
            try:
                target_date = date.fromisoformat(date_str.strip())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "status": "error",
                        "message": "Invalid date format. Expected YYYY-MM-DD",
                    },
                )
        else:
            target_date = now_user.date()

        tasks = db.query(Task).filter(Task.user_id == user_id).all()
        availability_list = SettingsService.get_or_create_availability(
            db, user_id
        )
        preferences = SettingsService.get_or_create_preferences(db, user_id)

        sched_result = generate_daily_schedule(
            target_date=target_date,
            tasks=tasks,
            availability_list=availability_list,
            preferences=preferences,
            user_timezone=profile.timezone,
            reference_time=now_user,
        )

        return DayScheduleResponse(
            date=sched_result.date,
            day_of_week=sched_result.day_of_week,
            formatted_date=sched_result.formatted_date,
            is_today=sched_result.is_today,
            items=[
                ScheduleItemResponse(
                    id=item.id,
                    task_id=item.task_id,
                    title=item.title,
                    category=item.category,
                    start_time=item.start_time,
                    end_time=item.end_time,
                    duration_minutes=item.duration_minutes,
                    status=item.status,
                    is_recommended=item.is_recommended,
                    recommendation_reason=item.recommendation_reason,
                    priority=item.priority,
                    notes=item.notes,
                )
                for item in sched_result.items
            ],
            total_scheduled_hours=sched_result.total_scheduled_hours,
            available_hours=sched_result.available_hours,
        )

    @staticmethod
    def get_schedule_update(
        db: Session,
        user_id: str,
        reference_time: Optional[datetime] = None,
    ) -> Optional[ScheduleUpdateResponse]:
        """Detect whether timeline adjustment notifications are needed."""
        profile = SettingsService.get_profile(db, user_id)
        user_tz = resolve_timezone(profile.timezone)

        now_user = reference_time or datetime.now(user_tz)
        if now_user.tzinfo is None:
            now_user = now_user.replace(tzinfo=user_tz)

        today_date = now_user.date()
        today_sched = ScheduleService.get_daily_schedule(
            db, user_id, str(today_date), now_user
        )
        scheduled_ids = [
            item.task_id for item in today_sched.items if item.task_id
        ]

        tasks = db.query(Task).filter(Task.user_id == user_id).all()
        trigger = detect_schedule_regeneration_triggers(
            tasks=tasks,
            current_scheduled_task_ids=scheduled_ids,
            reference_time=now_user,
        )

        if not trigger.needs_regeneration:
            return None

        return ScheduleUpdateResponse(
            id="update-adaptive",
            title="Schedule Updated",
            timestamp="Just now",
            summary="Adaptive engine adjusted your schedule based on latest progress and deadlines.",
            changes=trigger.changes,
            recommended_action=trigger.recommended_action,
        )

    @staticmethod
    def regenerate_schedule(
        db: Session,
        user_id: str,
        date_str: Optional[str] = None,
        reference_time: Optional[datetime] = None,
    ) -> DayScheduleResponse:
        """Recalculate and return dynamic schedule."""
        return ScheduleService.get_daily_schedule(
            db, user_id, date_str, reference_time
        )
