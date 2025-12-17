"""Unified sales channels - add channel_type to platforms, drop daily_sales

Revision ID: d5e6f7g8h003
Revises: c4d5e6f7g002
Create Date: 2025-12-17
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'd5e6f7g8h003'
down_revision: Union[str, None] = 'c4d5e6f7g002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add channel_type and is_system columns to online_platforms
    op.add_column('online_platforms',
        sa.Column('channel_type', sa.String(20), server_default='online', nullable=False)
    )
    op.add_column('online_platforms',
        sa.Column('is_system', sa.Boolean(), server_default='false', nullable=False)
    )

    # 2. Insert system channels (Salon and Telefon Paket)
    # These are global (no branch_id) and cannot be deleted
    op.execute("""
        INSERT INTO online_platforms (name, display_order, is_active, channel_type, is_system)
        VALUES
        ('Salon', 0, true, 'pos_salon', true),
        ('Telefon Paket', 1, true, 'pos_telefon', true)
    """)

    # 3. Update display_order of existing online platforms to come after system channels
    op.execute("""
        UPDATE online_platforms
        SET display_order = display_order + 10
        WHERE channel_type = 'online'
    """)

    # 4. Drop daily_sales table (test data only, no migration needed)
    op.drop_index('ix_daily_sales_sale_date', 'daily_sales')
    op.drop_index('ix_daily_sales_branch_id', 'daily_sales')
    op.drop_table('daily_sales')


def downgrade() -> None:
    # Recreate daily_sales table
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

    # Remove system channels
    op.execute("DELETE FROM online_platforms WHERE is_system = true")

    # Restore display_order
    op.execute("""
        UPDATE online_platforms
        SET display_order = display_order - 10
        WHERE channel_type = 'online'
    """)

    # Remove added columns
    op.drop_column('online_platforms', 'is_system')
    op.drop_column('online_platforms', 'channel_type')
