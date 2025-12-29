"""Fix purchase item total precision from 12,2 to 14,5

Revision ID: dd496a1b855b
Revises: cafac70ad8c1
Create Date: 2025-12-29 21:27:36.639501

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dd496a1b855b'
down_revision: Union[str, None] = 'cafac70ad8c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Fix precision for purchase_items.total: Numeric(12,2) -> Numeric(14,5)
    op.execute("ALTER TABLE purchase_items ALTER COLUMN total TYPE NUMERIC(14, 5)")
    # Fix precision for purchases.total: Numeric(12,2) -> Numeric(14,5)
    op.execute("ALTER TABLE purchases ALTER COLUMN total TYPE NUMERIC(14, 5)")


def downgrade() -> None:
    # Revert to original precision
    op.execute("ALTER TABLE purchase_items ALTER COLUMN total TYPE NUMERIC(12, 2)")
    op.execute("ALTER TABLE purchases ALTER COLUMN total TYPE NUMERIC(12, 2)")
