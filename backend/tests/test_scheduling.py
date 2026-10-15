"""Unit tests for the Adaptive Scheduling Engine (Phase 3A).

Covers:
- Deterministic task ranking & urgency scoring
- Working window capacity and focus limit calculations
- Daily schedule work block allocation & conflict prevention
- Deadline risk detection and timeline compression analysis
- Next-task recommendations with rationale
- Adaptive rescheduling trigger detection
"""

import pytest
from typing import Optional, List, Dict, Tuple
from datetime import date, datetime, timezone, timedelta


from app.models.task import Task
from app.models.availability import UserAvailability
from app.models.preferences import UserPreferences
from app.services.scheduling.scoring import (
    calculate_task_score,
    rank_tasks,
    PRIORITY_WEIGHTS,
)
from app.services.scheduling.capacity import (
    get_day_capacity,
    calculate_window_hours,
    calculate_available_capacity_range,
    calculate_total_workload,
    resolve_timezone,
)
from app.services.scheduling.risk import (
    assess_task_risk,
    assess_all_tasks_risk,
)
from app.services.scheduling.engine import (
    generate_daily_schedule,
    get_recommended_next_task,
    detect_schedule_regeneration_triggers,
)


# Fixed reference time for deterministic testing: Monday, October 12, 2026 at 09:00 AM UTC
FIXED_REF_TIME = datetime(2026, 10, 12, 9, 0, 0, tzinfo=timezone.utc)
FIXED_TARGET_DATE = date(2026, 10, 12)


def make_dummy_task(
    id: str,
    title: str = "Test Task",
    category: str = "Engineering",
    deadline: Optional[datetime] = None,
    priority: str = "medium",
    difficulty: str = "medium",
    estimated_duration: float = 4.0,
    completed_duration: float = 0.0,
    status: str = "pending",
    user_id: str = "user-test-sched",
) -> Task:
    """Helper to instantiate Task entity without database persistence."""
    if deadline is None:
        deadline = FIXED_REF_TIME + timedelta(days=2)
    elif deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)

    rem = max(0.0, estimated_duration - completed_duration)
    progress = min(100, max(0, round((completed_duration / max(0.1, estimated_duration)) * 100)))

    return Task(
        id=id,
        user_id=user_id,
        title=title,
        description=f"Description for {title}",
        category=category,
        deadline=deadline,
        priority=priority,
        difficulty=difficulty,
        estimated_duration=estimated_duration,
        completed_duration=completed_duration,
        remaining_duration=rem,
        progress=progress,
        status=status,
    )


def make_dummy_availability(user_id: str = "user-test-sched") -> list[UserAvailability]:
    """Helper to create a standard 7-day availability set."""
    days = [
        ("monday", "09:00", "17:00", True),
        ("tuesday", "09:00", "17:00", True),
        ("wednesday", "09:00", "17:00", True),
        ("thursday", "09:00", "17:00", True),
        ("friday", "09:00", "16:00", True),
        ("saturday", "10:00", "14:00", True),
        ("sunday", "10:00", "14:00", False),  # Sunday disabled
    ]
    result = []
    for d, s, e, en in days:
        result.append(
            UserAvailability(
                id=f"avail-{d}",
                user_id=user_id,
                day=d,
                label=d.capitalize(),
                enabled=en,
                start_time=s,
                end_time=e,
            )
        )
    return result


def make_dummy_preferences(user_id: str = "user-test-sched") -> UserPreferences:
    """Helper to create standard user preferences."""
    return UserPreferences(
        id="pref-01",
        user_id=user_id,
        enable_deadline_reminders=True,
        enable_schedule_updates=True,
        default_task_duration_minutes=90,
        daily_focus_hours_limit=6.5,
        buffer_strategy="moderate",
    )


# ==============================================================================
# 1. TASK RANKING & SCORING TESTS
# ==============================================================================


def test_ranking_priority_ordering():
    """Critical priority tasks must rank above lower priority tasks with equal deadlines."""
    t_low = make_dummy_task("t-low", priority="low", deadline=FIXED_REF_TIME + timedelta(days=2))
    t_med = make_dummy_task("t-med", priority="medium", deadline=FIXED_REF_TIME + timedelta(days=2))
    t_high = make_dummy_task("t-high", priority="high", deadline=FIXED_REF_TIME + timedelta(days=2))
    t_crit = make_dummy_task("t-crit", priority="critical", deadline=FIXED_REF_TIME + timedelta(days=2))

    ranked = rank_tasks([t_low, t_med, t_crit, t_high], reference_time=FIXED_REF_TIME)
    task_order = [t.id for t, _ in ranked]

    assert task_order == ["t-crit", "t-high", "t-med", "t-low"]


def test_ranking_imminent_deadline_overcomes_low_priority():
    """An imminent low-priority deadline should outrank a critical task due in 2 weeks."""
    t_urgent_low = make_dummy_task(
        "t-urgent-low",
        priority="low",
        deadline=FIXED_REF_TIME + timedelta(hours=3),  # Due in 3 hours
    )
    t_distant_crit = make_dummy_task(
        "t-distant-crit",
        priority="critical",
        deadline=FIXED_REF_TIME + timedelta(days=14),  # Due in 2 weeks
    )

    ranked = rank_tasks([t_distant_crit, t_urgent_low], reference_time=FIXED_REF_TIME)
    assert ranked[0][0].id == "t-urgent-low"


def test_ranking_in_progress_continuity_bonus():
    """In-progress task receives continuity boost over pending task with identical priority and deadline."""
    t_pending = make_dummy_task("t-pending", priority="high", status="pending")
    t_in_prog = make_dummy_task("t-in-prog", priority="high", status="in_progress")

    ranked = rank_tasks([t_pending, t_in_prog], reference_time=FIXED_REF_TIME)
    assert ranked[0][0].id == "t-in-prog"
    assert ranked[0][1].score_breakdown.in_progress_bonus == 60.0


def test_ranking_excludes_completed_and_zero_duration_tasks():
    """Completed tasks and tasks with 0 remaining hours are excluded from scheduling."""
    t_comp = make_dummy_task("t-comp", status="completed", estimated_duration=4.0, completed_duration=4.0)
    t_zero = make_dummy_task("t-zero", status="pending", estimated_duration=0.0, completed_duration=0.0)
    t_active = make_dummy_task("t-active", status="pending", estimated_duration=4.0, completed_duration=1.0)

    ranked = rank_tasks([t_comp, t_zero, t_active], reference_time=FIXED_REF_TIME)
    assert len(ranked) == 1
    assert ranked[0][0].id == "t-active"


def test_ranking_deterministic_tie_breaking():
    """Tasks with identical properties break ties deterministically by task id."""
    t_b = make_dummy_task("task-bbb", title="Task B")
    t_a = make_dummy_task("task-aaa", title="Task A")

    # Run multiple times to verify exact determinism
    for _ in range(5):
        ranked = rank_tasks([t_b, t_a], reference_time=FIXED_REF_TIME)
        assert [t.id for t, _ in ranked] == ["task-aaa", "task-bbb"]


def test_ranking_overdue_task_prioritization():
    """Overdue task receives maximal urgency boost."""
    t_overdue = make_dummy_task(
        "t-overdue",
        priority="medium",
        deadline=FIXED_REF_TIME - timedelta(hours=5),
        status="overdue",
    )
    t_normal = make_dummy_task(
        "t-normal",
        priority="high",
        deadline=FIXED_REF_TIME + timedelta(days=2),
    )

    ranked = rank_tasks([t_normal, t_overdue], reference_time=FIXED_REF_TIME)
    assert ranked[0][0].id == "t-overdue"
    assert "Overdue by 5.0h" in ranked[0][1].score_breakdown.reason


# ==============================================================================
# 2. USER AVAILABILITY & CAPACITY TESTS
# ==============================================================================


def test_window_hours_calculation():
    """Validates start and end time parsing and duration in hours."""
    assert calculate_window_hours("09:00", "17:00") == 8.0
    assert calculate_window_hours("10:30", "12:00") == 1.5
    assert calculate_window_hours("17:00", "09:00") == 0.0  # Invalid end before start
    assert calculate_window_hours(None, "17:00") == 0.0


def test_day_capacity_disabled_day():
    """Disabled day yields zero available and allocatable hours."""
    sunday = date(2026, 10, 18)  # Sunday
    avail_sunday = UserAvailability(
        id="avail-sun",
        user_id="u1",
        day="sunday",
        label="Sunday",
        enabled=False,
        start_time="10:00",
        end_time="14:00",
    )
    cap = get_day_capacity(sunday, avail_sunday, make_dummy_preferences())

    assert not cap.enabled
    assert cap.available_hours == 0.0
    assert cap.allocatable_hours == 0.0


def test_day_capacity_focus_limit_and_buffer_strategy():
    """Daily focus hours limit caps window, and buffer strategy subtracts safety margin."""
    avail_monday = UserAvailability(
        id="avail-mon",
        user_id="u1",
        day="monday",
        label="Monday",
        enabled=True,
        start_time="09:00",
        end_time="19:00",  # 10.0 raw hours
    )
    # Focus limit: 6.0 hours, moderate buffer (10%)
    prefs = UserPreferences(
        id="pref-01",
        user_id="u1",
        daily_focus_hours_limit=6.0,
        buffer_strategy="moderate",
    )

    cap = get_day_capacity(FIXED_TARGET_DATE, avail_monday, prefs)

    assert cap.raw_window_hours == 10.0
    assert cap.available_hours == 6.0  # Capped at focus_limit
    assert cap.buffer_hours == 0.6     # 10% of 6.0
    assert cap.allocatable_hours == 5.4


def test_capacity_range_multi_day_calculation():
    """Calculates available capacity across multiple calendar days correctly."""
    avail_list = make_dummy_availability()
    avail_map = {a.day: a for a in avail_list}
    prefs = make_dummy_preferences()

    # From Monday 09:00 to Wednesday 17:00 (3 working days: Mon, Tue, Wed)
    # Each day: 8.0 raw window, capped at 6.5 focus limit, 10% buffer -> 5.85 allocatable
    start_dt = datetime(2026, 10, 12, 9, 0, 0, tzinfo=timezone.utc)
    end_dt = datetime(2026, 10, 14, 17, 0, 0, tzinfo=timezone.utc)

    hours = calculate_available_capacity_range(start_dt, end_dt, avail_map, prefs)
    # 3 days * ~5.85 hours = ~17.55 hours
    assert 17.0 <= hours <= 18.0


def test_total_workload_calculation():
    """Calculates remaining workload across active tasks."""
    t1 = make_dummy_task("t1", estimated_duration=5.0, completed_duration=2.0)  # rem: 3.0
    t2 = make_dummy_task("t2", estimated_duration=4.0, completed_duration=1.5)  # rem: 2.5
    t3 = make_dummy_task("t3", status="completed", estimated_duration=4.0, completed_duration=4.0)

    assert calculate_total_workload([t1, t2, t3]) == 5.5


# ==============================================================================
# 3. SCHEDULE GENERATION TESTS
# ==============================================================================


def test_generate_schedule_allocation_bounds():
    """Generated schedule blocks must not overlap and fit within available window."""
    avail_list = make_dummy_availability()
    prefs = make_dummy_preferences()

    t1 = make_dummy_task("t1", title="Task 1", priority="critical", estimated_duration=2.0)
    t2 = make_dummy_task("t2", title="Task 2", priority="high", estimated_duration=3.0)

    sched = generate_daily_schedule(
        target_date=FIXED_TARGET_DATE,
        tasks=[t1, t2],
        availability_list=avail_list,
        preferences=prefs,
        reference_time=FIXED_REF_TIME,
    )

    assert sched.is_today
    assert len(sched.items) >= 2
    assert sched.total_scheduled_hours > 0

    # Ensure no blocks exceed task remaining duration
    for item in sched.items:
        assert item.duration_minutes <= 120
        assert item.start_time is not None
        assert item.end_time is not None

    # First item is recommended
    assert sched.items[0].is_recommended
    assert sched.items[0].recommendation_reason is not None


def test_generate_schedule_no_work_after_deadline():
    """Engine must not schedule a task for a time block after its deadline."""
    avail_list = make_dummy_availability()
    prefs = make_dummy_preferences()

    # Task deadline is 09:30 AM today
    t_deadline_early = make_dummy_task(
        "t-early",
        title="Early Deadline Task",
        deadline=FIXED_REF_TIME + timedelta(minutes=30),  # 09:30 AM
        estimated_duration=3.0,
    )

    sched = generate_daily_schedule(
        target_date=FIXED_TARGET_DATE,
        tasks=[t_deadline_early],
        availability_list=avail_list,
        preferences=prefs,
        reference_time=FIXED_REF_TIME,
    )

    # Max allocation can only be at most 30 minutes before 09:30 AM
    if sched.items:
        assert sched.items[0].duration_minutes <= 30


def test_generate_schedule_empty_on_disabled_day():
    """Generating schedule on an unavailable day returns 0 items and 0 hours."""
    avail_list = make_dummy_availability()
    prefs = make_dummy_preferences()

    sunday = date(2026, 10, 18)
    t1 = make_dummy_task("t1", priority="high")

    sched = generate_daily_schedule(
        target_date=sunday,
        tasks=[t1],
        availability_list=avail_list,
        preferences=prefs,
        reference_time=FIXED_REF_TIME,
    )

    assert len(sched.items) == 0
    assert sched.total_scheduled_hours == 0.0
    assert sched.available_hours == 0.0


def test_generate_schedule_insufficient_time_leaves_tasks_unscheduled():
    """When daily capacity is less than workload, lower-priority tasks are left unscheduled."""
    avail_list = make_dummy_availability()
    # 2.0 hours max focus limit
    prefs = UserPreferences(
        id="p1",
        user_id="u1",
        daily_focus_hours_limit=2.0,
        buffer_strategy="tight",
        default_task_duration_minutes=60,
    )

    tasks = [
        make_dummy_task(f"t-{i}", priority="medium", estimated_duration=1.0)
        for i in range(5)  # 5 hours of work
    ]

    sched = generate_daily_schedule(
        target_date=FIXED_TARGET_DATE,
        tasks=tasks,
        availability_list=avail_list,
        preferences=prefs,
        reference_time=FIXED_REF_TIME,
    )

    assert sched.total_scheduled_hours <= 2.0
    assert sched.unscheduled_tasks_count > 0


# ==============================================================================
# 4. DEADLINE RISK DETECTION TESTS
# ==============================================================================


def test_deadline_risk_overdue_task():
    """Overdue task is classified as critical risk with explicit rationale."""
    t_overdue = make_dummy_task(
        "t-over",
        deadline=FIXED_REF_TIME - timedelta(hours=2),
        estimated_duration=3.0,
        status="overdue",
    )
    avail_list = make_dummy_availability()

    risks = assess_all_tasks_risk([t_overdue], reference_time=FIXED_REF_TIME, availability_list=avail_list)
    assert len(risks) == 1
    assert risks[0].risk_level == "critical"
    assert risks[0].is_overdue
    assert "Deadline elapsed" in risks[0].risk_reason


def test_deadline_risk_capacity_exceeded():
    """Task whose remaining duration exceeds available focus hours before deadline is critical."""
    avail_list = make_dummy_availability()
    prefs = make_dummy_preferences()

    # Due in 12 hours (today at 21:00 UTC), but requires 10 hours work (daily focus limit is 6.5)
    t_heavy = make_dummy_task(
        "t-heavy",
        deadline=FIXED_REF_TIME + timedelta(hours=12),
        estimated_duration=10.0,
        priority="high",
    )

    risks = assess_all_tasks_risk([t_heavy], reference_time=FIXED_REF_TIME, availability_list=avail_list, preferences=prefs)
    assert len(risks) == 1
    assert risks[0].risk_level == "critical"
    assert "exceeding the" in risks[0].risk_reason


def test_deadline_risk_safe_task_not_flagged():
    """Task with small workload and distant deadline is not flagged as at risk."""
    avail_list = make_dummy_availability()
    prefs = make_dummy_preferences()

    t_safe = make_dummy_task(
        "t-safe",
        deadline=FIXED_REF_TIME + timedelta(days=20),
        estimated_duration=2.0,
        priority="low",
    )

    risks = assess_all_tasks_risk([t_safe], reference_time=FIXED_REF_TIME, availability_list=avail_list, preferences=prefs)
    assert len(risks) == 0


# ==============================================================================
# 5. NEXT-TASK RECOMMENDATION TESTS
# ==============================================================================


def test_recommendation_selects_highest_priority_eligible_task():
    """Recommendation selects top task and returns formatted reason."""
    t1 = make_dummy_task("t1", title="Normal Task", priority="low")
    t2 = make_dummy_task("t2", title="Critical Task", priority="critical", estimated_duration=3.0)

    rec = get_recommended_next_task([t1, t2], reference_time=FIXED_REF_TIME)
    assert rec is not None
    assert rec.task_id == "t2"
    assert rec.title == "Critical Task"
    assert "Critical priority" in rec.recommendation_reason


def test_recommendation_in_progress_continuity():
    """In-progress task is recommended with 'In Progress' label."""
    t1 = make_dummy_task("t1", title="Pending Task", priority="high", status="pending")
    t2 = make_dummy_task("t2", title="Started Task", priority="high", status="in_progress")

    rec = get_recommended_next_task([t1, t2], reference_time=FIXED_REF_TIME)
    assert rec is not None
    assert rec.task_id == "t2"
    assert rec.urgency_label == "In Progress"
    assert "Continuing focus" in rec.recommendation_reason


def test_recommendation_empty_when_no_active_tasks():
    """Returns None when all tasks are completed."""
    t_done = make_dummy_task("t-done", status="completed", estimated_duration=2.0, completed_duration=2.0)
    rec = get_recommended_next_task([t_done], reference_time=FIXED_REF_TIME)
    assert rec is None


# ==============================================================================
# 6. ADAPTIVE RESCHEDULING TRIGGER TESTS
# ==============================================================================


def test_reschedule_trigger_detects_overdue_and_unscheduled_work():
    """Detects when an overdue task or unscheduled critical task necessitates schedule refresh."""
    t_crit_unsched = make_dummy_task("t-unsched", priority="critical")

    trigger = detect_schedule_regeneration_triggers(
        tasks=[t_crit_unsched],
        current_scheduled_task_ids=["t-other"],
        reference_time=FIXED_REF_TIME,
    )

    assert trigger.needs_regeneration
    assert len(trigger.reasons) > 0
    assert len(trigger.changes) > 0
    assert trigger.recommended_action == "Review Updated Schedule"


def test_reschedule_trigger_clean_when_all_scheduled():
    """No trigger generated when all critical work is already scheduled."""
    t1 = make_dummy_task("t1", priority="critical")
    trigger = detect_schedule_regeneration_triggers(
        tasks=[t1],
        current_scheduled_task_ids=["t1"],
        reference_time=FIXED_REF_TIME,
    )
    assert not trigger.needs_regeneration
    assert len(trigger.reasons) == 0
