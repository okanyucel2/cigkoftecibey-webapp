---
title: ADR-001 - Menu System with Branch-Specific Pricing
date: 2026-01-14
status: implemented
decision_makers: [okan.yucel, MAX]
related_commits: [d90ddf5, e32f068, acf40c0]
---

# ADR-001: Menu System with Branch-Specific Pricing

## Context

Cigkofteci Bey restaurant management system needs a menu management feature that supports:
1. Organizing menu items into categories
2. Branch-specific pricing (same item can have different prices at different branches)
3. Default prices that apply when no branch-specific price exists

**Key Question:** How to implement branch-specific pricing without data duplication?

## Decision

Implement **normalized two-table design** with price resolution logic:

### Data Model

```
┌─────────────────────────────────────────┐
│ MenuCategory                            │
│ - id, name, description                 │
│ - branch_id (NULL = global)             │
│ - display_order, is_active, is_system   │
└─────────────────────────────────────────┘
                    │
                    │ 1:N
                    ▼
┌─────────────────────────────────────────┐
│ MenuItem                                │
│ - id, category_id, name, description    │
│ - image_url, display_order, is_active   │
│ - created_by, created_at                │
└─────────────────────────────────────────┘
                    │
                    │ 1:N
                    ▼
┌─────────────────────────────────────────┐
│ MenuItemPrice                           │
│ - id, menu_item_id                      │
│ - branch_id (NULL = default price)      │
│ - price                                 │
│ UNIQUE(menu_item_id, branch_id)         │
└─────────────────────────────────────────┘
```

### Price Resolution Algorithm

```python
def resolve_price(item_id, branch_id):
    # 1. Try branch-specific price
    branch_price = get_price(item_id, branch_id)
    if branch_price:
        return (branch_price, is_default=False)

    # 2. Fall back to default price
    default_price = get_price(item_id, branch_id=NULL)
    if default_price:
        return (default_price, is_default=True)

    # 3. No price set
    return (None, None)
```

## Alternatives Considered

### Option A: Price on MenuItem with branch_id
- Each branch has its own MenuItem record
- **Rejected:** Causes data duplication (name, description, image repeated)

### Option B: MenuItem + MenuItemPrice (SELECTED)
- Single MenuItem record
- Separate prices per branch
- **Selected:** Normalized, no duplication, flexible

### Option C: MenuItem + price override table
- Default price on MenuItem
- Override table for exceptions
- **Rejected:** Less flexible, harder to query

## API Design

### Menu Items CRUD
```
GET    /api/v1/menu-items                    # List with resolved prices
GET    /api/v1/menu-items/{id}               # Single item with price
POST   /api/v1/menu-items                    # Create item
PUT    /api/v1/menu-items/{id}               # Update item
DELETE /api/v1/menu-items/{id}               # Delete item
```

### Price Management
```
GET    /api/v1/menu-items/{id}/prices        # All prices for item
PUT    /api/v1/menu-items/{id}/prices        # Set/update price
DELETE /api/v1/menu-items/{id}/prices/{bid}  # Remove branch override
```

### Response Schema
```json
{
  "id": 1,
  "name": "Cig Kofte Durum",
  "category_id": 1,
  "image_url": "/images/durum.jpg",
  "price": 85.00,
  "price_is_default": true,
  "is_active": true
}
```

## Implementation Details

### Files Modified/Created

| File | Change |
|------|--------|
| `app/models/__init__.py` | Added MenuItem, MenuItemPrice models |
| `app/schemas/__init__.py` | Added schemas with price fields |
| `app/api/menu_items.py` | Full CRUD + price endpoints |
| `app/api/menu_categories.py` | Category CRUD |
| `tests/test_menu_items.py` | 26 TDD tests |
| `tests/test_menu_categories.py` | 24 TDD tests |
| `alembic/versions/o6p7q8r9s014_*.py` | MenuCategory migration |
| `alembic/versions/p7q8r9s0t015_*.py` | MenuItem migration |
| `alembic/versions/q8r9s0t1u016_*.py` | MenuItemPrice migration |

### Test Coverage

| Category | Tests | Status |
|----------|-------|--------|
| MenuCategory GET | 6 | PASS |
| MenuCategory POST | 6 | PASS |
| MenuCategory PUT | 6 | PASS |
| MenuCategory DELETE | 5 | PASS |
| MenuItem GET | 8 | PASS |
| MenuItem POST | 4 | PASS |
| MenuItem PUT | 3 | PASS |
| MenuItem DELETE | 2 | PASS |
| Prices | 9 | PASS |
| **Total** | **50** | **PASS** |

## Future Enhancements (Not Implemented)

Per brainstorming session, the following were noted for future:
- `preparation_time` - Estimated prep time
- `calories` - Nutritional info
- `allergens` - Allergy warnings
- `ingredients` - Ingredient list
- `is_vegetarian`, `is_spicy` - Dietary flags
- `sku_code` - Inventory integration

## Consequences

### Positive
- No data duplication for multi-branch pricing
- Easy to add/remove branch-specific prices
- Default price provides fallback
- API returns resolved price (no client-side logic needed)

### Negative
- Extra JOIN for price resolution (mitigated by index)
- More complex migration if changing pricing model

## References

- Commit: `d90ddf5` - Menu categories feature
- Commit: `e32f068` - Menu categories migration
- Commit: `acf40c0` - Menu items with branch pricing
