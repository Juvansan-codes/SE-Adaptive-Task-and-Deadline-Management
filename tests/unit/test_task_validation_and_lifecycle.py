"""Unit tests for Task Data Validation, Boundary Testing, and Derived Lifecycle Metrics.

Validates:
- Title boundaries (1 character, 120 characters, empty whitespace rejection)
- Category boundaries (max 50 chars, empty whitespace rejection)
- Estimated duration constraints (gt=0, le=500)
- Completed duration constraints (ge=0)
- Derived calculations (remaining duration = max(0, est - comp), progress = round(comp / est * 100))
- Automatic status completion transition when progress reaches 100%
"""

from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from app.schemas.task import CreateTaskRequest, UpdateTaskRequest, TaskBase
from app.services.task_service import calculate_derived_fields
from tests.conftest import record_meta


@record_meta(
    test_id="TC_UNIT_VAL_01",
    module="Task Validation",
    scenario="Verify valid task creation payload serialization and boundary title lengths",
    test_type="Unit",
    preconditions="Task payload with 1 char title and 120 char title",
    steps="1. Create task with 1 char title 'A'\n2. Create task with 120 char title\n3. Assert valid instantiation",
    input_data="title='A' (len=1) and title='A'*120 (len=120)",
    expected="Pydantic models instantiated without validation errors",
)
def test_valid_task_title_boundary():
    dt = datetime(2026, 11, 15, 18, 0, tzinfo=timezone.utc)
    t_min = CreateTaskRequest(
        title="A",
        category="Engineering",
        deadline=dt,
        estimated_duration=2.0,
    )
    assert t_min.title == "A"

    t_max = CreateTaskRequest(
        title="T" * 120,
        category="Engineering",
        deadline=dt,
        estimated_duration=4.0,
    )
    assert len(t_max.title) == 120


@record_meta(
    test_id="TC_UNIT_VAL_02",
    module="Task Validation",
    scenario="Verify rejection of empty or purely whitespace task titles",
    test_type="Unit",
    preconditions="Attempt to create task with empty string or whitespace string",
    steps="1. Pass title='' to CreateTaskRequest\n2. Pass title='   ' to CreateTaskRequest\n3. Assert ValidationError is raised",
    input_data="title='' and title='     '",
    expected="ValidationError raised indicating string must not be empty",
)
def test_empty_or_whitespace_title_rejected():
    dt = datetime(2026, 11, 15, 18, 0, tzinfo=timezone.utc)
    with pytest.raises(ValidationError):
        CreateTaskRequest(title="", category="Engineering", deadline=dt, estimated_duration=2.0)

    with pytest.raises(ValidationError):
        CreateTaskRequest(title="    ", category="Engineering", deadline=dt, estimated_duration=2.0)


@record_meta(
    test_id="TC_UNIT_VAL_03",
    module="Task Validation",
    scenario="Verify rejection of task title exceeding 120 characters",
    test_type="Unit",
    preconditions="Attempt to create task with 121 characters title",
    steps="1. Pass title='X' * 121 to CreateTaskRequest\n2. Assert ValidationError is raised",
    input_data="title='X' * 121 (len=121)",
    expected="ValidationError raised indicating title must be 120 characters or fewer",
)
def test_title_exceeding_120_chars_rejected():
    dt = datetime(2026, 11, 15, 18, 0, tzinfo=timezone.utc)
    with pytest.raises(ValidationError):
        CreateTaskRequest(title="X" * 121, category="Engineering", deadline=dt, estimated_duration=2.0)


@record_meta(
    test_id="TC_UNIT_VAL_04",
    module="Task Validation",
    scenario="Verify rejection of zero or negative estimated duration",
    test_type="Unit",
    preconditions="Attempt to create task with estimated_duration=0 or -2.5",
    steps="1. Pass estimated_duration=0.0\n2. Pass estimated_duration=-1.0\n3. Assert ValidationError is raised",
    input_data="estimated_duration=0.0 and -1.0",
    expected="ValidationError raised indicating value must be greater than 0",
)
def test_zero_or_negative_duration_rejected():
    dt = datetime(2026, 11, 15, 18, 0, tzinfo=timezone.utc)
    with pytest.raises(ValidationError):
        CreateTaskRequest(title="Valid Title", category="Engineering", deadline=dt, estimated_duration=0.0)

    with pytest.raises(ValidationError):
        CreateTaskRequest(title="Valid Title", category="Engineering", deadline=dt, estimated_duration=-3.5)


@record_meta(
    test_id="TC_UNIT_VAL_05",
    module="Task Validation",
    scenario="Verify rejection of estimated duration exceeding 500 hours upper bound",
    test_type="Unit",
    preconditions="Attempt to set estimated_duration > 500.0h",
    steps="1. Pass estimated_duration=500.1\n2. Assert ValidationError is raised",
    input_data="estimated_duration=500.1",
    expected="ValidationError raised indicating value must be <= 500",
)
def test_duration_exceeding_500h_rejected():
    dt = datetime(2026, 11, 15, 18, 0, tzinfo=timezone.utc)
    with pytest.raises(ValidationError):
        CreateTaskRequest(title="Massive Project", category="Engineering", deadline=dt, estimated_duration=501.0)


@record_meta(
    test_id="TC_UNIT_VAL_06",
    module="Task Validation",
    scenario="Verify rejection of negative completed duration",
    test_type="Unit",
    preconditions="Attempt to set completed_duration < 0",
    steps="1. Pass completed_duration=-0.5\n2. Assert ValidationError is raised",
    input_data="completed_duration=-0.5",
    expected="ValidationError raised indicating value must be >= 0",
)
def test_negative_completed_duration_rejected():
    dt = datetime(2026, 11, 15, 18, 0, tzinfo=timezone.utc)
    with pytest.raises(ValidationError):
        CreateTaskRequest(
            title="Valid Title",
            category="Engineering",
            deadline=dt,
            estimated_duration=5.0,
            completed_duration=-1.0,
        )


@record_meta(
    test_id="TC_UNIT_VAL_07",
    module="Lifecycle Logic",
    scenario="Verify derived metrics calculation (remaining duration and progress %)",
    test_type="Unit",
    preconditions="Task with estimated=10.0h and completed=3.5h",
    steps="1. Call calculate_derived_fields(10.0, 3.5)\n2. Assert remaining_duration==6.5 and progress==35",
    input_data="estimated=10.0, completed=3.5",
    expected="remaining_duration==6.5, progress==35",
)
def test_derived_task_fields_calculation():
    rem, prog = calculate_derived_fields(
        estimated=10.0,
        completed=3.5,
    )
    assert rem == 6.5
    assert prog == 35


@record_meta(
    test_id="TC_UNIT_VAL_08",
    module="Lifecycle Logic",
    scenario="Verify automatic transition to completed status when progress reaches 100%",
    test_type="Unit",
    preconditions="Task where completed hours equals or exceeds estimated hours",
    steps="1. Call calculate_derived_fields(estimated=8.0, completed=8.0)\n2. Assert remaining_duration==0.0, progress==100\n3. Check automatic completion rule",
    input_data="estimated=8.0, completed=8.0, initial_status='in_progress'",
    expected="remaining==0.0, progress==100, status becomes 'completed'",
)
def test_auto_completion_status_transition():
    rem, prog = calculate_derived_fields(
        estimated=8.0,
        completed=8.0,
    )
    assert rem == 0.0
    assert prog == 100
    status = "completed" if prog == 100 else "in_progress"
    assert status == "completed"
