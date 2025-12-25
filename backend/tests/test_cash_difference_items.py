# backend/tests/test_cash_difference_items.py
import pytest
from decimal import Decimal
from app.models import CashDifference, CashDifferenceItem, OnlinePlatform


def test_cash_difference_item_model(db):
    """CashDifferenceItem should store platform-specific amounts"""
    # Create platform
    platform = OnlinePlatform(name="Visa", channel_type="pos_visa", is_system=True)
    db.add(platform)
    db.commit()

    # Create cash difference
    from datetime import date
    cd = CashDifference(
        branch_id=1,
        difference_date=date.today(),
        created_by=1
    )
    db.add(cd)
    db.commit()

    # Create item
    item = CashDifferenceItem(
        cash_difference_id=cd.id,
        platform_id=platform.id,
        source_type="kasa",
        amount=Decimal("1000.00")
    )
    db.add(item)
    db.commit()

    # Query back
    result = db.query(CashDifferenceItem).filter_by(cash_difference_id=cd.id).first()
    assert result is not None
    assert result.amount == Decimal("1000.00")
    assert result.source_type == "kasa"
    assert result.platform.name == "Visa"


def test_cash_difference_items_relationship(db):
    """CashDifference should have items relationship"""
    from datetime import date

    # Create platforms
    visa = OnlinePlatform(name="Visa", channel_type="pos_visa", is_system=True)
    nakit = OnlinePlatform(name="Nakit", channel_type="pos_nakit", is_system=True)
    db.add_all([visa, nakit])
    db.commit()

    # Create cash difference with items
    cd = CashDifference(
        branch_id=1,
        difference_date=date.today(),
        created_by=1
    )
    db.add(cd)
    db.commit()

    # Add items
    items = [
        CashDifferenceItem(cash_difference_id=cd.id, platform_id=visa.id, source_type="kasa", amount=Decimal("5000")),
        CashDifferenceItem(cash_difference_id=cd.id, platform_id=visa.id, source_type="pos", amount=Decimal("5100")),
        CashDifferenceItem(cash_difference_id=cd.id, platform_id=nakit.id, source_type="kasa", amount=Decimal("3000")),
        CashDifferenceItem(cash_difference_id=cd.id, platform_id=nakit.id, source_type="pos", amount=Decimal("2900")),
    ]
    db.add_all(items)
    db.commit()

    # Query through relationship
    db.refresh(cd)
    assert len(cd.items) == 4
