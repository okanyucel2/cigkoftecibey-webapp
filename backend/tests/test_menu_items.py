"""
Tests for /api/v1/menu-items endpoint

TDD: Written BEFORE implementation per P0.40
Feature: Menu Item CRUD with hybrid tenant isolation
"""
import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Branch, MenuCategory, MenuItem


class TestMenuItemsEndpoint:
    """Test Menu Item CRUD operations"""

    # ==================== GET Tests ====================

    def test_get_menu_items_returns_empty_list(self, client: TestClient, db: Session):
        """GET /api/v1/menu-items returns empty list when no items exist"""
        response = client.get("/api/v1/menu-items")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_menu_items_returns_global_items(self, client: TestClient, db: Session):
        """Global items (branch_id=NULL) are visible to all branches"""
        # Create category first
        category = MenuCategory(name="Test Category", branch_id=None, created_by=1)
        db.add(category)
        db.flush()

        # Create global item
        item = MenuItem(
            category_id=category.id,
            name="Çiğ Köfte Dürüm",
            price=Decimal("45.00"),
            branch_id=None,  # Global
            created_by=1
        )
        db.add(item)
        db.commit()

        response = client.get("/api/v1/menu-items")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Çiğ Köfte Dürüm"
        assert data[0]["price"] == "45.00"
        assert data[0]["branch_id"] is None

    def test_get_menu_items_returns_branch_specific(self, client: TestClient, db: Session):
        """Branch-specific items only visible to that branch"""
        category = MenuCategory(name="Test Category", branch_id=1, created_by=1)
        db.add(category)
        db.flush()

        item = MenuItem(
            category_id=category.id,
            name="Şube Özel Ürün",
            price=Decimal("50.00"),
            branch_id=1,  # Test branch
            created_by=1
        )
        db.add(item)
        db.commit()

        response = client.get("/api/v1/menu-items")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Şube Özel Ürün"
        assert data[0]["branch_id"] == 1

    def test_get_menu_items_excludes_other_branch_items(self, client: TestClient, db: Session):
        """Items from other branches should NOT be visible"""
        # Create another branch
        other_branch = Branch(name="Other Branch", code="OTHER", city="Ankara", is_active=True)
        db.add(other_branch)
        db.flush()

        category = MenuCategory(name="Other Category", branch_id=other_branch.id, created_by=1)
        db.add(category)
        db.flush()

        # Create item for OTHER branch
        item = MenuItem(
            category_id=category.id,
            name="Diğer Şube Ürünü",
            price=Decimal("60.00"),
            branch_id=other_branch.id,
            created_by=1
        )
        db.add(item)
        db.commit()

        # Current branch is 1, should NOT see other branch's item
        response = client.get("/api/v1/menu-items")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_get_menu_items_filter_by_category(self, client: TestClient, db: Session):
        """Filter items by category_id"""
        cat1 = MenuCategory(name="Category 1", branch_id=None, created_by=1)
        cat2 = MenuCategory(name="Category 2", branch_id=None, created_by=1)
        db.add_all([cat1, cat2])
        db.flush()

        item1 = MenuItem(category_id=cat1.id, name="Item 1", price=Decimal("10.00"), branch_id=None, created_by=1)
        item2 = MenuItem(category_id=cat2.id, name="Item 2", price=Decimal("20.00"), branch_id=None, created_by=1)
        db.add_all([item1, item2])
        db.commit()

        response = client.get(f"/api/v1/menu-items?category_id={cat1.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Item 1"

    def test_get_menu_items_ordered_by_display_order(self, client: TestClient, db: Session):
        """Items should be ordered by display_order"""
        category = MenuCategory(name="Test", branch_id=None, created_by=1)
        db.add(category)
        db.flush()

        item1 = MenuItem(category_id=category.id, name="Third", display_order=3, price=Decimal("10.00"), branch_id=None, created_by=1)
        item2 = MenuItem(category_id=category.id, name="First", display_order=1, price=Decimal("10.00"), branch_id=None, created_by=1)
        item3 = MenuItem(category_id=category.id, name="Second", display_order=2, price=Decimal("10.00"), branch_id=None, created_by=1)
        db.add_all([item1, item2, item3])
        db.commit()

        response = client.get("/api/v1/menu-items")

        assert response.status_code == 200
        data = response.json()
        names = [item["name"] for item in data]
        assert names == ["First", "Second", "Third"]

    # ==================== POST Tests ====================

    def test_create_menu_item_branch_specific(self, client: TestClient, db: Session):
        """POST creates a branch-specific item by default"""
        category = MenuCategory(name="Test Category", branch_id=1, created_by=1)
        db.add(category)
        db.commit()
        db.refresh(category)

        payload = {
            "category_id": category.id,
            "name": "Yeni Ürün",
            "description": "Lezzetli bir ürün",
            "price": "55.00",
            "display_order": 1,
            "is_global": False
        }

        response = client.post("/api/v1/menu-items", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Yeni Ürün"
        assert data["description"] == "Lezzetli bir ürün"
        assert data["price"] == "55.00"
        assert data["branch_id"] == 1
        assert data["is_active"] is True
        assert data["is_available"] is True

    def test_create_menu_item_global(self, client: TestClient, db: Session):
        """POST with is_global=True creates global item (branch_id=NULL)"""
        category = MenuCategory(name="Global Category", branch_id=None, created_by=1)
        db.add(category)
        db.commit()
        db.refresh(category)

        payload = {
            "category_id": category.id,
            "name": "Global Ürün",
            "price": "40.00",
            "is_global": True
        }

        response = client.post("/api/v1/menu-items", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Global Ürün"
        assert data["branch_id"] is None

    def test_create_menu_item_invalid_category(self, client: TestClient, db: Session):
        """POST with non-existent category fails"""
        payload = {
            "category_id": 99999,
            "name": "Invalid Category Item",
            "price": "30.00"
        }

        response = client.post("/api/v1/menu-items", json=payload)

        assert response.status_code == 404
        assert "kategori" in response.json()["detail"].lower()

    def test_create_menu_item_duplicate_name_same_category_fails(self, client: TestClient, db: Session):
        """Cannot create duplicate item name in same category and branch"""
        category = MenuCategory(name="Test", branch_id=1, created_by=1)
        db.add(category)
        db.flush()

        existing = MenuItem(
            category_id=category.id,
            name="Existing Item",
            price=Decimal("25.00"),
            branch_id=1,
            created_by=1
        )
        db.add(existing)
        db.commit()

        payload = {
            "category_id": category.id,
            "name": "Existing Item",
            "price": "30.00"
        }

        response = client.post("/api/v1/menu-items", json=payload)

        assert response.status_code == 400
        assert "zaten mevcut" in response.json()["detail"].lower()

    # ==================== PUT Tests ====================

    def test_update_menu_item_success(self, client: TestClient, db: Session):
        """PUT updates item fields"""
        category = MenuCategory(name="Test", branch_id=1, created_by=1)
        db.add(category)
        db.flush()

        item = MenuItem(
            category_id=category.id,
            name="Original Name",
            price=Decimal("30.00"),
            branch_id=1,
            created_by=1
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        payload = {
            "name": "Updated Name",
            "price": "45.00"
        }

        response = client.put(f"/api/v1/menu-items/{item.id}", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["price"] == "45.00"

    def test_update_menu_item_not_found(self, client: TestClient, db: Session):
        """PUT returns 404 for non-existent item"""
        payload = {"name": "Whatever"}
        response = client.put("/api/v1/menu-items/99999", json=payload)

        assert response.status_code == 404

    def test_update_menu_item_other_branch_forbidden(self, client: TestClient, db: Session):
        """PUT returns 404 for item from another branch (tenant isolation)"""
        other_branch = Branch(name="Other", code="OTH", city="Izmir", is_active=True)
        db.add(other_branch)
        db.flush()

        category = MenuCategory(name="Other Cat", branch_id=other_branch.id, created_by=1)
        db.add(category)
        db.flush()

        item = MenuItem(
            category_id=category.id,
            name="Other Branch Item",
            price=Decimal("20.00"),
            branch_id=other_branch.id,
            created_by=1
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        payload = {"name": "Hacked"}
        response = client.put(f"/api/v1/menu-items/{item.id}", json=payload)

        assert response.status_code == 404

    def test_update_menu_item_toggle_availability(self, client: TestClient, db: Session):
        """PUT can toggle is_available status"""
        category = MenuCategory(name="Test", branch_id=1, created_by=1)
        db.add(category)
        db.flush()

        item = MenuItem(
            category_id=category.id,
            name="Available Item",
            price=Decimal("30.00"),
            branch_id=1,
            is_available=True,
            created_by=1
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        payload = {"is_available": False}
        response = client.put(f"/api/v1/menu-items/{item.id}", json=payload)

        assert response.status_code == 200
        assert response.json()["is_available"] is False

    # ==================== DELETE Tests ====================

    def test_delete_menu_item_success(self, client: TestClient, db: Session):
        """DELETE removes item"""
        category = MenuCategory(name="Test", branch_id=1, created_by=1)
        db.add(category)
        db.flush()

        item = MenuItem(
            category_id=category.id,
            name="To Delete",
            price=Decimal("20.00"),
            branch_id=1,
            created_by=1
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        item_id = item.id

        response = client.delete(f"/api/v1/menu-items/{item_id}")

        assert response.status_code == 204

        # Verify deleted
        deleted = db.query(MenuItem).filter(MenuItem.id == item_id).first()
        assert deleted is None

    def test_delete_menu_item_not_found(self, client: TestClient, db: Session):
        """DELETE returns 404 for non-existent item"""
        response = client.delete("/api/v1/menu-items/99999")

        assert response.status_code == 404

    def test_delete_menu_item_other_branch_forbidden(self, client: TestClient, db: Session):
        """DELETE returns 404 for item from another branch (tenant isolation)"""
        other_branch = Branch(name="Delete Test", code="DEL", city="Bursa", is_active=True)
        db.add(other_branch)
        db.flush()

        category = MenuCategory(name="Del Cat", branch_id=other_branch.id, created_by=1)
        db.add(category)
        db.flush()

        item = MenuItem(
            category_id=category.id,
            name="Other Branch Delete",
            price=Decimal("15.00"),
            branch_id=other_branch.id,
            created_by=1
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        response = client.delete(f"/api/v1/menu-items/{item.id}")

        assert response.status_code == 404

        # Verify NOT deleted
        still_exists = db.query(MenuItem).filter(MenuItem.id == item.id).first()
        assert still_exists is not None

    # ==================== GET Single Item Tests ====================

    def test_get_single_menu_item_success(self, client: TestClient, db: Session):
        """GET /{id} returns single item"""
        category = MenuCategory(name="Test", branch_id=1, created_by=1)
        db.add(category)
        db.flush()

        item = MenuItem(
            category_id=category.id,
            name="Single Item",
            price=Decimal("35.00"),
            branch_id=1,
            created_by=1
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        response = client.get(f"/api/v1/menu-items/{item.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Single Item"
        assert data["price"] == "35.00"

    def test_get_single_menu_item_not_found(self, client: TestClient, db: Session):
        """GET /{id} returns 404 for non-existent item"""
        response = client.get("/api/v1/menu-items/99999")

        assert response.status_code == 404
