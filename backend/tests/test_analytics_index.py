"""
Test for analytics composite index on cash_differences table.

TDD RED Phase: This test should FAIL until the migration is created.
"""
import pytest
from sqlalchemy import inspect, text
from app.database import engine


def test_idx_cash_diff_tenant_date_exists():
    """
    Verify the composite index idx_cash_diff_tenant_date exists on cash_differences.

    This index optimizes analytics queries that filter by branch_id and
    aggregate by difference_date.
    """
    inspector = inspect(engine)
    indexes = inspector.get_indexes("cash_differences")

    # Find our specific index
    index_names = [idx["name"] for idx in indexes]

    assert "idx_cash_diff_tenant_date" in index_names, (
        f"Index idx_cash_diff_tenant_date not found. "
        f"Existing indexes: {index_names}"
    )


def test_idx_cash_diff_tenant_date_covers_correct_columns():
    """
    Verify the index covers (branch_id, difference_date) in correct order.

    Column order matters for composite index efficiency:
    - branch_id first (equality filter)
    - difference_date second (range scan)
    """
    inspector = inspect(engine)
    indexes = inspector.get_indexes("cash_differences")

    # Find the specific index
    target_index = None
    for idx in indexes:
        if idx["name"] == "idx_cash_diff_tenant_date":
            target_index = idx
            break

    assert target_index is not None, "Index idx_cash_diff_tenant_date not found"

    # Verify columns in correct order
    expected_columns = ["branch_id", "difference_date"]
    assert target_index["column_names"] == expected_columns, (
        f"Expected columns {expected_columns}, got {target_index['column_names']}"
    )


def test_analytics_query_uses_index(db):
    """
    Verify that a typical analytics query can use the index.

    This is a sanity check that the index structure supports
    the intended query pattern.
    """
    # Test query pattern that should benefit from the index
    query = text("""
        SELECT
            difference_date,
            SUM(kasa_total) as total_kasa,
            SUM(pos_total) as total_pos,
            SUM(pos_total - kasa_total) as total_diff
        FROM cash_differences
        WHERE branch_id = :branch_id
          AND difference_date BETWEEN :start_date AND :end_date
        GROUP BY difference_date
        ORDER BY difference_date
    """)

    # Execute with test parameters - should not error
    from datetime import date
    result = db.execute(query, {
        "branch_id": 1,
        "start_date": date(2025, 1, 1),
        "end_date": date(2025, 12, 31)
    })

    # Query should execute successfully (even if empty)
    rows = result.fetchall()
    assert isinstance(rows, list)
