"""
Test suite for BranchOperatingHours feature.
TDD: These tests define expected behavior before implementation.

Uses TenantIsolationHelper for proper multi-tenant testing.
"""
import pytest
from datetime import time
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.fixtures.tenant_fixtures import (
    multi_tenant_db,
    tenant1_context,
    tenant2_context,
    TenantIsolationHelper
)


class TestBranchOperatingHoursModel:
    """Tests for BranchOperatingHours model"""

    def test_model_exists(self, multi_tenant_db: Session):
        """BranchOperatingHours model should exist and be importable"""
        from app.models import BranchOperatingHours
        assert BranchOperatingHours is not None

    def test_create_global_default_hours(self, multi_tenant_db: Session):
        """Global default hours have branch_id=NULL"""
        from app.models import BranchOperatingHours

        hours = BranchOperatingHours(
            branch_id=None,  # Global default
            day_of_week=0,  # Monday
            open_time=time(10, 0),
            close_time=time(22, 0),
            is_closed=False
        )
        multi_tenant_db.add(hours)
        multi_tenant_db.commit()
        multi_tenant_db.refresh(hours)

        assert hours.id is not None
        assert hours.branch_id is None
        assert hours.day_of_week == 0
        assert hours.open_time == time(10, 0)
        assert hours.close_time == time(22, 0)
        assert hours.is_closed is False

    def test_create_branch_specific_hours(self, tenant1_context: dict):
        """Branch-specific hours override global defaults"""
        from app.models import BranchOperatingHours

        db = tenant1_context["session"]
        branch_id = tenant1_context["branch_id"]

        # Create branch-specific hours
        hours = BranchOperatingHours(
            branch_id=branch_id,  # Branch specific (from tenant1 context)
            day_of_week=0,  # Monday
            open_time=time(11, 0),  # Different from global
            close_time=time(23, 0),
            is_closed=False
        )
        db.add(hours)
        db.commit()
        db.refresh(hours)

        assert hours.id is not None
        assert hours.branch_id == branch_id
        assert hours.open_time == time(11, 0)

    def test_closed_day(self, tenant1_context: dict):
        """Branch can mark specific days as closed"""
        from app.models import BranchOperatingHours

        db = tenant1_context["session"]
        branch_id = tenant1_context["branch_id"]

        # Sunday closed
        hours = BranchOperatingHours(
            branch_id=branch_id,
            day_of_week=6,  # Sunday
            open_time=None,
            close_time=None,
            is_closed=True
        )
        db.add(hours)
        db.commit()
        db.refresh(hours)

        assert hours.is_closed is True
        assert hours.open_time is None
        assert hours.close_time is None

    def test_day_of_week_valid_range(self, multi_tenant_db: Session):
        """Day of week should be 0-6 (Monday-Sunday)"""
        from app.models import BranchOperatingHours

        # All days should be valid
        for day in range(7):
            hours = BranchOperatingHours(
                branch_id=None,
                day_of_week=day,
                open_time=time(10, 0),
                close_time=time(22, 0),
                is_closed=False
            )
            multi_tenant_db.add(hours)
        multi_tenant_db.commit()

        # Query all - should have 7 records
        all_hours = multi_tenant_db.query(BranchOperatingHours).filter(
            BranchOperatingHours.branch_id == None
        ).all()
        assert len(all_hours) == 7


class TestBranchOperatingHoursAPI:
    """Tests for BranchOperatingHours API endpoints"""

    def test_get_hours_returns_global_defaults(self, client: TestClient, db: Session):
        """GET /api/v1/branch-hours returns global defaults when no branch override"""
        from app.models import BranchOperatingHours

        # Create global defaults for Monday
        global_hours = BranchOperatingHours(
            branch_id=None,
            day_of_week=0,
            open_time=time(10, 0),
            close_time=time(22, 0),
            is_closed=False
        )
        db.add(global_hours)
        db.commit()

        response = client.get("/api/v1/branch-hours")
        assert response.status_code == 200

        data = response.json()
        assert len(data) >= 1
        monday = next((h for h in data if h["day_of_week"] == 0), None)
        assert monday is not None
        assert monday["open_time"] == "10:00:00"
        assert monday["close_time"] == "22:00:00"

    def test_get_hours_branch_overrides_global(self, client: TestClient, db: Session):
        """Branch-specific hours take precedence over global defaults"""
        from app.models import BranchOperatingHours

        # Create global default
        global_hours = BranchOperatingHours(
            branch_id=None,
            day_of_week=0,
            open_time=time(10, 0),
            close_time=time(22, 0),
            is_closed=False
        )
        db.add(global_hours)

        # Create branch override (branch_id=1 from conftest)
        branch_hours = BranchOperatingHours(
            branch_id=1,
            day_of_week=0,
            open_time=time(11, 30),
            close_time=time(23, 30),
            is_closed=False
        )
        db.add(branch_hours)
        db.commit()

        response = client.get("/api/v1/branch-hours")
        assert response.status_code == 200

        data = response.json()
        monday = next((h for h in data if h["day_of_week"] == 0), None)
        assert monday is not None
        # Should have branch-specific time, not global
        assert monday["open_time"] == "11:30:00"
        assert monday["close_time"] == "23:30:00"

    def test_get_hours_returns_all_days(self, client: TestClient, db: Session):
        """GET should return hours for all 7 days of the week"""
        from app.models import BranchOperatingHours

        # Create global defaults for all days
        for day in range(7):
            hours = BranchOperatingHours(
                branch_id=None,
                day_of_week=day,
                open_time=time(10, 0),
                close_time=time(22, 0),
                is_closed=False
            )
            db.add(hours)
        db.commit()

        response = client.get("/api/v1/branch-hours")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 7

        # Verify all days present
        days = {h["day_of_week"] for h in data}
        assert days == {0, 1, 2, 3, 4, 5, 6}

    def test_post_hours_creates_branch_override(self, client: TestClient, db: Session):
        """POST creates branch-specific hours"""
        payload = {
            "day_of_week": 0,
            "open_time": "09:00:00",
            "close_time": "21:00:00",
            "is_closed": False
        }

        response = client.post("/api/v1/branch-hours", json=payload)
        assert response.status_code == 201

        data = response.json()
        assert data["day_of_week"] == 0
        assert data["open_time"] == "09:00:00"
        assert data["close_time"] == "21:00:00"
        assert data["branch_id"] == 1  # Current branch from conftest

    def test_post_hours_updates_existing(self, client: TestClient, db: Session):
        """POST updates existing branch hours for same day"""
        from app.models import BranchOperatingHours

        # Create initial hours
        existing = BranchOperatingHours(
            branch_id=1,
            day_of_week=0,
            open_time=time(10, 0),
            close_time=time(22, 0),
            is_closed=False
        )
        db.add(existing)
        db.commit()

        # Update via POST
        payload = {
            "day_of_week": 0,
            "open_time": "08:00:00",
            "close_time": "23:00:00",
            "is_closed": False
        }

        response = client.post("/api/v1/branch-hours", json=payload)
        assert response.status_code == 201

        # Verify only one record exists for this day
        count = db.query(BranchOperatingHours).filter(
            BranchOperatingHours.branch_id == 1,
            BranchOperatingHours.day_of_week == 0
        ).count()
        assert count == 1

        data = response.json()
        assert data["open_time"] == "08:00:00"

    def test_post_hours_batch_update(self, client: TestClient, db: Session):
        """POST can update multiple days at once"""
        payload = {
            "hours": [
                {"day_of_week": 0, "open_time": "10:00:00", "close_time": "22:00:00", "is_closed": False},
                {"day_of_week": 1, "open_time": "10:00:00", "close_time": "22:00:00", "is_closed": False},
                {"day_of_week": 6, "open_time": None, "close_time": None, "is_closed": True},
            ]
        }

        response = client.post("/api/v1/branch-hours/batch", json=payload)
        assert response.status_code == 201

        data = response.json()
        assert len(data) == 3

    def test_post_hours_closed_day(self, client: TestClient, db: Session):
        """POST can mark a day as closed"""
        payload = {
            "day_of_week": 6,  # Sunday
            "open_time": None,
            "close_time": None,
            "is_closed": True
        }

        response = client.post("/api/v1/branch-hours", json=payload)
        assert response.status_code == 201

        data = response.json()
        assert data["is_closed"] is True


class TestBranchOperatingHoursTenantIsolation:
    """Tests ensuring different branches have isolated schedules (uses TenantIsolationHelper)"""

    def test_different_branches_different_hours(
        self,
        tenant1_context: dict,
        tenant2_context: dict
    ):
        """Different branches can have completely different schedules"""
        from app.models import BranchOperatingHours

        # Both contexts share the same session (multi_tenant_db)
        db = tenant1_context["session"]
        branch1_id = tenant1_context["branch_id"]
        branch2_id = tenant2_context["branch_id"]

        # Branch 1: Opens at 10:00
        hours1 = BranchOperatingHours(
            branch_id=branch1_id,
            day_of_week=0,
            open_time=time(10, 0),
            close_time=time(22, 0),
            is_closed=False
        )
        db.add(hours1)

        # Branch 2: Opens at 08:00 (earlier)
        hours2 = BranchOperatingHours(
            branch_id=branch2_id,
            day_of_week=0,
            open_time=time(8, 0),
            close_time=time(20, 0),
            is_closed=False
        )
        db.add(hours2)
        db.commit()

        # Query branch 1 hours
        branch1_hours = db.query(BranchOperatingHours).filter(
            BranchOperatingHours.branch_id == branch1_id,
            BranchOperatingHours.day_of_week == 0
        ).first()

        # Query branch 2 hours
        branch2_hours = db.query(BranchOperatingHours).filter(
            BranchOperatingHours.branch_id == branch2_id,
            BranchOperatingHours.day_of_week == 0
        ).first()

        # Verify they are different
        assert branch1_hours.open_time != branch2_hours.open_time
        assert branch1_hours.open_time == time(10, 0)
        assert branch2_hours.open_time == time(8, 0)

    def test_branch_closed_day_independent(
        self,
        tenant1_context: dict,
        tenant2_context: dict
    ):
        """One branch can be closed while another is open"""
        from app.models import BranchOperatingHours

        db = tenant1_context["session"]
        branch1_id = tenant1_context["branch_id"]
        branch2_id = tenant2_context["branch_id"]

        # Branch 1: Open on Sunday
        hours1 = BranchOperatingHours(
            branch_id=branch1_id,
            day_of_week=6,  # Sunday
            open_time=time(12, 0),
            close_time=time(20, 0),
            is_closed=False
        )
        db.add(hours1)

        # Branch 2: Closed on Sunday
        hours2 = BranchOperatingHours(
            branch_id=branch2_id,
            day_of_week=6,  # Sunday
            open_time=None,
            close_time=None,
            is_closed=True
        )
        db.add(hours2)
        db.commit()

        # Verify independence
        branch1_sunday = db.query(BranchOperatingHours).filter(
            BranchOperatingHours.branch_id == branch1_id,
            BranchOperatingHours.day_of_week == 6
        ).first()

        branch2_sunday = db.query(BranchOperatingHours).filter(
            BranchOperatingHours.branch_id == branch2_id,
            BranchOperatingHours.day_of_week == 6
        ).first()

        assert branch1_sunday.is_closed is False
        assert branch2_sunday.is_closed is True

    def test_global_defaults_apply_to_all_branches(
        self,
        tenant1_context: dict,
        tenant2_context: dict
    ):
        """Global defaults (branch_id=NULL) apply when no branch-specific hours"""
        from app.models import BranchOperatingHours

        db = tenant1_context["session"]
        branch1_id = tenant1_context["branch_id"]
        branch2_id = tenant2_context["branch_id"]

        # Create global default for Monday
        global_hours = BranchOperatingHours(
            branch_id=None,  # Global
            day_of_week=0,
            open_time=time(10, 0),
            close_time=time(22, 0),
            is_closed=False
        )
        db.add(global_hours)

        # Branch 1 overrides for Monday
        branch1_override = BranchOperatingHours(
            branch_id=branch1_id,
            day_of_week=0,
            open_time=time(9, 0),
            close_time=time(21, 0),
            is_closed=False
        )
        db.add(branch1_override)

        # Branch 2 has NO override - should use global
        db.commit()

        # Query effective hours for branch 1 (should be override)
        branch1_effective = db.query(BranchOperatingHours).filter(
            BranchOperatingHours.branch_id == branch1_id,
            BranchOperatingHours.day_of_week == 0
        ).first()

        # Query effective hours for branch 2 (should be global since no override)
        branch2_effective = db.query(BranchOperatingHours).filter(
            BranchOperatingHours.branch_id == branch2_id,
            BranchOperatingHours.day_of_week == 0
        ).first()

        assert branch1_effective is not None
        assert branch1_effective.open_time == time(9, 0)

        # Branch 2 has no specific hours, so query returns None
        # In the API, we would fall back to global
        assert branch2_effective is None

        # Global should exist
        global_effective = db.query(BranchOperatingHours).filter(
            BranchOperatingHours.branch_id == None,
            BranchOperatingHours.day_of_week == 0
        ).first()
        assert global_effective is not None
        assert global_effective.open_time == time(10, 0)
