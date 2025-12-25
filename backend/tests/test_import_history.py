"""Tests for ImportHistory model"""
import pytest
from datetime import date
from app.models import ImportHistory, ImportHistoryItem


def test_import_history_model(db):
    """ImportHistory should track imports with metadata"""
    history = ImportHistory(
        branch_id=1,
        import_type="kasa_raporu",
        import_date=date.today(),
        source_filename="1453.xlsx",
        status="completed",
        created_by=1
    )
    db.add(history)
    db.commit()

    result = db.query(ImportHistory).filter_by(branch_id=1).first()
    assert result is not None
    assert result.import_type == "kasa_raporu"
    assert result.status == "completed"


def test_import_history_items(db):
    """ImportHistory should have items for detailed tracking"""
    history = ImportHistory(
        branch_id=1,
        import_type="kasa_raporu",
        import_date=date.today(),
        source_filename="test.xlsx",
        status="completed",
        created_by=1
    )
    db.add(history)
    db.commit()

    item = ImportHistoryItem(
        import_history_id=history.id,
        entity_type="expense",
        entity_id=1,
        action="created",
        data={"amount": 100, "description": "Test expense"}
    )
    db.add(item)
    db.commit()

    db.refresh(history)
    assert len(history.items) == 1
    assert history.items[0].entity_type == "expense"
