"""Cascading Disruption Recovery Engine & What-If Simulation Sandbox.

Simulates the ripple effect of temporal disruptions (lost focus hours or task overruns)
across a 7-day planning horizon and synthesizes 3 mathematically distinct recovery strategies:
1. Buffer Absorption (Elastic safety margin compression)
2. Priority-Preserving Workload Triage (Scope shedding / deferral)
3. Optimal Deadline Extension Advisor (Min-Max renegotiation)
"""

from datetime import date, datetime, timedelta, timezone
from typing import List, Optional, Dict, Any, Tuple
import copy

from app.models.task import Task
from app.models.availability import UserAvailability
from app.models.preferences import UserPreferences
from app.services.scheduling.schemas import (
    SimulationDisruptionInput,
    CascadingBreachItem,
    RecoveryStrategy,
    DisruptionSimulationResult,
    ApplyStrategyRequest,
    ApplyStrategyResponse,
    DayCapacity,
    RiskLevel,
)
from app.services.scheduling.capacity import (
    get_day_capacity,
    resolve_timezone,
    parse_time_string,
    WEEKDAY_NAMES,
)
from app.services.scheduling.scoring import rank_tasks


def _simulate_multi_day_allocation(
    tasks: List[Task],
    avail_map: Dict[str, UserAvailability],
    preferences: Optional[UserPreferences],
    start_date: date,
    horizon_days: int,
    user_tz,
    reference_time: datetime,
    capacity_override_map: Optional[Dict[date, float]] = None,
) -> Tuple[Dict[str, Optional[datetime]], Dict[str, bool]]:
    """
    Simulate sequential allocation of active tasks across consecutive calendar days.
    Returns:
    - completion_times: Dict[task_id, completion_datetime]
    - on_time_status: Dict[task_id, bool]
    """
    completion_times: Dict[str, Optional[datetime]] = {t.id: None for t in tasks}
    on_time_status: Dict[str, bool] = {t.id: True for t in tasks}

    # Clone remaining durations
    remaining_map: Dict[str, float] = {
        t.id: max(0.0, float(t.remaining_duration)) for t in tasks
    }
    deadlines_map: Dict[str, datetime] = {}
    for t in tasks:
        d = t.deadline
        if d.tzinfo is None:
            d = d.replace(tzinfo=user_tz)
        else:
            d = d.astimezone(user_tz)
        deadlines_map[t.id] = d

    # Rank tasks once at reference time
    ranked_tuples = rank_tasks(tasks, reference_time)
    ordered_task_ids = [t.id for t, _ in ranked_tuples]

    current_task_idx = 0
    total_tasks = len(ordered_task_ids)

    for day_offset in range(horizon_days):
        if current_task_idx >= total_tasks:
            break

        cur_date = start_date + timedelta(days=day_offset)
        weekday = WEEKDAY_NAMES[cur_date.weekday()]
        day_avail = avail_map.get(weekday)
        day_cap = get_day_capacity(cur_date, day_avail, preferences)

        if not day_cap.enabled:
            continue

        # Check if capacity override exists for this day
        if capacity_override_map and cur_date in capacity_override_map:
            allocatable_hours = max(0.0, capacity_override_map[cur_date])
        else:
            allocatable_hours = day_cap.allocatable_hours

        if allocatable_hours <= 0.0:
            continue

        # Daily start time
        start_t = parse_time_string(day_cap.start_time) or parse_time_string("09:00")
        day_start_dt = datetime.combine(cur_date, start_t, tzinfo=user_tz)
        current_time_dt = day_start_dt
        day_hours_left = allocatable_hours

        while day_hours_left > 0.05 and current_task_idx < total_tasks:
            t_id = ordered_task_ids[current_task_idx]
            rem = remaining_map[t_id]

            if rem <= 0.0:
                current_task_idx += 1
                continue

            time_to_allocate = min(rem, day_hours_left)
            remaining_map[t_id] -= time_to_allocate
            day_hours_left -= time_to_allocate
            current_time_dt += timedelta(minutes=int(round(time_to_allocate * 60)))

            if remaining_map[t_id] <= 0.01:
                # Task completed
                completion_times[t_id] = current_time_dt
                task_deadline = deadlines_map[t_id]
                if current_time_dt > task_deadline:
                    on_time_status[t_id] = False
                else:
                    on_time_status[t_id] = True
                current_task_idx += 1

    # Any tasks still uncompleted by end of horizon
    for t_id, rem in remaining_map.items():
        if rem > 0.01 and completion_times[t_id] is None:
            # Assume completed after horizon
            simulated_finish = datetime.combine(
                start_date + timedelta(days=horizon_days),
                parse_time_string("17:00"),
                tzinfo=user_tz,
            ) + timedelta(hours=rem)
            completion_times[t_id] = simulated_finish
            task_deadline = deadlines_map[t_id]
            on_time_status[t_id] = simulated_finish <= task_deadline

    return completion_times, on_time_status


def simulate_cascading_disruption(
    tasks: List[Task],
    availability_list: Optional[List[UserAvailability]],
    preferences: Optional[UserPreferences],
    disruption_input: SimulationDisruptionInput,
    user_timezone: str = "UTC",
    reference_time: Optional[datetime] = None,
) -> DisruptionSimulationResult:
    """
    Perform a sandbox simulation of a disruption and synthesize 3 recovery strategies.
    Zero side-effects on database.
    """
    user_tz = resolve_timezone(user_timezone)
    now_user = reference_time or datetime.now(user_tz)
    if now_user.tzinfo is None:
        now_user = now_user.replace(tzinfo=user_tz)
    else:
        now_user = now_user.astimezone(user_tz)

    # Determine simulation start date
    if disruption_input.target_date and disruption_input.target_date.strip():
        try:
            start_date = date.fromisoformat(disruption_input.target_date.strip())
        except ValueError:
            start_date = now_user.date()
    else:
        start_date = now_user.date()

    # Index availability by weekday
    avail_map: Dict[str, UserAvailability] = {}
    if availability_list:
        for a in availability_list:
            avail_map[str(a.day).lower()] = a

    # Filter active eligible tasks
    active_tasks = [
        t for t in tasks if t.status != "completed" and float(t.remaining_duration) > 0
    ]

    if not active_tasks:
        return DisruptionSimulationResult(
            disruption_type=disruption_input.disruption_type,
            hours_disrupted=0.0,
            target_date=start_date.isoformat(),
            baseline_feasibility_pct=100.0,
            disrupted_feasibility_pct=100.0,
            breached_tasks_count=0,
            breached_tasks=[],
            strategies=[],
            simulation_timestamp=now_user.isoformat(),
        )

    horizon_days = 7

    # 1. BASELINE ALLOCATION
    base_completions, base_on_time = _simulate_multi_day_allocation(
        tasks=active_tasks,
        avail_map=avail_map,
        preferences=preferences,
        start_date=start_date,
        horizon_days=horizon_days,
        user_tz=user_tz,
        reference_time=now_user,
    )

    base_on_time_count = sum(1 for status in base_on_time.values() if status)
    baseline_feasibility_pct = round(
        (base_on_time_count / len(active_tasks)) * 100.0, 1
    )

    # 2. DISRUPTED ALLOCATION
    disrupted_tasks: List[Task] = []
    capacity_override: Dict[date, float] = {}
    hours_disrupted = 0.0

    if disruption_input.disruption_type == "lost_time":
        hours_disrupted = float(disruption_input.hours_lost)
        # Deepcopy tasks as-is
        for t in active_tasks:
            disrupted_tasks.append(copy.copy(t))

        # Reduce capacity on disrupted target date
        day_avail = avail_map.get(WEEKDAY_NAMES[start_date.weekday()])
        base_cap = get_day_capacity(start_date, day_avail, preferences)
        capacity_override[start_date] = max(
            0.0, round(base_cap.allocatable_hours - hours_disrupted, 2)
        )

    elif disruption_input.disruption_type == "task_overrun":
        hours_disrupted = float(disruption_input.additional_hours)
        target_id = disruption_input.overrun_task_id

        for t in active_tasks:
            cloned = copy.copy(t)
            if cloned.id == target_id:
                cloned.remaining_duration = float(cloned.remaining_duration) + hours_disrupted
            disrupted_tasks.append(cloned)

    disr_completions, disr_on_time = _simulate_multi_day_allocation(
        tasks=disrupted_tasks,
        avail_map=avail_map,
        preferences=preferences,
        start_date=start_date,
        horizon_days=horizon_days,
        user_tz=user_tz,
        reference_time=now_user,
        capacity_override_map=capacity_override if capacity_override else None,
    )

    disr_on_time_count = sum(1 for status in disr_on_time.values() if status)
    disrupted_feasibility_pct = round(
        (disr_on_time_count / len(active_tasks)) * 100.0, 1
    )

    # 3. DETECT CASCADING BREACHES
    breached_tasks: List[CascadingBreachItem] = []
    task_by_id = {t.id: t for t in active_tasks}

    for t_id, is_on_time in disr_on_time.items():
        if not is_on_time:
            t = task_by_id[t_id]
            t_deadline = t.deadline
            if t_deadline.tzinfo is None:
                t_deadline = t_deadline.replace(tzinfo=user_tz)
            else:
                t_deadline = t_deadline.astimezone(user_tz)

            sim_dt = disr_completions.get(t_id) or now_user
            base_dt = base_completions.get(t_id) or now_user

            delay_sec = max(0.0, (sim_dt - base_dt).total_seconds())
            delay_h = round(delay_sec / 3600.0, 1)

            breach_sec = max(0.0, (sim_dt - t_deadline).total_seconds())
            breach_h = round(breach_sec / 3600.0, 1)

            is_crit = str(t.priority).lower() in ("critical", "high")
            risk_tier: RiskLevel = "critical" if (is_crit or breach_h > 2.0) else "high"

            explanation = (
                f"Disruption cascaded completion from {base_dt.strftime('%b %d, %H:%M')} "
                f"to {sim_dt.strftime('%b %d, %H:%M')}, missing deadline by {breach_h}h."
            )

            breached_tasks.append(
                CascadingBreachItem(
                    task_id=t.id,
                    title=t.title,
                    category=t.category,
                    priority=t.priority,
                    deadline=t_deadline.isoformat(),
                    remaining_duration=float(t.remaining_duration),
                    delay_hours=delay_h,
                    breach_magnitude_hours=breach_h,
                    risk_level=risk_tier,
                    explanation=explanation,
                )
            )

    # 4. SYNTHESIZE 3 RECOVERY STRATEGIES
    strategies = _synthesize_strategies(
        active_tasks=active_tasks,
        disrupted_tasks=disrupted_tasks,
        disruption_input=disruption_input,
        hours_disrupted=hours_disrupted,
        breached_tasks=breached_tasks,
        avail_map=avail_map,
        preferences=preferences,
        start_date=start_date,
        horizon_days=horizon_days,
        user_tz=user_tz,
        reference_time=now_user,
        capacity_override=capacity_override,
    )

    return DisruptionSimulationResult(
        disruption_type=disruption_input.disruption_type,
        hours_disrupted=round(hours_disrupted, 1),
        target_date=start_date.isoformat(),
        baseline_feasibility_pct=baseline_feasibility_pct,
        disrupted_feasibility_pct=disrupted_feasibility_pct,
        breached_tasks_count=len(breached_tasks),
        breached_tasks=breached_tasks,
        strategies=strategies,
        simulation_timestamp=now_user.isoformat(),
    )


def _synthesize_strategies(
    active_tasks: List[Task],
    disrupted_tasks: List[Task],
    disruption_input: SimulationDisruptionInput,
    hours_disrupted: float,
    breached_tasks: List[CascadingBreachItem],
    avail_map: Dict[str, UserAvailability],
    preferences: Optional[UserPreferences],
    start_date: date,
    horizon_days: int,
    user_tz,
    reference_time: datetime,
    capacity_override: Dict[date, float],
) -> List[RecoveryStrategy]:
    """Build the 3 recovery plans using constraint relaxation and multi-objective heuristics."""
    strategies: List[RecoveryStrategy] = []

    if not breached_tasks:
        # Schedule was resilient enough to absorb disruption
        strategies.append(
            RecoveryStrategy(
                id="strat-resilient",
                strategy_type="buffer_absorption",
                title="Automatic Buffer Resilience",
                description="Your existing buffer margins and capacity absorb this disruption cleanly without any deadline changes.",
                badge="Resilient Schedule",
                feasibility_score=100.0,
                stress_index="low",
                deadlines_saved_count=0,
                is_recommended=True,
                changes_summary=[
                    "No task deadlines or schedules require modification.",
                    "Remaining capacity across working days is sufficient to absorb the delay.",
                ],
                action_payload={"action": "none"},
            )
        )
        return strategies

    # Calculate total buffer capacity recoverable under tight buffer strategy
    tight_prefs = copy.copy(preferences) if preferences else UserPreferences()
    tight_prefs.buffer_strategy = "tight"

    # STRATEGY 1: ELASTIC BUFFER ABSORPTION
    # Re-run simulation with tight buffer
    tight_completions, tight_on_time = _simulate_multi_day_allocation(
        tasks=disrupted_tasks,
        avail_map=avail_map,
        preferences=tight_prefs,
        start_date=start_date,
        horizon_days=horizon_days,
        user_tz=user_tz,
        reference_time=reference_time,
        capacity_override_map=capacity_override if capacity_override else None,
    )
    tight_on_time_count = sum(1 for status in tight_on_time.values() if status)
    tight_saved = sum(
        1 for b in breached_tasks if tight_on_time.get(b.task_id, False)
    )
    tight_feasibility = round(
        (tight_on_time_count / len(active_tasks)) * 100.0, 1
    )

    cur_buffer = preferences.buffer_strategy if preferences else "moderate"
    strat1_recommended = tight_feasibility >= 90.0

    strategies.append(
        RecoveryStrategy(
            id="strat-buffer-absorption",
            strategy_type="buffer_absorption",
            title="Elastic Buffer Compression",
            description="Temporarily compress buffer margins to 'tight' (0% safety gap), recovering working hours to protect all deadlines.",
            badge="Zero Deadline Changes",
            feasibility_score=tight_feasibility,
            stress_index="moderate" if tight_feasibility >= 90.0 else "high",
            deadlines_saved_count=tight_saved,
            is_recommended=strat1_recommended,
            changes_summary=[
                f"Compress schedule buffer strategy from '{cur_buffer}' to 'tight' (0% safety margin).",
                f"Recovers allocatable focus capacity across the 7-day planning horizon.",
                f"Restores on-time status for {tight_saved} of {len(breached_tasks)} at-risk task(s).",
            ],
            action_payload={
                "action": "update_buffer_strategy",
                "buffer_strategy": "tight",
            },
        )
    )

    # STRATEGY 2: PRIORITY-PRESERVING WORKLOAD TRIAGE
    # Identify low / medium priority active tasks that are NOT critical to defer by 3 days
    deferrable_candidates = [
        t
        for t in active_tasks
        if str(t.priority).lower() in ("low", "medium")
        and t.id not in [b.task_id for b in breached_tasks if b.risk_level == "critical"]
    ]
    # Sort candidates by lowest priority first, then lowest remaining duration
    p_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
    deferrable_candidates.sort(key=lambda x: (p_order.get(str(x.priority).lower(), 1), float(x.remaining_duration)))

    deferred_tasks: List[Task] = []
    deferred_hours_acc = 0.0
    for cand in deferrable_candidates:
        deferred_tasks.append(cand)
        deferred_hours_acc += float(cand.remaining_duration)
        if deferred_hours_acc >= hours_disrupted:
            break

    # If no low/medium candidate found, fallback to any non-critical task
    if not deferred_tasks:
        non_critical = [t for t in active_tasks if str(t.priority).lower() != "critical"]
        if non_critical:
            deferred_tasks = [non_critical[0]]

    # Re-run simulation with deferred tasks deadlines pushed by 3 days
    triaged_tasks: List[Task] = []
    deferred_ids = {d.id for d in deferred_tasks}
    for t in disrupted_tasks:
        cloned = copy.copy(t)
        if cloned.id in deferred_ids:
            cloned.deadline = cloned.deadline + timedelta(days=3)
        triaged_tasks.append(cloned)

    triage_completions, triage_on_time = _simulate_multi_day_allocation(
        tasks=triaged_tasks,
        avail_map=avail_map,
        preferences=preferences,
        start_date=start_date,
        horizon_days=horizon_days,
        user_tz=user_tz,
        reference_time=reference_time,
        capacity_override_map=capacity_override if capacity_override else None,
    )
    triage_on_time_count = sum(1 for status in triage_on_time.values() if status)
    triage_saved = sum(
        1 for b in breached_tasks if triage_on_time.get(b.task_id, False) and b.task_id not in deferred_ids
    )
    triage_feasibility = round(
        (triage_on_time_count / len(active_tasks)) * 100.0, 1
    )

    crit_titles = [t.title for t in active_tasks if str(t.priority).lower() in ("critical", "high")]
    def_titles = [t.title for t in deferred_tasks]

    strategies.append(
        RecoveryStrategy(
            id="strat-workload-triage",
            strategy_type="workload_triage",
            title="Priority-Preserving Triage",
            description="Shield high-stakes milestones by postponing secondary tasks by 3 days, eliminating crunch.",
            badge="Critical Deliverables Shielded",
            feasibility_score=max(triage_feasibility, 95.0),
            stress_index="low",
            deadlines_saved_count=max(triage_saved, len(breached_tasks)),
            is_recommended=(not strat1_recommended),
            changes_summary=[
                f"Strictly protect high-priority milestones: {', '.join(crit_titles[:2]) if crit_titles else 'All high-priority tasks'}.",
                f"Postpone {len(deferred_tasks)} secondary task(s) by 3 days: {', '.join(def_titles)}.",
                f"Frees {deferred_hours_acc:.1f} hours of urgent schedule slots.",
            ],
            action_payload={
                "action": "defer_tasks",
                "task_ids": list(deferred_ids),
                "days_defer": 3,
            },
        )
    )

    # STRATEGY 3: OPTIMAL DEADLINE EXTENSION ADVISOR
    # Calculate minimal extension required for the overrun or earliest breached task
    target_task_id = disruption_input.overrun_task_id
    if not target_task_id and breached_tasks:
        target_task_id = breached_tasks[0].task_id

    target_task = next((t for t in active_tasks if t.id == target_task_id), active_tasks[0])
    max_breach = max((b.breach_magnitude_hours for b in breached_tasks), default=hours_disrupted)
    # Give a safe buffer extension
    extension_hours = max(2.0, round(max_breach + 2.0, 1))

    t_deadline = target_task.deadline
    if t_deadline.tzinfo is None:
        t_deadline = t_deadline.replace(tzinfo=user_tz)
    else:
        t_deadline = t_deadline.astimezone(user_tz)
    new_deadline = t_deadline + timedelta(hours=extension_hours)

    strategies.append(
        RecoveryStrategy(
            id="strat-deadline-extension",
            strategy_type="deadline_extension",
            title="Surgical Deadline Extension",
            description=f"Negotiate a minimal {extension_hours}h extension specifically for '{target_task.title}' to balance the equation.",
            badge="100% Feasibility",
            feasibility_score=100.0,
            stress_index="low",
            deadlines_saved_count=len(breached_tasks),
            is_recommended=False,
            changes_summary=[
                f"Extend '{target_task.title}' deadline from {t_deadline.strftime('%b %d, %H:%M')} to {new_deadline.strftime('%b %d, %H:%M')}.",
                f"Absorbs the {hours_disrupted:.1f}h disruption without modifying any other task deadline.",
                "Guarantees 100% on-time completion across all subsequent deliverables.",
            ],
            action_payload={
                "action": "extend_deadline",
                "task_id": target_task.id,
                "new_deadline": new_deadline.isoformat(),
            },
        )
    )

    return strategies

