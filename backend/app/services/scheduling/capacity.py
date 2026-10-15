"""User availability and capacity calculations.

Computes working windows, focus-hour caps, buffer margins, and workload balances.
Respects:
- Day enabled flags
- Start and end time bounds (HH:MM format)
- UserPreferences daily_focus_hours_limit
- Buffer strategies ('tight'=0%, 'moderate'=10%, 'relaxed'=20%)
"""

from datetime import date, datetime, time
from typing import List, Optional, Dict
from zoneinfo import ZoneInfo
import zoneinfo

from app.models.availability import UserAvailability
from app.models.preferences import UserPreferences
from app.models.task import Task
from app.services.scheduling.schemas import DayCapacity, BufferStrategy

BUFFER_RATIOS: Dict[str, float] = {
    "tight": 0.0,
    "moderate": 0.10,
    "relaxed": 0.20,
}

WEEKDAY_NAMES = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


def resolve_timezone(tz_name: Optional[str]) -> zoneinfo.ZoneInfo:
    """Safely resolve user timezone string with UTC fallback."""
    if not tz_name or not tz_name.strip():
        return ZoneInfo("UTC")

    clean_name = tz_name.strip()
    # Handle common labels like "UTC-05:00 (Eastern Time)"
    if "Eastern" in clean_name or "America/New_York" in clean_name:
        return ZoneInfo("America/New_York")
    if "Pacific" in clean_name or "America/Los_Angeles" in clean_name:
        return ZoneInfo("America/Los_Angeles")
    if "Kolkata" in clean_name or "Asia/Kolkata" in clean_name or "IST" in clean_name:
        return ZoneInfo("Asia/Kolkata")
    if "Tokyo" in clean_name or "Asia/Tokyo" in clean_name:
        return ZoneInfo("Asia/Tokyo")

    try:
        return ZoneInfo(clean_name)
    except Exception:
        return ZoneInfo("UTC")


def parse_time_string(time_str: Optional[str]) -> Optional[time]:
    """Parse 'HH:MM' 24-hour time string into a datetime.time object."""
    if not time_str:
        return None
    try:
        parts = time_str.strip().split(":")
        hours = int(parts[0])
        minutes = int(parts[1]) if len(parts) > 1 else 0
        if 0 <= hours <= 23 and 0 <= minutes <= 59:
            return time(hour=hours, minute=minutes)
    except Exception:
        pass
    return None


def calculate_window_hours(start_str: Optional[str], end_str: Optional[str]) -> float:
    """Calculate duration in decimal hours between start and end times."""
    t_start = parse_time_string(start_str)
    t_end = parse_time_string(end_str)

    if not t_start or not t_end:
        return 0.0

    start_minutes = t_start.hour * 60 + t_start.minute
    end_minutes = t_end.hour * 60 + t_end.minute

    if end_minutes <= start_minutes:
        return 0.0

    return round((end_minutes - start_minutes) / 60.0, 2)


def get_day_capacity(
    target_date: date,
    availability: Optional[UserAvailability] = None,
    preferences: Optional[UserPreferences] = None,
) -> DayCapacity:
    """
    Compute capacity metrics for a given calendar date based on availability and preferences.
    """
    weekday_str = WEEKDAY_NAMES[target_date.weekday()]

    if availability is None or not availability.enabled:
        return DayCapacity(
            date=target_date,
            day_of_week=weekday_str,
            enabled=False,
            start_time=None,
            end_time=None,
            raw_window_hours=0.0,
            focus_limit_hours=0.0,
            available_hours=0.0,
            buffer_hours=0.0,
            allocatable_hours=0.0,
        )

    raw_hours = calculate_window_hours(
        availability.start_time, availability.end_time
    )

    if raw_hours <= 0.0:
        return DayCapacity(
            date=target_date,
            day_of_week=weekday_str,
            enabled=False,
            start_time=availability.start_time,
            end_time=availability.end_time,
            raw_window_hours=0.0,
            focus_limit_hours=0.0,
            available_hours=0.0,
            buffer_hours=0.0,
            allocatable_hours=0.0,
        )

    # Apply daily focus hours limit
    focus_limit = 24.0
    buffer_strategy = "moderate"
    if preferences:
        focus_limit = max(0.5, float(preferences.daily_focus_hours_limit))
        buffer_strategy = str(preferences.buffer_strategy).lower()

    available_hours = min(raw_hours, focus_limit)

    # Apply buffer strategy
    buffer_ratio = BUFFER_RATIOS.get(buffer_strategy, 0.10)
    buffer_hours = round(available_hours * buffer_ratio, 2)
    allocatable_hours = max(0.0, round(available_hours - buffer_hours, 2))

    return DayCapacity(
        date=target_date,
        day_of_week=weekday_str,
        enabled=True,
        start_time=availability.start_time,
        end_time=availability.end_time,
        raw_window_hours=raw_hours,
        focus_limit_hours=focus_limit,
        available_hours=available_hours,
        buffer_hours=buffer_hours,
        allocatable_hours=allocatable_hours,
    )


def calculate_available_capacity_range(
    start_dt: datetime,
    end_dt: datetime,
    availability_map: Dict[str, UserAvailability],
    preferences: Optional[UserPreferences],
) -> float:
    """
    Calculate the total allocatable working hours available between start_dt and end_dt.
    Used for deadline feasibility and risk analysis.
    """
    if end_dt <= start_dt:
        return 0.0

    current_date = start_dt.date()
    end_date = end_dt.date()
    total_hours = 0.0

    while current_date <= end_date:
        weekday = WEEKDAY_NAMES[current_date.weekday()]
        day_avail = availability_map.get(weekday)
        cap = get_day_capacity(current_date, day_avail, preferences)

        if cap.enabled and cap.allocatable_hours > 0:
            if current_date == start_dt.date() and current_date == end_date:
                # Same day slice: fraction between start and end
                t_start = parse_time_string(cap.start_time)
                t_end = parse_time_string(cap.end_time)
                if t_start and t_end:
                    win_start = datetime.combine(
                        current_date, t_start, tzinfo=start_dt.tzinfo
                    )
                    win_end = datetime.combine(
                        current_date, t_end, tzinfo=start_dt.tzinfo
                    )
                    eff_start = max(win_start, start_dt)
                    eff_end = min(win_end, end_dt)
                    if eff_end > eff_start:
                        ratio = (
                            eff_end - eff_start
                        ).total_seconds() / (win_end - win_start).total_seconds()
                        total_hours += round(cap.allocatable_hours * ratio, 2)
            elif current_date == start_dt.date():
                # First day: from start_dt to end of window
                t_start = parse_time_string(cap.start_time)
                t_end = parse_time_string(cap.end_time)
                if t_start and t_end:
                    win_start = datetime.combine(
                        current_date, t_start, tzinfo=start_dt.tzinfo
                    )
                    win_end = datetime.combine(
                        current_date, t_end, tzinfo=start_dt.tzinfo
                    )
                    eff_start = max(win_start, start_dt)
                    if win_end > eff_start:
                        ratio = (
                            win_end - eff_start
                        ).total_seconds() / (win_end - win_start).total_seconds()
                        total_hours += round(cap.allocatable_hours * ratio, 2)
            elif current_date == end_date:
                # Last day: from start of window to end_dt
                t_start = parse_time_string(cap.start_time)
                t_end = parse_time_string(cap.end_time)
                if t_start and t_end:
                    win_start = datetime.combine(
                        current_date, t_start, tzinfo=end_dt.tzinfo
                    )
                    win_end = datetime.combine(
                        current_date, t_end, tzinfo=end_dt.tzinfo
                    )
                    eff_end = min(win_end, end_dt)
                    if eff_end > win_start:
                        ratio = (
                            eff_end - win_start
                        ).total_seconds() / (win_end - win_start).total_seconds()
                        total_hours += round(cap.allocatable_hours * ratio, 2)
            else:
                # Full day in between
                total_hours += cap.allocatable_hours

        # Move to next day
        current_date = date.fromordinal(current_date.toordinal() + 1)

    return round(total_hours, 2)


def calculate_total_workload(tasks: List[Task]) -> float:
    """Sum total remaining workload in decimal hours across active tasks."""
    return round(
        sum(
            max(0.0, float(t.remaining_duration))
            for t in tasks
            if t.status != "completed"
        ),
        2,
    )
