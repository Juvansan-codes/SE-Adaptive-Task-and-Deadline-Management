"""Dashboard service aggregating metrics, recommendations, at-risk tasks, and schedules."""

from datetime import datetime, timezone
from typing import List, Optional, Dict
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.profile import Profile
from app.schemas.task import TaskResponse
from app.schemas.dashboard import (
    DashboardOverviewResponse,
    RecommendedTaskResponse,
    AtRiskTaskResponse,
    ScheduleBlockResponse,
)
from app.services.settings_service import SettingsService
from app.services.scheduling.capacity import (
    resolve_timezone,
    get_day_capacity,
    parse_time_string,
    WEEKDAY_NAMES,
)
from app.services.scheduling.risk import assess_all_tasks_risk
from app.services.scheduling.engine import (
    generate_daily_schedule,
    get_recommended_next_task,
)


class DashboardService:
    """Computes real-time dashboard analytics from authenticated user data."""

    @staticmethod
    def get_overview(
        db: Session, user_id: str, reference_time: Optional[datetime] = None
    ) -> DashboardOverviewResponse:
        """
        Calculate summary metrics for the active user:
        - availableTimeHours: Capacity for today based on availability & focus limit
        - scheduledWorkloadHours: Total hours allocated in today's generated schedule
        - overallProgress: Total completed / total estimated duration percentage across all tasks
        - pendingTasksCount: Count of pending and in_progress tasks
        - atRiskTasksCount: Count of active tasks flagged at risk
        - completedTodayCount: Tasks marked completed on today's local date
        """
        profile = SettingsService.get_profile(db, user_id)
        user_tz = resolve_timezone(profile.timezone)

        now_user = reference_time or datetime.now(user_tz)
        if now_user.tzinfo is None:
            now_user = now_user.replace(tzinfo=user_tz)
        else:
            now_user = now_user.astimezone(user_tz)

        today_date = now_user.date()

        tasks: List[Task] = (
            db.query(Task).filter(Task.user_id == user_id).all()
        )
        availability_list = SettingsService.get_or_create_availability(
            db, user_id
        )
        preferences = SettingsService.get_or_create_preferences(db, user_id)

        # 1. Available Time Hours for today
        weekday_name = WEEKDAY_NAMES[today_date.weekday()]
        avail_map = {a.day.lower(): a for a in availability_list}
        day_avail = avail_map.get(weekday_name)
        day_cap = get_day_capacity(today_date, day_avail, preferences)
        available_time_hours = day_cap.available_hours

        # 2. Scheduled Workload Hours for today
        today_sched = generate_daily_schedule(
            target_date=today_date,
            tasks=tasks,
            availability_list=availability_list,
            preferences=preferences,
            user_timezone=profile.timezone,
            reference_time=now_user,
        )
        scheduled_workload_hours = today_sched.total_scheduled_hours

        # 3. Overall Progress
        total_estimated = sum(float(t.estimated_duration) for t in tasks)
        total_completed = sum(float(t.completed_duration) for t in tasks)
        overall_progress = (
            min(100, round((total_completed / total_estimated) * 100))
            if total_estimated > 0
            else 0
        )

        # 4. Pending / In-Progress Tasks Count
        pending_count = sum(
            1 for t in tasks if t.status in ("pending", "in_progress")
        )

        # 5. At-Risk Tasks Count
        risks = assess_all_tasks_risk(
            tasks=tasks,
            reference_time=now_user,
            availability_list=availability_list,
            preferences=preferences,
        )
        at_risk_count = len(risks)

        # 6. Completed Today Count
        completed_today_count = 0
        for t in tasks:
            if t.status == "completed":
                t_updated = t.updated_at or t.created_at
                if t_updated:
                    if t_updated.tzinfo is None:
                        t_updated = t_updated.replace(tzinfo=timezone.utc)
                    t_updated_local = t_updated.astimezone(user_tz)
                    if t_updated_local.date() == today_date:
                        completed_today_count += 1

        return DashboardOverviewResponse(
            available_time_hours=available_time_hours,
            scheduled_workload_hours=scheduled_workload_hours,
            overall_progress=overall_progress,
            pending_tasks_count=pending_count,
            at_risk_tasks_count=at_risk_count,
            completed_today_count=completed_today_count,
        )

    @staticmethod
    def get_recommendation(
        db: Session, user_id: str, reference_time: Optional[datetime] = None
    ) -> Optional[RecommendedTaskResponse]:
        """Retrieve highest-priority recommended next task."""
        profile = SettingsService.get_profile(db, user_id)
        user_tz = resolve_timezone(profile.timezone)

        now_user = reference_time or datetime.now(user_tz)
        if now_user.tzinfo is None:
            now_user = now_user.replace(tzinfo=user_tz)

        tasks: List[Task] = (
            db.query(Task).filter(Task.user_id == user_id).all()
        )

        rec = get_recommended_next_task(
            tasks=tasks,
            reference_time=now_user,
            user_timezone=profile.timezone,
        )

        if not rec:
            return None

        task_entity = next((t for t in tasks if t.id == rec.task_id), None)
        if not task_entity:
            return None

        return RecommendedTaskResponse(
            task=TaskResponse.model_validate(task_entity),
            recommendation_reason=rec.recommendation_reason,
            urgency_label=rec.urgency_label,
        )

    @staticmethod
    def get_at_risk_tasks(
        db: Session, user_id: str, reference_time: Optional[datetime] = None
    ) -> List[AtRiskTaskResponse]:
        """Retrieve all tasks currently flagged as at risk."""
        profile = SettingsService.get_profile(db, user_id)
        user_tz = resolve_timezone(profile.timezone)

        now_user = reference_time or datetime.now(user_tz)
        if now_user.tzinfo is None:
            now_user = now_user.replace(tzinfo=user_tz)

        tasks: List[Task] = (
            db.query(Task).filter(Task.user_id == user_id).all()
        )
        availability_list = SettingsService.get_or_create_availability(
            db, user_id
        )
        preferences = SettingsService.get_or_create_preferences(db, user_id)

        risks = assess_all_tasks_risk(
            tasks=tasks,
            reference_time=now_user,
            availability_list=availability_list,
            preferences=preferences,
        )

        task_map = {t.id: t for t in tasks}
        response_items: List[AtRiskTaskResponse] = []

        for r in risks:
            t = task_map.get(r.task_id)
            if t:
                response_items.append(
                    AtRiskTaskResponse(
                        task=TaskResponse.model_validate(t),
                        risk_level=r.risk_level,
                        risk_reason=r.risk_reason,
                    )
                )

        return response_items

    @staticmethod
    def get_upcoming_deadlines(
        db: Session, user_id: str, limit: int = 5
    ) -> List[TaskResponse]:
        """Retrieve active upcoming tasks ordered chronologically by deadline."""
        tasks = (
            db.query(Task)
            .filter(Task.user_id == user_id, Task.status != "completed")
            .order_by(Task.deadline.asc())
            .limit(limit)
            .all()
        )
        return [TaskResponse.model_validate(t) for t in tasks]

    @staticmethod
    def get_today_schedule_blocks(
        db: Session, user_id: str, reference_time: Optional[datetime] = None
    ) -> List[ScheduleBlockResponse]:
        """Generate chronological schedule blocks for today matching frontend ScheduleBlock type."""
        profile = SettingsService.get_profile(db, user_id)
        user_tz = resolve_timezone(profile.timezone)

        now_user = reference_time or datetime.now(user_tz)
        if now_user.tzinfo is None:
            now_user = now_user.replace(tzinfo=user_tz)

        today_date = now_user.date()
        tasks = db.query(Task).filter(Task.user_id == user_id).all()
        availability_list = SettingsService.get_or_create_availability(
            db, user_id
        )
        preferences = SettingsService.get_or_create_preferences(db, user_id)

        sched = generate_daily_schedule(
            target_date=today_date,
            tasks=tasks,
            availability_list=availability_list,
            preferences=preferences,
            user_timezone=profile.timezone,
            reference_time=now_user,
        )

        blocks: List[ScheduleBlockResponse] = []
        for item in sched.items:
            # Parse times to determine completed vs current vs upcoming
            status = "upcoming"
            try:
                t_start = datetime.strptime(item.start_time, "%I:%M %p").time()
                t_end = datetime.strptime(item.end_time, "%I:%M %p").time()
                block_start = datetime.combine(today_date, t_start, tzinfo=user_tz)
                block_end = datetime.combine(today_date, t_end, tzinfo=user_tz)

                if block_end < now_user:
                    status = "completed"
                elif block_start <= now_user <= block_end:
                    status = "current"
                else:
                    status = "upcoming"
            except Exception:
                status = "upcoming"

            blocks.append(
                ScheduleBlockResponse(
                    id=item.id,
                    start_time=item.start_time,
                    end_time=item.end_time,
                    title=item.title,
                    category=item.category,
                    task_id=item.task_id,
                    status=status,
                    duration_minutes=item.duration_minutes,
                )
            )

        return blocks
