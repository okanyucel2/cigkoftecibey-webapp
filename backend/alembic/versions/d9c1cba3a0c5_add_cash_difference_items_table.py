"""add_cash_difference_items_table

Revision ID: d9c1cba3a0c5
Revises: ccba155171a4
Create Date: 2025-12-25 03:31:01.006298

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd9c1cba3a0c5'
down_revision: Union[str, None] = 'ccba155171a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'cash_difference_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cash_difference_id', sa.Integer(), nullable=False),
        sa.Column('platform_id', sa.Integer(), nullable=False),
        sa.Column('source_type', sa.String(10), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['cash_difference_id'], ['cash_differences.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['platform_id'], ['online_platforms.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_cdi_cash_difference_id', 'cash_difference_items', ['cash_difference_id'])
    op.create_index('ix_cdi_platform_source', 'cash_difference_items', ['platform_id', 'source_type'])


def downgrade() -> None:
    op.drop_index('ix_cdi_platform_source', 'cash_difference_items')
    op.drop_index('ix_cdi_cash_difference_id', 'cash_difference_items')
    op.drop_table('cash_difference_items')
