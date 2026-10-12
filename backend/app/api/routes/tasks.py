"""Task REST API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.auth import get_current_user, AuthenticatedUser
from app.services.task_service import TaskService
from app.schemas.task import (
    CreateTaskRequest,
    UpdateTaskRequest,
    TaskResponse,
    TaskFilterParams,
    SortDirection,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=List[TaskResponse])
def list_tasks(
    search: Optional[str] = Query(None, description="Search keyword in title, description, category"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status or 'all'"),
    priority: Optional[str] = Query(None, description="Filter by priority or 'all'"),
    category: Optional[str] = Query(None, description="Filter by category or 'all'"),
    sort_by: Optional[str] = Query(None, alias="sortBy", description="Sort field: deadline, priority, title, status, progress"),
    sort_direction: Optional[SortDirection] = Query("asc", alias="sortDirection", description="asc or desc"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[TaskResponse]:
    """List all tasks belonging exclusively to the authenticated user."""
    filters = TaskFilterParams(
        search=search,
        status=status_filter,
        priority=priority,
        category=category,
        sort_by=sort_by,
        sort_direction=sort_direction,
    )
    tasks = TaskService.get_user_tasks(db, current_user.id, filters)
    return [TaskResponse.model_validate(t) for t in tasks]


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: CreateTaskRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskResponse:
    """Create a new task for the authenticated user."""
    task = TaskService.create_task(db, current_user.id, payload)
    return TaskResponse.model_validate(task)


@router.get("/categories", response_model=List[str])
def get_categories(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[str]:
    """Retrieve distinct list of task categories for the authenticated user."""
    return TaskService.get_user_categories(db, current_user.id)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskResponse:
    """Retrieve a single task owned by the authenticated user."""
    task = TaskService.get_task_by_id(db, current_user.id, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"status": "error", "message": "Task not found"},
        )
    return TaskResponse.model_validate(task)


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: str,
    payload: UpdateTaskRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskResponse:
    """Update fields of an existing task owned by the authenticated user."""
    task = TaskService.update_task(db, current_user.id, task_id, payload)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"status": "error", "message": "Task not found"},
        )
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    """Delete a task owned by the authenticated user."""
    deleted = TaskService.delete_task(db, current_user.id, task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"status": "error", "message": "Task not found"},
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
