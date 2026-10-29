"""Schedule service coordinating timeline generation and adaptive rescheduling."""

from datetime import date, datetime, timedelta, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.task import Task
from app.models.preferences import UserPreferences
from app.schemas.schedule import (
    DayScheduleResponse,
    ScheduleItemResponse,
    ScheduleUpdateResponse,
    SimulationDisruptionInput,
    DisruptionSimulationResult,
    ApplyStrategyRequest,
    ApplyStrategyResponse,
)
from app.services.settings_service import SettingsService
from app.services.scheduling.capacity import resolve_timezone
from app.services.scheduling.engine import (
    generate_daily_schedule,
    detect_schedule_regeneration_triggers,
)
from app.services.scheduling.simulation import simulate_cascading_disruption


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

    @staticmethod
    def simulate_disruption(
        db: Session,
        user_id: str,
        disruption_input: SimulationDisruptionInput,
        reference_time: Optional[datetime] = None,
    ) -> DisruptionSimulationResult:
        """Execute sandbox disruption simulation and return candidate recovery plans."""
        profile = SettingsService.get_profile(db, user_id)
        tasks = db.query(Task).filter(Task.user_id == user_id).all()
        availability_list = SettingsService.get_or_create_availability(db, user_id)
        preferences = SettingsService.get_or_create_preferences(db, user_id)

        return simulate_cascading_disruption(
            tasks=tasks,
            availability_list=availability_list,
            preferences=preferences,
            disruption_input=disruption_input,
            user_timezone=profile.timezone,
            reference_time=reference_time,
        )

    @staticmethod
    def apply_recovery_strategy(
        db: Session,
        user_id: str,
        request: ApplyStrategyRequest,
    ) -> ApplyStrategyResponse:
        """Commit an approved recovery strategy to the persistent database."""
        action = request.action_payload.get("action")
        applied_name = "Recovery Strategy"
        changes: List[str] = []

        if action == "update_buffer_strategy":
            new_strategy = request.action_payload.get("buffer_strategy", "tight")
            prefs = SettingsService.get_or_create_preferences(db, user_id)
            old_strat = prefs.buffer_strategy
            prefs.buffer_strategy = new_strategy
            db.commit()
            applied_name = "Elastic Buffer Compression"
            changes.append(
                f"Schedule buffer strategy updated from '{old_strat}' to '{new_strategy}'."
            )

        elif action == "defer_tasks":
            task_ids = request.action_payload.get("task_ids", [])
            days_defer = int(request.action_payload.get("days_defer", 3))
            deferred_titles = []
            for t_id in task_ids:
                task = (
                    db.query(Task)
                    .filter(Task.id == t_id, Task.user_id == user_id)
                    .first()
                )
                if task:
                    task.deadline = task.deadline + timedelta(days=days_defer)
                    deferred_titles.append(task.title)
            db.commit()
            applied_name = "Priority-Preserving Triage"
            changes.append(
                f"Deferred {len(deferred_titles)} tasks by {days_defer} days: {', '.join(deferred_titles)}."
            )

        elif action == "extend_deadline":
            task_id = request.action_payload.get("task_id")
            new_dl_str = request.action_payload.get("new_deadline")
            task = (
                db.query(Task)
                .filter(Task.id == task_id, Task.user_id == user_id)
                .first()
            )
            if task and new_dl_str:
                new_dl = datetime.fromisoformat(new_dl_str)
                task.deadline = new_dl
                db.commit()
                applied_name = "Surgical Deadline Extension"
                changes.append(
                    f"Extended deadline for '{task.title}' to {new_dl.strftime('%b %d, %Y %H:%M')}."
                )

        else:
            applied_name = "Automatic Resilience"
            changes.append("No modifications needed; schedule is naturally resilient.")

        return ApplyStrategyResponse(
            success=True,
            message="Recovery strategy successfully applied.",
            applied_strategy_name=applied_name,
            changes_applied=changes,
        )
