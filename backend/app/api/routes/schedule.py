"""Schedule REST API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.auth import get_current_user, AuthenticatedUser
from app.schemas.schedule import (
    DayScheduleResponse,
    ScheduleUpdateResponse,
    RegenerateScheduleRequest,
)
from app.services.schedule_service import ScheduleService

router = APIRouter(prefix="/schedule", tags=["schedule"])


@router.get("", response_model=DayScheduleResponse)
def get_schedule(
    date: Optional[str] = Query(
        None, description="Optional ISO calendar date (YYYY-MM-DD)"
    ),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DayScheduleResponse:
    """
    Retrieve the day's schedule timeline for requested date (or today in user timezone).
    Conflict-free, idempotent, and dynamically calculated.
    """
    return ScheduleService.get_daily_schedule(
        db=db, user_id=current_user.id, date_str=date
    )


@router.get("/update", response_model=Optional[ScheduleUpdateResponse])
def get_schedule_update(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Optional[ScheduleUpdateResponse]:
    """Retrieve adaptive schedule update notification if circumstances warrant recalculation."""
    return ScheduleService.get_schedule_update(db=db, user_id=current_user.id)


@router.post("/regenerate", response_model=DayScheduleResponse)
def regenerate_schedule(
    payload: Optional[RegenerateScheduleRequest] = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DayScheduleResponse:
    """Recalculate dynamic schedule for requested date."""
    req_date = payload.date if payload else None
    return ScheduleService.regenerate_schedule(
        db=db, user_id=current_user.id, date_str=req_date
    )


@router.post("/update/dismiss")
def dismiss_schedule_update(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Acknowledge or dismiss schedule update notification."""
    return {"success": True}
