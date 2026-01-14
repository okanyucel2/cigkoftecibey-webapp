"""
Tests for /api/reports/dashboard/comparison endpoint.

This endpoint returns sales and expense comparison data for trend badges.
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.models import (
    OnlinePlatform, OnlineSale, Purchase, Expense,
    CourierExpense, PartTimeCost, StaffMeal, Supplier, ExpenseCategory
)


class TestDashboardComparison:
    """Test suite for dashboard comparison endpoint."""

    def test_comparison_endpoint_returns_correct_structure(self, client: TestClient, db: Session):
        """Test that endpoint returns the expected response structure."""
        response = client.get("/api/reports/dashboard/comparison")

        assert response.status_code == 200
        data = response.json()

        # Check top-level fields
        assert "current_date" in data
        assert "compare_date" in data
        assert "sales" in data
        assert "expenses" in data

        # Check sales metric structure
        assert "current" in data["sales"]
        assert "previous" in data["sales"]
        assert "diff" in data["sales"]
        assert "diff_percent" in data["sales"]

        # Check expenses metric structure
        assert "current" in data["expenses"]
        assert "previous" in data["expenses"]
        assert "diff" in data["expenses"]
        assert "diff_percent" in data["expenses"]

    def test_comparison_with_no_data_returns_zeros(self, client: TestClient, db: Session):
        """Test that endpoint returns zeros when no sales/expenses exist."""
        response = client.get("/api/reports/dashboard/comparison")

        assert response.status_code == 200
        data = response.json()

        # With no data, all values should be 0
        assert data["sales"]["current"] == 0
        assert data["sales"]["previous"] == 0
        assert data["sales"]["diff"] == 0
        assert data["sales"]["diff_percent"] == 0

        assert data["expenses"]["current"] == 0
        assert data["expenses"]["previous"] == 0
        assert data["expenses"]["diff"] == 0
        assert data["expenses"]["diff_percent"] == 0

    def test_comparison_with_sales_data(self, client: TestClient, db: Session):
        """Test that endpoint correctly calculates sales comparison."""
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Create a platform for sales
        platform = OnlinePlatform(
            id=1,
            branch_id=1,
            name="Test Platform",
            channel_type="online",
            is_system=False,
            is_active=True
        )
        db.add(platform)
        db.commit()

        # Add today's sales: 1000
        today_sale = OnlineSale(
            branch_id=1,
            platform_id=1,
            sale_date=today,
            amount=Decimal("1000.00"),
            created_by=1
        )
        db.add(today_sale)

        # Add yesterday's sales: 800
        yesterday_sale = OnlineSale(
            branch_id=1,
            platform_id=1,
            sale_date=yesterday,
            amount=Decimal("800.00"),
            created_by=1
        )
        db.add(yesterday_sale)
        db.commit()

        response = client.get("/api/reports/dashboard/comparison")

        assert response.status_code == 200
        data = response.json()

        # Verify sales calculation
        assert data["sales"]["current"] == 1000.0
        assert data["sales"]["previous"] == 800.0
        assert data["sales"]["diff"] == 200.0
        assert data["sales"]["diff_percent"] == 25.0  # (200/800) * 100

    def test_comparison_compare_to_yesterday(self, client: TestClient, db: Session):
        """Test compare_to=yesterday parameter (default)."""
        response = client.get("/api/reports/dashboard/comparison?compare_to=yesterday")

        assert response.status_code == 200
        data = response.json()

        today = date.today()
        yesterday = today - timedelta(days=1)

        assert data["current_date"] == today.isoformat()
        assert data["compare_date"] == yesterday.isoformat()

    def test_comparison_compare_to_last_week(self, client: TestClient, db: Session):
        """Test compare_to=last_week parameter."""
        response = client.get("/api/reports/dashboard/comparison?compare_to=last_week")

        assert response.status_code == 200
        data = response.json()

        today = date.today()
        last_week = today - timedelta(days=7)

        assert data["current_date"] == today.isoformat()
        assert data["compare_date"] == last_week.isoformat()

    def test_comparison_compare_to_last_month(self, client: TestClient, db: Session):
        """Test compare_to=last_month parameter."""
        response = client.get("/api/reports/dashboard/comparison?compare_to=last_month")

        assert response.status_code == 200
        data = response.json()

        today = date.today()
        last_month = today - timedelta(days=30)

        assert data["current_date"] == today.isoformat()
        assert data["compare_date"] == last_month.isoformat()

    def test_comparison_invalid_compare_to_returns_400(self, client: TestClient, db: Session):
        """Test that invalid compare_to value returns 400 error."""
        response = client.get("/api/reports/dashboard/comparison?compare_to=invalid")

        assert response.status_code == 400
        assert "Invalid compare_to value" in response.json()["detail"]

    def test_comparison_invalid_date_format_returns_400(self, client: TestClient, db: Session):
        """Test that invalid target_date format returns 400 error."""
        response = client.get("/api/reports/dashboard/comparison?target_date=not-a-date")

        assert response.status_code == 400
        assert "Invalid date format" in response.json()["detail"]

    def test_comparison_with_expenses_data(self, client: TestClient, db: Session):
        """Test that endpoint correctly calculates expense comparison."""
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Create expense category
        category = ExpenseCategory(
            id=1,
            name="Test Category",
            is_fixed=False,
            display_order=1
        )
        db.add(category)

        # Create supplier for purchases
        supplier = Supplier(
            id=1,
            branch_id=1,
            name="Test Supplier",
            is_active=True
        )
        db.add(supplier)
        db.commit()

        # Add today's expenses: 500 (purchase) + 200 (expense) = 700
        today_purchase = Purchase(
            branch_id=1,
            supplier_id=1,
            purchase_date=today,
            total=Decimal("500.00"),
            created_by=1
        )
        db.add(today_purchase)

        today_expense = Expense(
            branch_id=1,
            category_id=1,
            expense_date=today,
            amount=Decimal("200.00"),
            created_by=1
        )
        db.add(today_expense)

        # Add yesterday's expenses: 300 (purchase) + 100 (expense) = 400
        yesterday_purchase = Purchase(
            branch_id=1,
            supplier_id=1,
            purchase_date=yesterday,
            total=Decimal("300.00"),
            created_by=1
        )
        db.add(yesterday_purchase)

        yesterday_expense = Expense(
            branch_id=1,
            category_id=1,
            expense_date=yesterday,
            amount=Decimal("100.00"),
            created_by=1
        )
        db.add(yesterday_expense)
        db.commit()

        response = client.get("/api/reports/dashboard/comparison")

        assert response.status_code == 200
        data = response.json()

        # Verify expenses calculation
        assert data["expenses"]["current"] == 700.0
        assert data["expenses"]["previous"] == 400.0
        assert data["expenses"]["diff"] == 300.0
        assert data["expenses"]["diff_percent"] == 75.0  # (300/400) * 100

    def test_comparison_all_expense_types(self, client: TestClient, db: Session):
        """Test that all expense types are included in calculation."""
        today = date.today()

        # Create required related entities
        category = ExpenseCategory(id=1, name="Test", is_fixed=False, display_order=1)
        supplier = Supplier(id=1, branch_id=1, name="Test", is_active=True)
        db.add(category)
        db.add(supplier)
        db.commit()

        # Add all expense types for today
        purchase = Purchase(branch_id=1, supplier_id=1, purchase_date=today, total=Decimal("100"), created_by=1)
        expense = Expense(branch_id=1, category_id=1, expense_date=today, amount=Decimal("50"), created_by=1)
        courier = CourierExpense(branch_id=1, expense_date=today, package_count=10, amount=Decimal("80"), vat_rate=10, created_by=1)
        parttime = PartTimeCost(branch_id=1, cost_date=today, amount=Decimal("200"), created_by=1)
        # StaffMeal.total is computed property (unit_price * staff_count), not a settable field
        staff_meal = StaffMeal(branch_id=1, meal_date=today, unit_price=Decimal("30"), staff_count=5, created_by=1)

        db.add_all([purchase, expense, courier, parttime, staff_meal])
        db.commit()

        response = client.get("/api/reports/dashboard/comparison")

        assert response.status_code == 200
        data = response.json()

        # Total should be: 100 + 50 + 88 (80 + 8 VAT) + 200 + 150 (30*5) = 588
        expected_total = 100 + 50 + 88 + 200 + 150
        assert data["expenses"]["current"] == expected_total
