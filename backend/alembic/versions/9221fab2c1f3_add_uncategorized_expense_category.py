"""add_uncategorized_expense_category

Revision ID: 9221fab2c1f3
Revises: c87f7da88f99
Create Date: 2025-12-23 19:11:51.064710

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9221fab2c1f3'
down_revision: Union[str, None] = 'c87f7da88f99'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_system column
    op.add_column('expense_categories',
        sa.Column('is_system', sa.Boolean(), server_default='false', nullable=False))

    # Insert "Kategorize Edilmemis" category
    op.execute("""
        INSERT INTO expense_categories (name, is_fixed, is_system, display_order)
        VALUES ('Kategorize Edilmemis', false, true, -1)
    """)


def downgrade() -> None:
    op.execute("DELETE FROM expense_categories WHERE name = 'Kategorize Edilmemis'")
    op.drop_column('expense_categories', 'is_system')
