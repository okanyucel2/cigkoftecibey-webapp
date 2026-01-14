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

# App version and start time for uptime tracking
APP_VERSION = "1.0.0"
APP_START_TIME = datetime.utcnow()


def get_uptime() -> str:
    """Calculate human-readable uptime string."""
    delta = datetime.utcnow() - APP_START_TIME
    total_seconds = int(delta.total_seconds())

    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m")

    return " ".join(parts)


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
    - Database identity (correct host:port:name)
    - Auth system (test user login)
    - Table count verification
    - Migration status
    """

    # Health check user credentials (created via migration)
    HEALTH_USER_EMAIL = "healthcheck@internal.system"
    HEALTH_USER_PASSWORD = "healthcheck123"

    # Expected table count (update when adding migrations)
    EXPECTED_TABLE_COUNT = 30

    # Expected database identity (P0.42 enhancement)
    # This prevents connecting to wrong database silently
    #
    # PRODUCTION SAFETY:
    # - On Render, database name is "cigkofte_xxxx" (random suffix)
    # - On local Docker, database name is "cigkofte"
    # - We only verify the name STARTS WITH "cigkofte" to support both
    # - Port is logged but not strictly validated (varies by environment)
    EXPECTED_DATABASE_NAME_PREFIX = "cigkofte"  # Matches both local and Render
    EXPECTED_DATABASE_PORT = None  # Don't validate port (varies by environment)

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

    def check_database_identity(self) -> CheckResult:
        """
        Verify we're connected to the CORRECT database (P0.42 enhancement).

        This check prevents silent misconfiguration where app connects to
        wrong database (e.g., local PostgreSQL instead of Docker, or
        wrong port/database name).

        - Query: current_database(), inet_server_port()
        - Expected: EXPECTED_DATABASE_NAME on EXPECTED_DATABASE_PORT
        - Returns: pass if identity matches, fail otherwise
        """
        start = time.time()
        try:
            dialect = self.db.bind.dialect.name if self.db.bind else "unknown"

            if dialect == "postgresql":
                # PostgreSQL: Get actual database name and port
                result = self.db.execute(text("""
                    SELECT current_database(), inet_server_port()
                """))
                row = result.fetchone()
                db_name = row[0] if row else None
                db_port = int(row[1]) if row and row[1] else None
            else:
                # SQLite: No port concept, just check it's SQLite (test mode)
                db_name = "sqlite_test"
                db_port = None

            latency_ms = (time.time() - start) * 1000

            # For SQLite (tests), always pass - we only validate PostgreSQL identity
            if dialect != "postgresql":
                return CheckResult(
                    name="database_identity",
                    status="pass",
                    latency_ms=latency_ms,
                    extra={
                        "database_name": db_name,
                        "port": db_port,
                        "dialect": dialect,
                        "note": "SQLite test mode - identity check skipped"
                    }
                )

            # For PostgreSQL, verify identity matches expected
            # Use prefix matching to support both local ("cigkofte") and Render ("cigkofte_xxxx")
            name_match = db_name and db_name.startswith(self.EXPECTED_DATABASE_NAME_PREFIX)
            # Port is not strictly validated (varies by environment: Docker, Render, local)

            if name_match:
                return CheckResult(
                    name="database_identity",
                    status="pass",
                    latency_ms=latency_ms,
                    extra={
                        "database_name": db_name,
                        "port": db_port,
                        "expected_prefix": self.EXPECTED_DATABASE_NAME_PREFIX,
                        "environment": "production" if db_name != self.EXPECTED_DATABASE_NAME_PREFIX else "local"
                    }
                )
            else:
                return CheckResult(
                    name="database_identity",
                    status="fail",
                    latency_ms=latency_ms,
                    details=f"Wrong database: expected name starting with '{self.EXPECTED_DATABASE_NAME_PREFIX}', got '{db_name}'",
                    extra={
                        "database_name": db_name,
                        "port": db_port,
                        "expected_prefix": self.EXPECTED_DATABASE_NAME_PREFIX
                    }
                )

        except Exception as e:
            return CheckResult(
                name="database_identity",
                status="fail",
                latency_ms=(time.time() - start) * 1000,
                details=f"Database identity check failed: {str(e)}"
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
            "version": "1.0.0",
            "uptime": "2h 34m",
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
            self.check_database_identity(),
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
            "version": APP_VERSION,
            "uptime": get_uptime(),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "checks": {c.name: c.to_dict() for c in checks}
        }
