"""Add health check user for E2E verification (P0.42)

Revision ID: j1k2l3m4n009
Revises: i0j1k2l3m008
Create Date: 2026-01-03 13:30:00.000000

This migration creates the health check user required by the /api/health/deep
endpoint for E2E auth verification. The user is created with ON CONFLICT DO NOTHING
to ensure idempotency.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'j1k2l3m4n009'
down_revision: Union[str, None] = 'i0j1k2l3m008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create health check user if not exists."""
    # Password: healthcheck123 (bcrypt hashed)
    # This user is ONLY for health check verification, not for actual login
    op.execute("""
        INSERT INTO users (
            email,
            password_hash,
            name,
            role,
            is_active,
            is_super_admin,
            created_at,
            auth_provider
        )
        VALUES (
            'healthcheck@internal.system',
            '$2b$12$f6UtjjasZZCmfuQjCSCGo.0KlSn89OfH0tkJbMOHJm2FgRXrHugLe',
            'Health Check System User',
            'health_check',
            true,
            false,
            NOW(),
            'email'
        )
        ON CONFLICT (email) DO NOTHING;
    """)


def downgrade() -> None:
    """Remove health check user."""
    op.execute("""
        DELETE FROM users
        WHERE email = 'healthcheck@internal.system';
    """)
