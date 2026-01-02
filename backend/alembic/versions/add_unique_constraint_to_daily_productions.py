"""add unique constraint to daily_productions

This migration adds a unique constraint on (branch_id, production_date)
to allow different branches to have production records on the same date,
while preventing duplicate entries for the same branch and date.

Revision ID: a1b2c3d4e5f6
Revises: 211c185ab9f6
Create Date: 2025-01-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '211c185ab9f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    # Add unique constraint on (branch_id, production_date)
    # This allows different branches to have records on the same date
    op.create_unique_constraint(
        'uq_daily_production_branch_date',
        'daily_productions',
        ['branch_id', 'production_date']
    )


def downgrade() -> None:
    # Remove the unique constraint
    op.drop_constraint('uq_daily_production_branch_date', 'daily_productions', type_='unique')
