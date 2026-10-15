"""
Comprehensive tests for Phase 3B REST API integration:
- Dashboard: Overview calculations, empty behavior, recommendations, at-risk tasks, user isolation, timezone handling.
- Schedule: Date parameters, default date, disabled availability, invalid dates, regeneration, idempotent non-duplication.
- Settings: Unified GET/PATCH, preferences, availability validation, focus limits, reset, multi-tenant isolation.
"""

import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from tests.conftest import make_auth_headers
from app.models.task import Task
from app.models.profile import Profile
from app.models.preferences import UserPreferences
from app.models.availability import UserAvailability


# ==============================================================================
# DASHBOARD API TESTS
# ==============================================================================

def test_dashboard_overview_empty_user(authed_client: TestClient):
    """Verify clean empty metrics when a user has no tasks."""
    headers = make_auth_headers(user_id="user-dash-empty")

    response = authed_client.get("/api/dashboard/overview", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert "availableTimeHours" in data
    assert isinstance(data["availableTimeHours"], (int, float))
    assert data["scheduledWorkloadHours"] == 0.0
    assert data["overallProgress"] == 0
    assert data["pendingTasksCount"] == 0
    assert data["atRiskTasksCount"] == 0
    assert data["completedTodayCount"] == 0


def test_dashboard_overview_with_tasks(authed_client: TestClient, db_session):
    """Verify overview calculations for workload, progress, pending counts, and completion."""
    user_id = "user-dash-calc"
    headers = make_auth_headers(user_id=user_id)

    # 1. Create a pending task (6h est, 0h done)
    authed_client.post(
        "/api/tasks",
        json={
            "title": "Task One",
            "category": "Study",
            "deadline": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
            "priority": "high",
            "difficulty": "medium",
            "estimatedDuration": 6.0,
            "completedDuration": 0.0,
            "status": "pending",
        },
        headers=headers,
    )

    # 2. Create an in_progress task (4h est, 2h done)
    authed_client.post(
        "/api/tasks",
        json={
            "title": "Task Two",
            "category": "Lab",
            "deadline": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),
            "priority": "critical",
            "difficulty": "hard",
            "estimatedDuration": 4.0,
            "completedDuration": 2.0,
            "status": "in_progress",
        },
        headers=headers,
    )

    # 3. Create a completed task completed today (2h est, 2h done)
    authed_client.post(
        "/api/tasks",
        json={
            "title": "Task Three Completed",
            "category": "Admin",
            "deadline": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "priority": "low",
            "difficulty": "easy",
            "estimatedDuration": 2.0,
            "completedDuration": 2.0,
            "status": "completed",
        },
        headers=headers,
    )

    response = authed_client.get("/api/dashboard/overview", headers=headers)
    assert response.status_code == 200
    data = response.json()

    # Total estimated = 6 + 4 + 2 = 12h
    # Total completed = 0 + 2 + 2 = 4h
    # Expected overallProgress = round(4/12 * 100) = 33%
    assert data["overallProgress"] == 33
    # Pending (1) + in_progress (1) = 2
    assert data["pendingTasksCount"] == 2
    # 1 completed today
    assert data["completedTodayCount"] == 1
    assert data["scheduledWorkloadHours"] > 0


def test_dashboard_recommendation_flow(authed_client: TestClient):
    """Verify recommendation returns top task, then null when all complete."""
    user_id = "user-dash-rec"
    headers = make_auth_headers(user_id=user_id)

    # When no tasks exist, recommendation is null
    r_empty = authed_client.get("/api/dashboard/recommendation", headers=headers)
    assert r_empty.status_code == 200
    assert r_empty.json() is None

    # Create tasks of varying urgency
    authed_client.post(
        "/api/tasks",
        json={
            "title": "Low Priority Task",
            "category": "Reading",
            "deadline": (datetime.now(timezone.utc) + timedelta(days=10)).isoformat(),
            "priority": "low",
            "difficulty": "easy",
            "estimatedDuration": 2.0,
        },
        headers=headers,
    )

    res_critical = authed_client.post(
        "/api/tasks",
        json={
            "title": "Urgent Math Homework",
            "category": "Math",
            "deadline": (datetime.now(timezone.utc) + timedelta(hours=6)).isoformat(),
            "priority": "critical",
            "difficulty": "hard",
            "estimatedDuration": 3.0,
        },
        headers=headers,
    )
    task_crit_id = res_critical.json()["id"]

    # Recommendation should select the critical math homework
    r_rec = authed_client.get("/api/dashboard/recommendation", headers=headers)
    assert r_rec.status_code == 200
    rec_data = r_rec.json()
    assert rec_data is not None
    assert rec_data["task"]["id"] == task_crit_id
    assert "recommendationReason" in rec_data
    assert "urgencyLabel" in rec_data

    # Mark urgent task completed -> recommendation switches or reflects remaining
    authed_client.patch(
        f"/api/tasks/{task_crit_id}",
        json={"status": "completed"},
        headers=headers,
    )
    r_rec_after = authed_client.get("/api/dashboard/recommendation", headers=headers)
    assert r_rec_after.status_code == 200
    rec_data_after = r_rec_after.json()
    assert rec_data_after["task"]["title"] == "Low Priority Task"


def test_dashboard_at_risk_tasks(authed_client: TestClient):
    """Verify at-risk detection flags tasks whose remaining duration exceeds window."""
    user_id = "user-dash-risk"
    headers = make_auth_headers(user_id=user_id)

    # Create an impossible task (20 hours required, deadline in 4 hours)
    authed_client.post(
        "/api/tasks",
        json={
            "title": "Massive Overdue Project",
            "category": "Capstone",
            "deadline": (datetime.now(timezone.utc) + timedelta(hours=4)).isoformat(),
            "priority": "critical",
            "difficulty": "hard",
            "estimatedDuration": 20.0,
            "completedDuration": 0.0,
            "status": "pending",
        },
        headers=headers,
    )

    # Create a completely safe task (1 hour required, deadline in 14 days)
    authed_client.post(
        "/api/tasks",
        json={
            "title": "Safe Leisure Task",
            "category": "General",
            "deadline": (datetime.now(timezone.utc) + timedelta(days=14)).isoformat(),
            "priority": "low",
            "difficulty": "easy",
            "estimatedDuration": 1.0,
            "completedDuration": 0.0,
            "status": "pending",
        },
        headers=headers,
    )

    r_risk = authed_client.get("/api/dashboard/at-risk", headers=headers)
    assert r_risk.status_code == 200
    risk_list = r_risk.json()

    assert len(risk_list) == 1
    assert risk_list[0]["task"]["title"] == "Massive Overdue Project"
    assert risk_list[0]["riskLevel"] in ("critical", "high", "moderate")
    assert "riskReason" in risk_list[0]
    assert len(risk_list[0]["riskReason"]) > 5


def test_dashboard_upcoming_deadlines_and_schedule_blocks(authed_client: TestClient):
    """Verify upcoming deadlines and schedule blocks formatting."""
    user_id = "user-dash-blocks"
    headers = make_auth_headers(user_id=user_id)

    now = datetime.now(timezone.utc)
    t1 = authed_client.post(
        "/api/tasks",
        json={
            "title": "Early Deadline",
            "category": "Bio",
            "deadline": (now + timedelta(days=1)).isoformat(),
            "priority": "medium",
            "difficulty": "medium",
            "estimatedDuration": 2.0,
        },
        headers=headers,
    ).json()

    t2 = authed_client.post(
        "/api/tasks",
        json={
            "title": "Later Deadline",
            "category": "History",
            "deadline": (now + timedelta(days=4)).isoformat(),
            "priority": "low",
            "difficulty": "easy",
            "estimatedDuration": 1.0,
        },
        headers=headers,
    ).json()

    # Test /api/dashboard/upcoming
    up_resp = authed_client.get("/api/dashboard/upcoming", headers=headers)
    assert up_resp.status_code == 200
    upcoming = up_resp.json()
    assert len(upcoming) >= 2
    assert upcoming[0]["title"] == "Early Deadline"

    # Test /api/dashboard/schedule
    sched_resp = authed_client.get("/api/dashboard/schedule", headers=headers)
    assert sched_resp.status_code == 200
    blocks = sched_resp.json()
    assert isinstance(blocks, list)
    if blocks:
        block = blocks[0]
        assert "id" in block
        assert "startTime" in block
        assert "endTime" in block
        assert "status" in block
        assert block["status"] in ("completed", "current", "upcoming")


def test_dashboard_user_isolation(authed_client: TestClient):
    """Verify metrics and recommendations never leak across users."""
    headers_a = make_auth_headers(user_id="user-a-iso")
    headers_b = make_auth_headers(user_id="user-b-iso")

    # User A creates a task
    authed_client.post(
        "/api/tasks",
        json={
            "title": "User A Private Task",
            "category": "Private",
            "deadline": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "priority": "critical",
            "difficulty": "hard",
            "estimatedDuration": 4.0,
        },
        headers=headers_a,
    )

    # User B checks overview, recommendation, and at-risk
    b_overview = authed_client.get("/api/dashboard/overview", headers=headers_b).json()
    assert b_overview["pendingTasksCount"] == 0
    assert b_overview["scheduledWorkloadHours"] == 0.0

    b_rec = authed_client.get("/api/dashboard/recommendation", headers=headers_b).json()
    assert b_rec is None

    b_risk = authed_client.get("/api/dashboard/at-risk", headers=headers_b).json()
    assert len(b_risk) == 0


def test_dashboard_completed_today_timezone_sensitivity(authed_client: TestClient, db_session):
    """
    Verify completed-today counting respects the user's specific local date,
    avoiding UTC date discrepancies.
    """
    user_id = "user-tz-test"
    headers = make_auth_headers(user_id=user_id)

    # Set user profile timezone to America/New_York (UTC-5/UTC-4)
    # Ensure profile exists first
    authed_client.get("/api/dashboard/overview", headers=headers)
    profile = db_session.query(Profile).filter(Profile.id == user_id).first()
    profile.timezone = "America/New_York"
    db_session.commit()

    # Create a task completed at 2026-10-15 01:30:00 UTC
    # In UTC, that is Oct 15.
    # In America/New_York (EDT, UTC-4), that is 2026-10-14 21:30:00 (Oct 14).
    task_ny = Task(
        user_id=user_id,
        title="Completed at Night",
        category="Test",
        deadline=datetime(2026, 10, 20, 12, 0, tzinfo=timezone.utc),
        priority="low",
        difficulty="easy",
        estimated_duration=1.0,
        completed_duration=1.0,
        status="completed",
        updated_at=datetime(2026, 10, 15, 1, 30, tzinfo=timezone.utc),
    )
    db_session.add(task_ny)
    db_session.commit()

    # Overview called with reference time in NY afternoon on Oct 15
    from app.services.dashboard_service import DashboardService
    ref_time_oct15 = datetime(2026, 10, 15, 15, 0, tzinfo=timezone.utc)
    overview_oct15 = DashboardService.get_overview(
        db_session, user_id, reference_time=ref_time_oct15
    )
    # Since the task was completed on Oct 14 in NY local time, completed_today on Oct 15 should be 0!
    assert overview_oct15.completed_today_count == 0

    # If queried on Oct 14 local NY time (e.g. 2026-10-14 23:00 UTC which is 19:00 NY time)
    ref_time_oct14 = datetime(2026, 10, 14, 23, 0, tzinfo=timezone.utc)
    overview_oct14 = DashboardService.get_overview(
        db_session, user_id, reference_time=ref_time_oct14
    )
    assert overview_oct14.completed_today_count == 1


# ==============================================================================
# SCHEDULE API TESTS
# ==============================================================================

def test_schedule_generation_specified_and_default_date(authed_client: TestClient):
    """Verify schedule generation for specific and default calendar dates."""
    user_id = "user-sched-gen"
    headers = make_auth_headers(user_id=user_id)

    # 1. Default date (omitted query param)
    r_default = authed_client.get("/api/schedule", headers=headers)
    assert r_default.status_code == 200
    data_def = r_default.json()
    assert "date" in data_def
    assert "dayOfWeek" in data_def
    assert "formattedDate" in data_def
    assert "items" in data_def
    assert "totalScheduledHours" in data_def
    assert "availableHours" in data_def

    # 2. Specified ISO date (e.g. a future Tuesday: 2026-10-20)
    r_spec = authed_client.get("/api/schedule?date=2026-10-20", headers=headers)
    assert r_spec.status_code == 200
    data_spec = r_spec.json()
    assert data_spec["date"] == "2026-10-20"
    assert data_spec["dayOfWeek"] == "Tuesday"
    assert data_spec["availableHours"] == 6.5  # Standard weekday default


def test_schedule_invalid_date(authed_client: TestClient):
    """Verify bad date format returns HTTP 400."""
    headers = make_auth_headers(user_id="user-sched-err")

    r = authed_client.get("/api/schedule?date=invalid-date-string", headers=headers)
    assert r.status_code == 400
    assert "Invalid date format" in r.json()["detail"]["message"]

    r_bad_day = authed_client.get("/api/schedule?date=2026-02-31", headers=headers)
    assert r_bad_day.status_code == 400


def test_schedule_disabled_availability_returns_empty(authed_client: TestClient):
    """Verify disabled days (like default Sunday) return 0 available hours and 0 blocks."""
    headers = make_auth_headers(user_id="user-sched-sunday")

    # Sunday: 2026-10-18
    r = authed_client.get("/api/schedule?date=2026-10-18", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["dayOfWeek"] == "Sunday"
    assert data["availableHours"] == 0.0
    assert len(data["items"]) == 0
    assert data["totalScheduledHours"] == 0.0


def test_schedule_regeneration_and_idempotence(authed_client: TestClient):
    """
    Verify schedule regeneration recalculates immediately and does not duplicate
    blocks on repeated calls.
    """
    user_id = "user-sched-regen"
    headers = make_auth_headers(user_id=user_id)

    # Create task
    authed_client.post(
        "/api/tasks",
        json={
            "title": "Operating Systems Lab",
            "category": "CS",
            "deadline": "2026-10-21T18:00:00Z",
            "priority": "high",
            "difficulty": "medium",
            "estimatedDuration": 3.0,
        },
        headers=headers,
    )

    # Repeated calls produce identical idempotent results
    r1 = authed_client.post(
        "/api/schedule/regenerate",
        json={"date": "2026-10-20"},
        headers=headers,
    )
    assert r1.status_code == 200
    items1 = r1.json()["items"]

    r2 = authed_client.post(
        "/api/schedule/regenerate",
        json={"date": "2026-10-20"},
        headers=headers,
    )
    assert r2.status_code == 200
    items2 = r2.json()["items"]

    assert len(items1) == len(items2)
    assert [i["title"] for i in items1] == [i["title"] for i in items2]


def test_schedule_update_and_dismiss_routes(authed_client: TestClient):
    """Verify /api/schedule/update and /api/schedule/update/dismiss routes."""
    headers = make_auth_headers(user_id="user-sched-upd")

    # Dismiss notification
    r_dismiss = authed_client.post("/api/schedule/update/dismiss", headers=headers)
    assert r_dismiss.status_code == 200
    assert r_dismiss.json() == {"success": True}

    # Check update status
    r_upd = authed_client.get("/api/schedule/update", headers=headers)
    assert r_upd.status_code == 200
    # Returns None or ScheduleUpdateResponse


def test_schedule_empty_task_collection(authed_client: TestClient):
    """Verify schedule generation for a user with enabled availability but no tasks."""
    headers = make_auth_headers(user_id="user-sched-no-tasks")

    # Tuesday: 2026-10-20 (enabled by default)
    r = authed_client.get("/api/schedule?date=2026-10-20", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["date"] == "2026-10-20"
    assert data["dayOfWeek"] == "Tuesday"
    assert data["availableHours"] == 6.5
    assert data["totalScheduledHours"] == 0.0
    assert data["items"] == []


def test_schedule_regeneration_reflects_task_and_availability_changes(
    authed_client: TestClient,
):
    """Verify that schedule regeneration immediately reflects task additions and availability edits."""
    user_id = "user-sched-dyn"
    headers = make_auth_headers(user_id=user_id)
    target_date = "2026-10-20"

    # 1. Initial schedule with no tasks
    r_init = authed_client.post(
        "/api/schedule/regenerate", json={"date": target_date}, headers=headers
    )
    assert r_init.status_code == 200
    assert len(r_init.json()["items"]) == 0

    # 2. Add an urgent task
    authed_client.post(
        "/api/tasks",
        json={
            "title": "Algorithms Exam Prep",
            "category": "CS",
            "deadline": "2026-10-21T18:00:00Z",
            "priority": "critical",
            "difficulty": "hard",
            "estimatedDuration": 2.0,
        },
        headers=headers,
    )

    # 3. Regenerate -> task now appears on schedule
    r_after_task = authed_client.post(
        "/api/schedule/regenerate", json={"date": target_date}, headers=headers
    )
    assert r_after_task.status_code == 200
    items_after = r_after_task.json()["items"]
    assert len(items_after) == 1
    assert items_after[0]["title"] == "Algorithms Exam Prep"

    # 4. Modify Tuesday availability to reduce window to 1 hour (10:00 - 11:00)
    avail_payload = [
        {
            "day": "tuesday",
            "label": "Tuesday",
            "enabled": True,
            "startTime": "10:00",
            "endTime": "11:00",
        }
    ]
    authed_client.put(
        "/api/settings/availability", json=avail_payload, headers=headers
    )

    # 5. Regenerate -> availableHours drops to 1.0, task is allocated within the 1-hour window
    r_after_avail = authed_client.post(
        "/api/schedule/regenerate", json={"date": target_date}, headers=headers
    )
    assert r_after_avail.status_code == 200
    data_after = r_after_avail.json()
    assert data_after["availableHours"] == 1.0


def test_schedule_user_isolation(authed_client: TestClient):
    """Verify schedules are strictly isolated per tenant."""
    headers_a = make_auth_headers(user_id="user-sched-iso-a")
    headers_b = make_auth_headers(user_id="user-sched-iso-b")
    target_date = "2026-10-20"

    # User A creates a task
    authed_client.post(
        "/api/tasks",
        json={
            "title": "Secret Research Task",
            "category": "Research",
            "deadline": "2026-10-21T18:00:00Z",
            "priority": "critical",
            "difficulty": "hard",
            "estimatedDuration": 3.0,
        },
        headers=headers_a,
    )

    # User B requests schedule for same date -> 0 items
    r_b = authed_client.get(f"/api/schedule?date={target_date}", headers=headers_b)
    assert r_b.status_code == 200
    assert len(r_b.json()["items"]) == 0


# ==============================================================================
# SETTINGS API TESTS
# ==============================================================================

def test_get_settings_structure(authed_client: TestClient):
    """Verify GET /api/settings returns profile, preferences, and weekly availability in camelCase."""
    headers = make_auth_headers(user_id="user-sett-get", name="Alex Mercer")

    response = authed_client.get("/api/settings", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert "profile" in data
    assert data["profile"]["name"] == "Alex Mercer"
    assert "timezone" in data["profile"]

    assert "preferences" in data
    assert data["preferences"]["dailyFocusHoursLimit"] == 6.5
    assert data["preferences"]["bufferStrategy"] == "moderate"

    assert "availability" in data
    assert len(data["availability"]) == 7
    days = [a["day"] for a in data["availability"]]
    assert days == [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]


def test_patch_settings_partial_update(authed_client: TestClient):
    """Verify PATCH /api/settings partially updates profile and preferences while preserving other values."""
    headers = make_auth_headers(user_id="user-sett-patch", name="Original Name")

    # Update only profile.name and preferences.buffer_strategy
    payload = {
        "profile": {"name": "Updated Name"},
        "preferences": {"bufferStrategy": "relaxed", "dailyFocusHoursLimit": 5.0},
    }

    response = authed_client.patch("/api/settings", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()

    # Profile updated
    assert data["profile"]["name"] == "Updated Name"
    # Preserved profile fields
    assert data["profile"]["timezone"] == "UTC"

    # Preferences updated
    assert data["preferences"]["bufferStrategy"] == "relaxed"
    assert data["preferences"]["dailyFocusHoursLimit"] == 5.0
    # Preserved preferences fields
    assert data["preferences"]["defaultTaskDurationMinutes"] == 60
    assert data["preferences"]["enableDeadlineReminders"] is True

    # Availability untouched and preserved
    assert len(data["availability"]) == 7


def test_granular_settings_endpoints(authed_client: TestClient):
    """Verify granular profile, preferences, and availability sub-routes."""
    headers = make_auth_headers(user_id="user-sett-granular")

    # 1. Profile sub-routes
    r_prof = authed_client.patch(
        "/api/settings/profile",
        json={"timezone": "Asia/Tokyo", "role": "Senior Student"},
        headers=headers,
    )
    assert r_prof.status_code == 200
    assert r_prof.json()["timezone"] == "Asia/Tokyo"
    assert r_prof.json()["role"] == "Senior Student"

    # 2. Preferences sub-routes
    r_pref = authed_client.patch(
        "/api/settings/preferences",
        json={"defaultTaskDurationMinutes": 45},
        headers=headers,
    )
    assert r_pref.status_code == 200
    assert r_pref.json()["defaultTaskDurationMinutes"] == 45

    # 3. Availability sub-routes
    r_avail = authed_client.get("/api/settings/availability", headers=headers)
    assert r_avail.status_code == 200
    assert len(r_avail.json()) == 7


def test_update_availability_validation_and_reset(authed_client: TestClient):
    """Verify availability validation for time order, duplicates, and reset functionality."""
    headers = make_auth_headers(user_id="user-sett-avail")

    # 1. Invalid time window (start_time >= end_time)
    bad_payload = [
        {
            "day": "monday",
            "label": "Monday",
            "enabled": True,
            "startTime": "17:00",
            "endTime": "09:00",
        }
    ]
    r_bad_time = authed_client.put(
        "/api/settings/availability", json=bad_payload, headers=headers
    )
    assert r_bad_time.status_code == 400
    assert "start_time (17:00) must precede end_time (09:00)" in r_bad_time.json()["detail"]["message"]

    # 2. Duplicate day in availability payload
    dup_payload = [
        {
            "day": "monday",
            "label": "Monday",
            "enabled": True,
            "startTime": "09:00",
            "endTime": "12:00",
        },
        {
            "day": "monday",
            "label": "Monday Afternoon",
            "enabled": True,
            "startTime": "13:00",
            "endTime": "17:00",
        },
    ]
    r_dup = authed_client.put(
        "/api/settings/availability", json=dup_payload, headers=headers
    )
    assert r_dup.status_code == 400
    assert "Duplicate entry for day" in r_dup.json()["detail"]["message"]

    # 3. Valid update
    good_payload = [
        {
            "day": "monday",
            "label": "Monday",
            "enabled": True,
            "startTime": "10:00",
            "endTime": "18:00",
        }
    ]
    r_good = authed_client.put(
        "/api/settings/availability", json=good_payload, headers=headers
    )
    assert r_good.status_code == 200
    mon = next(a for a in r_good.json() if a["day"] == "monday")
    assert mon["startTime"] == "10:00"
    assert mon["endTime"] == "18:00"

    # 4. Reset weekly availability back to defaults
    r_reset = authed_client.post("/api/settings/availability/reset", headers=headers)
    assert r_reset.status_code == 200
    mon_reset = next(a for a in r_reset.json() if a["day"] == "monday")
    assert mon_reset["startTime"] == "09:00"
    assert mon_reset["endTime"] == "17:00"


def test_settings_validation_invalid_limits(authed_client: TestClient):
    """Verify validation errors on dailyFocusHoursLimit and invalid formats."""
    headers = make_auth_headers(user_id="user-sett-invalid")

    # Focus hours limit > 24
    r_limit_high = authed_client.patch(
        "/api/settings/preferences",
        json={"dailyFocusHoursLimit": 25.0},
        headers=headers,
    )
    assert r_limit_high.status_code == 422

    # Focus hours limit <= 0
    r_limit_zero = authed_client.patch(
        "/api/settings/preferences",
        json={"dailyFocusHoursLimit": 0.0},
        headers=headers,
    )
    assert r_limit_zero.status_code == 422

    # Invalid buffer strategy enum
    r_bad_buffer = authed_client.patch(
        "/api/settings/preferences",
        json={"bufferStrategy": "super_relaxed"},
        headers=headers,
    )
    assert r_bad_buffer.status_code == 422


def test_settings_user_isolation(authed_client: TestClient):
    """Verify settings changes made by User A do not affect User B."""
    headers_a = make_auth_headers(user_id="user-sett-iso-a")
    headers_b = make_auth_headers(user_id="user-sett-iso-b")

    # User A sets dailyFocusHoursLimit to 3.0 and bufferStrategy to 'tight'
    authed_client.patch(
        "/api/settings/preferences",
        json={"dailyFocusHoursLimit": 3.0, "bufferStrategy": "tight"},
        headers=headers_a,
    )

    # User B should still have default preferences (6.5h and 'moderate')
    b_prefs = authed_client.get("/api/settings/preferences", headers=headers_b).json()
    assert b_prefs["dailyFocusHoursLimit"] == 6.5
    assert b_prefs["bufferStrategy"] == "moderate"
