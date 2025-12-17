"""Add invitation codes table for user onboarding

Revision ID: f7g8h9i0j005
Revises: e6f7g8h9i004
Create Date: 2025-12-17
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'f7g8h9i0j005'
down_revision: Union[str, None] = 'e6f7g8h9i004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create invitation_codes table
    op.create_table(
        'invitation_codes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('code', sa.String(20), unique=True, nullable=False),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('branch_id', sa.Integer(), sa.ForeignKey('branches.id'), nullable=True),  # NULL = all branches
        sa.Column('role', sa.String(20), nullable=False),  # owner, manager, cashier
        sa.Column('max_uses', sa.Integer(), server_default='1', nullable=False),
        sa.Column('used_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False)
    )
    op.create_index('ix_invitation_codes_code', 'invitation_codes', ['code'], unique=True)
    op.create_index('ix_invitation_codes_organization_id', 'invitation_codes', ['organization_id'])

    # 2. Create invitation_code_uses table for tracking usage
    op.create_table(
        'invitation_code_uses',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('code_id', sa.Integer(), sa.ForeignKey('invitation_codes.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('used_at', sa.DateTime(), server_default=sa.func.now())
    )
    op.create_index('ix_invitation_code_uses_code_id', 'invitation_code_uses', ['code_id'])
    op.create_index('ix_invitation_code_uses_user_id', 'invitation_code_uses', ['user_id'])


def downgrade() -> None:
    # Drop invitation_code_uses table
    op.drop_index('ix_invitation_code_uses_user_id', table_name='invitation_code_uses')
    op.drop_index('ix_invitation_code_uses_code_id', table_name='invitation_code_uses')
    op.drop_table('invitation_code_uses')

    # Drop invitation_codes table
    op.drop_index('ix_invitation_codes_organization_id', table_name='invitation_codes')
    op.drop_index('ix_invitation_codes_code', table_name='invitation_codes')
    op.drop_table('invitation_codes')
