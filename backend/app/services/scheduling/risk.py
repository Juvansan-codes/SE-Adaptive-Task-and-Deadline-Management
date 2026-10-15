"""Deadline risk detection and timeline compression analysis.

Classifies active tasks into deterministic risk tiers:
- 'critical': Deadline elapsed, or remaining work exceeds available capacity before deadline.
- 'high': Timeline is severely compressed (capacity < 1.25x remaining work within 36h).
- 'moderate': Tight buffer (capacity < 1.5x remaining work within 72h) or approaching high-priority deadline.
"""

from datetime import datetime, timezone
from typing import List, Dict, Optional
from app.models.task import Task
from app.models.availability import UserAvailability
from app.models.preferences import UserPreferences
from app.services.scheduling.schemas import TaskRiskAssessment, RiskLevel
from app.services.scheduling.capacity import calculate_available_capacity_range


def assess_task_risk(
    task: Task,
    reference_time: datetime,
    availability_map: Dict[str, UserAvailability],
    preferences: Optional[UserPreferences] = None,
) -> Optional[TaskRiskAssessment]:
    """
    Evaluate deadline risk for an individual active task.
    Returns TaskRiskAssessment if at risk, or None if safe / completed.
    """
    remaining_work = max(0.0, float(task.remaining_duration))
    if task.status == "completed" or remaining_work <= 0.0:
        return None

    task_deadline = task.deadline
    if task_deadline.tzinfo is None:
        task_deadline = task_deadline.replace(tzinfo=timezone.utc)
    if reference_time.tzinfo is None:
        reference_time = reference_time.replace(tzinfo=timezone.utc)

    delta_seconds = (task_deadline - reference_time).total_seconds()
    delta_hours = round(delta_seconds / 3600.0, 2)
    deadline_fmt = task_deadline.strftime("%Y-%m-%d %H:%M UTC")

    # 1. Overdue task
    if delta_hours <= 0:
        overdue_hours = abs(delta_hours)
        return TaskRiskAssessment(
            task_id=task.id,
            risk_level="critical",
            risk_reason=(
                f"Deadline elapsed ({deadline_fmt}) with {remaining_work:.1f}h remaining work. "
                "Immediate schedule rescheduling or deadline extension required."
            ),
            hours_until_deadline=delta_hours,
            remaining_duration_hours=remaining_work,
            available_capacity_before_deadline=0.0,
            is_overdue=True,
        )

    # Calculate actual allocatable focus capacity between now and task deadline
    available_cap = calculate_available_capacity_range(
        reference_time, task_deadline, availability_map, preferences
    )

    # 2. Critical: remaining work strictly exceeds available working hours before deadline
    if available_cap < remaining_work:
        return TaskRiskAssessment(
            task_id=task.id,
            risk_level="critical",
            risk_reason=(
                f"Due in {delta_hours:.1f}h with {remaining_work:.1f}h remaining work, "
                f"exceeding the {available_cap:.1f}h available focus capacity before deadline."
            ),
            hours_until_deadline=delta_hours,
            remaining_duration_hours=remaining_work,
            available_capacity_before_deadline=available_cap,
            is_overdue=False,
        )

    # 3. High: tight window (due within 36h and capacity < 1.25x remaining) or large critical task
    if delta_hours <= 36.0 and available_cap < remaining_work * 1.25:
        return TaskRiskAssessment(
            task_id=task.id,
            risk_level="high",
            risk_reason=(
                f"Due in {delta_hours:.1f}h with {remaining_work:.1f}h remaining work "
                f"and only {available_cap:.1f}h available capacity; timeline buffer critically eroded."
            ),
            hours_until_deadline=delta_hours,
            remaining_duration_hours=remaining_work,
            available_capacity_before_deadline=available_cap,
            is_overdue=False,
        )

    if task.priority == "critical" and remaining_work >= 8.0 and available_cap < remaining_work * 1.5:
        return TaskRiskAssessment(
            task_id=task.id,
            risk_level="high",
            risk_reason=(
                f"Critical priority task requires {remaining_work:.1f}h work with constrained "
                f"available capacity ({available_cap:.1f}h) before deadline."
            ),
            hours_until_deadline=delta_hours,
            remaining_duration_hours=remaining_work,
            available_capacity_before_deadline=available_cap,
            is_overdue=False,
        )

    # 4. Moderate: approaching milestone within 72h with limited buffer, or high priority within 48h
    if delta_hours <= 72.0 and available_cap < remaining_work * 1.5:
        return TaskRiskAssessment(
            task_id=task.id,
            risk_level="moderate",
            risk_reason=(
                f"Milestone due in {delta_hours / 24.0:.1f} days with {remaining_work:.1f}h remaining work; "
                "early allocation recommended to prevent buffer erosion."
            ),
            hours_until_deadline=delta_hours,
            remaining_duration_hours=remaining_work,
            available_capacity_before_deadline=available_cap,
            is_overdue=False,
        )

    if task.priority in ("critical", "high") and delta_hours <= 48.0:
        return TaskRiskAssessment(
            task_id=task.id,
            risk_level="moderate",
            risk_reason=(
                f"{task.priority.capitalize()} priority deliverable due in {delta_hours / 24.0:.1f} days "
                f"with {remaining_work:.1f}h remaining work."
            ),
            hours_until_deadline=delta_hours,
            remaining_duration_hours=remaining_work,
            available_capacity_before_deadline=available_cap,
            is_overdue=False,
        )

    # On track / safe
    return None


def assess_all_tasks_risk(
    tasks: List[Task],
    reference_time: Optional[datetime] = None,
    availability_list: Optional[List[UserAvailability]] = None,
    preferences: Optional[UserPreferences] = None,
) -> List[TaskRiskAssessment]:
    """
    Assess deadline risk across all active tasks and sort by severity.
    Severity order: critical > high > moderate, then earliest deadline.
    """
    if reference_time is None:
        reference_time = datetime.now(timezone.utc)
    elif reference_time.tzinfo is None:
        reference_time = reference_time.replace(tzinfo=timezone.utc)

    avail_map: Dict[str, UserAvailability] = {}
    if availability_list:
        for a in availability_list:
            avail_map[str(a.day).lower()] = a

    severity_weight = {
        "critical": 3,
        "high": 2,
        "moderate": 1,
    }

    assessments: List[TaskRiskAssessment] = []
    for t in tasks:
        risk = assess_task_risk(t, reference_time, avail_map, preferences)
        if risk is not None:
            assessments.append(risk)

    assessments.sort(
        key=lambda r: (
            -severity_weight.get(r.risk_level, 0),
            r.hours_until_deadline,
            -r.remaining_duration_hours,
        )
    )

    return assessments
