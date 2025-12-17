"""Add Google auth fields to users table

Revision ID: g8h9i0j1k006
Revises: f7g8h9i0j005
Create Date: 2025-12-17
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'g8h9i0j1k006'
down_revision: Union[str, None] = 'f7g8h9i0j005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add google_id column for Google OAuth users
    op.add_column('users',
        sa.Column('google_id', sa.String(100), unique=True, nullable=True)
    )
    op.create_index('ix_users_google_id', 'users', ['google_id'], unique=True)

    # 2. Add avatar_url for profile picture from Google
    op.add_column('users',
        sa.Column('avatar_url', sa.String(500), nullable=True)
    )

    # 3. Add auth_provider to track how user authenticated
    op.add_column('users',
        sa.Column('auth_provider', sa.String(20), server_default='email', nullable=False)
    )

    # 4. Make password_hash nullable (Google users won't have one)
    op.alter_column('users', 'password_hash',
        existing_type=sa.String(255),
        nullable=True
    )

    # 5. Make branch_id nullable (new Google users won't have a branch yet)
    op.alter_column('users', 'branch_id',
        existing_type=sa.Integer(),
        nullable=True
    )


def downgrade() -> None:
    # Restore branch_id to not nullable (might fail if there are NULL values)
    op.alter_column('users', 'branch_id',
        existing_type=sa.Integer(),
        nullable=False
    )

    # Restore password_hash to not nullable
    op.alter_column('users', 'password_hash',
        existing_type=sa.String(255),
        nullable=False
    )

    # Remove auth_provider
    op.drop_column('users', 'auth_provider')

    # Remove avatar_url
    op.drop_column('users', 'avatar_url')

    # Remove google_id
    op.drop_index('ix_users_google_id', table_name='users')
    op.drop_column('users', 'google_id')
