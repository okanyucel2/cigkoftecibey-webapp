"""add cash_diff analytics composite index

Revision ID: n5o6p7q8r013
Revises: m4n5o6p7q012
Create Date: 2026-01-09 18:00:00.000000

This migration adds a composite index on (branch_id, difference_date) to optimize
analytics queries that filter by tenant and aggregate by date.

Query pattern optimized:
    SELECT ... FROM cash_differences
    WHERE branch_id = :branch_id
      AND difference_date BETWEEN :start_date AND :end_date
    GROUP BY difference_date
    ORDER BY difference_date
"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'n5o6p7q8r013'
down_revision: Union[str, None] = 'm4n5o6p7q012'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Composite index for analytics queries
    # Column order: branch_id (equality) then difference_date (range/order)
    op.create_index(
        'idx_cash_diff_tenant_date',
        'cash_differences',
        ['branch_id', 'difference_date'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('idx_cash_diff_tenant_date', table_name='cash_differences')
