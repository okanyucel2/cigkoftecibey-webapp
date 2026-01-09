"""add branch_holidays table

Revision ID: m4n5o6p7q012
Revises: l3m4n5o6p011
Create Date: 2026-01-09 10:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'm4n5o6p7q012'
down_revision: Union[str, None] = 'l3m4n5o6p011'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('branch_holidays',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('branch_id', sa.Integer(), nullable=True),  # NULL = global holiday
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('is_closed', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # Index for efficient lookup by date
    op.create_index(
        'ix_branch_holidays_date',
        'branch_holidays',
        ['date'],
        unique=False
    )
    # Index for efficient lookup by branch + date
    op.create_index(
        'ix_branch_holidays_branch_date',
        'branch_holidays',
        ['branch_id', 'date'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('ix_branch_holidays_branch_date', table_name='branch_holidays')
    op.drop_index('ix_branch_holidays_date', table_name='branch_holidays')
    op.drop_table('branch_holidays')
