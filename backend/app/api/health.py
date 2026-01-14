"""
Health Check API Endpoints (P0.42)

Provides shallow and deep health check endpoints for system verification.

Endpoints:
- GET /api/health - Quick check (verifies DB connectivity, fast for load balancers)
- GET /api/health/deep - E2E verification (comprehensive)
"""
import time
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.health_checks import HealthChecker
from app.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Health check with database connectivity verification.

    Used by load balancers and quick status checks.
    Verifies database is reachable (SELECT 1).

    Returns:
    - 200 with status "healthy" if database responds
    - 503 with status "unhealthy" if database fails
    """
    try:
        start = time.time()
        db.execute(text("SELECT 1"))
        latency_ms = (time.time() - start) * 1000

        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "database": "connected",
            "latency_ms": round(latency_ms, 2)
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "app": settings.APP_NAME,
                "database": "disconnected",
                "error": str(e)
            }
        )


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
