"""Unit tests for Cascading Disruption Recovery Engine & What-If Simulation Sandbox."""

import pytest
from datetime import datetime, date, timedelta, timezone
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.profile import Profile
from app.models.task import Task
from app.models.availability import UserAvailability
from app.models.preferences import UserPreferences
from app.services.scheduling.schemas import (
    SimulationDisruptionInput,
    ApplyStrategyRequest,
)
from app.services.scheduling.simulation import (
    simulate_cascading_disruption,
)
from app.services.schedule_service import ScheduleService
from tests.conftest import record_meta


@pytest.fixture
def base_availability():
    """Standard Monday-Friday 09:00-17:00 availability."""
    days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    avail_list = []
    for d in days:
        enabled = d not in ("saturday", "sunday")
        avail_list.append(
            UserAvailability(
                id=str(uuid.uuid4()),
                user_id="test-user-sim",
                day=d,
                enabled=enabled,
                start_time="09:00",
                end_time="17:00",
            )
        )
    return avail_list


@pytest.fixture
def base_preferences():
    return UserPreferences(
        id=str(uuid.uuid4()),
        user_id="test-user-sim",
        daily_focus_hours_limit=6.0,
        buffer_strategy="moderate",
    )


@pytest.fixture
def in_memory_db():
    """Isolated in-memory SQLite session for testing database mutations."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        profile = Profile(
            id="test-user-sim",
            email="test@sim.com",
            name="Sim User",
            timezone="UTC",
        )
        session.add(profile)
        session.commit()
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@record_meta(
    test_id="TC_UNIT_SIM_01",
    module="Disruption Simulator",
    scenario="Verify resilient schedule absorbs minor disruptions without cascading breaches",
    test_type="Unit",
    preconditions="Task due in 2 days with moderate buffer capacity",
    steps="1. Define task requiring 2h\n2. Introduce 1h lost time disruption\n3. Run simulate_cascading_disruption\n4. Assert breach count is 0 and resilient plan returned",
    input_data="hours_lost=1.0, disruption_type='lost_time'",
    expected="breached_tasks_count==0, disrupted_feasibility_pct==100.0",
)
def test_simulation_resilient_schedule_when_disruption_is_small(
    base_availability, base_preferences
):
    """Small disruption within available buffer should not cause any cascading breaches."""
    ref_time = datetime(2026, 10, 12, 9, 0, tzinfo=timezone.utc)  # Monday

    t1 = Task(
        id="t-1",
        user_id="test-user-sim",
        title="Quick Documentation",
        category="Docs",
        deadline=ref_time + timedelta(days=2),
        priority="medium",
        difficulty="easy",
        estimated_duration=2.0,
        completed_duration=0.0,
        remaining_duration=2.0,
        progress=0,
        status="pending",
    )

    disruption = SimulationDisruptionInput(
        disruption_type="lost_time",
        target_date="2026-10-12",
        hours_lost=1.0,
    )

    result = simulate_cascading_disruption(
        tasks=[t1],
        availability_list=base_availability,
        preferences=base_preferences,
        disruption_input=disruption,
        user_timezone="UTC",
        reference_time=ref_time,
    )

    assert result.breached_tasks_count == 0
    assert result.disrupted_feasibility_pct == 100.0
    assert len(result.strategies) >= 1
    assert result.strategies[0].id == "strat-resilient"


@record_meta(
    test_id="TC_UNIT_SIM_02",
    module="Disruption Simulator",
    scenario="Verify severe task overrun triggers cascading breach detection across downstream horizon",
    test_type="Unit",
    preconditions="Two sequential tasks on adjacent days under daily focus limits",
    steps="1. Create root task and downstream victim task\n2. Overrun root task by 4 hours\n3. Run simulation\n4. Assert cascading breach detected on downstream task",
    input_data="additional_hours=4.0, disruption_type='task_overrun'",
    expected="breached_tasks_count > 0, disrupted_feasibility_pct < 100.0, 3 strategies generated",
)
def test_simulation_cascading_breaches_detected_on_overrun(
    base_availability, base_preferences
):
    """Severe task overrun pushes downstream tasks past their deadlines, triggering cascading breach detection."""
    ref_time = datetime(2026, 10, 12, 9, 0, tzinfo=timezone.utc)  # Monday

    t1 = Task(
        id="task-root-overrun",
        user_id="test-user-sim",
        title="Core Database Engine",
        category="Backend",
        deadline=ref_time + timedelta(hours=8),  # Mon 17:00
        priority="critical",
        difficulty="hard",
        estimated_duration=4.0,
        completed_duration=0.0,
        remaining_duration=4.0,
        progress=0,
        status="in_progress",
    )

    t2 = Task(
        id="task-downstream-victim",
        user_id="test-user-sim",
        title="Frontend Integration API",
        category="Frontend",
        deadline=ref_time + timedelta(days=1, hours=3),  # Tue 12:00
        priority="high",
        difficulty="medium",
        estimated_duration=4.0,
        completed_duration=0.0,
        remaining_duration=4.0,
        progress=0,
        status="pending",
    )

    disruption = SimulationDisruptionInput(
        disruption_type="task_overrun",
        overrun_task_id="task-root-overrun",
        additional_hours=4.0,
        target_date="2026-10-12",
    )

    result = simulate_cascading_disruption(
        tasks=[t1, t2],
        availability_list=base_availability,
        preferences=base_preferences,
        disruption_input=disruption,
        user_timezone="UTC",
        reference_time=ref_time,
    )

    assert result.breached_tasks_count > 0
    assert result.disrupted_feasibility_pct < 100.0

    strat_types = [s.strategy_type for s in result.strategies]
    assert "buffer_absorption" in strat_types
    assert "workload_triage" in strat_types
    assert "deadline_extension" in strat_types


@record_meta(
    test_id="TC_UNIT_SIM_03",
    module="Disruption Simulator",
    scenario="Verify workload triage recovery strategy defers non-critical tasks and strictly protects critical deliverables",
    test_type="Unit",
    preconditions="Critical task and low-priority task active in workspace",
    steps="1. Define critical deliverable and low priority task\n2. Introduce 3h capacity loss\n3. Run simulation\n4. Assert low priority task is selected for deferral and critical task preserved",
    input_data="hours_lost=3.0, priorities=['critical', 'low']",
    expected="triage strategy defers low priority task only, never critical deliverable",
)
def test_simulation_priority_triage_preserves_critical_milestones(
    base_availability, base_preferences
):
    """Workload triage must defer lower-priority tasks and shield critical deliverables."""
    ref_time = datetime(2026, 10, 12, 9, 0, tzinfo=timezone.utc)

    crit_task = Task(
        id="t-crit",
        user_id="test-user-sim",
        title="Final Architecture Submission",
        category="Architecture",
        deadline=ref_time + timedelta(days=1),
        priority="critical",
        difficulty="hard",
        estimated_duration=5.0,
        completed_duration=0.0,
        remaining_duration=5.0,
        progress=0,
        status="in_progress",
    )

    low_task = Task(
        id="t-low",
        user_id="test-user-sim",
        title="Optional UI Polish",
        category="Design",
        deadline=ref_time + timedelta(days=1, hours=4),
        priority="low",
        difficulty="easy",
        estimated_duration=3.0,
        completed_duration=0.0,
        remaining_duration=3.0,
        progress=0,
        status="pending",
    )

    disruption = SimulationDisruptionInput(
        disruption_type="lost_time",
        target_date="2026-10-12",
        hours_lost=3.0,
    )

    result = simulate_cascading_disruption(
        tasks=[crit_task, low_task],
        availability_list=base_availability,
        preferences=base_preferences,
        disruption_input=disruption,
        user_timezone="UTC",
        reference_time=ref_time,
    )

    triage_strat = next(
        s for s in result.strategies if s.strategy_type == "workload_triage"
    )
    assert "t-low" in triage_strat.action_payload.get("task_ids", [])
    assert "t-crit" not in triage_strat.action_payload.get("task_ids", [])


@record_meta(
    test_id="TC_UNIT_SIM_04",
    module="Disruption Simulator",
    scenario="Verify applying buffer absorption recovery strategy updates user preferences buffer margin",
    test_type="Unit",
    preconditions="User preferences initialized with relaxed buffer strategy",
    steps="1. Create user preferences with buffer='relaxed'\n2. Dispatch apply_recovery_strategy for buffer_absorption\n3. Assert preferences updated to 'tight'",
    input_data="strategy_type='buffer_absorption', buffer_strategy='tight'",
    expected="resp.success is True, preferences.buffer_strategy == 'tight'",
)
def test_apply_recovery_strategy_buffer_update(in_memory_db):
    """Verify applying a buffer_absorption strategy updates user preferences."""
    prefs = UserPreferences(
        id=str(uuid.uuid4()),
        user_id="test-user-sim",
        buffer_strategy="relaxed",
        daily_focus_hours_limit=7.0,
    )
    in_memory_db.add(prefs)
    in_memory_db.commit()

    req = ApplyStrategyRequest(
        strategy_id="strat-buffer-absorption",
        strategy_type="buffer_absorption",
        action_payload={"action": "update_buffer_strategy", "buffer_strategy": "tight"},
    )

    resp = ScheduleService.apply_recovery_strategy(
        db=in_memory_db, user_id="test-user-sim", request=req
    )

    assert resp.success is True
    assert "Elastic Buffer Compression" in resp.applied_strategy_name

    in_memory_db.refresh(prefs)
    assert prefs.buffer_strategy == "tight"


@record_meta(
    test_id="TC_UNIT_SIM_05",
    module="Disruption Simulator",
    scenario="Verify applying workload triage recovery strategy defers task deadlines in persistent database",
    test_type="Unit",
    preconditions="Task persisted in database with initial deadline",
    steps="1. Persist task in database\n2. Dispatch apply_recovery_strategy with defer_tasks action\n3. Assert task deadline shifted by exactly 3 days",
    input_data="strategy_type='workload_triage', days_defer=3",
    expected="resp.success is True, task deadline shifted by 3 days in DB",
)
def test_apply_recovery_strategy_task_deferral(in_memory_db):
    """Verify applying workload_triage defers task deadlines."""
    base_dl = datetime.now(timezone.utc) + timedelta(days=2)
    task = Task(
        id="defer-target-task",
        user_id="test-user-sim",
        title="Defer Me",
        category="Testing",
        deadline=base_dl,
        priority="low",
        difficulty="easy",
        estimated_duration=3.0,
        completed_duration=0.0,
        remaining_duration=3.0,
        progress=0,
        status="pending",
    )
    in_memory_db.add(task)
    in_memory_db.commit()

    req = ApplyStrategyRequest(
        strategy_id="strat-workload-triage",
        strategy_type="workload_triage",
        action_payload={"action": "defer_tasks", "task_ids": ["defer-target-task"], "days_defer": 3},
    )

    resp = ScheduleService.apply_recovery_strategy(
        db=in_memory_db, user_id="test-user-sim", request=req
    )

    assert resp.success is True
    in_memory_db.refresh(task)
    task_dl = task.deadline.replace(tzinfo=timezone.utc) if task.deadline.tzinfo is None else task.deadline
    diff_days = (task_dl - base_dl).days
    assert diff_days == 3
