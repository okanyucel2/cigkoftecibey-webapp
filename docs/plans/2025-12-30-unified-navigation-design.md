# Unified Navigation & Design System

> **Created:** 2025-12-30
> **Status:** Design Approved
> **Next:** Implementation via superpowers:writing-plans

---

## 🎯 Goal

Simplify navigation from 9 menu items to 4 main categories using vertical sub-navigation, while establishing a consistent design system across all views.

**Current State:** 9 separate menu items
**Target State:** 4 main categories with nested tabs

---

## 📊 New Menu Structure

| Menu Item | Route | Sub-Tabs |
|-----------|-------|----------|
| 📊 **Bilanço** | `/` | - (unchanged) |
| 💸 **Giderler** | `/giderler` | • Mal Alımları<br>• Hizmet Alımları<br> ├─ Personel İaşe<br> └─ Kurye Hizmetleri<br>• Üretim (Leğen)<br>• Genel Giderler |
| 💰 **Gelirler** | `/gelirler` | • Kasa Hareketleri<br>• Kasa Farkı |
| 👤 **Personel** | `/personel` | • Çalışanlar<br>• Maaş/Ödemeler<br>• Part-time Giderleri |

**Migration:**
- `Purchases.vue` → `Giderler` → `Mal Alımları`
- `StaffMeals.vue` → `Giderler` → `Hizmet Alımları` → `Personel İaşe`
- `CourierExpenses.vue` → `Giderler` → `Hizmet Alımları` → `Kurye Hizmetleri`
- `Production.vue` → `Giderler` → `Üretim`
- `Expenses.vue` → `Giderler` → `Genel Giderler`
- `UnifiedSales.vue` → `Gelirler` → `Kasa Hareketleri`
- `CashDifference.vue` → `Gelirler` → `Kasa Farkı`
- `Personnel.vue` → `Personel` → (tabs preserved)

---

## 🏗️ Page Skeleton

```
┌─────────────────────────────────────────────────────────────┐
│  [PAGE TITLE]                                              │
│  ─────────────────────────────────────────────────────────  │
│                                                              │
│  ┌───────────────────────┬────────────────────────────────┐ │
│  │                       │                                │ │
│  │  [SUB NAV - Vertical] │   [UNIFIED FILTER BAR]         │ │
│  │                       │   - Date Range                │ │
│  │  📦 Tab 1            │   - Entity Filter (optional)   │ │
│  │  🍽️ Tab 2            │   - Primary Action Button     │ │
│  │     ├─ SubTab A      │                                │ │
│  │     └─ SubTab B      │   [SUMMARY CARDS] (optional)   │ │
│  │  🥙 Tab 3            │   ┌────┐ ┌────┐ ┌────┐        │ │
│  │                       │   │ K1 │ │ K2 │ │ K3 │        │ │
│  │                       │   └────┘ └────┘ └────┘        │ │
│  │                       │                                │ │
│  │                       │   [MAIN CONTENT]              │ │
│  │                       │   - Table / Cards / Chart     │ │
│  │                       │                                │ │
│  └───────────────────────┴────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Standard Sections

| Section | Component | Required | Description |
|---------|-----------|----------|-------------|
| Page Title | `PageHeader` | ✅ | H1 + description |
| Sub Navigation | `VerticalNav` | ⚠️ | If tabs exist |
| Filter Bar | `UnifiedFilterBar` | ✅ | All list views |
| Summary Cards | `SummaryCard[]` | ⚠️ | If statistics exist |
| Main Content | Table/Cards/Chart | ✅ | Primary content |
| Modals | `PageModal` | ⚠️ | If forms exist |

---

## 🧩 Component Standards

### UnifiedFilterBar (All list views)

```typescript
interface FilterConfig {
  dateRange: {
    mode: 'month' | 'range' | 'custom'
    start: string
    end: string
  }
  entityFilter?: {
    entityId: number | null
    entities: EntityConfig
  }
  primaryAction: {
    label: string  // No "+" prefix, no icon
    onClick: () => void
  }
}
```

**Standard Labels:** `Yeni Kayıt`, `Kayıt Ekle`, `Veri Yükle` (NOT `+ Yeni Kayıt`)

### SummaryCard (Max 4 cards)

```typescript
interface SummaryCardProps {
  label: string
  value: string | number
  subtext?: string
  variant?: 'default' | 'primary' | 'danger' | 'purple' | 'info'
}
```

**Variant Usage:**
| Variant | Color | Use Case |
|---------|-------|----------|
| `default` | Gray | Neutral data |
| `primary` | Blue | Main metrics |
| `danger` | Red | Expenses, negatives |
| `purple` | Purple | Fixed expenses, special |
| `info` | Teal | Averages, helpers |

### PageModal (Forms)

```typescript
interface ModalConfig {
  show: boolean
  title: string
  size: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  onClose: () => void
}
```

**Size Guidelines:**
- `sm` → Single field (delete confirmation)
- `md` → 2-3 fields
- `lg` → 4-6 fields (standard entry form)
- `xl` → 7-10 fields
- `full` → Complex forms (exceptional)

### VerticalNav (New component)

```typescript
interface NavItem {
  id: string
  label: string
  icon?: string  // Emoji optional
  subItems?: NavItem[]  // Nested items
}

interface VerticalNavProps {
  modelValue: string
  items: NavItem[]
  collapsible?: boolean  // For mobile
}
```

### DataTable (Standard table structure)

- `<thead>` with `bg-gray-50`
- `<tbody>` with `divide-y divide-gray-200`
- Rows: `hover:bg-gray-50`
- Standard column alignment: left (text), right (numbers)

---

## 🎨 Visual Standards

### Color Palette

| Purpose | Color | Usage |
|---------|-------|-------|
| Primary | Brand Red | Buttons, active menu |
| Danger | Red | Expenses, delete |
| Success | Green | Positive deltas |
| Warning | Yellow/Orange | Warnings |
| Info | Teal/Blue | Info, helpers |
| Neutral | Gray | Neutral content |

### Spacing

- Between cards: `gap-4` (16px)
- Between sections: `space-y-6` (24px)
- Padding: `p-6` (24px)
- Items within section: `space-y-4` (16px)

### Typography

- **Page Title**: `text-2xl font-display font-bold`
- **Section Title**: `text-lg font-semibold`
- **Card Label**: `text-sm font-medium text-gray-700`
- **Table Header**: `text-xs font-medium text-gray-500 uppercase`

### Animations

- Tab switch: fade-in (100-150ms)
- Modal open: scale + fade (200ms)
- Hover: background color (150ms)
- Loading: skeleton or spinner

### Responsive

- Mobile (<640px): Single column, stacked
- Tablet (640-1024px): 2 column grid
- Desktop (1024+): Sidebar + main content

### Loading & Empty States

- **Loading**: Skeleton matching data structure
- **Empty**: Icon + description + "create first record" CTA
- **Error**: ErrorAlert component

---

## 🔄 State Management Pattern

### Every View Has

```typescript
const data = ref<T[]>([])
const loading = ref(true)
const error = ref('')
const filters = ref<FilterConfig>(...)
const showModal = ref(false)

// For tabbed views
const activeTab = ref<string>('default')
```

### Data Loading Pattern

1. Load data on `onMounted`
2. Reload on filter change via `watch`
3. Reload after form submit

### API Error Pattern

```typescript
try {
  await api.call(params)
} catch (e) {
  error.value = e.response?.data?.detail || 'Operation failed'
}
```

### Form State Pattern

```typescript
const form = ref({ ...initialValues })
const submitting = ref(false)
const editingId = ref<number | null>(null)

function handleSubmit() { /* validate + submit */ }
function closeModal() { /* close + reset */ }
```

### Tab State (VerticalNav)

```typescript
const activeTab = ref('tab-id')

// Sync with URL (recommended)
watch(activeTab, () => {
  router.replace({ query: { tab: activeTab.value } })
})
```

---

## 🌐 URL Structure

### Giderler
- `/giderler/mal-alim`
- `/giderler/hizmet-alim/personel-ias`
- `/giderler/hizmet-alim/kurye`
- `/giderler/uretim`
- `/giderler/genel`

### Gelirler
- `/gelirler/kasa`
- `/gelirler/kasa-farki`

### Personel
- `/personel/calisanlar`
- `/personel/maas`
- `/personel/part-time`

### Browser Support

- ✅ Back/forward buttons work
- ✅ URLs are shareable
- ✅ Page reload preserves tab state

---

## 📱 Mobile Navigation

- Desktop: Vertical sub-nav on left
- Mobile: Horizontal scrollable tabs or dropdown
- Sub-tabs NOT in hamburger menu (inside page)

---

## 🚀 Implementation Approach

**Recommended:** Single Component + State Management

**Reasoning:**
1. Full animation control
2. Easy state sharing
3. Manual URL sync possible
4. Less boilerplate than nested routes

---

## 📋 New Components Needed

| Component | File | Priority |
|-----------|------|----------|
| `VerticalNav` | `src/components/ui/VerticalNav.vue` | P0 |
| `PageHeader` | `src/components/ui/PageHeader.vue` | P1 |
| `SummaryCards` | `src/components/ui/SummaryCards.vue` | P1 |
| `GiderlerView` | `src/views/Giderler.vue` | P0 |
| `GelirlerView` | `src/views/Gelirler.vue` | P0 |

---

## ✅ Acceptance Criteria

1. [ ] Sidebar has 4 main menu items (down from 9)
2. [ ] All views share the same skeleton structure
3. [ ] All components follow styling standards
4. [ ] URL routing works with browser back/forward
5. [ ] Mobile responsive
6. [ ] All existing functionality preserved
7. [ ] Loading/empty states consistent
8. [ ] No hardcoded "+" or icons in button labels

---

## 📝 Notes

- **Bilanço page remains unchanged** - user explicitly requested
- **Service Alımları** groups Staff Meals + Courier Expenses under one logical category
- **Üretim** moved under Giderler as it's also an operational cost
- **All entry forms** use modal approach (no page navigation for new records)
