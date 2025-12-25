"""
Test cash difference import history tracking
"""
import pytest
from datetime import date
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import get_db, SessionLocal
from app.models import (
    User, Branch, CashDifference, Expense, ExpenseCategory,
    OnlineSale, OnlinePlatform, ImportHistory, ImportHistoryItem
)
from app.api.deps import get_current_user, get_branch_context
from app.schemas import CashDifferenceImportRequest, ExpenseItem


@pytest.fixture
def db():
    """Get a database session for tests"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_branch(db: Session):
    """Create a test branch"""
    branch = Branch(
        name="Test Branch History",
        code="TEST_HIST_001",
        city="Istanbul"
    )
    db.add(branch)
    db.commit()
    db.refresh(branch)
    yield branch
    # Cleanup
    db.delete(branch)
    db.commit()


@pytest.fixture
def test_user(db: Session, test_branch):
    """Create a test user"""
    user = User(
        email="history_test@example.com",
        name="History Test User",
        branch_id=test_branch.id,
        password_hash="fake_hash"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    # Cleanup
    db.delete(user)
    db.commit()


@pytest.fixture
def uncategorized_category(db: Session):
    """Create uncategorized expense category"""
    category = db.query(ExpenseCategory).filter(
        ExpenseCategory.name == "Kategorize Edilmemis"
    ).first()

    if not category:
        category = ExpenseCategory(
            name="Kategorize Edilmemis",
            is_system=True
        )
        db.add(category)
        db.commit()
        db.refresh(category)

    return category


@pytest.fixture
def online_platforms(db: Session):
    """Ensure online platforms exist"""
    platforms = {
        'Visa': 'pos_visa',
        'Nakit': 'pos_nakit',
        'Trendyol': 'online',
        'Getir': 'online',
        'Yemek Sepeti': 'online',
        'Migros Yemek': 'online'
    }

    created_platforms = []
    for name, channel_type in platforms.items():
        platform = db.query(OnlinePlatform).filter(
            OnlinePlatform.name == name
        ).first()

        if not platform:
            platform = OnlinePlatform(
                name=name,
                channel_type=channel_type,
                is_system=(channel_type.startswith('pos_'))
            )
            db.add(platform)

        created_platforms.append(platform)

    db.commit()
    return created_platforms


@pytest.fixture
def client(test_user, test_branch):
    """Create test client with auth mocked"""

    def override_get_current_user():
        return test_user

    def override_get_branch_context():
        from app.api.deps import BranchContext
        return BranchContext(
            user=test_user,
            current_branch_id=test_branch.id,
            current_branch=test_branch,
            accessible_branches=[test_branch],
            is_super_admin=False
        )

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_branch_context] = override_get_branch_context

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()


def test_cash_difference_import_creates_history_record(
    client, db, test_branch, test_user, uncategorized_category, online_platforms
):
    """Test that importing cash difference creates ImportHistory record"""

    # Prepare import request
    import_date = date(2024, 12, 25)
    request_data = {
        "difference_date": str(import_date),
        "kasa_visa": 1000.0,
        "kasa_nakit": 500.0,
        "kasa_trendyol": 300.0,
        "kasa_getir": 200.0,
        "kasa_yemeksepeti": 150.0,
        "kasa_migros": 100.0,
        "kasa_total": 2250.0,
        "pos_visa": 1100.0,
        "pos_nakit": 450.0,
        "pos_trendyol": 320.0,
        "pos_getir": 180.0,
        "pos_yemeksepeti": 160.0,
        "pos_migros": 90.0,
        "pos_total": 2300.0,
        "ocr_confidence_score": 0.95,
        "expenses": [
            {"description": "Test expense 1", "amount": 100.0},
            {"description": "Test expense 2", "amount": 50.0}
        ]
    }

    # Make the import request
    response = client.post(
        "/api/cash-difference/import?import_expenses=true&sync_to_sales=true",
        json=request_data
    )

    assert response.status_code == 200
    cash_diff_data = response.json()
    cash_diff_id = cash_diff_data["id"]

    # Verify ImportHistory record was created
    history = db.query(ImportHistory).filter(
        ImportHistory.branch_id == test_branch.id,
        ImportHistory.import_type == "kasa_raporu",
        ImportHistory.import_date == import_date
    ).first()

    assert history is not None
    assert history.status == "completed"
    assert history.created_by == test_user.id
    assert history.import_metadata is not None
    assert history.import_metadata["kasa_total"] == 2250.0
    assert history.import_metadata["pos_total"] == 2300.0
    assert history.import_metadata["diff_total"] == 50.0
    assert history.import_metadata["ocr_confidence"] == 0.95

    # Verify ImportHistoryItem for cash_difference was created
    cash_diff_item = db.query(ImportHistoryItem).filter(
        ImportHistoryItem.import_history_id == history.id,
        ImportHistoryItem.entity_type == "cash_difference",
        ImportHistoryItem.entity_id == cash_diff_id
    ).first()

    assert cash_diff_item is not None
    assert cash_diff_item.action == "created"
    assert cash_diff_item.data["difference_date"] == str(import_date)

    # Verify ImportHistoryItems for expenses were created
    expense_items = db.query(ImportHistoryItem).filter(
        ImportHistoryItem.import_history_id == history.id,
        ImportHistoryItem.entity_type == "expense"
    ).all()

    assert len(expense_items) == 2

    # Verify ImportHistoryItems for online_sales were created
    online_sale_items = db.query(ImportHistoryItem).filter(
        ImportHistoryItem.import_history_id == history.id,
        ImportHistoryItem.entity_type == "online_sale"
    ).all()

    # Should have items for each non-zero POS value
    assert len(online_sale_items) == 6  # All 6 platforms have non-zero values

    # Cleanup
    db.query(CashDifference).filter(CashDifference.id == cash_diff_id).delete()
    db.query(Expense).filter(
        Expense.branch_id == test_branch.id,
        Expense.expense_date == import_date
    ).delete()
    db.query(OnlineSale).filter(
        OnlineSale.branch_id == test_branch.id,
        OnlineSale.sale_date == import_date
    ).delete()
    db.query(ImportHistoryItem).filter(
        ImportHistoryItem.import_history_id == history.id
    ).delete()
    db.query(ImportHistory).filter(ImportHistory.id == history.id).delete()
    db.commit()


def test_cash_difference_import_without_expenses_still_tracks_history(
    client, db, test_branch, test_user, online_platforms
):
    """Test that import without expenses still creates history tracking"""

    import_date = date(2024, 12, 26)
    request_data = {
        "difference_date": str(import_date),
        "kasa_visa": 500.0,
        "kasa_nakit": 300.0,
        "kasa_trendyol": 0.0,
        "kasa_getir": 0.0,
        "kasa_yemeksepeti": 0.0,
        "kasa_migros": 0.0,
        "kasa_total": 800.0,
        "pos_visa": 550.0,
        "pos_nakit": 280.0,
        "pos_trendyol": 0.0,
        "pos_getir": 0.0,
        "pos_yemeksepeti": 0.0,
        "pos_migros": 0.0,
        "pos_total": 830.0,
        "ocr_confidence_score": None,
        "expenses": []
    }

    # Make the import request without importing expenses
    response = client.post(
        "/api/cash-difference/import?import_expenses=false&sync_to_sales=false",
        json=request_data
    )

    assert response.status_code == 200
    cash_diff_id = response.json()["id"]

    # Verify ImportHistory record was created
    history = db.query(ImportHistory).filter(
        ImportHistory.branch_id == test_branch.id,
        ImportHistory.import_type == "kasa_raporu",
        ImportHistory.import_date == import_date
    ).first()

    assert history is not None
    assert history.import_metadata["ocr_confidence"] is None

    # Verify only cash_difference item exists (no expenses or sales)
    items = db.query(ImportHistoryItem).filter(
        ImportHistoryItem.import_history_id == history.id
    ).all()

    assert len(items) == 1
    assert items[0].entity_type == "cash_difference"

    # Cleanup
    db.query(CashDifference).filter(CashDifference.id == cash_diff_id).delete()
    db.query(ImportHistoryItem).filter(
        ImportHistoryItem.import_history_id == history.id
    ).delete()
    db.query(ImportHistory).filter(ImportHistory.id == history.id).delete()
    db.commit()
