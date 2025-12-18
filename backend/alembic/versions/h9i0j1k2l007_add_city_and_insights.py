"""add_city_and_insights

Revision ID: h9i0j1k2l007
Revises: g8h9i0j1k006
Create Date: 2025-12-18 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'h9i0j1k2l007'
down_revision = '722c39806bf5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    # Add city column to branches if not exists
    columns = [c['name'] for c in inspector.get_columns('branches')]
    if 'city' not in columns:
        op.add_column('branches', sa.Column('city', sa.String(length=100), nullable=True))

    # Create daily_insights table if not exists
    if 'daily_insights' not in tables:
        op.create_table('daily_insights',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('branch_id', sa.Integer(), nullable=False),
            sa.Column('date', sa.Date(), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ),
            sa.PrimaryKeyConstraint('id')
        )


def downgrade() -> None:
    # Drop daily_insights table
    op.drop_table('daily_insights')

    # Drop city column from branches
    op.drop_column('branches', 'city')
