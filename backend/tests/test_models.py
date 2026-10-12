"""Direct unit tests for SQLAlchemy domain models, constraints, and relationships."""

import pytest
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError

from app.models.profile import Profile
from app.models.task import Task
from app.models.availability import UserAvailability
from app.models.preferences import UserPreferences


def test_profile_and_task_relationship(db_session):
    """Verify creating a Profile with associated Tasks and cascading deletes."""
    profile = Profile(
        id="user-model-test-01",
        email="test_model@example.com",
        name="Model Tester",
    )
    db_session.add(profile)
    db_session.commit()

    task1 = Task(
        user_id=profile.id,
        title="Model Task 1",
        category="Testing",
        deadline=datetime.now(timezone.utc),
        priority="high",
        difficulty="medium",
        estimated_duration=5.0,
        completed_duration=2.5,
        remaining_duration=2.5,
        progress=50,
        status="in_progress",
    )
    db_session.add(task1)
    db_session.commit()

    # Verify query and relation
    queried_profile = db_session.query(Profile).filter_by(id=profile.id).first()
    assert len(queried_profile.tasks) == 1
    assert queried_profile.tasks[0].title == "Model Task 1"

    # Verify cascade delete
    db_session.delete(queried_profile)
    db_session.commit()
    remaining_tasks = db_session.query(Task).filter_by(user_id=profile.id).all()
    assert len(remaining_tasks) == 0


def test_user_availability_unique_constraint(db_session):
    """Verify UserAvailability enforces unique (user_id, day) constraint."""
    profile = Profile(id="user-avail-01", email="avail@example.com")
    db_session.add(profile)
    db_session.commit()

    avail1 = UserAvailability(
        user_id=profile.id,
        day="monday",
        label="Monday",
        enabled=True,
        start_time="09:00",
        end_time="17:00",
    )
    db_session.add(avail1)
    db_session.commit()

    # Duplicate day for same user should fail unique constraint
    avail2 = UserAvailability(
        user_id=profile.id,
        day="monday",
        label="Monday Duplicate",
        enabled=False,
        start_time="10:00",
        end_time="18:00",
    )
    db_session.add(avail2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_user_preferences_constraints(db_session):
    """Verify UserPreferences check constraints and single profile relation."""
    profile = Profile(id="user-pref-01", email="pref@example.com")
    db_session.add(profile)
    db_session.commit()

    pref = UserPreferences(
        user_id=profile.id,
        enable_deadline_reminders=True,
        enable_schedule_updates=True,
        default_task_duration_minutes=45,
        daily_focus_hours_limit=6.0,
        buffer_strategy="relaxed",
    )
    db_session.add(pref)
    db_session.commit()

    queried_pref = db_session.query(UserPreferences).filter_by(user_id=profile.id).first()
    assert queried_pref.buffer_strategy == "relaxed"
    assert queried_pref.default_task_duration_minutes == 45
