"""add menu_categories table

Revision ID: o6p7q8r9s014
Revises: n5o6p7q8r013
Create Date: 2026-01-14 19:30:00.000000

Menu categories for future menu/ordering system.
Uses hybrid tenant isolation (NULL branch_id = global, value = branch-specific).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'o6p7q8r9s014'
down_revision: Union[str, None] = 'n5o6p7q8r013'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('menu_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('branch_id', sa.Integer(), nullable=True),  # NULL = global (all branches)
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_system', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # Index for efficient lookup by branch (hybrid tenant isolation)
    op.create_index(
        'ix_menu_categories_branch_id',
        'menu_categories',
        ['branch_id'],
        unique=False
    )
    # Index for display ordering
    op.create_index(
        'ix_menu_categories_display_order',
        'menu_categories',
        ['display_order'],
        unique=False
    )
    # Unique constraint: name must be unique within scope (branch or global)
    op.create_index(
        'ix_menu_categories_name_branch_unique',
        'menu_categories',
        ['name', 'branch_id'],
        unique=True
    )


def downgrade() -> None:
    op.drop_index('ix_menu_categories_name_branch_unique', table_name='menu_categories')
    op.drop_index('ix_menu_categories_display_order', table_name='menu_categories')
    op.drop_index('ix_menu_categories_branch_id', table_name='menu_categories')
    op.drop_table('menu_categories')
