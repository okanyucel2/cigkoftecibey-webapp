"""add branch_operating_hours table

Revision ID: l3m4n5o6p011
Revises: k2l3m4n5o010
Create Date: 2026-01-08 21:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'l3m4n5o6p011'
down_revision: Union[str, None] = 'k2l3m4n5o010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('branch_operating_hours',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('branch_id', sa.Integer(), nullable=True),  # NULL = global default
        sa.Column('day_of_week', sa.Integer(), nullable=False),  # 0=Monday, 6=Sunday
        sa.Column('open_time', sa.Time(), nullable=True),
        sa.Column('close_time', sa.Time(), nullable=True),
        sa.Column('is_closed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # Index for efficient lookup by branch + day
    op.create_index(
        'ix_branch_operating_hours_branch_day',
        'branch_operating_hours',
        ['branch_id', 'day_of_week'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('ix_branch_operating_hours_branch_day', table_name='branch_operating_hours')
    op.drop_table('branch_operating_hours')
