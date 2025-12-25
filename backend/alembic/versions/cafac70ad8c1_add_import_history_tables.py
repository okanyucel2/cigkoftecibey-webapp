"""add_import_history_tables

Revision ID: cafac70ad8c1
Revises: d9c1cba3a0c5
Create Date: 2025-12-25 12:22:49.951517

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cafac70ad8c1'
down_revision: Union[str, None] = 'd9c1cba3a0c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'import_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('branch_id', sa.Integer(), nullable=False),
        sa.Column('import_type', sa.String(50), nullable=False),
        sa.Column('import_date', sa.Date(), nullable=False),
        sa.Column('source_filename', sa.String(255), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('import_metadata', sa.JSON(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_import_history_branch_date', 'import_history', ['branch_id', 'import_date'])

    op.create_table(
        'import_history_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('import_history_id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(20), nullable=False),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['import_history_id'], ['import_history.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_import_history_items_history', 'import_history_items', ['import_history_id'])


def downgrade() -> None:
    op.drop_index('ix_import_history_items_history', table_name='import_history_items')
    op.drop_table('import_history_items')
    op.drop_index('ix_import_history_branch_date', table_name='import_history')
    op.drop_table('import_history')
