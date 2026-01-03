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
