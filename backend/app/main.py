"""FastAPI application entry point, CORS middleware, and route mounting."""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.routes.health import router as health_router
from app.api.routes.tasks import router as tasks_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.schedule import router as schedule_router
from app.api.routes.settings import router as settings_router


def create_application() -> FastAPI:
    """Instantiate and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_title,
        version=settings.app_version,
        description=(
            "REST API for Adaptive Task & Deadline Management System. "
            "Dynamically generates and adapts schedules based on deadlines, "
            "priorities, difficulty, progress, and user availability."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Configure CORS for local Next.js frontend development server
    # Avoid wildcard with credentials
    configured_origin = settings.frontend_origin.rstrip("/") if settings.frontend_origin else "http://localhost:3000"
    origins = list(set([
        configured_origin,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]))

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        import logging
        logging.getLogger(__name__).error(f"Unhandled server error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": {"status": "error", "message": "Internal server error"}},
        )

    # Mount API routers under /api
    app.include_router(health_router, prefix=settings.api_prefix)
    app.include_router(tasks_router, prefix=settings.api_prefix)
    app.include_router(dashboard_router, prefix=settings.api_prefix)
    app.include_router(schedule_router, prefix=settings.api_prefix)
    app.include_router(settings_router, prefix=settings.api_prefix)

    # Root redirect / status indicator
    @app.get("/", tags=["Root"], include_in_schema=False)
    def root():
        return {
            "service": settings.app_title,
            "version": settings.app_version,
            "status": "running",
            "documentation": "/docs",
        }

    return app


app = create_application()
