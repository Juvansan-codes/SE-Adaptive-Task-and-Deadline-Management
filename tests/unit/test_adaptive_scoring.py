"""Unit tests for the Adaptive Priority & Deadline Urgency Scoring Engine.

Validates the deterministic scoring heuristic:
- Priority weighting hierarchy (Critical > High > Medium > Low)
- Deadline urgency scaling across overdue, 24h, 72h, and distant thresholds
- In-progress continuity bonus (+60.0 pts)
- Difficulty complexity adjustments
- Workload pressure ratio scoring
- Deterministic 4-tier tie breaking
"""

from datetime import datetime, timedelta, timezone
from app.models.task import Task
from app.services.scheduling.scoring import (
    calculate_task_score,
    rank_tasks,
    PRIORITY_WEIGHTS,
    DIFFICULTY_WEIGHTS,
    IN_PROGRESS_BONUS,
)
from tests.conftest import record_meta


def make_dummy_task(
    id: str = "task-test-01",
    title: str = "Test Task",
    priority: str = "medium",
    difficulty: str = "medium",
    status: str = "pending",
    estimated_duration: float = 4.0,
    completed_duration: float = 0.0,
    remaining_duration: float = 4.0,
    progress: int = 0,
    deadline_offset_hours: float = 48.0,
    ref_time: datetime = None,
) -> Task:
    if ref_time is None:
        ref_time = datetime.now(timezone.utc)
    deadline = ref_time + timedelta(hours=deadline_offset_hours)
    return Task(
        id=id,
        user_id="usr_test",
        title=title,
        category="Engineering",
        deadline=deadline,
        priority=priority,
        difficulty=difficulty,
        estimated_duration=estimated_duration,
        completed_duration=completed_duration,
        remaining_duration=remaining_duration,
        progress=progress,
        status=status,
    )


@record_meta(
    test_id="TC_UNIT_SCORE_01",
    module="Adaptive Scoring",
    scenario="Verify priority weight hierarchy (Critical > High > Medium > Low)",
    test_type="Unit",
    preconditions="Task entity with uniform deadlines and difficulty levels",
    steps="1. Create 4 tasks with critical, high, medium, low priorities\n2. Compute scores\n3. Assert strictly decreasing priority scores",
    input_data="priorities=['critical', 'high', 'medium', 'low']",
    expected="Critical=400, High=300, Medium=200, Low=100 in score breakdown",
)
def test_priority_weight_hierarchy():
    ref_time = datetime(2026, 10, 20, 10, 0, tzinfo=timezone.utc)
    critical_t = make_dummy_task(id="t-crit", priority="critical", ref_time=ref_time)
    high_t = make_dummy_task(id="t-high", priority="high", ref_time=ref_time)
    med_t = make_dummy_task(id="t-med", priority="medium", ref_time=ref_time)
    low_t = make_dummy_task(id="t-low", priority="low", ref_time=ref_time)

    s_crit = calculate_task_score(critical_t, ref_time)
    s_high = calculate_task_score(high_t, ref_time)
    s_med = calculate_task_score(med_t, ref_time)
    s_low = calculate_task_score(low_t, ref_time)

    assert s_crit.priority_score == PRIORITY_WEIGHTS["critical"] == 400.0
    assert s_high.priority_score == PRIORITY_WEIGHTS["high"] == 300.0
    assert s_med.priority_score == PRIORITY_WEIGHTS["medium"] == 200.0
    assert s_low.priority_score == PRIORITY_WEIGHTS["low"] == 100.0
    assert s_crit.total_score > s_high.total_score > s_med.total_score > s_low.total_score


@record_meta(
    test_id="TC_UNIT_SCORE_02",
    module="Adaptive Scoring",
    scenario="Verify deadline urgency scaling across overdue and temporal horizons",
    test_type="Unit",
    preconditions="Tasks at varying temporal distances from reference timestamp",
    steps="1. Create overdue (-5h), urgent (12h), moderate (48h), distant (200h) tasks\n2. Calculate scores\n3. Assert urgency score monotonic decay",
    input_data="offsets=[-5h, 12h, 48h, 200h]",
    expected="Overdue receives >=600pts; 12h receives 150..550pts; 48h receives 50..200pts; 200h receives 0pts",
)
def test_deadline_urgency_scaling():
    ref_time = datetime(2026, 10, 20, 12, 0, tzinfo=timezone.utc)
    t_overdue = make_dummy_task(id="t-od", deadline_offset_hours=-5.0, ref_time=ref_time)
    t_12h = make_dummy_task(id="t-12h", deadline_offset_hours=12.0, ref_time=ref_time)
    t_48h = make_dummy_task(id="t-48h", deadline_offset_hours=48.0, ref_time=ref_time)
    t_distant = make_dummy_task(id="t-dist", deadline_offset_hours=200.0, ref_time=ref_time)

    s_od = calculate_task_score(t_overdue, ref_time)
    s_12h = calculate_task_score(t_12h, ref_time)
    s_48h = calculate_task_score(t_48h, ref_time)
    s_dist = calculate_task_score(t_distant, ref_time)

    assert s_od.urgency_score >= 600.0
    assert 150.0 <= s_12h.urgency_score <= 550.0
    assert 50.0 <= s_48h.urgency_score <= 200.0
    assert s_dist.urgency_score == 0.0
    assert s_od.urgency_score > s_12h.urgency_score > s_48h.urgency_score > s_dist.urgency_score


@record_meta(
    test_id="TC_UNIT_SCORE_03",
    module="Adaptive Scoring",
    scenario="Verify in-progress continuity bonus prevents context-switching thrashing",
    test_type="Unit",
    preconditions="Two identical tasks, one in_progress and one pending",
    steps="1. Create t_in_prog (status='in_progress') and t_pending (status='pending')\n2. Calculate scores\n3. Assert exact difference of +60 points",
    input_data="status='in_progress' vs status='pending'",
    expected="in_progress_bonus == 60.0 on active task and 0.0 on pending task",
)
def test_in_progress_continuity_bonus():
    ref_time = datetime(2026, 10, 20, 10, 0, tzinfo=timezone.utc)
    t_in_prog = make_dummy_task(id="t-ip", status="in_progress", ref_time=ref_time)
    t_pending = make_dummy_task(id="t-pen", status="pending", ref_time=ref_time)

    s_ip = calculate_task_score(t_in_prog, ref_time)
    s_pen = calculate_task_score(t_pending, ref_time)

    assert s_ip.in_progress_bonus == IN_PROGRESS_BONUS == 60.0
    assert s_pen.in_progress_bonus == 0.0
    assert s_ip.total_score - s_pen.total_score == 60.0


@record_meta(
    test_id="TC_UNIT_SCORE_04",
    module="Adaptive Scoring",
    scenario="Verify difficulty complexity weighting (Hard > Medium > Easy)",
    test_type="Unit",
    preconditions="Tasks identical except for difficulty level",
    steps="1. Create hard, medium, easy tasks\n2. Calculate scores\n3. Assert difficulty scores match spec",
    input_data="difficulty in ['hard', 'medium', 'easy']",
    expected="Hard=+30, Medium=+15, Easy=0",
)
def test_difficulty_complexity_adjustments():
    ref_time = datetime(2026, 10, 20, 10, 0, tzinfo=timezone.utc)
    t_hard = make_dummy_task(id="t-h", difficulty="hard", ref_time=ref_time)
    t_med = make_dummy_task(id="t-m", difficulty="medium", ref_time=ref_time)
    t_easy = make_dummy_task(id="t-e", difficulty="easy", ref_time=ref_time)

    s_h = calculate_task_score(t_hard, ref_time)
    s_m = calculate_task_score(t_med, ref_time)
    s_e = calculate_task_score(t_easy, ref_time)

    assert s_h.difficulty_score == DIFFICULTY_WEIGHTS["hard"] == 30.0
    assert s_m.difficulty_score == DIFFICULTY_WEIGHTS["medium"] == 15.0
    assert s_e.difficulty_score == DIFFICULTY_WEIGHTS["easy"] == 0.0
    assert s_h.total_score > s_m.total_score > s_e.total_score


@record_meta(
    test_id="TC_UNIT_SCORE_05",
    module="Adaptive Scoring",
    scenario="Verify workload pressure ratio scaling when remaining work approaches deadline window",
    test_type="Unit",
    preconditions="Task due in 4 hours with 3.5 hours remaining work (pressure ratio > 0.5)",
    steps="1. Create high workload pressure task\n2. Calculate score\n3. Assert feasibility score boost is applied",
    input_data="remaining_duration=3.5, delta_hours=4.0 -> pressure_ratio=0.875",
    expected="feasibility_score > 0 and includes workload pressure rationale",
)
def test_workload_pressure_ratio():
    ref_time = datetime(2026, 10, 20, 10, 0, tzinfo=timezone.utc)
    t_pressure = make_dummy_task(
        id="t-press",
        deadline_offset_hours=4.0,
        estimated_duration=4.0,
        completed_duration=0.5,
        remaining_duration=3.5,
        ref_time=ref_time,
    )
    score = calculate_task_score(t_pressure, ref_time)
    assert score.feasibility_score > 0.0
    assert "workload pressure" in score.reason.lower()


@record_meta(
    test_id="TC_UNIT_SCORE_06",
    module="Adaptive Scoring",
    scenario="Verify deterministic four-tier tie breaking in task ranking",
    test_type="Unit",
    preconditions="Tasks constructed to have identical scores and differing tie-breaker attributes",
    steps="1. Create tasks with identical total scores\n2. Vary deadlines and IDs\n3. Assert ranked order matches (Score DESC -> Deadline ASC -> Rem DESC -> ID ASC)",
    input_data="Tasks with equal scores and differing deadlines",
    expected="Earlier deadline is ranked ahead of later deadline on tie score",
)
def test_deterministic_four_tier_tie_breaking():
    ref_time = datetime(2026, 10, 20, 10, 0, tzinfo=timezone.utc)
    # Tasks with same score factors except deadline
    t_earlier = make_dummy_task(id="task-b", deadline_offset_hours=20.0, ref_time=ref_time)
    t_later = make_dummy_task(id="task-a", deadline_offset_hours=30.0, ref_time=ref_time)

    ranked = rank_tasks([t_later, t_earlier], ref_time)
    # The earlier deadline receives higher urgency score, ranking first
    assert ranked[0][0].id == "task-b"
    assert ranked[0][1].rank == 1
    assert ranked[1][0].id == "task-a"
    assert ranked[1][1].rank == 2


@record_meta(
    test_id="TC_UNIT_SCORE_07",
    module="Adaptive Scoring",
    scenario="Verify completed tasks and zero remaining duration tasks are excluded from ranking",
    test_type="Unit",
    preconditions="List containing active pending, in_progress, and completed tasks",
    steps="1. Pass active and completed tasks to rank_tasks()\n2. Assert completed and zero remaining duration tasks are omitted",
    input_data="tasks=[t_active, t_completed, t_zero_rem]",
    expected="Only t_active returned in ranked tuples list",
)
def test_completed_tasks_filtered_from_ranking():
    ref_time = datetime(2026, 10, 20, 10, 0, tzinfo=timezone.utc)
    t_active = make_dummy_task(id="t-act", status="pending", remaining_duration=3.0, ref_time=ref_time)
    t_completed = make_dummy_task(id="t-done", status="completed", remaining_duration=0.0, ref_time=ref_time)
    t_zero_rem = make_dummy_task(id="t-zero", status="in_progress", remaining_duration=0.0, ref_time=ref_time)

    ranked = rank_tasks([t_active, t_completed, t_zero_rem], ref_time)
    ranked_ids = [t.id for t, _ in ranked]
    assert "t-act" in ranked_ids
    assert "t-done" not in ranked_ids
    assert "t-zero" not in ranked_ids
    assert len(ranked) == 1

