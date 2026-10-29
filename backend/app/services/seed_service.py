"""Automated initial seed service for user profiles, tasks, and scheduling."""

import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from app.models.profile import Profile
from app.models.task import Task
from app.services.settings_service import SettingsService

logger = logging.getLogger(__name__)


def ensure_user_seeded(db: Session, user_id: str, email: str, name: str = "") -> None:
    """
    Ensure the user has an initialized profile, default availability,
    preferences, and a rich set of starter tasks if they have no existing tasks.
    Guarantees the dashboard, tasks view, and schedule view are never empty or broken.
    """
    try:
        # 1. Ensure Profile exists
        profile = db.query(Profile).filter(Profile.id == user_id).first()
        if profile is None:
            profile = Profile(
                id=user_id,
                email=email,
                name=name or email.split("@")[0].capitalize(),
                timezone="UTC",
                role="student",
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)

        # 2. Ensure Availability & Preferences exist
        SettingsService.get_or_create_availability(db, user_id)
        SettingsService.get_or_create_preferences(db, user_id)

        # 3. Check existing tasks count
        existing_task_count = db.query(Task).filter(Task.user_id == user_id).count()
        if existing_task_count > 0:
            return

        # 4. Seed initial realistic microproject tasks
        now = datetime.now(timezone.utc)
        sample_tasks = [
            Task(
                user_id=user_id,
                title="Software Architecture & Design Specification",
                description="Finalize system component diagrams, data flow models, and REST contracts.",
                category="Academic",
                deadline=now + timedelta(days=1, hours=4),
                priority="critical",
                difficulty="hard",
                estimated_duration=4.0,
                completed_duration=1.0,
                remaining_duration=3.0,
                progress=25,
                status="in_progress",
            ),
            Task(
                user_id=user_id,
                title="Database Schema Migration & Indexing",
                description="Set up relational tables, foreign key cascades, and check constraints.",
                category="Development",
                deadline=now + timedelta(days=2),
                priority="high",
                difficulty="medium",
                estimated_duration=3.5,
                completed_duration=3.5,
                remaining_duration=0.0,
                progress=100,
                status="completed",
            ),
            Task(
                user_id=user_id,
                title="Frontend Integration & Dashboard Testing",
                description="Connect Next.js App Router views with FastAPI endpoints and verify metrics.",
                category="Quality Assurance",
                deadline=now + timedelta(days=2, hours=6),
                priority="high",
                difficulty="medium",
                estimated_duration=3.0,
                completed_duration=0.5,
                remaining_duration=2.5,
                progress=17,
                status="in_progress",
            ),
            Task(
                user_id=user_id,
                title="Adaptive Scheduling Algorithm Evaluation",
                description="Run stress-test scenarios comparing EDF vs dynamic difficulty-weighted planning.",
                category="Research",
                deadline=now + timedelta(days=3),
                priority="high",
                difficulty="hard",
                estimated_duration=5.0,
                completed_duration=0.0,
                remaining_duration=5.0,
                progress=0,
                status="pending",
            ),
            Task(
                user_id=user_id,
                title="UI/UX Accessibility & Responsive Layout Polish",
                description="Verify contrast ratios, keyboard navigation, and drawer responsiveness.",
                category="Design",
                deadline=now + timedelta(days=5),
                priority="medium",
                difficulty="easy",
                estimated_duration=2.0,
                completed_duration=0.0,
                remaining_duration=2.0,
                progress=0,
                status="pending",
            ),
            Task(
                user_id=user_id,
                title="Project Presentation & Demonstration Deck",
                description="Compile architecture slides, demo video clips, and evaluation benchmark charts.",
                category="Academic",
                deadline=now + timedelta(days=7),
                priority="medium",
                difficulty="easy",
                estimated_duration=2.5,
                completed_duration=0.0,
                remaining_duration=2.5,
                progress=0,
                status="pending",
            ),
        ]

        for t in sample_tasks:
            db.add(t)
        db.commit()
        logger.info("Successfully seeded %d starter tasks for user %s", len(sample_tasks), user_id)

    except Exception as exc:
        db.rollback()
        logger.warning("Automatic seed for user %s encountered exception: %s", user_id, exc)

