"""Health check endpoints for API process and database connectivity."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.db.session import get_db, ping_database

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str
    service: str


class DatabaseHealthResponse(BaseModel):
    status: str
    database: str


class ErrorResponse(BaseModel):
    status: str
    message: str


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Application Health Check",
    description="Indicates that the FastAPI application process is running and responsive.",
)
def check_service_health() -> HealthResponse:
    """Return operational status of the FastAPI backend service."""
    return HealthResponse(
        status="ok",
        service="adaptive-task-manager-api",
    )


@router.get(
    "/health/db",
    response_model=DatabaseHealthResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ErrorResponse,
            "description": "Database connection failed or is not configured.",
        }
    },
    summary="Database Connectivity Check",
    description="Executes a lightweight query (SELECT 1) to verify active PostgreSQL database connectivity.",
)
def check_database_health(db: Session = Depends(get_db)) -> DatabaseHealthResponse:
    """
    Test database connection responsiveness.
    Returns HTTP 503 if the database is unreachable or unconfigured without exposing
    connection strings, passwords, or internal infrastructure details.
    """
    try:
        is_connected = ping_database(db)
        if not is_connected:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"status": "error", "message": "Database connection unavailable"},
            )
        return DatabaseHealthResponse(status="ok", database="connected")
    except (SQLAlchemyError, RuntimeError) as exc:
        # Prevent credential or internal connection exposure
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "error", "message": "Database connection unavailable"},
        ) from exc
