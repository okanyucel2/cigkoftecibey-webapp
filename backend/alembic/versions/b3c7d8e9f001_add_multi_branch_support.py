"""add multi branch support

Revision ID: b3c7d8e9f001
Revises: 38f6ba6f7834
Create Date: 2025-12-17 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3c7d8e9f001'
down_revision: Union[str, None] = '38f6ba6f7834'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add is_super_admin to users table
    op.add_column('users', sa.Column('is_super_admin', sa.Boolean(), server_default='false', nullable=False))

    # 2. Create user_branches table (Many-to-Many: User <-> Branch)
    op.create_table(
        'user_branches',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('branch_id', sa.Integer(), sa.ForeignKey('branches.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(50), nullable=False, server_default='owner'),  # owner, manager, cashier
        sa.Column('is_default', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint('user_id', 'branch_id', name='uq_user_branch')
    )
    op.create_index('ix_user_branches_user_id', 'user_branches', ['user_id'])
    op.create_index('ix_user_branches_branch_id', 'user_branches', ['branch_id'])

    # 3. Create branch_products table (Hybrid pricing: Branch-specific price overrides)
    op.create_table(
        'branch_products',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('branch_id', sa.Integer(), sa.ForeignKey('branches.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('price_override', sa.Numeric(10, 2), nullable=True),  # NULL = use base price
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('display_order', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.func.now()),
        sa.UniqueConstraint('branch_id', 'product_id', name='uq_branch_product')
    )
    op.create_index('ix_branch_products_branch_id', 'branch_products', ['branch_id'])
    op.create_index('ix_branch_products_product_id', 'branch_products', ['product_id'])

    # 4. Add branch_id to expense_categories (nullable - NULL means global)
    op.add_column('expense_categories', sa.Column('branch_id', sa.Integer(), sa.ForeignKey('branches.id', ondelete='CASCADE'), nullable=True))
    op.create_index('ix_expense_categories_branch_id', 'expense_categories', ['branch_id'])

    # 5. Add branch_id to online_platforms (nullable - NULL means global)
    op.add_column('online_platforms', sa.Column('branch_id', sa.Integer(), sa.ForeignKey('branches.id', ondelete='CASCADE'), nullable=True))
    op.create_index('ix_online_platforms_branch_id', 'online_platforms', ['branch_id'])

    # 6. Add branch_id to purchase_product_groups (nullable - NULL means global)
    op.add_column('purchase_product_groups', sa.Column('branch_id', sa.Integer(), sa.ForeignKey('branches.id', ondelete='CASCADE'), nullable=True))
    op.create_index('ix_purchase_product_groups_branch_id', 'purchase_product_groups', ['branch_id'])

    # 7. Add branch_id to purchase_products (nullable - NULL means global)
    op.add_column('purchase_products', sa.Column('branch_id', sa.Integer(), sa.ForeignKey('branches.id', ondelete='CASCADE'), nullable=True))
    op.create_index('ix_purchase_products_branch_id', 'purchase_products', ['branch_id'])

    # 8. Migrate existing data: Create user_branches entries for existing users
    # Each user gets an entry in user_branches with their current branch_id and role
    op.execute("""
        INSERT INTO user_branches (user_id, branch_id, role, is_default)
        SELECT id, branch_id, role, true
        FROM users
        WHERE branch_id IS NOT NULL
    """)


def downgrade() -> None:
    # Remove user_branches entries (data loss warning)
    op.drop_table('user_branches')

    # Remove branch_products table
    op.drop_table('branch_products')

    # Remove branch_id from global tables
    op.drop_index('ix_purchase_products_branch_id', table_name='purchase_products')
    op.drop_column('purchase_products', 'branch_id')

    op.drop_index('ix_purchase_product_groups_branch_id', table_name='purchase_product_groups')
    op.drop_column('purchase_product_groups', 'branch_id')

    op.drop_index('ix_online_platforms_branch_id', table_name='online_platforms')
    op.drop_column('online_platforms', 'branch_id')

    op.drop_index('ix_expense_categories_branch_id', table_name='expense_categories')
    op.drop_column('expense_categories', 'branch_id')

    # Remove is_super_admin from users
    op.drop_column('users', 'is_super_admin')
