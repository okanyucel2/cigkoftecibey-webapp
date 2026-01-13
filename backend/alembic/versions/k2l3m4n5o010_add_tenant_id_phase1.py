"""Add tenant_id column to all tables - Phase 1 (nullable)

Revision ID: k2l3m4n5o010
Revises: j1k2l3m4n009
Create Date: 2026-01-05 10:00:00.000000

Multi-tenant infrastructure Phase 1:
- Add tenant_id column (nullable) to all tenant-scoped tables
- Backfill tenant_id from branches.organization_id
- Handle items tables via parent table joins
- Index all tenant_id columns for query performance
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'k2l3m4n5o010'
down_revision = 'j1k2l3m4n009'
branch_labels = None
depends_on = None


# Tables with branch_id - can join via branches.organization_id
TABLES_WITH_BRANCH_ID = [
    'purchases',
    'suppliers',
    'cash_differences',
    'import_history',
    'expenses',
    'staff_meals',
    'employees',
    'monthly_payrolls',
    'part_time_costs',
    'online_sales',
    'daily_summaries',
    'daily_productions',
    'courier_expenses',
    'daily_insights',
]

# Items tables - need parent table join
ITEMS_TABLE_MAPPING = {
    'purchase_items': 'purchases',
    'supplier_payments': 'suppliers',
    'supplier_transactions': 'suppliers',
    'cash_difference_items': 'cash_differences',
    'import_history_items': 'import_history',
}

# Global tables - tenant_id NULL means system record
GLOBAL_TABLES = [
    'expense_categories',
    'online_platforms',
    'purchase_product_groups',
    'purchase_products',
]


def upgrade() -> None:
    # Step 1: Add tenant_id column to all tables with branch_id
    for table in TABLES_WITH_BRANCH_ID:
        op.add_column(table, sa.Column('tenant_id', sa.Integer(), nullable=True))
        op.create_index(f'ix_{table}_tenant_id', table, ['tenant_id'], unique=False)
        op.create_foreign_key(
            f'fk_{table}_tenant_id',
            table,
            'organizations',
            ['tenant_id'],
            ['id'],
            ondelete='RESTRICT'
        )

    # Step 2: Add tenant_id to items tables
    for items_table in ITEMS_TABLE_MAPPING.keys():
        op.add_column(items_table, sa.Column('tenant_id', sa.Integer(), nullable=True))
        op.create_index(f'ix_{items_table}_tenant_id', items_table, ['tenant_id'], unique=False)
        op.create_foreign_key(
            f'fk_{items_table}_tenant_id',
            items_table,
            'organizations',
            ['tenant_id'],
            ['id'],
            ondelete='RESTRICT'
        )

    # Step 3: Add tenant_id to global tables (nullable for system records)
    for table in GLOBAL_TABLES:
        op.add_column(table, sa.Column('tenant_id', sa.Integer(), nullable=True))
        op.create_index(f'ix_{table}_tenant_id', table, ['tenant_id'], unique=False)
        op.create_foreign_key(
            f'fk_{table}_tenant_id',
            table,
            'organizations',
            ['tenant_id'],
            ['id'],
            ondelete='RESTRICT'
        )

    # Step 4: Backfill tenant_id for tables with branch_id
    # Join through branches to get organization_id
    for table in TABLES_WITH_BRANCH_ID:
        op.execute(f"""
            UPDATE {table}
            SET tenant_id = (
                SELECT b.organization_id
                FROM branches b
                WHERE b.id = {table}.branch_id
            )
            WHERE tenant_id IS NULL
        """)

    # Step 5: Backfill items tables via parent
    # CRITICAL: Must do after parent tables are backfilled!
    for items_table, parent_table in ITEMS_TABLE_MAPPING.items():
        # Determine the foreign key column name
        if items_table == 'purchase_items':
            fk_col = 'purchase_id'
        elif items_table in ['supplier_payments', 'supplier_transactions']:
            fk_col = 'supplier_id'
        elif items_table == 'cash_difference_items':
            fk_col = 'cash_difference_id'
        elif items_table == 'import_history_items':
            fk_col = 'import_history_id'
        else:
            continue

        op.execute(f"""
            UPDATE {items_table}
            SET tenant_id = (
                SELECT p.tenant_id
                FROM {parent_table} p
                WHERE p.id = {items_table}.{fk_col}
            )
            WHERE tenant_id IS NULL
        """)

    # Step 6: Backfill global tables with branch_id (branch-specific records)
    for table in GLOBAL_TABLES:
        op.execute(f"""
            UPDATE {table}
            SET tenant_id = (
                SELECT b.organization_id
                FROM branches b
                WHERE b.id = {table}.branch_id
            )
            WHERE branch_id IS NOT NULL AND tenant_id IS NULL
        """)
        # Note: Records with branch_id = NULL remain tenant_id = NULL (system records)

    # Step 7: Create composite indexes for common date-filtered queries
    # These indexes optimize tenant-scoped queries filtered by date
    op.create_index(
        'ix_purchases_tenant_date',
        'purchases',
        ['tenant_id', 'purchase_date'],
        unique=False
    )
    op.create_index(
        'ix_online_sales_tenant_date',
        'online_sales',
        ['tenant_id', 'sale_date'],
        unique=False
    )
    op.create_index(
        'ix_expenses_tenant_date',
        'expenses',
        ['tenant_id', 'expense_date'],
        unique=False
    )
    op.create_index(
        'ix_daily_summaries_tenant_date',
        'daily_summaries',
        ['tenant_id', 'summary_date'],
        unique=False
    )


def downgrade() -> None:
    # Step 1: Remove composite indexes first
    op.drop_index('ix_purchases_tenant_date', 'purchases')
    op.drop_index('ix_online_sales_tenant_date', 'online_sales')
    op.drop_index('ix_expenses_tenant_date', 'expenses')
    op.drop_index('ix_daily_summaries_tenant_date', 'daily_summaries')

    # Step 2: Remove tenant_id from all tables in reverse order
    all_tables = GLOBAL_TABLES + list(ITEMS_TABLE_MAPPING.keys()) + TABLES_WITH_BRANCH_ID

    for table in all_tables:
        op.drop_constraint(f'fk_{table}_tenant_id', table, type_='foreignkey')
        op.drop_index(f'ix_{table}_tenant_id', table)
        op.drop_column(table, 'tenant_id')
