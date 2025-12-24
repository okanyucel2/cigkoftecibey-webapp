"""cleanup_duplicate_visa_nakit_platforms

Revision ID: ccba155171a4
Revises: 30f626a1df57
Create Date: 2025-12-24

Delete duplicate VISA and NAKİT platforms (uppercase versions).
Keep only Visa and Nakit (proper case).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'ccba155171a4'
down_revision: Union[str, None] = '30f626a1df57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    
    # Delete sales for duplicate platforms (VISA, NAKİT - uppercase versions)
    conn.execute(sa.text("""
        DELETE FROM online_sales WHERE platform_id IN (
            SELECT id FROM online_platforms 
            WHERE name IN ('VISA', 'NAKİT', 'VİSA', 'NAKIT')
        )
    """))
    
    # Delete the duplicate platforms
    conn.execute(sa.text("""
        DELETE FROM online_platforms 
        WHERE name IN ('VISA', 'NAKİT', 'VİSA', 'NAKIT')
    """))


def downgrade() -> None:
    # Not reversible - data is deleted
    pass
