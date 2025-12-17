"""Add organizations table for multi-tenant support

Revision ID: e6f7g8h9i004
Revises: d5e6f7g8h003
Create Date: 2025-12-17
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'e6f7g8h9i004'
down_revision: Union[str, None] = 'd5e6f7g8h003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('code', sa.String(20), unique=True, nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )
    op.create_index('ix_organizations_code', 'organizations', ['code'], unique=True)

    # 2. Add organization_id to branches table
    op.add_column('branches',
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id'), nullable=True)
    )
    op.create_index('ix_branches_organization_id', 'branches', ['organization_id'])

    # 3. Add organization_id to users table
    op.add_column('users',
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id'), nullable=True)
    )
    op.create_index('ix_users_organization_id', 'users', ['organization_id'])

    # 4. Create default organization and assign existing data
    op.execute("""
        INSERT INTO organizations (name, code, is_active)
        VALUES ('Cig Kofte Bey', 'CIGKOFTEBEY', true)
    """)

    # 5. Assign existing branches to default organization
    op.execute("""
        UPDATE branches
        SET organization_id = (SELECT id FROM organizations WHERE code = 'CIGKOFTEBEY')
    """)

    # 6. Assign existing users to default organization
    op.execute("""
        UPDATE users
        SET organization_id = (SELECT id FROM organizations WHERE code = 'CIGKOFTEBEY')
    """)


def downgrade() -> None:
    # Remove organization_id from users
    op.drop_index('ix_users_organization_id', table_name='users')
    op.drop_column('users', 'organization_id')

    # Remove organization_id from branches
    op.drop_index('ix_branches_organization_id', table_name='branches')
    op.drop_column('branches', 'organization_id')

    # Drop organizations table
    op.drop_index('ix_organizations_code', table_name='organizations')
    op.drop_table('organizations')
