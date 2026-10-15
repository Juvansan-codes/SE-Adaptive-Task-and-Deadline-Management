"""Dashboard REST API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.auth import get_current_user, AuthenticatedUser
from app.schemas.task import TaskResponse
from app.schemas.dashboard import (
    DashboardOverviewResponse,
    RecommendedTaskResponse,
    AtRiskTaskResponse,
    ScheduleBlockResponse,
)
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=DashboardOverviewResponse)
def get_dashboard_overview(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardOverviewResponse:
    """Retrieve high-level summary overview of today's schedule and task status."""
    return DashboardService.get_overview(db, current_user.id)


@router.get("/recommendation", response_model=Optional[RecommendedTaskResponse])
def get_dashboard_recommendation(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Optional[RecommendedTaskResponse]:
    """Retrieve the single highest-priority recommended next task with explanation."""
    return DashboardService.get_recommendation(db, current_user.id)


@router.get("/at-risk", response_model=List[AtRiskTaskResponse])
def get_at_risk_tasks(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[AtRiskTaskResponse]:
    """Retrieve tasks flagged as at-risk along with explicit calculated rationale."""
    return DashboardService.get_at_risk_tasks(db, current_user.id)


@router.get("/upcoming", response_model=List[TaskResponse])
def get_upcoming_deadlines(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[TaskResponse]:
    """Retrieve upcoming active tasks ordered chronologically by deadline."""
    return DashboardService.get_upcoming_deadlines(db, current_user.id)


@router.get("/schedule", response_model=List[ScheduleBlockResponse])
def get_today_schedule(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[ScheduleBlockResponse]:
    """Retrieve chronological schedule blocks for today."""
    return DashboardService.get_today_schedule_blocks(db, current_user.id)
