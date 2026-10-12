"""Task service implementing domain logic, filtering, calculations, and persistence."""

import uuid
from typing import List, Optional, Tuple
from sqlalchemy import or_, func, case
from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import (
    CreateTaskRequest,
    UpdateTaskRequest,
    TaskFilterParams,
)


def calculate_derived_fields(estimated: float, completed: float) -> Tuple[float, int]:
    """
    Compute remainingDuration and progress percentage from durations.
    - Prevents division by zero with safe floor.
    - Caps progress between 0 and 100.
    """
    safe_estimated = max(0.1, float(estimated))
    safe_completed = max(0.0, float(completed))
    remaining = max(0.0, round(safe_estimated - safe_completed, 1))
    progress = min(100, max(0, round((safe_completed / safe_estimated) * 100)))
    return remaining, progress


class TaskService:
    """Service class encapsulating Task CRUD and business rules."""

    @staticmethod
    def get_user_tasks(
        db: Session, user_id: str, filters: Optional[TaskFilterParams] = None
    ) -> List[Task]:
        """Retrieve tasks belonging strictly to the authenticated user."""
        query = db.query(Task).filter(Task.user_id == user_id)

        if not filters:
            return query.order_by(Task.updated_at.desc()).all()

        # 1. Text search across title, description, category
        if filters.search and filters.search.strip():
            term = f"%{filters.search.strip()}%"
            query = query.filter(
                or_(
                    Task.title.ilike(term),
                    Task.description.ilike(term),
                    Task.category.ilike(term),
                )
            )

        # 2. Status filter
        if filters.status and filters.status.lower() != "all":
            query = query.filter(Task.status == filters.status.lower())

        # 3. Priority filter
        if filters.priority and filters.priority.lower() != "all":
            query = query.filter(Task.priority == filters.priority.lower())

        # 4. Category filter
        if filters.category and filters.category.lower() != "all":
            query = query.filter(
                func.lower(Task.category) == filters.category.strip().lower()
            )

        # 5. Sorting
        direction = filters.sort_direction or "asc"
        is_desc = direction.lower() == "desc"

        sort_by = (filters.sort_by or "").lower()

        if sort_by == "deadline":
            query = query.order_by(Task.deadline.desc() if is_desc else Task.deadline.asc())
        elif sort_by == "priority":
            priority_weight = case(
                (Task.priority == "critical", 4),
                (Task.priority == "high", 3),
                (Task.priority == "medium", 2),
                (Task.priority == "low", 1),
                else_=0,
            )
            # Default priority sort order: critical first if asc/desc
            query = query.order_by(priority_weight.asc() if is_desc else priority_weight.desc())
        elif sort_by == "title":
            query = query.order_by(Task.title.desc() if is_desc else Task.title.asc())
        elif sort_by == "status":
            query = query.order_by(Task.status.desc() if is_desc else Task.status.asc())
        elif sort_by == "progress":
            query = query.order_by(Task.progress.desc() if is_desc else Task.progress.asc())
        else:
            query = query.order_by(Task.updated_at.desc())

        return query.all()

    @staticmethod
    def get_task_by_id(db: Session, user_id: str, task_id: str) -> Optional[Task]:
        """Retrieve single task by ID enforcing user ownership."""
        return (
            db.query(Task)
            .filter(Task.id == task_id, Task.user_id == user_id)
            .first()
        )

    @staticmethod
    def create_task(
        db: Session, user_id: str, payload: CreateTaskRequest
    ) -> Task:
        """Create a new task with computed progress and duration fields."""
        completed = payload.completed_duration or 0.0
        remaining, progress = calculate_derived_fields(
            payload.estimated_duration, completed
        )

        status = payload.status or "pending"
        if progress == 100 and status != "completed":
            status = "completed"

        task = Task(
            id=f"task-{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            title=payload.title,
            description=payload.description or "",
            category=payload.category,
            deadline=payload.deadline,
            priority=payload.priority,
            difficulty=payload.difficulty,
            estimated_duration=payload.estimated_duration,
            completed_duration=completed,
            remaining_duration=remaining,
            progress=progress,
            status=status,
        )

        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def update_task(
        db: Session, user_id: str, task_id: str, payload: UpdateTaskRequest
    ) -> Optional[Task]:
        """Update existing task fields and re-derive progress and status."""
        task = TaskService.get_task_by_id(db, user_id, task_id)
        if not task:
            return None

        if payload.title is not None:
            task.title = payload.title
        if payload.description is not None:
            task.description = payload.description
        if payload.category is not None:
            task.category = payload.category
        if payload.deadline is not None:
            task.deadline = payload.deadline
        if payload.priority is not None:
            task.priority = payload.priority
        if payload.difficulty is not None:
            task.difficulty = payload.difficulty

        # Recalculate duration fields if either is provided
        est_changed = payload.estimated_duration is not None
        comp_changed = payload.completed_duration is not None

        if est_changed or comp_changed:
            estimated = (
                payload.estimated_duration
                if est_changed
                else task.estimated_duration
            )
            completed = (
                payload.completed_duration
                if comp_changed
                else task.completed_duration
            )
            task.estimated_duration = estimated
            task.completed_duration = completed
            remaining, progress = calculate_derived_fields(estimated, completed)
            task.remaining_duration = remaining
            task.progress = progress

        # Explicit status update
        if payload.status is not None:
            task.status = payload.status
        elif task.progress == 100 and task.status != "completed":
            task.status = "completed"

        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def delete_task(db: Session, user_id: str, task_id: str) -> bool:
        """Delete task owned by user."""
        task = TaskService.get_task_by_id(db, user_id, task_id)
        if not task:
            return False

        db.delete(task)
        db.commit()
        return True

    @staticmethod
    def get_user_categories(db: Session, user_id: str) -> List[str]:
        """Retrieve list of unique categories used by user's tasks."""
        rows = (
            db.query(Task.category)
            .filter(Task.user_id == user_id)
            .distinct()
            .all()
        )
        return sorted([r[0] for r in rows if r[0]])
