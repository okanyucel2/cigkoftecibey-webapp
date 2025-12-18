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
down_revision = 'g8h9i0j1k006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add city column to branches
    op.add_column('branches', sa.Column('city', sa.String(length=100), nullable=True))

    # Create daily_insights table
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
