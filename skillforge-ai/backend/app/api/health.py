"""Health and readiness endpoints."""

from fastapi import APIRouter

from app.core.config import settings
from app.core.database import check_database_connection

router = APIRouter()


@router.get("/health")
def health() -> dict[str, object]:
    """Liveness check — does not require database connectivity."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "environment": settings.app_env,
        "phase": 3,
        "ai_provider": settings.ai_provider,
        "course_provider_mode": settings.course_provider_mode,
    }


@router.get("/ready")
def ready() -> dict[str, object]:
    """Readiness check — verifies PostgreSQL connectivity without exposing secrets."""
    if check_database_connection():
        return {
            "status": "ready",
            "database": "connected",
        }
    return {
        "status": "not_ready",
        "database": "unavailable",
    }
