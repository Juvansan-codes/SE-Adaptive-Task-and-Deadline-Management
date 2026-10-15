"""Task priority and deadline urgency scoring engine.

Implements a deterministic, rule-based ranking heuristic:
- Priority weighting (critical > high > medium > low)
- Deadline proximity and overdue status scaling
- In-progress continuity bonus to minimize cognitive task switching
- Workload pressure ratio (remaining work vs available window)
- Difficulty complexity adjustments
- Deterministic multi-tier tie-breaking
"""

from datetime import datetime, timezone
from typing import List, Tuple, Optional
from app.models.task import Task
from app.services.scheduling.schemas import TaskScoreBreakdown, RankedTask

PRIORITY_WEIGHTS = {
    "critical": 400.0,
    "high": 300.0,
    "medium": 200.0,
    "low": 100.0,
}

DIFFICULTY_WEIGHTS = {
    "hard": 30.0,
    "medium": 15.0,
    "easy": 0.0,
}

IN_PROGRESS_BONUS = 60.0


def calculate_task_score(
    task: Task, reference_time: datetime
) -> TaskScoreBreakdown:
    """
    Calculate an itemized score breakdown for a single task relative to reference_time.
    """
    # 1. Base Priority
    p_weight = PRIORITY_WEIGHTS.get(str(task.priority).lower(), 150.0)

    # 2. Deadline Urgency
    task_deadline = task.deadline
    if task_deadline.tzinfo is None:
        task_deadline = task_deadline.replace(tzinfo=timezone.utc)
    if reference_time.tzinfo is None:
        reference_time = reference_time.replace(tzinfo=timezone.utc)

    delta_seconds = (task_deadline - reference_time).total_seconds()
    delta_hours = delta_seconds / 3600.0

    urgency_score = 0.0
    urgency_desc = ""

    if delta_hours <= 0:
        # Overdue task receives maximal urgency boost
        overdue_hours = abs(delta_hours)
        urgency_score = 600.0 + min(150.0, overdue_hours * 2.0)
        urgency_desc = f"Overdue by {overdue_hours:.1f}h"
    elif delta_hours <= 24.0:
        # Due today or within 24 hours
        urgency_score = 400.0 * (1.0 - (delta_hours / 24.0)) + 150.0
        urgency_desc = f"Due in {delta_hours:.1f}h"
    elif delta_hours <= 72.0:
        # Due within 3 days
        fraction = (delta_hours - 24.0) / 48.0
        urgency_score = 150.0 * (1.0 - fraction) + 50.0
        urgency_desc = f"Due in {delta_hours / 24.0:.1f} days"
    elif delta_hours <= 168.0:
        # Due within 7 days
        fraction = (delta_hours - 72.0) / 96.0
        urgency_score = 50.0 * (1.0 - fraction)
        urgency_desc = f"Due in {delta_hours / 24.0:.1f} days"
    else:
        urgency_score = 0.0
        urgency_desc = f"Due in {delta_hours / 24.0:.0f} days"

    # 3. Difficulty Complexity
    diff_score = DIFFICULTY_WEIGHTS.get(str(task.difficulty).lower(), 10.0)

    # 4. In-Progress Continuity Bonus
    in_prog_bonus = IN_PROGRESS_BONUS if task.status == "in_progress" else 0.0

    # 5. Workload Pressure (Remaining duration vs time until deadline)
    remaining_work = max(0.0, float(task.remaining_duration))
    feasibility_score = 0.0
    if delta_hours > 0 and remaining_work > 0:
        pressure_ratio = remaining_work / max(1.0, delta_hours)
        if pressure_ratio > 0.5:
            feasibility_score = min(120.0, pressure_ratio * 40.0)
    elif delta_hours <= 0 and remaining_work > 0:
        feasibility_score = 100.0

    total_score = round(
        p_weight + urgency_score + diff_score + in_prog_bonus + feasibility_score,
        2,
    )

    # Generate transparent explanation reason
    reasons = [f"{task.priority.capitalize()} priority ({p_weight:.0f}pts)"]
    if urgency_desc:
        reasons.append(f"{urgency_desc} (+{urgency_score:.0f}pts)")
    if in_prog_bonus > 0:
        reasons.append(f"in-progress continuity (+{in_prog_bonus:.0f}pts)")
    if feasibility_score > 0:
        reasons.append(f"high workload pressure (+{feasibility_score:.0f}pts)")

    summary_reason = "; ".join(reasons)

    return TaskScoreBreakdown(
        task_id=task.id,
        total_score=total_score,
        priority_score=p_weight,
        urgency_score=round(urgency_score, 2),
        difficulty_score=diff_score,
        in_progress_bonus=in_prog_bonus,
        feasibility_score=round(feasibility_score, 2),
        reason=summary_reason,
    )


def rank_tasks(
    tasks: List[Task], reference_time: Optional[datetime] = None
) -> List[Tuple[Task, RankedTask]]:
    """
    Filter for active eligible tasks and sort them deterministically.
    Completed tasks and tasks with 0 remaining duration are excluded.

    Tie-breaking order:
    1. Highest total_score (descending)
    2. Earliest deadline (ascending)
    3. Highest remaining_duration (descending)
    4. Task id (ascending alphabetical)
    """
    if reference_time is None:
        reference_time = datetime.now(timezone.utc)
    elif reference_time.tzinfo is None:
        reference_time = reference_time.replace(tzinfo=timezone.utc)

    # Filter eligible tasks
    eligible = [
        t
        for t in tasks
        if t.status != "completed" and max(0.0, float(t.remaining_duration)) > 0.0
    ]

    scored_items: List[Tuple[Task, TaskScoreBreakdown]] = []
    for t in eligible:
        breakdown = calculate_task_score(t, reference_time)
        scored_items.append((t, breakdown))

    def sort_key(item: Tuple[Task, TaskScoreBreakdown]):
        t, b = item
        t_deadline = t.deadline
        if t_deadline.tzinfo is None:
            t_deadline = t_deadline.replace(tzinfo=timezone.utc)
        return (
            -b.total_score,
            t_deadline,
            -float(t.remaining_duration),
            str(t.id),
        )

    scored_items.sort(key=sort_key)

    ranked: List[Tuple[Task, RankedTask]] = []
    for rank_idx, (t, b) in enumerate(scored_items, start=1):
        ranked_meta = RankedTask(
            task_id=t.id,
            rank=rank_idx,
            score=b.total_score,
            score_breakdown=b,
        )
        ranked.append((t, ranked_meta))

    return ranked
