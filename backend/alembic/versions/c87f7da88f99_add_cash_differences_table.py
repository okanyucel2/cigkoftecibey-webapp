"""add_cash_differences_table

Revision ID: c87f7da88f99
Revises: h9i0j1k2l007
Create Date: 2025-12-23 19:07:35.246641

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c87f7da88f99'
down_revision: Union[str, None] = 'h9i0j1k2l007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('cash_differences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('branch_id', sa.Integer(), nullable=False),
        sa.Column('difference_date', sa.Date(), nullable=False),

        # Kasa Raporu (Excel)
        sa.Column('kasa_visa', sa.Numeric(precision=12, scale=2), server_default='0'),
        sa.Column('kasa_nakit', sa.Numeric(precision=12, scale=2), server_default='0'),
        sa.Column('kasa_trendyol', sa.Numeric(precision=12, scale=2), server_default='0'),
        sa.Column('kasa_getir', sa.Numeric(precision=12, scale=2), server_default='0'),
        sa.Column('kasa_yemeksepeti', sa.Numeric(precision=12, scale=2), server_default='0'),
        sa.Column('kasa_migros', sa.Numeric(precision=12, scale=2), server_default='0'),
        sa.Column('kasa_total', sa.Numeric(precision=12, scale=2), server_default='0'),

        # POS Hasilat (Gorsel)
        sa.Column('pos_visa', sa.Numeric(precision=12, scale=2), server_default='0'),
        sa.Column('pos_nakit', sa.Numeric(precision=12, scale=2), server_default='0'),
        sa.Column('pos_trendyol', sa.Numeric(precision=12, scale=2), server_default='0'),
        sa.Column('pos_getir', sa.Numeric(precision=12, scale=2), server_default='0'),
        sa.Column('pos_yemeksepeti', sa.Numeric(precision=12, scale=2), server_default='0'),
        sa.Column('pos_migros', sa.Numeric(precision=12, scale=2), server_default='0'),
        sa.Column('pos_total', sa.Numeric(precision=12, scale=2), server_default='0'),

        # Meta
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('severity', sa.String(20), server_default='ok'),
        sa.Column('resolution_note', sa.Text(), nullable=True),
        sa.Column('resolved_by', sa.Integer(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),

        # Files
        sa.Column('excel_file_url', sa.Text(), nullable=True),
        sa.Column('pos_image_url', sa.Text(), nullable=True),
        sa.Column('ocr_confidence_score', sa.Numeric(precision=5, scale=2), nullable=True),

        # Audit
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True),

        sa.ForeignKeyConstraint(['branch_id'], ['branches.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('branch_id', 'difference_date', name='uq_cash_diff_branch_date')
    )
    op.create_index('ix_cash_differences_date', 'cash_differences', ['difference_date'])
    op.create_index('ix_cash_differences_status', 'cash_differences', ['status'])


def downgrade() -> None:
    op.drop_index('ix_cash_differences_status', table_name='cash_differences')
    op.drop_index('ix_cash_differences_date', table_name='cash_differences')
    op.drop_table('cash_differences')
