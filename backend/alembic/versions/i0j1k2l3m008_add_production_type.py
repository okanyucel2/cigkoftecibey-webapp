"""add_production_type

Revision ID: i0j1k2l3m008
Revises: h9i0j1k2l007
Create Date: 2025-01-02 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'i0j1k2l3m008'
down_revision = 'h9i0j1k2l007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add production_type column to daily_productions
    # Default value 'etli' (meat-based) for existing records
    op.add_column('daily_productions',
        sa.Column('production_type',
                  sa.String(length=20),
                  nullable=False,
                  server_default='etli')
    )

    # Create index for production_type for faster filtering
    op.create_index('ix_daily_productions_production_type',
                    'daily_productions',
                    ['production_type'])

    # Drop old unique constraint on (branch_id, production_date)
    # and create new one on (branch_id, production_date, production_type)
    # This allows both "etli" and "etsiz" on the same date
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    constraints = [c['name'] for c in inspector.get_unique_constraints('daily_productions')]

    # Drop the old unique constraint if it exists
    if 'uq_daily_production_branch_date' in constraints:
        op.drop_constraint('uq_daily_production_branch_date',
                          'daily_productions',
                          type_='unique')

    # Create new unique constraint with production_type
    op.create_unique_constraint('uq_daily_production_branch_date_type',
                                'daily_productions',
                                ['branch_id', 'production_date', 'production_type'])


def downgrade() -> None:
    # Drop new unique constraint
    op.drop_constraint('uq_daily_production_branch_date_type',
                       'daily_productions',
                       type_='unique')

    # Restore old unique constraint
    op.create_unique_constraint('uq_daily_production_branch_date',
                                'daily_productions',
                                ['branch_id', 'production_date'])

    # Drop index
    op.drop_index('ix_daily_productions_production_type', 'daily_productions')

    # Drop column
    op.drop_column('daily_productions', 'production_type')
