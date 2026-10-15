"""Adaptive Scheduling Engine.

Generates dynamic, rule-based daily schedules, recommends the next task to work on,
and detects when adaptive rescheduling should be triggered.
"""

from datetime import date, datetime, timedelta, time, timezone
from typing import List, Optional, Dict
from zoneinfo import ZoneInfo

from app.models.task import Task
from app.models.availability import UserAvailability
from app.models.preferences import UserPreferences
from app.services.scheduling.schemas import (
    DailyScheduleResult,
    ScheduleBlockItem,
    TaskRecommendation,
    ScheduleRegenerationTrigger,
)
from app.services.scheduling.capacity import (
    get_day_capacity,
    resolve_timezone,
    parse_time_string,
    WEEKDAY_NAMES,
)
from app.services.scheduling.scoring import rank_tasks


def generate_daily_schedule(
    target_date: date,
    tasks: List[Task],
    availability_list: Optional[List[UserAvailability]] = None,
    preferences: Optional[UserPreferences] = None,
    user_timezone: str = "UTC",
    reference_time: Optional[datetime] = None,
) -> DailyScheduleResult:
    """
    Generate a deterministic, conflict-free daily work schedule for target_date.

    Rules:
    1. Resolves user timezone and local calendar day.
    2. Respects user availability (start/end time, enabled flag).
    3. Caps capacity to preferences.daily_focus_hours_limit.
    4. Reserves buffer margins (tight=0%, moderate=10%, relaxed=20%).
    5. Excludes completed tasks and tasks with 0 remaining duration.
    6. Ranks tasks by priority, urgency, difficulty, and in-progress continuity.
    7. Allocates non-overlapping work blocks within available hours.
    8. Never allocates work past a task's deadline.
    9. Never allocates more time than a task's remaining duration.
    """
    tz = resolve_timezone(user_timezone)

    if reference_time is None:
        reference_time = datetime.now(tz)
    elif reference_time.tzinfo is None:
        reference_time = reference_time.replace(tzinfo=tz)
    else:
        reference_time = reference_time.astimezone(tz)

    weekday_name = WEEKDAY_NAMES[target_date.weekday()]
    formatted_date = target_date.strftime("%A, %B %d, %Y")
    is_today = target_date == reference_time.date()

    # Index availability by weekday
    avail_map: Dict[str, UserAvailability] = {}
    if availability_list:
        for a in availability_list:
            avail_map[str(a.day).lower()] = a

    day_avail = avail_map.get(weekday_name)
    capacity = get_day_capacity(target_date, day_avail, preferences)

    # Empty schedule if day is disabled or window is zero
    if not capacity.enabled or capacity.allocatable_hours <= 0.0:
        return DailyScheduleResult(
            date=target_date.isoformat(),
            day_of_week=weekday_name.capitalize(),
            formatted_date=formatted_date,
            is_today=is_today,
            items=[],
            total_scheduled_hours=0.0,
            available_hours=0.0,
            unscheduled_tasks_count=len(
                [t for t in tasks if t.status != "completed" and float(t.remaining_duration) > 0]
            ),
        )

    # Filter and rank eligible tasks
    ranked_tuples = rank_tasks(tasks, reference_time)
    if not ranked_tuples:
        return DailyScheduleResult(
            date=target_date.isoformat(),
            day_of_week=weekday_name.capitalize(),
            formatted_date=formatted_date,
            is_today=is_today,
            items=[],
            total_scheduled_hours=0.0,
            available_hours=capacity.available_hours,
            unscheduled_tasks_count=0,
        )

    # Determine work window
    t_start = parse_time_string(capacity.start_time) or time(9, 0)
    t_end = parse_time_string(capacity.end_time) or time(17, 0)

    window_start_dt = datetime.combine(target_date, t_start, tzinfo=tz)
    window_end_dt = datetime.combine(target_date, t_end, tzinfo=tz)

    # If scheduling for today and current time is already past window start, begin from current time
    current_pointer = window_start_dt
    if is_today and reference_time > current_pointer:
        # Snap forward to next 15-minute increment
        minute_rem = reference_time.minute % 15
        if minute_rem > 0:
            current_pointer = reference_time + timedelta(minutes=(15 - minute_rem))
        else:
            current_pointer = reference_time
        # Round seconds/microseconds
        current_pointer = current_pointer.replace(second=0, microsecond=0)

    # Buffer gap between blocks based on strategy
    buffer_strategy = "moderate"
    default_block_mins = 60
    if preferences:
        buffer_strategy = str(preferences.buffer_strategy).lower()
        if preferences.default_task_duration_minutes > 0:
            default_block_mins = min(120, preferences.default_task_duration_minutes)

    gap_minutes = 15 if buffer_strategy == "relaxed" else (10 if buffer_strategy == "moderate" else 0)

    total_allocatable_minutes = int(round(capacity.allocatable_hours * 60))
    scheduled_minutes_total = 0
    items: List[ScheduleBlockItem] = []

    # Track remaining duration per task during this schedule simulation
    task_rem_duration = {
        t.id: max(0.0, float(t.remaining_duration)) for t, _ in ranked_tuples
    }

    item_counter = 1
    scheduled_task_ids = set()

    for task, ranked_meta in ranked_tuples:
        if scheduled_minutes_total >= total_allocatable_minutes:
            break
        if current_pointer >= window_end_dt:
            break

        rem_hours = task_rem_duration[task.id]
        if rem_hours <= 0.0:
            continue

        # Convert task deadline to user timezone
        task_deadline = task.deadline
        if task_deadline.tzinfo is None:
            task_deadline = task_deadline.replace(tzinfo=timezone.utc)
        task_deadline_local = task_deadline.astimezone(tz)

        # Do not schedule work after task deadline
        if task_deadline_local <= current_pointer:
            continue

        # Effective upper limit for this block
        max_possible_mins = min(
            int(round(rem_hours * 60)),
            default_block_mins,
            total_allocatable_minutes - scheduled_minutes_total,
            int((window_end_dt - current_pointer).total_seconds() / 60),
            int((task_deadline_local - current_pointer).total_seconds() / 60),
        )

        # Minimum viable work block is 15 minutes
        if max_possible_mins < 15:
            continue

        block_start = current_pointer
        block_end = block_start + timedelta(minutes=max_possible_mins)

        is_top_rec = (item_counter == 1)
        rec_reason = ranked_meta.score_breakdown.reason if is_top_rec else None

        block_item = ScheduleBlockItem(
            id=f"item-{item_counter:02d}",
            task_id=task.id,
            title=task.title,
            category=task.category,
            start_time=block_start.strftime("%I:%M %p"),
            end_time=block_end.strftime("%I:%M %p"),
            duration_minutes=max_possible_mins,
            status=task.status,
            is_recommended=is_top_rec,
            recommendation_reason=rec_reason,
            priority=task.priority,
            notes=(
                f"{task.difficulty.capitalize()} difficulty task with {rem_hours:.1f}h remaining work. "
                f"Allocated {max_possible_mins}m focus block."
            ),
        )

        items.append(block_item)
        scheduled_task_ids.add(task.id)
        scheduled_minutes_total += max_possible_mins
        item_counter += 1

        # Deduct from task simulation remaining duration
        allocated_hours = max_possible_mins / 60.0
        task_rem_duration[task.id] = max(0.0, rem_hours - allocated_hours)

        # Advance pointer with buffer gap
        current_pointer = block_end + timedelta(minutes=gap_minutes)

    total_scheduled_hours = round(scheduled_minutes_total / 60.0, 1)
    unscheduled_count = len(ranked_tuples) - len(scheduled_task_ids)

    return DailyScheduleResult(
        date=target_date.isoformat(),
        day_of_week=weekday_name.capitalize(),
        formatted_date=formatted_date,
        is_today=is_today,
        items=items,
        total_scheduled_hours=total_scheduled_hours,
        available_hours=capacity.available_hours,
        unscheduled_tasks_count=max(0, unscheduled_count),
    )


def get_recommended_next_task(
    tasks: List[Task],
    reference_time: Optional[datetime] = None,
    user_timezone: str = "UTC",
) -> Optional[TaskRecommendation]:
    """
    Select the single highest-priority eligible task to focus on right now.
    Considers priority, urgency, difficulty, remaining duration, and in-progress status.
    """
    tz = resolve_timezone(user_timezone)
    if reference_time is None:
        reference_time = datetime.now(tz)
    elif reference_time.tzinfo is None:
        reference_time = reference_time.replace(tzinfo=tz)
    else:
        reference_time = reference_time.astimezone(tz)

    ranked = rank_tasks(tasks, reference_time)
    if not ranked:
        return None

    top_task, top_ranked = ranked[0]
    rem_work = max(0.0, float(top_task.remaining_duration))

    # Deadline comparison
    task_deadline = top_task.deadline
    if task_deadline.tzinfo is None:
        task_deadline = task_deadline.replace(tzinfo=timezone.utc)
    task_deadline_local = task_deadline.astimezone(tz)

    delta_hours = (task_deadline_local - reference_time).total_seconds() / 3600.0

    # Determine urgency label
    if delta_hours <= 0:
        urgency_label = "Overdue"
    elif delta_hours <= 24:
        urgency_label = "Due Tomorrow" if task_deadline_local.date() > reference_time.date() else "Due Today"
    elif top_task.status == "in_progress":
        urgency_label = "In Progress"
    elif top_task.priority == "critical":
        urgency_label = "Critical Priority"
    else:
        urgency_label = "Next in Queue"

    # Generate human-readable, specific rationale
    if delta_hours <= 0:
        rec_reason = (
            f"Overdue task with {rem_work:.1f}h remaining work. "
            "Completing this item immediately resolves deadline slippage and clears blocked work."
        )
    elif delta_hours <= 24:
        rec_reason = (
            f"Due {urgency_label.lower()} at {task_deadline_local.strftime('%I:%M %p')} with {rem_work:.1f}h remaining work. "
            "Completing this deliverable during today's focus block prevents deadline risk cascade."
        )
    elif top_task.status == "in_progress":
        rec_reason = (
            f"Currently in-progress with {rem_work:.1f}h remaining work. "
            "Continuing focus capitalizes on existing mental context and momentum."
        )
    else:
        rec_reason = (
            f"{top_task.priority.capitalize()} priority item with {rem_work:.1f}h remaining work. "
            "Early progress maintains schedule stability and safeguards buffer margins."
        )

    return TaskRecommendation(
        task_id=top_task.id,
        title=top_task.title,
        category=top_task.category,
        recommendation_reason=rec_reason,
        urgency_label=urgency_label,
        priority=top_task.priority,
        remaining_duration=rem_work,
        progress=int(top_task.progress),
        status=top_task.status,
    )


def detect_schedule_regeneration_triggers(
    tasks: List[Task],
    current_scheduled_task_ids: Optional[List[str]] = None,
    reference_time: Optional[datetime] = None,
) -> ScheduleRegenerationTrigger:
    """
    Evaluate whether circumstances have changed enough to warrant schedule regeneration.
    Triggers:
    - Overdue tasks not yet addressed
    - Incomplete tasks with progress changes
    - New high-priority tasks not present on timeline
    """
    if reference_time is None:
        reference_time = datetime.now(timezone.utc)
    elif reference_time.tzinfo is None:
        reference_time = reference_time.replace(tzinfo=timezone.utc)

    scheduled_ids = set(current_scheduled_task_ids or [])
    reasons: List[str] = []
    changes: List[str] = []

    # Check for overdue tasks
    for t in tasks:
        if t.status != "completed" and float(t.remaining_duration) > 0:
            t_deadline = t.deadline
            if t_deadline.tzinfo is None:
                t_deadline = t_deadline.replace(tzinfo=timezone.utc)
            if t_deadline < reference_time:
                reasons.append(f"Task '{t.title}' is overdue")
                changes.append(f"Rescheduled '{t.title}' to urgent recovery block")
                break

    # Check for unscheduled critical/high tasks
    for t in tasks:
        if t.status != "completed" and float(t.remaining_duration) > 0:
            if t.priority in ("critical", "high") and t.id not in scheduled_ids:
                reasons.append(f"High-priority task '{t.title}' is not yet scheduled")
                changes.append(f"Added focus slot for '{t.title}' ({t.priority} priority)")
                break

    needs_regen = len(reasons) > 0
    rec_action = "Review Updated Schedule" if needs_regen else None

    return ScheduleRegenerationTrigger(
        needs_regeneration=needs_regen,
        reasons=reasons,
        changes=changes,
        recommended_action=rec_action,
    )
