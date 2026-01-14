# Phase 2: RLS Policy Reference

## Critical: Use missing_ok Parameter

PostgreSQL's `current_setting()` throws an ERROR if the variable is not set.
Always use the `missing_ok` parameter (second argument = `true`).

### WRONG (throws error if variable not set):
```sql
USING (tenant_id = current_setting('app.current_tenant')::integer)
```

### CORRECT (returns NULL safely):
```sql
USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::integer)
```

---

## Policy Templates

### 1. Strict Isolation (purchases, suppliers, expenses, etc.)

Use for tables where ALL records must belong to a tenant.

```sql
CREATE POLICY tenant_isolation ON purchases
FOR ALL
USING (
    current_setting('app.is_superuser', true) = 'on'
    OR
    tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::integer
);
```

### 2. Global + Tenant (expense_categories, online_platforms)

Use for tables with both system records (tenant_id = NULL) and tenant records.

```sql
CREATE POLICY global_or_tenant ON expense_categories
FOR ALL
USING (
    current_setting('app.is_superuser', true) = 'on'
    OR
    tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::integer
    OR
    tenant_id IS NULL  -- System records visible to all
);
```

### 3. Write Protection (prevent modifying global records)

Prevent tenants from creating/modifying system records.

```sql
CREATE POLICY prevent_global_write ON expense_categories
FOR INSERT
WITH CHECK (
    tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::integer
);
```

---

## Super Admin Bypass

The `app.is_superuser` session variable is set in `backend/app/api/deps.py`
when the user has `is_super_admin = True`.

```python
# In get_current_tenant():
if user.is_super_admin:
    db.execute(
        text("SELECT set_config('app.is_superuser', 'on', true)")
    )
```

RLS policies check this flag FIRST, granting full access to super admins:
```sql
current_setting('app.is_superuser', true) = 'on'
```

---

## Session Variables Set by get_current_tenant()

| Variable | Value | Scope |
|----------|-------|-------|
| `app.current_tenant` | tenant_id (integer as string) | Transaction |
| `app.is_superuser` | 'on' (only for super admin) | Transaction |

Both use `true` for the `is_local` parameter, making them transaction-scoped.
This prevents connection pool leaks.

---

## Implementation Checklist for Phase 2

1. [ ] Create RLS policies for all tenant-scoped tables
2. [ ] Enable RLS on each table: `ALTER TABLE x ENABLE ROW LEVEL SECURITY;`
3. [ ] Test with regular user (should only see own tenant data)
4. [ ] Test with super admin (should see all data)
5. [ ] Test without session variable (should see nothing or error safely)
6. [ ] Update affected queries to ensure session variable is always set

---

## Tables Requiring RLS Policies

### Strict Isolation (14 tables)
- purchases
- suppliers
- cash_differences
- import_history
- expenses
- staff_meals
- employees
- monthly_payrolls
- part_time_costs
- online_sales
- daily_summaries
- daily_productions
- courier_expenses
- daily_insights

### Strict Isolation - Items (5 tables)
- purchase_items
- supplier_payments
- supplier_transactions
- cash_difference_items
- import_history_items

### Global + Tenant (4 tables)
- expense_categories
- online_platforms
- purchase_product_groups
- purchase_products

---

## Testing RLS

```sql
-- Set tenant context
SELECT set_config('app.current_tenant', '1', true);

-- Query should only return tenant 1 data
SELECT * FROM purchases;

-- Super admin bypass
SELECT set_config('app.is_superuser', 'on', true);
SELECT * FROM purchases;  -- Returns all data
```
