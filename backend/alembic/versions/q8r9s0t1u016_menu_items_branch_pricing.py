"""menu_items branch-specific pricing refactor

Revision ID: q8r9s0t1u016
Revises: p7q8r9s0t015
Create Date: 2026-01-14 21:45:00.000000

Refactors menu_items for branch-specific pricing:
- Removes price, branch_id, is_available, updated_at from menu_items
- Adds image_url to menu_items
- Creates menu_item_prices table for branch-specific pricing
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'q8r9s0t1u016'
down_revision: Union[str, None] = 'p7q8r9s0t015'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop old indexes that reference columns being removed
    op.drop_index('ix_menu_items_branch_id', table_name='menu_items')
    op.drop_index('ix_menu_items_name_category_branch_unique', table_name='menu_items')

    # Remove old columns from menu_items
    op.drop_column('menu_items', 'price')
    op.drop_column('menu_items', 'branch_id')
    op.drop_column('menu_items', 'is_available')
    op.drop_column('menu_items', 'updated_at')

    # Add new column
    op.add_column('menu_items', sa.Column('image_url', sa.String(500), nullable=True))

    # Create new unique constraint (name + category only, no branch)
    op.create_index(
        'ix_menu_items_name_category_unique',
        'menu_items',
        ['name', 'category_id'],
        unique=True
    )

    # Create menu_item_prices table
    op.create_table('menu_item_prices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('menu_item_id', sa.Integer(), nullable=False),
        sa.Column('branch_id', sa.Integer(), nullable=True),  # NULL = default price
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['menu_item_id'], ['menu_items.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # Unique constraint: one price per item per branch
    op.create_index(
        'ix_menu_item_prices_item_branch',
        'menu_item_prices',
        ['menu_item_id', 'branch_id'],
        unique=True
    )


def downgrade() -> None:
    # Drop menu_item_prices table
    op.drop_index('ix_menu_item_prices_item_branch', table_name='menu_item_prices')
    op.drop_table('menu_item_prices')

    # Drop new unique constraint
    op.drop_index('ix_menu_items_name_category_unique', table_name='menu_items')

    # Remove new column
    op.drop_column('menu_items', 'image_url')

    # Add back old columns
    op.add_column('menu_items', sa.Column('price', sa.Numeric(10, 2), nullable=False, server_default='0.00'))
    op.add_column('menu_items', sa.Column('branch_id', sa.Integer(), nullable=True))
    op.add_column('menu_items', sa.Column('is_available', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('menu_items', sa.Column('updated_at', sa.DateTime(), nullable=True))

    # Recreate old indexes
    op.create_index('ix_menu_items_branch_id', 'menu_items', ['branch_id'], unique=False)
    op.create_index('ix_menu_items_name_category_branch_unique', 'menu_items', ['name', 'category_id', 'branch_id'], unique=True)
