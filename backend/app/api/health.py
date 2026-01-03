"""
Health Check API Endpoints (P0.42)

Provides shallow and deep health check endpoints for system verification.

Endpoints:
- GET /api/health - Shallow check (fast, for load balancers)
- GET /api/health/deep - E2E verification (comprehensive)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.health_checks import HealthChecker
from app.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health_shallow():
    """
    Shallow health check - confirms app is running.

    Used by load balancers and quick status checks.
    Does NOT verify database or auth.
    """
    return {"status": "healthy", "app": settings.APP_NAME}


@router.get("/health/deep")
def health_deep(db: Session = Depends(get_db)):
    """
    Deep health check - E2E system verification.

    Verifies:
    - Database connectivity and latency
    - Auth system (health check user login)
    - Expected tables exist
    - Migrations are current

    Returns:
    - 200 with status "healthy" if ALL checks pass
    - 200 with status "degraded" if ANY check fails
    - 503 if database unreachable (status "unhealthy")
    """
    checker = HealthChecker(db)
    return checker.run_all_checks()
