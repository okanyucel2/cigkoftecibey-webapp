"""
E2E Health Check Tests (P0.42)

Tests for /api/health and /api/health/deep endpoints.
These tests verify that the health check system accurately reports
system state including database, auth, tables, and migrations.

TDD: Write tests FIRST, then implement.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User


class TestHealthShallow:
    """Tests for GET /api/health (shallow check)"""

    def test_health_returns_200(self, client: TestClient):
        """Shallow health should always return 200 if app is running"""
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_returns_healthy_status(self, client: TestClient):
        """Shallow health should return status: healthy"""
        response = client.get("/api/health")
        data = response.json()
        assert data["status"] == "healthy"


class TestHealthDeep:
    """Tests for GET /api/health/deep (E2E verification)"""

    def test_deep_health_returns_200(self, client: TestClient, db: Session):
        """Deep health endpoint should exist and return 200"""
        response = client.get("/api/health/deep")
        assert response.status_code == 200

    def test_deep_health_returns_required_fields(self, client: TestClient, db: Session):
        """Deep health must return status, timestamp, and checks"""
        response = client.get("/api/health/deep")
        data = response.json()

        assert "status" in data
        assert "timestamp" in data
        assert "checks" in data

    def test_deep_health_checks_database(self, client: TestClient, db: Session):
        """Deep health must verify database connectivity"""
        response = client.get("/api/health/deep")
        data = response.json()

        assert "database" in data["checks"]
        assert data["checks"]["database"]["status"] in ["pass", "fail"]
        assert "latency_ms" in data["checks"]["database"]

    def test_deep_health_checks_auth(self, client: TestClient, db: Session):
        """Deep health must verify auth system works"""
        # Create health check user for auth test
        from app.api.deps import get_password_hash
        health_user = User(
            email="healthcheck@internal.system",
            password_hash=get_password_hash("healthcheck123"),
            name="Health Check",
            role="health_check",
            is_active=True,
            is_super_admin=False
        )
        db.add(health_user)
        db.commit()

        response = client.get("/api/health/deep")
        data = response.json()

        assert "auth" in data["checks"]
        assert data["checks"]["auth"]["status"] == "pass"

    def test_deep_health_checks_tables(self, client: TestClient, db: Session):
        """Deep health must verify expected tables exist"""
        response = client.get("/api/health/deep")
        data = response.json()

        assert "tables" in data["checks"]
        assert data["checks"]["tables"]["status"] in ["pass", "fail"]
        assert "count" in data["checks"]["tables"]

    def test_deep_health_checks_migrations(self, client: TestClient, db: Session):
        """Deep health must verify migrations are current"""
        response = client.get("/api/health/deep")
        data = response.json()

        assert "migrations" in data["checks"]
        assert data["checks"]["migrations"]["status"] in ["pass", "fail"]

    def test_deep_health_status_healthy_when_all_pass(self, client: TestClient, db: Session):
        """Status should be 'healthy' only when ALL checks pass"""
        # Create health check user
        from app.api.deps import get_password_hash
        health_user = User(
            email="healthcheck@internal.system",
            password_hash=get_password_hash("healthcheck123"),
            name="Health Check",
            role="health_check",
            is_active=True,
            is_super_admin=False
        )
        db.add(health_user)
        db.commit()

        response = client.get("/api/health/deep")
        data = response.json()

        all_pass = all(
            check["status"] == "pass"
            for check in data["checks"].values()
        )

        if all_pass:
            assert data["status"] == "healthy"
        else:
            assert data["status"] in ["degraded", "unhealthy"]


class TestHealthDeepDegraded:
    """Tests for degraded state detection"""

    def test_deep_health_degraded_when_auth_fails(self, client: TestClient, db: Session):
        """Status should be 'degraded' when auth check fails (no health user)"""
        # Don't create health check user - auth should fail
        response = client.get("/api/health/deep")
        data = response.json()

        # Auth should fail because no health check user exists
        assert data["checks"]["auth"]["status"] == "fail"
        assert data["status"] == "degraded"


class TestLoginEndpoint:
    """Tests for actual login endpoint (P0.42 improvement: endpoint-level verification)"""

    def test_login_json_endpoint_loads_without_import_errors(self, client: TestClient, db: Session):
        """
        Login endpoint must not have import errors (500).

        This test catches bugs where the endpoint code has wrong imports
        that only fail at runtime, not at module load time.
        """
        # Create a test user
        from app.api.deps import get_password_hash
        test_user = User(
            email="testuser@example.com",
            password_hash=get_password_hash("testpass123"),
            name="Test User",
            role="cashier",
            is_active=True,
            is_super_admin=False
        )
        db.add(test_user)
        db.commit()

        # Call login endpoint - should NOT return 500
        response = client.post("/api/auth/login-json", json={
            "email": "testuser@example.com",
            "password": "testpass123"
        })

        # Any response code except 500 indicates endpoint loaded correctly
        # 401 = bad credentials (acceptable)
        # 200 = success (ideal)
        # 500 = import error or runtime crash (BUG!)
        assert response.status_code != 500, f"Login endpoint crashed: {response.text}"

    def test_login_json_returns_token_for_valid_user(self, client: TestClient, db: Session):
        """Successful login returns access token"""
        from app.api.deps import get_password_hash
        test_user = User(
            email="validuser@example.com",
            password_hash=get_password_hash("validpass123"),
            name="Valid User",
            role="cashier",
            is_active=True,
            is_super_admin=False
        )
        db.add(test_user)
        db.commit()

        response = client.post("/api/auth/login-json", json={
            "email": "validuser@example.com",
            "password": "validpass123"
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_login_json_rejects_invalid_credentials(self, client: TestClient, db: Session):
        """Login with wrong password returns 401, not 500"""
        from app.api.deps import get_password_hash
        test_user = User(
            email="wrongpass@example.com",
            password_hash=get_password_hash("correctpass"),
            name="Wrong Pass User",
            role="cashier",
            is_active=True,
            is_super_admin=False
        )
        db.add(test_user)
        db.commit()

        response = client.post("/api/auth/login-json", json={
            "email": "wrongpass@example.com",
            "password": "wrongpassword"
        })

        # Should be 401 Unauthorized, NOT 500 Server Error
        assert response.status_code == 401

    def test_login_json_admin_autoprovision_no_import_error(self, client: TestClient, db: Session):
        """
        Admin auto-provision code must not have import errors.

        The login-json endpoint has special logic to auto-create admin@cigkofte.com
        for E2E testing. This code path has a nested import that may have wrong path.
        """
        # This specifically tests the auto-provision code path (lines 47-75 in auth.py)
        # which triggers when admin@cigkofte.com / admin123 is used with no existing user

        # Ensure admin user doesn't exist (to trigger auto-provision)
        existing = db.query(User).filter(User.email == "admin@cigkofte.com").first()
        if existing:
            db.delete(existing)
            db.commit()

        response = client.post("/api/auth/login-json", json={
            "email": "admin@cigkofte.com",
            "password": "admin123"
        })

        # Should NOT be 500 Internal Server Error
        # May fail with 401 if FK constraints prevent auto-provision, but not 500 import error
        assert response.status_code != 500, f"Auto-provision code crashed with import error: {response.text}"


class TestDatabaseIdentity:
    """Tests for database identity verification (P0.42 enhancement)

    These tests verify we're connected to the CORRECT database,
    not just ANY working database. This catches configuration
    mismatches like connecting to wrong port/database.
    """

    def test_deep_health_includes_database_identity_check(self, client: TestClient, db: Session):
        """Deep health must include database_identity check"""
        response = client.get("/api/health/deep")
        data = response.json()

        assert "database_identity" in data["checks"], \
            "P0.42 requires database_identity check to prevent wrong-database bugs"
        assert data["checks"]["database_identity"]["status"] in ["pass", "fail"]

    def test_database_identity_returns_connection_info(self, client: TestClient, db: Session):
        """Database identity check must return actual connection details"""
        response = client.get("/api/health/deep")
        data = response.json()

        identity = data["checks"]["database_identity"]
        # Must include actual connection info for debugging
        assert "database_name" in identity, "Should show connected database name"
        assert "port" in identity, "Should show connected port"

    def test_database_identity_verifies_expected_database(self, client: TestClient, db: Session):
        """Database identity must match expected configuration"""
        response = client.get("/api/health/deep")
        data = response.json()

        identity = data["checks"]["database_identity"]

        # If we're connected to the expected database, status should be pass
        # The check should fail if we're connected to wrong database
        if identity["status"] == "pass":
            # In test mode (SQLite), name is "sqlite_test"
            # In production (PostgreSQL), name should START WITH "cigkofte"
            # (Render uses "cigkofte_xxxx" format)
            if identity.get("dialect") == "sqlite":
                assert identity["database_name"] == "sqlite_test", \
                    "SQLite test mode should report 'sqlite_test'"
            else:
                assert identity["database_name"].startswith("cigkofte"), \
                    f"Expected database name starting with 'cigkofte', got '{identity.get('database_name')}'"
