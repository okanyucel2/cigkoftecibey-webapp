"""add online platforms and sales tables

Revision ID: 38f6ba6f7834
Revises: 50070868fced
Create Date: 2025-12-17 04:51:29.563466

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '38f6ba6f7834'
down_revision: Union[str, None] = '50070868fced'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create online_platforms table
    op.create_table(
        'online_platforms',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('display_order', sa.Integer(), default=0),
        sa.Column('is_active', sa.Boolean(), default=True),
    )

    # Create online_sales table
    op.create_table(
        'online_sales',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('branch_id', sa.Integer(), sa.ForeignKey('branches.id'), nullable=False),
        sa.Column('platform_id', sa.Integer(), sa.ForeignKey('online_platforms.id'), nullable=False),
        sa.Column('sale_date', sa.Date(), nullable=False, index=True),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    # Seed default platforms
    op.execute("""
        INSERT INTO online_platforms (name, display_order, is_active) VALUES
        ('Trendyol', 1, true),
        ('Getir', 2, true),
        ('Yemek Sepeti', 3, true),
        ('Migros Yemek', 4, true)
    """)


def downgrade() -> None:
    op.drop_table('online_sales')
    op.drop_table('online_platforms')
