"""Comprehensive tests for Task CRUD, calculations, filtering, ownership, and frontend contracts."""

import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from tests.conftest import make_auth_headers


def test_create_task_success_and_contract_compatibility(authed_client: TestClient):
    """
    Verify creating a task returns HTTP 201 with exact camelCase fields
    matching the frontend TypeScript interface.
    """
    headers = make_auth_headers(user_id="user-task-001")
    payload = {
        "title": "Build Adaptive Scheduler Core",
        "description": "Implement priority and deadline based heuristics",
        "category": "Engineering",
        "deadline": "2026-10-20T18:00:00Z",
        "priority": "critical",
        "difficulty": "hard",
        "estimatedDuration": 10.0,
        "completedDuration": 2.5,
        "status": "in_progress",
    }

    response = authed_client.post("/api/tasks", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()

    # Exact camelCase contract assertion
    assert data["id"].startswith("task-")
    assert data["title"] == "Build Adaptive Scheduler Core"
    assert data["description"] == "Implement priority and deadline based heuristics"
    assert data["category"] == "Engineering"
    assert data["priority"] == "critical"
    assert data["difficulty"] == "hard"
    assert data["estimatedDuration"] == 10.0
    assert data["completedDuration"] == 2.5
    assert data["remainingDuration"] == 7.5
    assert data["progress"] == 25
    assert data["status"] == "in_progress"
    assert "createdAt" in data
    assert "updatedAt" in data


def test_derived_fields_calculation_and_auto_complete(authed_client: TestClient):
    """
    Verify progress computation and auto-transition to completed when progress hits 100%.
    """
    headers = make_auth_headers(user_id="user-calc-002")

    # 1. 100% completed on creation
    payload = {
        "title": "Completed Task",
        "category": "General",
        "deadline": "2026-10-15T12:00:00Z",
        "priority": "low",
        "difficulty": "easy",
        "estimatedDuration": 4.0,
        "completedDuration": 4.0,
        "status": "pending",
    }
    response = authed_client.post("/api/tasks", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["progress"] == 100
    assert data["remainingDuration"] == 0.0
    assert data["status"] == "completed"

    # 2. Update task completedDuration to 100%
    task_id = data["id"]
    update_res = authed_client.patch(
        f"/api/tasks/{task_id}",
        json={"completedDuration": 5.0},
        headers=headers,
    )
    assert update_res.status_code == 200
    updated_data = update_res.json()
    assert updated_data["progress"] == 100
    assert updated_data["remainingDuration"] == 0.0


def test_task_validation_errors(authed_client: TestClient):
    """Verify input validation rejects invalid fields with HTTP 422."""
    headers = make_auth_headers(user_id="user-val-003")

    # Zero or negative estimated duration
    res = authed_client.post(
        "/api/tasks",
        json={
            "title": "Invalid Duration",
            "category": "Test",
            "deadline": "2026-10-20T12:00:00Z",
            "estimatedDuration": 0,
        },
        headers=headers,
    )
    assert res.status_code == 422

    # Estimated duration exceeding 500 hours
    res = authed_client.post(
        "/api/tasks",
        json={
            "title": "Too Long",
            "category": "Test",
            "deadline": "2026-10-20T12:00:00Z",
            "estimatedDuration": 501,
        },
        headers=headers,
    )
    assert res.status_code == 422

    # Negative completed duration
    res = authed_client.post(
        "/api/tasks",
        json={
            "title": "Negative Complete",
            "category": "Test",
            "deadline": "2026-10-20T12:00:00Z",
            "estimatedDuration": 5,
            "completedDuration": -1,
        },
        headers=headers,
    )
    assert res.status_code == 422

    # Blank title
    res = authed_client.post(
        "/api/tasks",
        json={
            "title": "   ",
            "category": "Test",
            "deadline": "2026-10-20T12:00:00Z",
            "estimatedDuration": 5,
        },
        headers=headers,
    )
    assert res.status_code == 422

    # Invalid priority enum
    res = authed_client.post(
        "/api/tasks",
        json={
            "title": "Valid Title",
            "category": "Test",
            "deadline": "2026-10-20T12:00:00Z",
            "estimatedDuration": 5,
            "priority": "super-urgent",
        },
        headers=headers,
    )
    assert res.status_code == 422


def test_task_retrieval_and_update(authed_client: TestClient):
    """Verify GET /api/tasks/{id} and PATCH /api/tasks/{id}."""
    headers = make_auth_headers(user_id="user-crud-004")
    create_res = authed_client.post(
        "/api/tasks",
        json={
            "title": "Draft Research Report",
            "category": "Academics",
            "deadline": "2026-10-25T15:00:00Z",
            "priority": "medium",
            "difficulty": "medium",
            "estimatedDuration": 8.0,
        },
        headers=headers,
    )
    task_id = create_res.json()["id"]

    # Retrieve by ID
    get_res = authed_client.get(f"/api/tasks/{task_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Draft Research Report"

    # Update title and progress
    patch_res = authed_client.patch(
        f"/api/tasks/{task_id}",
        json={
            "title": "Finalize Research Report",
            "completedDuration": 4.0,
            "priority": "high",
        },
        headers=headers,
    )
    assert patch_res.status_code == 200
    patch_data = patch_res.json()
    assert patch_data["title"] == "Finalize Research Report"
    assert patch_data["priority"] == "high"
    assert patch_data["progress"] == 50
    assert patch_data["remainingDuration"] == 4.0


def test_task_deletion(authed_client: TestClient):
    """Verify DELETE /api/tasks/{id} returns 204 and removes task."""
    headers = make_auth_headers(user_id="user-del-005")
    create_res = authed_client.post(
        "/api/tasks",
        json={
            "title": "Temporary Task",
            "category": "Test",
            "deadline": "2026-10-30T10:00:00Z",
            "estimatedDuration": 2.0,
        },
        headers=headers,
    )
    task_id = create_res.json()["id"]

    # Delete task
    del_res = authed_client.delete(f"/api/tasks/{task_id}", headers=headers)
    assert del_res.status_code == 204

    # Confirm subsequent retrieval returns 404
    get_res = authed_client.get(f"/api/tasks/{task_id}", headers=headers)
    assert get_res.status_code == 404


def test_multi_tenant_user_ownership_isolation(authed_client: TestClient):
    """
    CRITICAL SECURITY TEST:
    User A creates a task. User B cannot view, edit, or delete it,
    and receiving 404 does not disclose task existence.
    """
    headers_user_a = make_auth_headers(user_id="user-tenant-alice")
    headers_user_b = make_auth_headers(user_id="user-tenant-bob")

    # User A creates a task
    res_a = authed_client.post(
        "/api/tasks",
        json={
            "title": "Alice Confidential Project",
            "category": "Private",
            "deadline": "2026-10-25T12:00:00Z",
            "estimatedDuration": 6.0,
        },
        headers=headers_user_a,
    )
    alice_task_id = res_a.json()["id"]

    # User B attempts to access Alice's task -> 404
    get_b = authed_client.get(f"/api/tasks/{alice_task_id}", headers=headers_user_b)
    assert get_b.status_code == 404
    assert get_b.json()["detail"]["message"] == "Task not found"

    # User B attempts to update Alice's task -> 404
    patch_b = authed_client.patch(
        f"/api/tasks/{alice_task_id}",
        json={"title": "Hacked Title"},
        headers=headers_user_b,
    )
    assert patch_b.status_code == 404

    # User B attempts to delete Alice's task -> 404
    del_b = authed_client.delete(f"/api/tasks/{alice_task_id}", headers=headers_user_b)
    assert del_b.status_code == 404

    # User B listing tasks does not see Alice's task
    list_b = authed_client.get("/api/tasks", headers=headers_user_b)
    assert list_b.status_code == 200
    assert len(list_b.json()) == 0

    # User A still has the task unmodified
    get_a = authed_client.get(f"/api/tasks/{alice_task_id}", headers=headers_user_a)
    assert get_a.status_code == 200
    assert get_a.json()["title"] == "Alice Confidential Project"


def test_task_filtering_and_sorting(authed_client: TestClient):
    """Verify task query parameters for search, category, status, priority, and sorting."""
    headers = make_auth_headers(user_id="user-filters-006")

    # Seed 3 distinct tasks
    authed_client.post(
        "/api/tasks",
        json={
            "title": "Alpha Database Optimization",
            "category": "Engineering",
            "deadline": "2026-10-18T10:00:00Z",
            "priority": "critical",
            "difficulty": "hard",
            "estimatedDuration": 10.0,
            "status": "in_progress",
        },
        headers=headers,
    )
    authed_client.post(
        "/api/tasks",
        json={
            "title": "Beta UI Accessibility",
            "category": "Design",
            "deadline": "2026-10-14T10:00:00Z",
            "priority": "high",
            "difficulty": "medium",
            "estimatedDuration": 4.0,
            "status": "pending",
        },
        headers=headers,
    )
    authed_client.post(
        "/api/tasks",
        json={
            "title": "Gamma Deployment Pipeline",
            "category": "Engineering",
            "deadline": "2026-10-22T10:00:00Z",
            "priority": "low",
            "difficulty": "easy",
            "estimatedDuration": 2.0,
            "status": "completed",
        },
        headers=headers,
    )

    # 1. Category filter
    res = authed_client.get("/api/tasks?category=Engineering", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 2

    # 2. Status filter
    res = authed_client.get("/api/tasks?status=completed", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["title"] == "Gamma Deployment Pipeline"

    # 3. Priority filter
    res = authed_client.get("/api/tasks?priority=critical", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["title"] == "Alpha Database Optimization"

    # 4. Search filter
    res = authed_client.get("/api/tasks?search=accessibility", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["title"] == "Beta UI Accessibility"

    # 5. Sort by deadline asc
    res = authed_client.get("/api/tasks?sortBy=deadline&sortDirection=asc", headers=headers)
    assert res.status_code == 200
    titles = [t["title"] for t in res.json()]
    assert titles == [
        "Beta UI Accessibility",          # Oct 14
        "Alpha Database Optimization",   # Oct 18
        "Gamma Deployment Pipeline",     # Oct 22
    ]


def test_task_categories_endpoint(authed_client: TestClient):
    """Verify GET /api/tasks/categories returns alphabetical list of user's categories."""
    headers = make_auth_headers(user_id="user-cats-007")

    authed_client.post(
        "/api/tasks",
        json={"title": "T1", "category": "DevOps", "deadline": "2026-10-20T12:00:00Z", "estimatedDuration": 1},
        headers=headers,
    )
    authed_client.post(
        "/api/tasks",
        json={"title": "T2", "category": "Academics", "deadline": "2026-10-20T12:00:00Z", "estimatedDuration": 1},
        headers=headers,
    )
    authed_client.post(
        "/api/tasks",
        json={"title": "T3", "category": "DevOps", "deadline": "2026-10-20T12:00:00Z", "estimatedDuration": 1},
        headers=headers,
    )

    res = authed_client.get("/api/tasks/categories", headers=headers)
    assert res.status_code == 200
    assert res.json() == ["Academics", "DevOps"]


def test_task_seed_endpoint(authed_client: TestClient):
    """Verify POST /api/tasks/seed populates sample starter tasks for an empty user."""
    headers = make_auth_headers(user_id="user-seed-check")

    res = authed_client.post("/api/tasks/seed", headers=headers)
    assert res.status_code == 200
    tasks = res.json()
    assert len(tasks) >= 5
    assert any("Architecture" in t["title"] for t in tasks)
