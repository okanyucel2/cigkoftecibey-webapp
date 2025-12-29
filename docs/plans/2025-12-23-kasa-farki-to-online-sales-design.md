# Kasa Farkı → Online Sales Integration

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** When importing Kasa Farkı data, automatically create/update online_sales entries so the dashboard counters reflect the imported data.

**Architecture:** Extend the `/cash-difference/import` endpoint to also upsert online_sales entries for the same date/branch.

**Tech Stack:** FastAPI, SQLAlchemy, existing OnlinePlatform and OnlineSale models

---

## Design Decisions

### 1. Which values to use: Kasa (Excel) vs POS?

**Decision: Use POS values** (the ones from the receipt/terminal image)

**Rationale:**
- POS values are the authoritative source (actual payment terminal records)
- Kasa values are manual entries that might have human error
- The whole point of Kasa Farkı is to find discrepancies between manual entries and actual sales
- Dashboard should show actual sales, not manual entries

### 2. How to handle existing sales data?

**Decision: Upsert pattern** - If sales exist for that date, update them; otherwise create new.

**Rationale:**
- User might re-import a corrected Excel/POS
- Should update existing records, not create duplicates
- Use date + branch_id + platform_id as unique constraint

### 3. When to sync?

**Decision: During import only** - Not real-time sync

**Rationale:**
- Simple to implement
- Clear user action triggers the sync
- User can verify data before it's saved to sales

---

## Implementation Plan

### Task 1: Update import endpoint to create online_sales entries

**Files:**
- Modify: `backend/app/api/cash_difference.py:89-155` (import_cash_difference function)

**Logic:**
```python
# After creating CashDifference record, create/update online_sales

platform_mapping = {
    'pos_visa': 'Visa',
    'pos_nakit': 'Nakit',
    'pos_trendyol': 'Trendyol',
    'pos_getir': 'Getir',
    'pos_yemeksepeti': 'Yemek Sepeti',
    'pos_migros': 'Migros Yemek',
}

for field, platform_name in platform_mapping.items():
    amount = getattr(request, field)
    if amount and amount > 0:
        platform = db.query(OnlinePlatform).filter(OnlinePlatform.name == platform_name).first()
        if platform:
            # Upsert: update existing or create new
            existing = db.query(OnlineSale).filter(
                OnlineSale.branch_id == ctx.current_branch_id,
                OnlineSale.sale_date == request.difference_date,
                OnlineSale.platform_id == platform.id
            ).first()

            if existing:
                existing.amount = amount
            else:
                sale = OnlineSale(
                    branch_id=ctx.current_branch_id,
                    platform_id=platform.id,
                    sale_date=request.difference_date,
                    amount=amount,
                    created_by=ctx.user.id
                )
                db.add(sale)
```

### Task 2: Add sync_to_sales flag (optional control)

**Files:**
- Modify: `backend/app/api/cash_difference.py`

Add query parameter:
```python
sync_to_sales: bool = Query(default=True)
```

This allows users to import without syncing if needed.

### Task 3: Update frontend to show sync status

**Files:**
- Modify: `frontend/src/views/CashDifferenceImport.vue`

Add info message:
```
"İçe aktarma sonrasında bu değerler otomatik olarak Kasa Hareketleri'ne kaydedilecektir."
```

---

## Verification

After implementation:
1. Import a Kasa Farkı record via the modal
2. Check the dashboard - Visa and Nakit counters should reflect the imported POS values
3. Check Kasa Hareketleri page - entries should appear for that date

## Edge Cases

1. **Re-import same date:** Should update existing sales, not create duplicates
2. **Zero values:** Don't create sales entries for zero amounts
3. **Missing platforms:** Skip if platform doesn't exist (shouldn't happen with current setup)
