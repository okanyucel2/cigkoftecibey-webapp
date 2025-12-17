"""add courier_expenses table

Revision ID: 722c39806bf5
Revises: g8h9i0j1k006
Create Date: 2025-12-17 22:31:25.616834

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '722c39806bf5'
down_revision: Union[str, None] = 'g8h9i0j1k006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('courier_expenses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('branch_id', sa.Integer(), nullable=False),
        sa.Column('expense_date', sa.Date(), nullable=False),
        sa.Column('package_count', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('vat_rate', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_courier_expenses_expense_date'), 'courier_expenses', ['expense_date'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_courier_expenses_expense_date'), table_name='courier_expenses')
    op.drop_table('courier_expenses')
