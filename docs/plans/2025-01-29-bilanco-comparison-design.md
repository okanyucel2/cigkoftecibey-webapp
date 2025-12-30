# Bilanco Comparison View Design

**Date:** 2025-01-29
**Status:** Approved
**Designer:** Claude + User

## Overview

Redesign Bilanco page from chronological scroll to **comparative side-by-side view**. Users can compare any two time periods with unified date picker and see delta indicators at a glance.

## Problem Statement

Current Bilanco page shows 4 sections vertically (Bugün → Dün → Hafta → Ay). Users cannot compare periods without scrolling, making analysis difficult.

## Solution

Side-by-side comparison cards with:
- Unified comparison mode selector
- Left period card | Right period card
- Delta band in between showing % differences
- All metrics visible on single screen

---

## Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│  🚀 Hızlı İşlemler (Quick Actions)                              │
│  [Kasa Girişi] [Mal Alımı] [Gider Ekle] [Üretim Gir]            │
├─────────────────────────────────────────────────────────────────┤
│  📅 Comparison Mode Selector                                    │
│  [Bugün vs Dün ▼]                                               │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────── ∆ Delta ─────────────────────────┐ │
│  │  Left Period               │  Right Period                 │ │
│  │  [Revenue Cards]           │  [Revenue Cards]             │ │
│  │  [Expense Cards]           │  [Expense Cards]             │ │
│  │  [Profit Cards]            │  [Profit Cards]              │ │
│  └────────────────────────────┴──────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  📊 Weekly Trend Chart (optional, below fold)                   │
├─────────────────────────────────────────────────────────────────┤
│  🤖 AI Asistan                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Comparison Modes

| Mode | Left Period | Right Period |
|------|-------------|--------------|
| Bugün vs Dün | Bugün | Dün |
| Bu Hafta vs Geçen Hafta | Current week (Mon-Sun) | Previous week |
| Bu Ay vs Geçen Ay | Current month | Previous month |
| Son 7 Gün vs Önceki 7 Gün | Last 7 days | Previous 7 days |
| Son 30 Gün vs Önceki 30 Gün | Last 30 days | Previous 30 days |
| Özel Karşılaştırma | User selected range 1 | User selected range 2 |

---

## Card Structure

Each comparison card contains:

### 1. Header
- Period icon (⏰/📅/📊)
- Period name + date range
- Comparison badge (if applicable)

### 2. Revenue Section
```
💳 Ciro Kanalları
┌─────────┬─────────┬─────────┐
│ 💳 Visa │ 💵 Nakit│ 📱Online│
│  45.000₺│  12.000₺│  8.500₺│
└─────────┴─────────┴─────────┘

💰 Toplam Ciro: 65.500 ₺
```

### 3. Expenses Section
```
📦 Gider Breakdown
Mal: 18.000  Gider: 3.500
Personel: 2.100  Kurye: 800
Part-time: 600  Üretim: 4.200

📦 Toplam Gider: 29.200 ₺
```

### 4. Profit Section
```
📈 Net Kar: 36.300 ₺
Karlılık: %55
```

---

## Delta Indicators

Delta band between cards shows:

| Metric | Format | Color |
|--------|--------|-------|
| Ciro farkı | ▲ %17.5 (▲ +9.800₺) | Green if ↑, Red if ↓ |
| Gider farkı | ▼ %5.0 (▼ -1.500₺) | Red if ↑, Green if ↓ |
| Kar farkı | ▲ %19.8 (▲ +6.000₺) | Green if ↑, Red if ↓ |
| Karlılık | → +1.0pp | Yellow if ±2% |

**Color Logic:**
- 🟢 Green (▲): Positive change (revenue up, profit up, expenses down)
- 🔴 Red (▼): Negative change (revenue down, profit down, expenses up)
- 🟡 Yellow (→): Neutral / minor change (±2%)

---

## Component Architecture

### New Components

1. **ComparisonModeSelector.vue**
   - Dropdown with predefined comparison modes
   - Custom range picker (dual date inputs)
   - V-model: `comparisonMode`

2. **ComparisonCard.vue**
   - Props: `period`, `data`, `label`, `icon`
   - Slots: `header`, `revenue`, `expenses`, `profit`
   - Revenue, Expenses, Profit subsections

3. **DeltaBand.vue**
   - Props: `leftData`, `rightData`
   - Computed deltas for all metrics
   - Color-coded indicators

### Modified Components

1. **Bilanco.vue** - Major refactor
   - Add ComparisonModeSelector
   - Replace 4 static sections with dynamic ComparisonCards
   - Add DeltaBand between cards
   - Keep QuickActions and SmartInsightCard

2. **UnifiedFilterBar.vue** - Extension
   - Add `comparison-mode` prop support
   - Or create separate BilancoFilterBar for this use case

---

## API Changes

### New Endpoint

```
GET /api/v1/reports/bilanco-compare
```

**Query Parameters:**
- `left_start`: ISO date string
- `left_end`: ISO date string
- `right_start`: ISO date string
- `right_end`: ISO date string

**Response:**
```json
{
  "left": {
    "period_label": "Bugün",
    "revenue_breakdown": { "visa": 45000, "nakit": 12000, "online": 8500 },
    "total_revenue": 65500,
    "expense_breakdown": { "mal_alimi": 18000, "gider": 3500, ... },
    "total_expenses": 29200,
    "net_profit": 36300,
    "profit_margin": 55
  },
  "right": {
    "period_label": "Dün",
    "revenue_breakdown": { "visa": 38000, "nakit": 10500, "online": 7200 },
    "total_revenue": 55700,
    "expense_breakdown": { "mal_alimi": 15200, "gider": 4200, ... },
    "total_expenses": 25400,
    "net_profit": 30300,
    "profit_margin": 54
  }
}
```

### Existing Endpoint (Keep for backward compatibility)

```
GET /api/v1/reports/bilanco (current endpoint - keep unchanged)
```

---

## Implementation Phases

### Phase 1: Backend API
1. Create `bilanco-compare` endpoint
2. Add date range calculation utilities
3. Test with various comparison modes

### Phase 2: Frontend Components
1. Create ComparisonModeSelector component
2. Create ComparisonCard component
3. Create DeltaBand component

### Phase 3: Page Refactor
1. Refactor Bilanco.vue with new layout
2. Wire up comparison mode selector
3. Add API integration

### Phase 4: Polish
1. Add loading states
2. Add error handling
3. Responsive design adjustments
4. Animation transitions

---

## Success Criteria

- [ ] All comparison modes work correctly
- [ ] Custom range selection functional
- [ ] Delta indicators accurate and color-coded
- [ ] All metrics visible on single screen (no scroll for comparison)
- [ ] Mobile responsive
- [ ] Loading states smooth
- [ ] Backward compatible with existing bilanco endpoint

---

## Open Questions

1. Should weekly trend chart remain below fold or be removed? → **Decision: Keep below fold as optional context**
2. Should there be a "toggle" to switch between old (chronological) and new (comparison) views? → **Decision: No, fully replace with new design**
3. Should comparison selection persist across page navigation? → **Decision: Yes, store in localStorage**
