"""
Test suite for BranchHolidays feature.
TDD: These tests define expected behavior before implementation.

Uses TenantIsolationHelper for proper multi-tenant testing.
"""
import pytest
from datetime import date, datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.fixtures.tenant_fixtures import (
    multi_tenant_db,
    tenant1_context,
    tenant2_context,
    TenantIsolationHelper
)


class TestBranchHolidayModel:
    """Tests for BranchHoliday model"""

    def test_model_exists(self, multi_tenant_db: Session):
        """BranchHoliday model should exist and be importable"""
        from app.models import BranchHoliday
        assert BranchHoliday is not None

    def test_create_global_holiday(self, multi_tenant_db: Session):
        """Global holidays have branch_id=NULL and apply to all branches"""
        from app.models import BranchHoliday

        holiday = BranchHoliday(
            branch_id=None,  # Global - applies to all branches
            date=date(2026, 6, 17),  # Kurban Bayramı
            name="Kurban Bayramı 1. Gün",
            is_closed=True
        )
        multi_tenant_db.add(holiday)
        multi_tenant_db.commit()
        multi_tenant_db.refresh(holiday)

        assert holiday.id is not None
        assert holiday.branch_id is None
        assert holiday.date == date(2026, 6, 17)
        assert holiday.name == "Kurban Bayramı 1. Gün"
        assert holiday.is_closed is True
        assert holiday.created_at is not None

    def test_create_branch_specific_holiday(self, tenant1_context: dict):
        """Branch-specific holidays only apply to that branch"""
        from app.models import BranchHoliday

        db = tenant1_context["session"]
        branch_id = tenant1_context["branch_id"]

        holiday = BranchHoliday(
            branch_id=branch_id,  # Branch-specific
            date=date(2026, 1, 15),
            name="Şube Özel Tatili",
            is_closed=True
        )
        db.add(holiday)
        db.commit()
        db.refresh(holiday)

        assert holiday.id is not None
        assert holiday.branch_id == branch_id
        assert holiday.name == "Şube Özel Tatili"

    def test_holiday_with_is_closed_false(self, tenant1_context: dict):
        """Holiday can be marked as is_closed=False (e.g., special hours day)"""
        from app.models import BranchHoliday

        db = tenant1_context["session"]
        branch_id = tenant1_context["branch_id"]

        holiday = BranchHoliday(
            branch_id=branch_id,
            date=date(2026, 12, 31),
            name="Yılbaşı Arefesi (Yarım Gün)",
            is_closed=False  # Not closed, maybe special hours
        )
        db.add(holiday)
        db.commit()
        db.refresh(holiday)

        assert holiday.is_closed is False

    def test_holiday_has_timestamps(self, multi_tenant_db: Session):
        """Holiday should have created_at and updated_at timestamps"""
        from app.models import BranchHoliday

        holiday = BranchHoliday(
            branch_id=None,
            date=date(2026, 1, 1),
            name="Yılbaşı",
            is_closed=True
        )
        multi_tenant_db.add(holiday)
        multi_tenant_db.commit()
        multi_tenant_db.refresh(holiday)

        assert holiday.created_at is not None
        assert isinstance(holiday.created_at, datetime)


class TestBranchHolidayAPI:
    """Tests for BranchHoliday API endpoints"""

    def test_list_holidays_returns_empty_initially(self, client: TestClient, db: Session):
        """GET /api/v1/branch-holidays returns empty list when no holidays"""
        response = client.get("/api/v1/branch-holidays")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_holidays_returns_global_holidays(self, client: TestClient, db: Session):
        """GET /api/v1/branch-holidays returns global holidays"""
        from app.models import BranchHoliday

        # Create global holiday
        holiday = BranchHoliday(
            branch_id=None,
            date=date(2026, 1, 1),
            name="Yılbaşı",
            is_closed=True
        )
        db.add(holiday)
        db.commit()

        response = client.get("/api/v1/branch-holidays")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Yılbaşı"
        assert data[0]["date"] == "2026-01-01"
        assert data[0]["is_closed"] is True
        assert data[0]["branch_id"] is None

    def test_list_holidays_includes_branch_specific(self, client: TestClient, db: Session):
        """GET returns both global and branch-specific holidays"""
        from app.models import BranchHoliday

        # Global holiday
        global_h = BranchHoliday(
            branch_id=None,
            date=date(2026, 1, 1),
            name="Yılbaşı",
            is_closed=True
        )
        # Branch-specific holiday (branch_id=1 from conftest)
        branch_h = BranchHoliday(
            branch_id=1,
            date=date(2026, 1, 15),
            name="Şube Tatili",
            is_closed=True
        )
        db.add_all([global_h, branch_h])
        db.commit()

        response = client.get("/api/v1/branch-holidays")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 2

    def test_list_holidays_branch_override_on_same_date(self, client: TestClient, db: Session):
        """Branch-specific holiday takes precedence over global on same date"""
        from app.models import BranchHoliday

        # Global: Closed on Jan 15
        global_h = BranchHoliday(
            branch_id=None,
            date=date(2026, 1, 15),
            name="Resmi Tatil",
            is_closed=True
        )
        # Branch: Open on Jan 15 (override)
        branch_h = BranchHoliday(
            branch_id=1,
            date=date(2026, 1, 15),
            name="Şube Açık (Override)",
            is_closed=False
        )
        db.add_all([global_h, branch_h])
        db.commit()

        response = client.get("/api/v1/branch-holidays")
        assert response.status_code == 200

        data = response.json()
        # Should return branch-specific, not global
        jan15 = [h for h in data if h["date"] == "2026-01-15"]
        assert len(jan15) == 1
        assert jan15[0]["is_closed"] is False
        assert jan15[0]["name"] == "Şube Açık (Override)"

    def test_create_holiday(self, client: TestClient, db: Session):
        """POST /api/v1/branch-holidays creates a branch-specific holiday"""
        payload = {
            "date": "2026-06-17",
            "name": "Kurban Bayramı 1. Gün",
            "is_closed": True
        }

        response = client.post("/api/v1/branch-holidays", json=payload)
        assert response.status_code == 201

        data = response.json()
        assert data["id"] is not None
        assert data["date"] == "2026-06-17"
        assert data["name"] == "Kurban Bayramı 1. Gün"
        assert data["is_closed"] is True
        assert data["branch_id"] == 1  # Current branch from conftest

    def test_create_holiday_duplicate_date_updates(self, client: TestClient, db: Session):
        """POST with same date updates existing holiday for that branch"""
        from app.models import BranchHoliday

        # Create initial holiday
        existing = BranchHoliday(
            branch_id=1,
            date=date(2026, 1, 15),
            name="Old Name",
            is_closed=True
        )
        db.add(existing)
        db.commit()

        # POST same date - should update
        payload = {
            "date": "2026-01-15",
            "name": "New Name",
            "is_closed": False
        }

        response = client.post("/api/v1/branch-holidays", json=payload)
        assert response.status_code == 201

        # Verify only one record exists
        count = db.query(BranchHoliday).filter(
            BranchHoliday.branch_id == 1,
            BranchHoliday.date == date(2026, 1, 15)
        ).count()
        assert count == 1

        data = response.json()
        assert data["name"] == "New Name"
        assert data["is_closed"] is False

    def test_update_holiday(self, client: TestClient, db: Session):
        """PUT /api/v1/branch-holidays/{id} updates a holiday"""
        from app.models import BranchHoliday

        holiday = BranchHoliday(
            branch_id=1,
            date=date(2026, 1, 15),
            name="Original Name",
            is_closed=True
        )
        db.add(holiday)
        db.commit()
        db.refresh(holiday)

        payload = {
            "name": "Updated Name",
            "is_closed": False
        }

        response = client.put(f"/api/v1/branch-holidays/{holiday.id}", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["is_closed"] is False

    def test_update_holiday_not_found(self, client: TestClient, db: Session):
        """PUT returns 404 for non-existent holiday"""
        payload = {"name": "Updated"}

        response = client.put("/api/v1/branch-holidays/99999", json=payload)
        assert response.status_code == 404

    def test_delete_holiday(self, client: TestClient, db: Session):
        """DELETE /api/v1/branch-holidays/{id} removes a holiday"""
        from app.models import BranchHoliday

        holiday = BranchHoliday(
            branch_id=1,
            date=date(2026, 1, 15),
            name="To Delete",
            is_closed=True
        )
        db.add(holiday)
        db.commit()
        db.refresh(holiday)

        response = client.delete(f"/api/v1/branch-holidays/{holiday.id}")
        assert response.status_code == 204

        # Verify deleted
        deleted = db.query(BranchHoliday).filter(
            BranchHoliday.id == holiday.id
        ).first()
        assert deleted is None

    def test_delete_holiday_not_found(self, client: TestClient, db: Session):
        """DELETE returns 404 for non-existent holiday"""
        response = client.delete("/api/v1/branch-holidays/99999")
        assert response.status_code == 404


class TestBranchHolidayTenantIsolation:
    """Tests ensuring different branches have isolated holidays"""

    def test_different_branches_different_holidays(
        self,
        tenant1_context: dict,
        tenant2_context: dict
    ):
        """Different branches can have different holidays"""
        from app.models import BranchHoliday

        db = tenant1_context["session"]
        branch1_id = tenant1_context["branch_id"]
        branch2_id = tenant2_context["branch_id"]

        # Branch 1: Has a holiday
        holiday1 = BranchHoliday(
            branch_id=branch1_id,
            date=date(2026, 3, 15),
            name="Branch 1 Holiday",
            is_closed=True
        )
        db.add(holiday1)

        # Branch 2: Different holiday
        holiday2 = BranchHoliday(
            branch_id=branch2_id,
            date=date(2026, 3, 20),
            name="Branch 2 Holiday",
            is_closed=True
        )
        db.add(holiday2)
        db.commit()

        # Query branch 1 holidays
        branch1_holidays = db.query(BranchHoliday).filter(
            BranchHoliday.branch_id == branch1_id
        ).all()

        # Query branch 2 holidays
        branch2_holidays = db.query(BranchHoliday).filter(
            BranchHoliday.branch_id == branch2_id
        ).all()

        assert len(branch1_holidays) == 1
        assert len(branch2_holidays) == 1
        assert branch1_holidays[0].name == "Branch 1 Holiday"
        assert branch2_holidays[0].name == "Branch 2 Holiday"

    def test_global_holiday_accessible_to_all_branches(
        self,
        tenant1_context: dict,
        tenant2_context: dict
    ):
        """Global holidays (branch_id=NULL) are accessible to all"""
        from app.models import BranchHoliday
        from sqlalchemy import or_

        db = tenant1_context["session"]
        branch1_id = tenant1_context["branch_id"]
        branch2_id = tenant2_context["branch_id"]

        # Create global holiday
        global_holiday = BranchHoliday(
            branch_id=None,  # Global
            date=date(2026, 4, 23),
            name="23 Nisan Ulusal Egemenlik ve Çocuk Bayramı",
            is_closed=True
        )
        db.add(global_holiday)
        db.commit()

        # Both branches should see this holiday via query including NULL
        branch1_view = db.query(BranchHoliday).filter(
            or_(
                BranchHoliday.branch_id == branch1_id,
                BranchHoliday.branch_id == None
            )
        ).all()

        branch2_view = db.query(BranchHoliday).filter(
            or_(
                BranchHoliday.branch_id == branch2_id,
                BranchHoliday.branch_id == None
            )
        ).all()

        assert len(branch1_view) == 1
        assert len(branch2_view) == 1
        assert branch1_view[0].name == "23 Nisan Ulusal Egemenlik ve Çocuk Bayramı"
        assert branch2_view[0].name == "23 Nisan Ulusal Egemenlik ve Çocuk Bayramı"

    def test_branch_override_global_on_same_date(
        self,
        tenant1_context: dict,
        tenant2_context: dict
    ):
        """Branch can override a global holiday for its own view"""
        from app.models import BranchHoliday

        db = tenant1_context["session"]
        branch1_id = tenant1_context["branch_id"]
        branch2_id = tenant2_context["branch_id"]

        # Global: All closed on May 19
        global_h = BranchHoliday(
            branch_id=None,
            date=date(2026, 5, 19),
            name="19 Mayıs (Kapalı)",
            is_closed=True
        )
        db.add(global_h)

        # Branch 1: Override - open on May 19
        branch1_override = BranchHoliday(
            branch_id=branch1_id,
            date=date(2026, 5, 19),
            name="19 Mayıs (Şube 1 Açık)",
            is_closed=False
        )
        db.add(branch1_override)
        db.commit()

        # Branch 1 effective: Should see override (is_closed=False)
        branch1_specific = db.query(BranchHoliday).filter(
            BranchHoliday.branch_id == branch1_id,
            BranchHoliday.date == date(2026, 5, 19)
        ).first()
        assert branch1_specific is not None
        assert branch1_specific.is_closed is False

        # Branch 2 effective: No override, should use global (is_closed=True)
        branch2_specific = db.query(BranchHoliday).filter(
            BranchHoliday.branch_id == branch2_id,
            BranchHoliday.date == date(2026, 5, 19)
        ).first()
        # No branch-specific entry
        assert branch2_specific is None

        # Global exists
        global_entry = db.query(BranchHoliday).filter(
            BranchHoliday.branch_id == None,
            BranchHoliday.date == date(2026, 5, 19)
        ).first()
        assert global_entry is not None
        assert global_entry.is_closed is True
