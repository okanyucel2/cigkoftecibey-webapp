"""
Tests for /api/v1/menu-items endpoint

TDD: Written BEFORE implementation per P0.40
Feature: Menu Items with branch-specific pricing
"""
import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Branch, MenuCategory


class TestMenuItemsEndpoint:
    """Test Menu Items CRUD operations"""

    @pytest.fixture(autouse=True)
    def setup_category(self, db: Session):
        """Create a menu category for testing"""
        cat = MenuCategory(
            name="Test Category",
            branch_id=None,  # Global
            created_by=1
        )
        db.add(cat)
        db.commit()
        db.refresh(cat)
        self.category_id = cat.id

    # ==================== GET List Tests ====================

    def test_get_menu_items_returns_empty_list(self, client: TestClient, db: Session):
        """GET /api/v1/menu-items returns empty list when no items exist"""
        response = client.get("/api/v1/menu-items")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_menu_items_returns_items_with_default_price(self, client: TestClient, db: Session):
        """Items with default price (branch_id=NULL) are returned"""
        from app.models import MenuItem, MenuItemPrice

        item = MenuItem(
            name="Cig Kofte Durum",
            category_id=self.category_id,
            created_by=1
        )
        db.add(item)
        db.flush()

        # Default price (branch_id=NULL)
        price = MenuItemPrice(
            menu_item_id=item.id,
            branch_id=None,
            price=Decimal("85.00")
        )
        db.add(price)
        db.commit()

        response = client.get("/api/v1/menu-items")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Cig Kofte Durum"
        assert float(data[0]["price"]) == 85.00
        assert data[0]["price_is_default"] is True

    def test_get_menu_items_returns_branch_specific_price(self, client: TestClient, db: Session):
        """Branch-specific price overrides default price"""
        from app.models import MenuItem, MenuItemPrice

        item = MenuItem(
            name="Ayran",
            category_id=self.category_id,
            created_by=1
        )
        db.add(item)
        db.flush()

        # Default price
        default_price = MenuItemPrice(
            menu_item_id=item.id,
            branch_id=None,
            price=Decimal("15.00")
        )
        # Branch-specific price for branch 1 (test branch)
        branch_price = MenuItemPrice(
            menu_item_id=item.id,
            branch_id=1,
            price=Decimal("18.00")
        )
        db.add_all([default_price, branch_price])
        db.commit()

        response = client.get("/api/v1/menu-items")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert float(data[0]["price"]) == 18.00  # Branch price, not default
        assert data[0]["price_is_default"] is False

    def test_get_menu_items_filters_by_category(self, client: TestClient, db: Session):
        """Filter items by category_id query param"""
        from app.models import MenuItem, MenuItemPrice

        # Create second category
        cat2 = MenuCategory(name="Icecekler", branch_id=None, created_by=1)
        db.add(cat2)
        db.flush()

        item1 = MenuItem(name="Durum", category_id=self.category_id, created_by=1)
        item2 = MenuItem(name="Ayran", category_id=cat2.id, created_by=1)
        db.add_all([item1, item2])
        db.commit()

        response = client.get(f"/api/v1/menu-items?category_id={self.category_id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Durum"

    def test_get_menu_items_ordered_by_display_order(self, client: TestClient, db: Session):
        """Items ordered by display_order"""
        from app.models import MenuItem

        item1 = MenuItem(name="Third", category_id=self.category_id, display_order=3, created_by=1)
        item2 = MenuItem(name="First", category_id=self.category_id, display_order=1, created_by=1)
        item3 = MenuItem(name="Second", category_id=self.category_id, display_order=2, created_by=1)
        db.add_all([item1, item2, item3])
        db.commit()

        response = client.get("/api/v1/menu-items")

        assert response.status_code == 200
        names = [item["name"] for item in response.json()]
        assert names == ["First", "Second", "Third"]

    def test_get_menu_items_excludes_inactive(self, client: TestClient, db: Session):
        """Inactive items not returned by default"""
        from app.models import MenuItem

        active = MenuItem(name="Active", category_id=self.category_id, is_active=True, created_by=1)
        inactive = MenuItem(name="Inactive", category_id=self.category_id, is_active=False, created_by=1)
        db.add_all([active, inactive])
        db.commit()

        response = client.get("/api/v1/menu-items")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Active"

    # ==================== GET Single Tests ====================

    def test_get_menu_item_by_id(self, client: TestClient, db: Session):
        """GET /api/v1/menu-items/{id} returns single item"""
        from app.models import MenuItem, MenuItemPrice

        item = MenuItem(
            name="Soslu Durum",
            description="Bol soslu",
            category_id=self.category_id,
            image_url="/images/soslu.jpg",
            created_by=1
        )
        db.add(item)
        db.flush()

        price = MenuItemPrice(menu_item_id=item.id, branch_id=None, price=Decimal("95.00"))
        db.add(price)
        db.commit()

        response = client.get(f"/api/v1/menu-items/{item.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Soslu Durum"
        assert data["description"] == "Bol soslu"
        assert data["image_url"] == "/images/soslu.jpg"
        assert float(data["price"]) == 95.00

    def test_get_menu_item_not_found(self, client: TestClient, db: Session):
        """GET returns 404 for non-existent item"""
        response = client.get("/api/v1/menu-items/99999")

        assert response.status_code == 404

    # ==================== POST Tests ====================

    def test_create_menu_item_success(self, client: TestClient, db: Session):
        """POST creates a new menu item"""
        payload = {
            "name": "Lavas Durum",
            "description": "Lavas ekmekli",
            "category_id": self.category_id,
            "image_url": "/images/lavas.jpg",
            "display_order": 1,
            "default_price": 90.00
        }

        response = client.post("/api/v1/menu-items", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Lavas Durum"
        assert data["description"] == "Lavas ekmekli"
        assert data["category_id"] == self.category_id
        assert float(data["price"]) == 90.00
        assert data["price_is_default"] is True

    def test_create_menu_item_minimal(self, client: TestClient, db: Session):
        """POST with only required fields"""
        payload = {
            "name": "Minimal Item",
            "category_id": self.category_id
        }

        response = client.post("/api/v1/menu-items", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Item"
        assert data["price"] is None  # No price set

    def test_create_menu_item_invalid_category(self, client: TestClient, db: Session):
        """POST fails with non-existent category"""
        payload = {
            "name": "Bad Category",
            "category_id": 99999
        }

        response = client.post("/api/v1/menu-items", json=payload)

        assert response.status_code == 400
        assert "kategori" in response.json()["detail"].lower()

    def test_create_menu_item_duplicate_name_same_category(self, client: TestClient, db: Session):
        """POST fails with duplicate name in same category"""
        from app.models import MenuItem

        existing = MenuItem(name="Duplicate", category_id=self.category_id, created_by=1)
        db.add(existing)
        db.commit()

        payload = {
            "name": "Duplicate",
            "category_id": self.category_id
        }

        response = client.post("/api/v1/menu-items", json=payload)

        assert response.status_code == 400
        assert "zaten mevcut" in response.json()["detail"].lower()

    # ==================== PUT Tests ====================

    def test_update_menu_item_success(self, client: TestClient, db: Session):
        """PUT updates menu item"""
        from app.models import MenuItem

        item = MenuItem(name="Original", category_id=self.category_id, created_by=1)
        db.add(item)
        db.commit()
        db.refresh(item)

        payload = {"name": "Updated", "description": "New description"}
        response = client.put(f"/api/v1/menu-items/{item.id}", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated"
        assert data["description"] == "New description"

    def test_update_menu_item_not_found(self, client: TestClient, db: Session):
        """PUT returns 404 for non-existent item"""
        response = client.put("/api/v1/menu-items/99999", json={"name": "Whatever"})

        assert response.status_code == 404

    def test_update_menu_item_partial(self, client: TestClient, db: Session):
        """PUT with partial payload only updates provided fields"""
        from app.models import MenuItem

        item = MenuItem(
            name="Keep This",
            description="Keep This Too",
            category_id=self.category_id,
            created_by=1
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        payload = {"description": "Only Update This"}
        response = client.put(f"/api/v1/menu-items/{item.id}", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Keep This"  # Unchanged
        assert data["description"] == "Only Update This"

    # ==================== DELETE Tests ====================

    def test_delete_menu_item_success(self, client: TestClient, db: Session):
        """DELETE removes menu item and its prices"""
        from app.models import MenuItem, MenuItemPrice

        item = MenuItem(name="To Delete", category_id=self.category_id, created_by=1)
        db.add(item)
        db.flush()

        price = MenuItemPrice(menu_item_id=item.id, branch_id=None, price=Decimal("50.00"))
        db.add(price)
        db.commit()
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


class TestMenuItemPricesEndpoint:
    """Test Menu Item Prices management"""

    @pytest.fixture(autouse=True)
    def setup_item(self, db: Session):
        """Create category and menu item for testing"""
        from app.models import MenuItem

        cat = MenuCategory(name="Price Test Category", branch_id=None, created_by=1)
        db.add(cat)
        db.flush()

        item = MenuItem(name="Price Test Item", category_id=cat.id, created_by=1)
        db.add(item)
        db.commit()
        db.refresh(item)
        self.item_id = item.id
        self.category_id = cat.id

    # ==================== GET Prices Tests ====================

    def test_get_prices_returns_all_prices(self, client: TestClient, db: Session):
        """GET /api/v1/menu-items/{id}/prices returns all prices"""
        from app.models import MenuItemPrice

        default_price = MenuItemPrice(menu_item_id=self.item_id, branch_id=None, price=Decimal("50.00"))
        branch_price = MenuItemPrice(menu_item_id=self.item_id, branch_id=1, price=Decimal("55.00"))
        db.add_all([default_price, branch_price])
        db.commit()

        response = client.get(f"/api/v1/menu-items/{self.item_id}/prices")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_prices_item_not_found(self, client: TestClient, db: Session):
        """GET prices returns 404 for non-existent item"""
        response = client.get("/api/v1/menu-items/99999/prices")

        assert response.status_code == 404

    # ==================== PUT Price Tests ====================

    def test_set_default_price(self, client: TestClient, db: Session):
        """PUT sets default price (branch_id=null)"""
        payload = {"price": 75.00}

        response = client.put(f"/api/v1/menu-items/{self.item_id}/prices", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert float(data["price"]) == 75.00
        assert data["branch_id"] is None

    def test_set_branch_specific_price(self, client: TestClient, db: Session):
        """PUT sets branch-specific price"""
        payload = {"price": 80.00, "branch_id": 1}

        response = client.put(f"/api/v1/menu-items/{self.item_id}/prices", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert float(data["price"]) == 80.00
        assert data["branch_id"] == 1

    def test_update_existing_price(self, client: TestClient, db: Session):
        """PUT updates existing price instead of creating duplicate"""
        from app.models import MenuItemPrice

        existing = MenuItemPrice(menu_item_id=self.item_id, branch_id=None, price=Decimal("50.00"))
        db.add(existing)
        db.commit()

        payload = {"price": 60.00}  # Update default price
        response = client.put(f"/api/v1/menu-items/{self.item_id}/prices", json=payload)

        assert response.status_code == 200
        assert float(response.json()["price"]) == 60.00

        # Verify only one price exists
        prices = db.query(MenuItemPrice).filter(
            MenuItemPrice.menu_item_id == self.item_id,
            MenuItemPrice.branch_id == None
        ).all()
        assert len(prices) == 1

    def test_set_price_item_not_found(self, client: TestClient, db: Session):
        """PUT price returns 404 for non-existent item"""
        response = client.put("/api/v1/menu-items/99999/prices", json={"price": 50.00})

        assert response.status_code == 404

    # ==================== DELETE Price Tests ====================

    def test_delete_branch_price(self, client: TestClient, db: Session):
        """DELETE removes branch-specific price override"""
        from app.models import MenuItemPrice

        branch_price = MenuItemPrice(menu_item_id=self.item_id, branch_id=1, price=Decimal("60.00"))
        db.add(branch_price)
        db.commit()

        response = client.delete(f"/api/v1/menu-items/{self.item_id}/prices/1")

        assert response.status_code == 204

        # Verify deleted
        deleted = db.query(MenuItemPrice).filter(
            MenuItemPrice.menu_item_id == self.item_id,
            MenuItemPrice.branch_id == 1
        ).first()
        assert deleted is None

    def test_delete_default_price(self, client: TestClient, db: Session):
        """DELETE default price uses branch_id=0 convention"""
        from app.models import MenuItemPrice

        default_price = MenuItemPrice(menu_item_id=self.item_id, branch_id=None, price=Decimal("50.00"))
        db.add(default_price)
        db.commit()

        # Use 0 to indicate default price deletion
        response = client.delete(f"/api/v1/menu-items/{self.item_id}/prices/0")

        assert response.status_code == 204

    def test_delete_price_not_found(self, client: TestClient, db: Session):
        """DELETE returns 404 for non-existent price"""
        response = client.delete(f"/api/v1/menu-items/{self.item_id}/prices/999")

        assert response.status_code == 404
