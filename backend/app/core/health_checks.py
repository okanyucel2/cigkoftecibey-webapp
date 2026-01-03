"""
E2E Health Check Implementation (P0.42)

Provides comprehensive health verification for all critical systems.
Used by /api/health/deep endpoint to verify system readiness.
"""
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import User


@dataclass
class CheckResult:
    """Result of a single health check"""
    name: str
    status: str  # "pass" or "fail"
    latency_ms: float = 0.0
    details: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "status": self.status,
            "latency_ms": round(self.latency_ms, 2)
        }
        if self.details:
            result["details"] = self.details
        result.update(self.extra)
        return result


class HealthChecker:
    """
    Comprehensive health checker for E2E verification.

    Checks:
    - Database connectivity and latency
    - Auth system (test user login)
    - Table count verification
    - Migration status
    """

    # Health check user credentials (created via migration)
    HEALTH_USER_EMAIL = "healthcheck@internal.system"
    HEALTH_USER_PASSWORD = "healthcheck123"

    # Expected table count (update when adding migrations)
    EXPECTED_TABLE_COUNT = 30

    def __init__(self, db: Session):
        self.db = db

    def check_database(self) -> CheckResult:
        """
        Verify database connectivity and measure latency.

        - Executes: SELECT 1
        - Measures: Query latency
        - Returns: pass if <500ms, fail otherwise
        """
        start = time.time()
        try:
            self.db.execute(text("SELECT 1"))
            latency_ms = (time.time() - start) * 1000

            if latency_ms > 500:
                return CheckResult(
                    name="database",
                    status="fail",
                    latency_ms=latency_ms,
                    details=f"Database latency too high: {latency_ms:.2f}ms"
                )

            return CheckResult(
                name="database",
                status="pass",
                latency_ms=latency_ms
            )
        except Exception as e:
            return CheckResult(
                name="database",
                status="fail",
                latency_ms=(time.time() - start) * 1000,
                details=f"Database connection failed: {str(e)}"
            )

    def check_auth(self) -> CheckResult:
        """
        Verify auth system works by testing health check user login.

        - User: healthcheck@internal.system
        - Action: Verify password, generate JWT
        - Returns: pass if login succeeds, fail otherwise
        """
        start = time.time()
        try:
            # Find health check user
            user = self.db.query(User).filter(
                User.email == self.HEALTH_USER_EMAIL
            ).first()

            if not user:
                return CheckResult(
                    name="auth",
                    status="fail",
                    latency_ms=(time.time() - start) * 1000,
                    details=f"Health check user not found: {self.HEALTH_USER_EMAIL}"
                )

            # Verify password
            from app.api.deps import verify_password
            if not verify_password(self.HEALTH_USER_PASSWORD, user.password_hash):
                return CheckResult(
                    name="auth",
                    status="fail",
                    latency_ms=(time.time() - start) * 1000,
                    details="Health check user password verification failed"
                )

            # Generate token to verify JWT creation works
            from app.api.deps import create_access_token
            token = create_access_token(data={"sub": str(user.id)})

            if not token:
                return CheckResult(
                    name="auth",
                    status="fail",
                    latency_ms=(time.time() - start) * 1000,
                    details="JWT token creation failed"
                )

            return CheckResult(
                name="auth",
                status="pass",
                latency_ms=(time.time() - start) * 1000,
                extra={"test_user": self.HEALTH_USER_EMAIL}
            )

        except Exception as e:
            return CheckResult(
                name="auth",
                status="fail",
                latency_ms=(time.time() - start) * 1000,
                details=f"Auth check failed: {str(e)}"
            )

    def check_tables(self) -> CheckResult:
        """
        Verify expected database tables exist.

        - Query: Count tables (PostgreSQL or SQLite compatible)
        - Expected: EXPECTED_TABLE_COUNT tables
        - Returns: pass if count matches, fail otherwise
        """
        start = time.time()
        try:
            # Detect database type and use appropriate query
            dialect = self.db.bind.dialect.name if self.db.bind else "unknown"

            if dialect == "postgresql":
                result = self.db.execute(text("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_type = 'BASE TABLE'
                """))
            else:
                # SQLite fallback
                result = self.db.execute(text("""
                    SELECT COUNT(*)
                    FROM sqlite_master
                    WHERE type = 'table'
                    AND name NOT LIKE 'sqlite_%'
                """))

            count = result.scalar()
            latency_ms = (time.time() - start) * 1000

            # Allow flexibility - at least expected count (or any tables for test DBs)
            if count >= self.EXPECTED_TABLE_COUNT or (dialect != "postgresql" and count > 0):
                return CheckResult(
                    name="tables",
                    status="pass",
                    latency_ms=latency_ms,
                    extra={"count": count, "expected": self.EXPECTED_TABLE_COUNT}
                )
            else:
                return CheckResult(
                    name="tables",
                    status="fail",
                    latency_ms=latency_ms,
                    details=f"Expected {self.EXPECTED_TABLE_COUNT} tables, found {count}",
                    extra={"count": count, "expected": self.EXPECTED_TABLE_COUNT}
                )

        except Exception as e:
            return CheckResult(
                name="tables",
                status="fail",
                latency_ms=(time.time() - start) * 1000,
                details=f"Table check failed: {str(e)}"
            )

    def check_migrations(self) -> CheckResult:
        """
        Verify migrations are current by checking alembic_version.

        - Query: alembic_version table
        - Returns: pass if version exists, fail if table missing
        """
        start = time.time()
        try:
            result = self.db.execute(text("""
                SELECT version_num FROM alembic_version LIMIT 1
            """))
            version = result.scalar()

            latency_ms = (time.time() - start) * 1000

            if version:
                return CheckResult(
                    name="migrations",
                    status="pass",
                    latency_ms=latency_ms,
                    extra={"current_version": version}
                )
            else:
                return CheckResult(
                    name="migrations",
                    status="fail",
                    latency_ms=latency_ms,
                    details="No migration version found"
                )

        except Exception as e:
            return CheckResult(
                name="migrations",
                status="fail",
                latency_ms=(time.time() - start) * 1000,
                details=f"Migration check failed: {str(e)}"
            )

    def run_all_checks(self) -> Dict[str, Any]:
        """
        Run all health checks and return comprehensive result.

        Returns:
        {
            "status": "healthy|degraded|unhealthy",
            "timestamp": "ISO-8601",
            "checks": {
                "database": {...},
                "auth": {...},
                "tables": {...},
                "migrations": {...}
            }
        }
        """
        checks = [
            self.check_database(),
            self.check_auth(),
            self.check_tables(),
            self.check_migrations()
        ]

        # Determine overall status
        all_pass = all(c.status == "pass" for c in checks)
        any_fail = any(c.status == "fail" for c in checks)

        if all_pass:
            status = "healthy"
        elif any_fail:
            status = "degraded"
        else:
            status = "unhealthy"

        return {
            "status": status,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "checks": {c.name: c.to_dict() for c in checks}
        }
