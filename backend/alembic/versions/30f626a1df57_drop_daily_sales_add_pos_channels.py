"""drop_daily_sales_remove_salon_telefon

Revision ID: 30f626a1df57
Revises: 9221fab2c1f3
Create Date: 2025-12-23 20:54:01.880642

This migration:
1. Drops the daily_sales table (if exists) - replaced by unified sales channels
2. Adds channel_type and is_system columns to online_platforms (if not exist)
3. DELETES Salon and Telefon Paket platforms (no longer needed)
4. Ensures Visa and Nakit platforms exist for POS data
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = '30f626a1df57'
down_revision: Union[str, None] = '9221fab2c1f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    # 1. Drop daily_sales table if it exists
    existing_tables = inspector.get_table_names()
    if 'daily_sales' in existing_tables:
        # Drop indexes first
        try:
            op.drop_index('ix_daily_sales_sale_date', 'daily_sales')
        except:
            pass
        try:
            op.drop_index('ix_daily_sales_branch_id', 'daily_sales')
        except:
            pass
        op.drop_table('daily_sales')

    # 2. Add channel_type and is_system columns to online_platforms if not exist
    existing_columns = [col['name'] for col in inspector.get_columns('online_platforms')]

    if 'channel_type' not in existing_columns:
        op.add_column('online_platforms',
            sa.Column('channel_type', sa.String(20), server_default='online', nullable=False)
        )

    if 'is_system' not in existing_columns:
        op.add_column('online_platforms',
            sa.Column('is_system', sa.Boolean(), server_default='false', nullable=False)
        )

    # 3. DELETE Salon and Telefon Paket platforms (and any related sales)
    conn.execute(sa.text("""
        DELETE FROM online_sales WHERE platform_id IN (
            SELECT id FROM online_platforms WHERE name IN ('Salon', 'Telefon Paket')
        )
    """))
    conn.execute(sa.text("""
        DELETE FROM online_platforms WHERE name IN ('Salon', 'Telefon Paket')
    """))

    # 4. Ensure Visa platform exists
    result = conn.execute(sa.text("SELECT id FROM online_platforms WHERE name = 'Visa'"))
    if not result.fetchone():
        conn.execute(sa.text("""
            INSERT INTO online_platforms (name, display_order, is_active, channel_type, is_system)
            VALUES ('Visa', 0, true, 'pos_visa', true)
        """))
    else:
        # Update existing to be system platform
        conn.execute(sa.text("""
            UPDATE online_platforms
            SET channel_type = 'pos_visa', is_system = true, display_order = 0
            WHERE name = 'Visa'
        """))

    # 5. Ensure Nakit platform exists
    result = conn.execute(sa.text("SELECT id FROM online_platforms WHERE name = 'Nakit'"))
    if not result.fetchone():
        conn.execute(sa.text("""
            INSERT INTO online_platforms (name, display_order, is_active, channel_type, is_system)
            VALUES ('Nakit', 1, true, 'pos_nakit', true)
        """))
    else:
        # Update existing to be system platform
        conn.execute(sa.text("""
            UPDATE online_platforms
            SET channel_type = 'pos_nakit', is_system = true, display_order = 1
            WHERE name = 'Nakit'
        """))

    # 6. Update display_order of online platforms to come after POS channels
    conn.execute(sa.text("""
        UPDATE online_platforms
        SET display_order = display_order + 10
        WHERE channel_type = 'online' AND display_order < 10
    """))


def downgrade() -> None:
    # This migration is not easily reversible
    pass
