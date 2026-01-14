"""
Tests for /api/v1/menu-categories endpoint

TDD: Written BEFORE implementation per P0.40
Feature: Menu Category CRUD with hybrid tenant isolation
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User, Branch, UserBranch


class TestMenuCategoriesEndpoint:
    """Test Menu Category CRUD operations"""

    # ==================== GET Tests ====================

    def test_get_menu_categories_returns_empty_list(self, client: TestClient, db: Session):
        """GET /api/v1/menu-categories returns empty list when no categories exist"""
        response = client.get("/api/v1/menu-categories")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_menu_categories_returns_global_categories(self, client: TestClient, db: Session):
        """Global categories (branch_id=NULL) are visible to all branches"""
        from app.models import MenuCategory

        # Create global category (branch_id=NULL)
        global_cat = MenuCategory(
            name="Çiğ Köfte",
            description="Ana ürünler",
            display_order=1,
            branch_id=None,  # Global
            created_by=1
        )
        db.add(global_cat)
        db.commit()

        response = client.get("/api/v1/menu-categories")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Çiğ Köfte"
        assert data[0]["branch_id"] is None

    def test_get_menu_categories_returns_branch_specific(self, client: TestClient, db: Session):
        """Branch-specific categories only visible to that branch"""
        from app.models import MenuCategory

        # Create branch-specific category for branch 1 (test fixture branch)
        branch_cat = MenuCategory(
            name="Şube Özel",
            display_order=1,
            branch_id=1,  # Test branch
            created_by=1
        )
        db.add(branch_cat)
        db.commit()

        response = client.get("/api/v1/menu-categories")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Şube Özel"
        assert data[0]["branch_id"] == 1

    def test_get_menu_categories_excludes_other_branch_categories(self, client: TestClient, db: Session):
        """Categories from other branches should NOT be visible"""
        from app.models import MenuCategory

        # Create another branch
        other_branch = Branch(name="Other Branch", code="OTHER", city="Ankara", is_active=True)
        db.add(other_branch)
        db.flush()

        # Create category for OTHER branch
        other_cat = MenuCategory(
            name="Diğer Şube Kategorisi",
            display_order=1,
            branch_id=other_branch.id,  # Different branch
            created_by=1
        )
        db.add(other_cat)
        db.commit()

        # Current branch is 1, should NOT see other branch's category
        response = client.get("/api/v1/menu-categories")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0  # Should be empty

    def test_get_menu_categories_combined_global_and_branch(self, client: TestClient, db: Session):
        """Should return both global AND current branch categories"""
        from app.models import MenuCategory

        # Global category
        global_cat = MenuCategory(
            name="Global Kategori",
            display_order=1,
            branch_id=None,
            created_by=1
        )
        # Branch-specific category
        branch_cat = MenuCategory(
            name="Şube Kategorisi",
            display_order=2,
            branch_id=1,
            created_by=1
        )
        db.add_all([global_cat, branch_cat])
        db.commit()

        response = client.get("/api/v1/menu-categories")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        names = [c["name"] for c in data]
        assert "Global Kategori" in names
        assert "Şube Kategorisi" in names

    def test_get_menu_categories_ordered_by_display_order(self, client: TestClient, db: Session):
        """Categories should be ordered by display_order"""
        from app.models import MenuCategory

        cat1 = MenuCategory(name="Third", display_order=3, branch_id=None, created_by=1)
        cat2 = MenuCategory(name="First", display_order=1, branch_id=None, created_by=1)
        cat3 = MenuCategory(name="Second", display_order=2, branch_id=None, created_by=1)
        db.add_all([cat1, cat2, cat3])
        db.commit()

        response = client.get("/api/v1/menu-categories")

        assert response.status_code == 200
        data = response.json()
        names = [c["name"] for c in data]
        assert names == ["First", "Second", "Third"]

    # ==================== POST Tests ====================

    def test_create_menu_category_branch_specific(self, client: TestClient, db: Session):
        """POST creates a branch-specific category by default"""
        payload = {
            "name": "İçecekler",
            "description": "Soğuk ve sıcak içecekler",
            "display_order": 1,
            "is_global": False
        }

        response = client.post("/api/v1/menu-categories", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "İçecekler"
        assert data["description"] == "Soğuk ve sıcak içecekler"
        assert data["display_order"] == 1
        assert data["branch_id"] == 1  # Current test branch
        assert data["is_active"] is True
        assert data["is_system"] is False
        assert "id" in data
        assert "created_at" in data

    def test_create_menu_category_global(self, client: TestClient, db: Session):
        """POST with is_global=True creates global category (branch_id=NULL)"""
        payload = {
            "name": "Tatlılar",
            "is_global": True
        }

        response = client.post("/api/v1/menu-categories", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Tatlılar"
        assert data["branch_id"] is None  # Global

    def test_create_menu_category_minimal_payload(self, client: TestClient, db: Session):
        """POST with only required field (name) works"""
        payload = {"name": "Minimal Kategori"}

        response = client.post("/api/v1/menu-categories", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Kategori"
        assert data["description"] is None
        assert data["display_order"] == 0  # Default
        assert data["is_active"] is True

    def test_create_menu_category_empty_name_fails(self, client: TestClient, db: Session):
        """POST with empty name should fail validation"""
        payload = {"name": ""}

        response = client.post("/api/v1/menu-categories", json=payload)

        assert response.status_code == 422  # Validation error

    def test_create_menu_category_duplicate_name_same_branch_fails(self, client: TestClient, db: Session):
        """Cannot create duplicate category name in same branch"""
        from app.models import MenuCategory

        # Create existing category
        existing = MenuCategory(
            name="Existing",
            branch_id=1,
            created_by=1
        )
        db.add(existing)
        db.commit()

        # Try to create duplicate
        payload = {"name": "Existing"}
        response = client.post("/api/v1/menu-categories", json=payload)

        assert response.status_code == 400
        assert "zaten mevcut" in response.json()["detail"].lower()

    def test_create_menu_category_same_name_different_branch_ok(self, client: TestClient, db: Session):
        """Same name in different branch should be allowed"""
        from app.models import MenuCategory

        # Create another branch
        other_branch = Branch(name="Other", code="OTH", city="Ankara", is_active=True)
        db.add(other_branch)
        db.flush()

        # Create category in OTHER branch
        other_cat = MenuCategory(
            name="Shared Name",
            branch_id=other_branch.id,
            created_by=1
        )
        db.add(other_cat)
        db.commit()

        # Create same name in current branch (1) - should succeed
        payload = {"name": "Shared Name"}
        response = client.post("/api/v1/menu-categories", json=payload)

        assert response.status_code == 201

    # ==================== Response Schema Tests ====================

    def test_response_includes_all_fields(self, client: TestClient, db: Session):
        """Response schema includes all expected fields"""
        payload = {
            "name": "Full Response Test",
            "description": "Test description",
            "display_order": 5
        }

        response = client.post("/api/v1/menu-categories", json=payload)

        assert response.status_code == 201
        data = response.json()

        # All expected fields present
        expected_fields = [
            "id", "name", "description", "display_order",
            "is_active", "is_system", "branch_id", "created_at"
        ]
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"

    # ==================== PUT Tests ====================

    def test_update_menu_category_success(self, client: TestClient, db: Session):
        """PUT updates category name and description"""
        from app.models import MenuCategory

        # Create category in current branch
        cat = MenuCategory(
            name="Original Name",
            description="Original desc",
            display_order=1,
            branch_id=1,
            created_by=1
        )
        db.add(cat)
        db.commit()
        db.refresh(cat)

        payload = {
            "name": "Updated Name",
            "description": "Updated desc"
        }
        response = client.put(f"/api/v1/menu-categories/{cat.id}", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "Updated desc"
        assert data["display_order"] == 1  # Unchanged

    def test_update_menu_category_partial(self, client: TestClient, db: Session):
        """PUT with partial payload only updates provided fields"""
        from app.models import MenuCategory

        cat = MenuCategory(
            name="Original",
            description="Keep this",
            display_order=5,
            branch_id=1,
            created_by=1
        )
        db.add(cat)
        db.commit()
        db.refresh(cat)

        # Only update name
        payload = {"name": "New Name Only"}
        response = client.put(f"/api/v1/menu-categories/{cat.id}", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name Only"
        assert data["description"] == "Keep this"  # Unchanged
        assert data["display_order"] == 5  # Unchanged

    def test_update_menu_category_not_found(self, client: TestClient, db: Session):
        """PUT returns 404 for non-existent category"""
        payload = {"name": "Whatever"}
        response = client.put("/api/v1/menu-categories/99999", json=payload)

        assert response.status_code == 404

    def test_update_menu_category_other_branch_forbidden(self, client: TestClient, db: Session):
        """PUT returns 404 for category from another branch (tenant isolation)"""
        from app.models import MenuCategory

        # Create another branch
        other_branch = Branch(name="Other Branch", code="OTH2", city="Izmir", is_active=True)
        db.add(other_branch)
        db.flush()

        # Create category in OTHER branch
        other_cat = MenuCategory(
            name="Other Branch Cat",
            branch_id=other_branch.id,
            created_by=1
        )
        db.add(other_cat)
        db.commit()
        db.refresh(other_cat)

        # Try to update from current branch (1) - should fail
        payload = {"name": "Hacked Name"}
        response = client.put(f"/api/v1/menu-categories/{other_cat.id}", json=payload)

        assert response.status_code == 404  # Not found (not accessible)

    def test_update_global_category_success(self, client: TestClient, db: Session):
        """PUT can update global categories (branch_id=NULL)"""
        from app.models import MenuCategory

        global_cat = MenuCategory(
            name="Global Original",
            branch_id=None,  # Global
            created_by=1
        )
        db.add(global_cat)
        db.commit()
        db.refresh(global_cat)

        payload = {"name": "Global Updated"}
        response = client.put(f"/api/v1/menu-categories/{global_cat.id}", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Global Updated"
        assert data["branch_id"] is None

    def test_update_menu_category_duplicate_name_fails(self, client: TestClient, db: Session):
        """PUT fails if updated name conflicts with existing in same scope"""
        from app.models import MenuCategory

        # Create two categories in same branch
        cat1 = MenuCategory(name="First", branch_id=1, created_by=1)
        cat2 = MenuCategory(name="Second", branch_id=1, created_by=1)
        db.add_all([cat1, cat2])
        db.commit()
        db.refresh(cat2)

        # Try to rename cat2 to "First" - should fail
        payload = {"name": "First"}
        response = client.put(f"/api/v1/menu-categories/{cat2.id}", json=payload)

        assert response.status_code == 400
        assert "zaten mevcut" in response.json()["detail"].lower()

    # ==================== DELETE Tests ====================

    def test_delete_menu_category_success(self, client: TestClient, db: Session):
        """DELETE removes category from current branch"""
        from app.models import MenuCategory

        cat = MenuCategory(
            name="To Delete",
            branch_id=1,
            created_by=1
        )
        db.add(cat)
        db.commit()
        db.refresh(cat)
        cat_id = cat.id

        response = client.delete(f"/api/v1/menu-categories/{cat_id}")

        assert response.status_code == 204

        # Verify deleted
        deleted = db.query(MenuCategory).filter(MenuCategory.id == cat_id).first()
        assert deleted is None

    def test_delete_menu_category_not_found(self, client: TestClient, db: Session):
        """DELETE returns 404 for non-existent category"""
        response = client.delete("/api/v1/menu-categories/99999")

        assert response.status_code == 404

    def test_delete_menu_category_other_branch_forbidden(self, client: TestClient, db: Session):
        """DELETE returns 404 for category from another branch (tenant isolation)"""
        from app.models import MenuCategory

        # Create another branch
        other_branch = Branch(name="Delete Test Branch", code="DEL1", city="Bursa", is_active=True)
        db.add(other_branch)
        db.flush()

        # Create category in OTHER branch
        other_cat = MenuCategory(
            name="Other Branch Delete",
            branch_id=other_branch.id,
            created_by=1
        )
        db.add(other_cat)
        db.commit()
        db.refresh(other_cat)

        # Try to delete from current branch (1) - should fail
        response = client.delete(f"/api/v1/menu-categories/{other_cat.id}")

        assert response.status_code == 404

        # Verify NOT deleted
        still_exists = db.query(MenuCategory).filter(MenuCategory.id == other_cat.id).first()
        assert still_exists is not None

    def test_delete_global_category_success(self, client: TestClient, db: Session):
        """DELETE can remove global categories (branch_id=NULL)"""
        from app.models import MenuCategory

        global_cat = MenuCategory(
            name="Global To Delete",
            branch_id=None,
            created_by=1
        )
        db.add(global_cat)
        db.commit()
        db.refresh(global_cat)
        cat_id = global_cat.id

        response = client.delete(f"/api/v1/menu-categories/{cat_id}")

        assert response.status_code == 204

    def test_delete_system_category_forbidden(self, client: TestClient, db: Session):
        """DELETE returns 400 for system categories (is_system=True)"""
        from app.models import MenuCategory

        system_cat = MenuCategory(
            name="System Category",
            branch_id=1,
            is_system=True,  # Cannot delete
            created_by=1
        )
        db.add(system_cat)
        db.commit()
        db.refresh(system_cat)

        response = client.delete(f"/api/v1/menu-categories/{system_cat.id}")

        assert response.status_code == 400
        assert "sistem" in response.json()["detail"].lower()
