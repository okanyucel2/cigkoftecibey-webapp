"""add menu_items table

Revision ID: p7q8r9s0t015
Revises: o6p7q8r9s014
Create Date: 2026-01-14 21:00:00.000000

Menu items linked to categories for ordering system.
Uses hybrid tenant isolation (NULL branch_id = global, value = branch-specific).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'p7q8r9s0t015'
down_revision: Union[str, None] = 'o6p7q8r9s014'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('menu_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('branch_id', sa.Integer(), nullable=True),  # NULL = global (all branches)
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_available', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['menu_categories.id'], ),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # Index for efficient lookup by category
    op.create_index(
        'ix_menu_items_category_id',
        'menu_items',
        ['category_id'],
        unique=False
    )
    # Index for efficient lookup by branch (hybrid tenant isolation)
    op.create_index(
        'ix_menu_items_branch_id',
        'menu_items',
        ['branch_id'],
        unique=False
    )
    # Index for display ordering
    op.create_index(
        'ix_menu_items_display_order',
        'menu_items',
        ['display_order'],
        unique=False
    )
    # Unique constraint: name must be unique within category and scope
    op.create_index(
        'ix_menu_items_name_category_branch_unique',
        'menu_items',
        ['name', 'category_id', 'branch_id'],
        unique=True
    )


def downgrade() -> None:
    op.drop_index('ix_menu_items_name_category_branch_unique', table_name='menu_items')
    op.drop_index('ix_menu_items_display_order', table_name='menu_items')
    op.drop_index('ix_menu_items_branch_id', table_name='menu_items')
    op.drop_index('ix_menu_items_category_id', table_name='menu_items')
    op.drop_table('menu_items')
