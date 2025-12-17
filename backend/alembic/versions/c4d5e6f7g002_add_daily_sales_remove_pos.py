"""Add daily_sales table and remove POS tables

Revision ID: c4d5e6f7g002
Revises: b3c7d8e9f001
Create Date: 2025-12-17
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'c4d5e6f7g002'
down_revision: Union[str, None] = 'b3c7d8e9f001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create daily_sales table
    op.create_table(
        'daily_sales',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('branch_id', sa.Integer(), nullable=False),
        sa.Column('sale_date', sa.Date(), nullable=False),
        sa.Column('salon_amount', sa.Numeric(12, 2), server_default='0', nullable=False),
        sa.Column('paket_amount', sa.Numeric(12, 2), server_default='0', nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('branch_id', 'sale_date', name='uq_daily_sales_branch_date')
    )
    op.create_index('ix_daily_sales_branch_id', 'daily_sales', ['branch_id'])
    op.create_index('ix_daily_sales_sale_date', 'daily_sales', ['sale_date'])

    # Drop old POS tables (order matters due to foreign keys)
    op.drop_table('sales_order_items')
    op.drop_table('sales_orders')
    op.drop_table('branch_products')
    op.drop_table('products')
    op.drop_table('product_categories')


def downgrade() -> None:
    # Recreate product_categories
    op.create_table(
        'product_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('display_order', sa.Integer(), server_default='0'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.PrimaryKeyConstraint('id')
    )

    # Recreate products
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('display_order', sa.Integer(), server_default='0'),
        sa.ForeignKeyConstraint(['category_id'], ['product_categories.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Recreate branch_products
    op.create_table(
        'branch_products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('branch_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('price_override', sa.Numeric(10, 2), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('display_order', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('branch_id', 'product_id', name='uq_branch_product')
    )

    # Recreate sales_orders
    op.create_table(
        'sales_orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('branch_id', sa.Integer(), nullable=False),
        sa.Column('order_number', sa.String(50), nullable=False),
        sa.Column('order_type', sa.String(20), nullable=False),
        sa.Column('total', sa.Numeric(10, 2), nullable=False),
        sa.Column('payment_method', sa.String(20), server_default='cash'),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_number')
    )

    # Recreate sales_order_items
    op.create_table(
        'sales_order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('total', sa.Numeric(10, 2), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['sales_orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Drop daily_sales
    op.drop_index('ix_daily_sales_sale_date', 'daily_sales')
    op.drop_index('ix_daily_sales_branch_id', 'daily_sales')
    op.drop_table('daily_sales')
