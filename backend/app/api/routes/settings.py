"""Settings REST API endpoints for user profile, preferences, and availability."""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.auth import get_current_user, AuthenticatedUser
from app.schemas.settings import (
    SettingsStateResponse,
    UpdateSettingsRequest,
    UserProfileSchema,
    UpdateProfileRequest,
    UserPreferencesSchema,
    UpdatePreferencesRequest,
    DayAvailabilitySchema,
)
from app.services.settings_service import SettingsService

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingsStateResponse)
def get_settings(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SettingsStateResponse:
    """Retrieve unified user settings (profile, preferences, and availability)."""
    return SettingsService.get_settings_state(db=db, user_id=current_user.id)


@router.patch("", response_model=SettingsStateResponse)
def update_settings(
    payload: UpdateSettingsRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SettingsStateResponse:
    """
    Apply partial updates across profile, preferences, or weekly availability.
    Preserves all fields not explicitly provided.
    """
    return SettingsService.update_settings(
        db=db, user_id=current_user.id, payload=payload
    )


@router.get("/profile", response_model=UserProfileSchema)
def get_profile(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserProfileSchema:
    """Retrieve user profile."""
    profile = SettingsService.get_profile(db=db, user_id=current_user.id)
    return UserProfileSchema.model_validate(profile)


@router.patch("/profile", response_model=UserProfileSchema)
def update_profile(
    payload: UpdateProfileRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserProfileSchema:
    """Partially update user profile."""
    updated = SettingsService.update_profile(
        db=db, user_id=current_user.id, payload=payload
    )
    return UserProfileSchema.model_validate(updated)


@router.get("/preferences", response_model=UserPreferencesSchema)
def get_preferences(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserPreferencesSchema:
    """Retrieve user scheduling and notification preferences."""
    prefs = SettingsService.get_or_create_preferences(
        db=db, user_id=current_user.id
    )
    return UserPreferencesSchema.model_validate(prefs)


@router.patch("/preferences", response_model=UserPreferencesSchema)
def update_preferences(
    payload: UpdatePreferencesRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserPreferencesSchema:
    """Partially update user preferences."""
    updated = SettingsService.update_preferences(
        db=db, user_id=current_user.id, payload=payload
    )
    return UserPreferencesSchema.model_validate(updated)


@router.get("/availability", response_model=List[DayAvailabilitySchema])
def get_availability(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[DayAvailabilitySchema]:
    """Retrieve weekly work/study availability schedule."""
    availability = SettingsService.get_or_create_availability(
        db=db, user_id=current_user.id
    )
    return [DayAvailabilitySchema.model_validate(a) for a in availability]


@router.put("/availability", response_model=List[DayAvailabilitySchema])
def update_availability(
    payload: List[DayAvailabilitySchema],
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[DayAvailabilitySchema]:
    """Update complete weekly availability schedule."""
    updated = SettingsService.update_weekly_availability(
        db=db, user_id=current_user.id, new_avail=payload
    )
    return [DayAvailabilitySchema.model_validate(a) for a in updated]


@router.post("/availability/reset", response_model=List[DayAvailabilitySchema])
def reset_availability(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[DayAvailabilitySchema]:
    """Reset weekly availability to standard default configuration."""
    reset_list = SettingsService.reset_weekly_availability(
        db=db, user_id=current_user.id
    )
    return [DayAvailabilitySchema.model_validate(a) for a in reset_list]
