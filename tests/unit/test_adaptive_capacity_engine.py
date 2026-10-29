"""Unit tests for the Adaptive Scheduling Engine, Capacity Calculation, and Risk Analysis.

Validates:
- Capacity limits clamped to user daily focus hours
- Disabled weekday zero-capacity behavior
- Buffer strategy spacing margins (relaxed=15m, moderate=10m, tight=0m)
- Sequential non-overlapping work block allocation
- Strict deadline boundary enforcement
- Adaptive schedule regeneration triggers
- Single next task recommendation selection
"""

from datetime import date, datetime, time, timedelta, timezone
from app.models.task import Task
from app.models.availability import UserAvailability
from app.models.preferences import UserPreferences
from app.services.scheduling.capacity import get_day_capacity
from app.services.scheduling.engine import (
    generate_daily_schedule,
    get_recommended_next_task,
    detect_schedule_regeneration_triggers,
)
from app.services.scheduling.risk import assess_task_risk
from tests.conftest import record_meta


def make_task(
    id: str,
    title: str,
    deadline_dt: datetime,
    priority: str = "medium",
    difficulty: str = "medium",
    status: str = "pending",
    estimated_duration: float = 2.0,
    remaining_duration: float = 2.0,
) -> Task:
    return Task(
        id=id,
        user_id="usr_test",
        title=title,
        category="Engineering",
        deadline=deadline_dt,
        priority=priority,
        difficulty=difficulty,
        estimated_duration=estimated_duration,
        completed_duration=0.0,
        remaining_duration=remaining_duration,
        progress=0,
        status=status,
    )


@record_meta(
    test_id="TC_UNIT_ENG_01",
    module="Capacity Engine",
    scenario="Verify daily allocatable capacity is clamped to daily_focus_hours_limit",
    test_type="Unit",
    preconditions="Availability window 09:00 - 17:00 (8h) with focus limit 5.0h and moderate buffer (10%)",
    steps="1. Define availability with 8h window\n2. Set daily_focus_hours_limit=5.0h\n3. Calculate day capacity\n4. Assert gross hours capped at 5.0h and allocatable reduced by buffer",
    input_data="window=8h, focus_limit=5.0h, buffer='moderate'",
    expected="available_hours == 5.0 and allocatable_hours == 4.5 (5.0 - 10%)",
)
def test_daily_capacity_clamped_to_focus_limit():
    target_date = date(2026, 10, 20)  # Tuesday
    avail = UserAvailability(
        user_id="usr_test",
        day="tuesday",
        enabled=True,
        start_time="09:00",
        end_time="17:00",
    )
    prefs = UserPreferences(
        user_id="usr_test",
        daily_focus_hours_limit=5.0,
        buffer_strategy="moderate",
    )
    cap = get_day_capacity(target_date, avail, prefs)
    assert cap.available_hours == 5.0
    assert cap.allocatable_hours == 4.5  # 5.0h - 10% buffer


@record_meta(
    test_id="TC_UNIT_ENG_02",
    module="Capacity Engine",
    scenario="Verify disabled weekday produces zero allocatable hours and empty schedule",
    test_type="Unit",
    preconditions="Sunday availability disabled (enabled=False)",
    steps="1. Set Sunday availability enabled=False\n2. Call generate_daily_schedule() for Sunday\n3. Assert items count is 0 and total scheduled hours is 0.0",
    input_data="day='sunday', enabled=False",
    expected="items==[], total_scheduled_hours==0.0, available_hours==0.0",
)
def test_disabled_weekday_zero_capacity():
    target_date = date(2026, 10, 25)  # Sunday
    avail = UserAvailability(
        user_id="usr_test",
        day="sunday",
        enabled=False,
        start_time="10:00",
        end_time="16:00",
    )
    task = make_task(
        "t-01", "Sunday Task", datetime(2026, 10, 26, 12, 0, tzinfo=timezone.utc)
    )
    result = generate_daily_schedule(
        target_date=target_date,
        tasks=[task],
        availability_list=[avail],
        user_timezone="UTC",
    )
    assert len(result.items) == 0
    assert result.total_scheduled_hours == 0.0
    assert result.available_hours == 0.0


@record_meta(
    test_id="TC_UNIT_ENG_03",
    module="Scheduling Engine",
    scenario="Verify non-overlapping schedule blocks and sequential allocation",
    test_type="Unit",
    preconditions="Two distinct tasks scheduled on the same working day",
    steps="1. Provide 2 eligible tasks to generate_daily_schedule()\n2. Assert both blocks are scheduled\n3. Assert block 2 starts strictly after block 1 ends",
    input_data="tasks=[task1 (2h), task2 (2h)], window 09:00 - 17:00",
    expected="Block 2 start_time >= Block 1 end_time + buffer gap",
)
def test_non_overlapping_schedule_blocks():
    target_date = date(2026, 10, 20)  # Tuesday
    ref_time = datetime(2026, 10, 20, 8, 30, tzinfo=timezone.utc)
    avail = UserAvailability(
        user_id="usr_test",
        day="tuesday",
        enabled=True,
        start_time="09:00",
        end_time="17:00",
    )
    prefs = UserPreferences(
        user_id="usr_test",
        daily_focus_hours_limit=6.0,
        buffer_strategy="moderate",
        default_task_duration_minutes=60,
    )
    t1 = make_task("t-1", "Task One", datetime(2026, 10, 22, 18, 0, tzinfo=timezone.utc), priority="critical")
    t2 = make_task("t-2", "Task Two", datetime(2026, 10, 22, 18, 0, tzinfo=timezone.utc), priority="high")

    schedule = generate_daily_schedule(
        target_date=target_date,
        tasks=[t1, t2],
        availability_list=[avail],
        preferences=prefs,
        user_timezone="UTC",
        reference_time=ref_time,
    )

    assert len(schedule.items) >= 2
    b1 = schedule.items[0]
    b2 = schedule.items[1]
    assert b1.start_time == "09:00 AM"
    assert b1.end_time == "10:00 AM"
    assert b2.start_time == "10:10 AM"


@record_meta(
    test_id="TC_UNIT_ENG_04",
    module="Scheduling Engine",
    scenario="Verify strict deadline boundary enforcement (no work allocated after deadline)",
    test_type="Unit",
    preconditions="Task deadline is 10:00 AM on target date; window starts at 09:00 AM",
    steps="1. Create task with deadline at 10:00 AM\n2. Run schedule generator\n3. Assert block duration is capped at 60 mins (ending by 10:00 AM)",
    input_data="task remaining=3h, deadline=10:00 AM, window_start=09:00 AM",
    expected="Allocated duration <= 60 mins and block end_time <= 10:00 AM",
)
def test_deadline_boundary_truncation():
    target_date = date(2026, 10, 20)
    ref_time = datetime(2026, 10, 20, 8, 30, tzinfo=timezone.utc)
    avail = UserAvailability(
        user_id="usr_test",
        day="tuesday",
        enabled=True,
        start_time="09:00",
        end_time="17:00",
    )
    prefs = UserPreferences(
        user_id="usr_test",
        daily_focus_hours_limit=6.0,
        buffer_strategy="tight",
        default_task_duration_minutes=120,
    )
    t_deadline_early = make_task(
        "t-early",
        "Early Deadline Task",
        datetime(2026, 10, 20, 10, 0, tzinfo=timezone.utc),
        remaining_duration=3.0,
    )

    schedule = generate_daily_schedule(
        target_date=target_date,
        tasks=[t_deadline_early],
        availability_list=[avail],
        preferences=prefs,
        user_timezone="UTC",
        reference_time=ref_time,
    )

    assert len(schedule.items) == 1
    block = schedule.items[0]
    assert block.duration_minutes <= 60
    assert block.end_time == "10:00 AM"


@record_meta(
    test_id="TC_UNIT_ENG_05",
    module="Adaptive Engine",
    scenario="Verify schedule regeneration trigger detects overdue deliverables",
    test_type="Unit",
    preconditions="An incomplete task whose deadline timestamp is earlier than reference_time",
    steps="1. Create overdue task\n2. Call detect_schedule_regeneration_triggers()\n3. Assert needs_regeneration is True and reason describes overdue task",
    input_data="t.deadline = reference_time - 2 hours",
    expected="trigger.needs_regeneration == True and 'overdue' in reasons[0]",
)
def test_regeneration_triggers_overdue():
    ref_time = datetime(2026, 10, 20, 14, 0, tzinfo=timezone.utc)
    t_od = make_task(
        "t-od",
        "Overdue Assignment",
        datetime(2026, 10, 20, 12, 0, tzinfo=timezone.utc),
        remaining_duration=2.0,
    )
    trigger = detect_schedule_regeneration_triggers([t_od], reference_time=ref_time)
    assert trigger.needs_regeneration is True
    assert any("overdue" in r.lower() for r in trigger.reasons)


@record_meta(
    test_id="TC_UNIT_ENG_06",
    module="Recommendation Engine",
    scenario="Verify single recommended task selection and specific explanation rationale",
    test_type="Unit",
    preconditions="A set of tasks with varying priorities and deadlines",
    steps="1. Provide critical urgent task and lower priority tasks\n2. Call get_recommended_next_task()\n3. Assert critical urgent task is selected with valid urgency label",
    input_data="tasks=[critical_urgent, low_distant]",
    expected="Recommendation points to critical urgent task with 'Urgent' or 'Due Tomorrow' label",
)
def test_recommendation_rationale_generation():
    ref_time = datetime(2026, 10, 20, 10, 0, tzinfo=timezone.utc)
    t_urgent = make_task(
        "t-urg",
        "Algorithms Midterm Prep",
        datetime(2026, 10, 21, 9, 0, tzinfo=timezone.utc),
        priority="critical",
        status="in_progress",
        remaining_duration=3.0,
    )
    t_casual = make_task(
        "t-cas",
        "Read Optional Blog",
        datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc),
        priority="low",
        remaining_duration=1.0,
    )

    rec = get_recommended_next_task([t_urgent, t_casual], reference_time=ref_time)
    assert rec is not None
    assert rec.task_id == "t-urg"
    assert rec.priority == "critical"
    assert len(rec.recommendation_reason) > 20
    assert rec.urgency_label in ("Due Tomorrow", "In Progress", "Critical Priority")


@record_meta(
    test_id="TC_UNIT_ENG_07",
    module="Risk Analysis",
    scenario="Verify deadline risk assessment flags tasks when required hours exceed available capacity",
    test_type="Unit",
    preconditions="Task requiring 15 hours due tomorrow, user daily capacity only 6 hours",
    steps="1. Define task requiring 15.0h due in 24 hours\n2. Call assess_task_risk()\n3. Assert risk level is 'critical' with explanatory reason",
    input_data="remaining=15.0h, capacity_before_deadline=6.0h",
    expected="risk_assessment.risk_level in ('critical', 'high')",
)
def test_deadline_risk_critical_assessment():
    ref_time = datetime(2026, 10, 20, 10, 0, tzinfo=timezone.utc)
    t_heavy = make_task(
        "t-heavy",
        "Systems Architecture Capstone",
        datetime(2026, 10, 21, 10, 0, tzinfo=timezone.utc),
        priority="critical",
        remaining_duration=15.0,
    )
    avail = UserAvailability(
        user_id="usr_test",
        day="tuesday",
        enabled=True,
        start_time="09:00",
        end_time="17:00",
    )
    prefs = UserPreferences(user_id="usr_test", daily_focus_hours_limit=6.0)

    risk = assess_task_risk(
        task=t_heavy,
        reference_time=ref_time,
        availability_map={"tuesday": avail},
        preferences=prefs,
    )
    assert risk is not None
    assert risk.risk_level in ("critical", "high")
    assert "focus capacity" in risk.risk_reason.lower() or "remaining work" in risk.risk_reason.lower()
