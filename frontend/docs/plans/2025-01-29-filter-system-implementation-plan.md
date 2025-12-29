# Filter System Implementation Plan

**Date:** 2025-01-29
**Status:** Implementation Ready
**Focus:** Tabs, Icons, Unified Filter Bar - AI features as optional extras

---

## Quick Decision Matrix

| Feature | Effort | Value | Decision |
|---------|--------|-------|----------|
| Turkish Locale | ⚡ Quick | High | ✅ **DO IT** (Done) |
| Icon System (Emoji) | ⚡ Quick | High | ✅ **DO IT** |
| TabBar Component | ⚡ Quick | High | ✅ **DO IT** |
| EntitySelector | Medium | High | ✅ **DO IT** |
| UnifiedPageLayout | Medium | High | ✅ **DO IT** |
| **Anomaly Detection** | ⚡ Quick | Medium | ✅ **QUICK WIN** |
| **Missing Data Warning** | ⚡ Quick | High | ✅ **QUICK WIN** (already exists!) |
| Smart Categorization | Hard | Medium | 🔮 Mock + Document |
| Demand Forecast | Hard | Low | 🔮 Mock + Document |
| Receipt OCR | Very Hard | Low | 🔮 Document only |

---

## Phase 1: Foundation (Day 1)

### 1.1 Icon System

```typescript
// frontend/src/src/icons.ts
export const ICONS = {
  // Navigation
  expenses: '💸',
  purchases: '🛒',
  personnel: '👥',
  production: '🏭',
  sales: '🛎️',
  settings: '⚙️',

  // Tabs
  employees: '👤',
  payroll: '💳',
  parttime: '⏱️',
  reports: '📊',

  // Actions
  add: '➕',
  edit: '✏️',
  delete: '🗑️',
  search: '🔍',
  filter: '🔽',
  export: '📤',
  settings: '⚙️',
  ai: '✨',

  // Status
  success: '✅',
  warning: '⚠️',
  error: '❌',
  info: 'ℹ️',
  loading: '⏳',

  // Time presets
  today: '📅',
  yesterday: '📆',
  thisWeek: '📅',
  thisMonth: '📊',
  thisYear: '📈',
  custom: '✏️',
} as const

export type IconName = keyof typeof ICONS
```

```vue
<!-- frontend/src/components/ui/Icon.vue -->
<template>
  <span class="icon" :class="sizeClass" v-if="isEmoji">{{ icon }}</span>
  <component v-else :is="icon" :class="sizeClass" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ICONS } from '@/icons'

const props = defineProps<{
  name: IconName | string
  size?: 'sm' | 'md' | 'lg'
}>()

const icon = computed(() => ICONS[props.name as IconName] || props.name)
const isEmoji = computed(() => !props.name.startsWith('svg-'))
const sizeClass = computed(() => `icon-${props.size || 'md'}`)
</script>

<style scoped>
.icon-sm { font-size: 14px; }
.icon-md { font-size: 18px; }
.icon-lg { font-size: 24px; }
.icon { display: inline-flex; align-items: center; justify-content: center; }
</style>
```

### 1.2 TabBar Component

```vue
<!-- frontend/src/components/ui/TabBar.vue -->
<template>
  <div class="tab-bar" v-if="tabs.length > 1">
    <button
      v-for="tab in tabs"
      :key="tab.id"
      @click="$emit('update:modelValue', tab.id)"
      :class="['tab-item', { active: modelValue === tab.id }]"
    >
      <span v-if="tab.icon" class="tab-icon">{{ tab.icon }}</span>
      <span class="tab-label">{{ tab.label }}</span>
      <span v-if="tab.badge" class="tab-badge">{{ tab.badge }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
interface Tab {
  id: string
  label: string
  icon?: string
  badge?: string | number
}

defineProps<{
  tabs: Tab[]
  modelValue: string
}>()

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<style scoped>
.tab-bar {
  display: flex;
  gap: 4px;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 16px;
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 12px 16px;
  border-bottom: 2px solid transparent;
  font-size: 14px;
  font-weight: 500;
  color: #6b7280;
  background: none;
  cursor: pointer;
  transition: all 0.15s;
}

.tab-item:hover {
  color: #374151;
  background: #f9fafb;
}

.tab-item.active {
  color: #dc2626;
  border-bottom-color: #dc2626;
}

.tab-icon { font-size: 16px; }
.tab-badge {
  background: #dc2626;
  color: white;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 9999px;
}
</style>
```

---

## Phase 2: Filter Components (Day 1-2)

### 2.1 EntitySelector Component

```vue
<!-- frontend/src/components/ui/EntitySelector.vue -->
<template>
  <div class="entity-selector">
    <select
      :value="modelValue"
      @change="$emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
      :class="['select-input', { 'has-settings': showSettings }]"
    >
      <option :value="allValue">{{ allLabel }}</option>
      <option v-for="item in items" :key="item.id" :value="item.id">
        {{ item.icon }} {{ item.label }}
        <template v-if="showCount && item.count !== undefined">
          ({{ item.count }})
        </template>
      </option>
    </select>
    <button
      v-if="showSettings"
      @click="$emit('settings')"
      class="settings-btn"
      title="Yönet"
    >
      ⚙️
    </button>
  </div>
</template>

<script setup lang="ts">
interface EntityItem {
  id: string | number
  label: string
  icon?: string
  count?: number
}

defineProps<{
  items: EntityItem[]
  modelValue: string | number | null
  allLabel?: string
  allValue?: null
  showSettings?: boolean
  showCount?: boolean
}>()

defineEmits<{
  'update:modelValue': [value: string | number | null]
  settings: []
}>()
</script>

<style scoped>
.entity-selector {
  display: flex;
  align-items: center;
  gap: 4px;
}

.select-input {
  background: #f3f4f6;
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  min-width: 160px;
}

.select-input.has-settings {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}

.settings-btn {
  background: #f3f4f6;
  border: none;
  border-radius: 8px;
  padding: 8px 10px;
  cursor: pointer;
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
}

.settings-btn:hover {
  background: #e5e7eb;
}
</style>
```

### 2.2 QuickActions Component

```vue
<!-- frontend/src/components/ui/QuickActions.vue -->
<template>
  <div class="quick-actions">
    <button
      v-if="showSearch"
      @click="$emit('search')"
      class="action-btn"
      title="Ara"
    >
      🔍
    </button>
    <button
      v-if="showExport"
      @click="$emit('export')"
      class="action-btn"
      title="Dışa Aktar"
    >
      📤
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  showSearch?: boolean
  showExport?: boolean
}>()

defineEmits<{
  search: []
  export: []
}>()
</script>

<style scoped>
.quick-actions {
  display: flex;
  gap: 4px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
}

.action-btn:hover {
  background: #f3f4f6;
}
</style>
```

---

## Phase 3: Unified Filter Bar (Day 2)

```vue
<!-- frontend/src/components/ui/UnifiedFilterBar.vue -->
<template>
  <div class="unified-filter-bar">
    <!-- Left: Date Filter + Entity Selector -->
    <div class="filter-left">
      <SingleRowDateFilter v-if="showDateFilter" v-model="localDateRange" :max-date="maxDate" />
      <EntitySelector
        v-if="entities"
        v-model="localEntityId"
        :items="entities.items"
        :all-label="entities.allLabel"
        :show-settings="entities.showSettings"
        :show-count="entities.showCount"
        @settings="$emit('entity-settings')"
      />
    </div>

    <!-- Center: Quick Actions -->
    <QuickActions
      v-if="quickActions"
      :show-search="quickActions.search"
      :show-export="quickActions.export"
      @search="$emit('search')"
      @export="$emit('export')"
    />

    <!-- Right: Primary Action -->
    <router-link
      v-if="primaryAction"
      :to="primaryAction.to || '#'"
      @click.prevent="primaryAction.onClick?.()"
      class="primary-action"
    >
      <span v-if="primaryAction.icon">{{ primaryAction.icon }}</span>
      <span>{{ primaryAction.label }}</span>
    </router-link>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { DateRangeValue } from '@/types/filters'

interface EntityConfig {
  items: Array<{ id: string | number; label: string; icon?: string; count?: number }>
  allLabel?: string
  showSettings?: boolean
  showCount?: boolean
}

interface ActionConfig {
  label: string
  icon?: string
  to?: string
  onClick?: () => void
}

const props = defineProps<{
  showDateFilter?: boolean
  dateRange?: DateRangeValue
  maxDate?: Date
  entities?: EntityConfig
  entityId?: string | number | null
  quickActions?: { search?: boolean; export?: boolean }
  primaryAction?: ActionConfig
}>()

const emit = defineEmits<{
  'update:dateRange': [value: DateRangeValue]
  'update:entityId': [value: string | number | null]
  'entity-settings': []
  search: []
  export: []
}>()

// Local state for v-model
const localDateRange = ref(props.dateRange || { mode: 'month', start: '', end: '' })
const localEntityId = ref(props.entityId || null)

watch(localDateRange, (val) => emit('update:dateRange', val))
watch(localEntityId, (val) => emit('update:entityId', val))
</script>

<style scoped>
.unified-filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 8px 12px;
  min-height: 42px;
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.primary-action {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #dc2626;
  color: white;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  white-space: nowrap;
  transition: background 0.15s;
}

.primary-action:hover {
  background: #b91c1c;
}
</style>
```

---

## Phase 4: Quick Win AI Features (Day 2)

### 4.1 InsightBanner Component (Mock-Ready)

```vue
<!-- frontend/src/components/ui/InsightBanner.vue -->
<template>
  <Transition name="slide">
    <div v-if="show && insight" :class="['insight-banner', `insight-${insight.type}`]">
      <span class="insight-icon">{{ insight.icon }}</span>
      <div class="insight-content">
        <p class="insight-title">{{ insight.title }}</p>
        <p v-if="insight.detail" class="insight-detail">{{ insight.detail }}</p>
      </div>
      <button v-if="insight.action" @click="insight.action.onClick" class="insight-action">
        {{ insight.action.label }}
      </button>
      <button @click="dismiss" class="insight-dismiss">✕</button>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface InsightAction {
  label: string
  onClick: () => void
}

interface Insight {
  type: 'info' | 'warning' | 'success' | 'error'
  icon: string
  title: string
  detail?: string
  action?: InsightAction
}

const props = defineProps<{
  insight: Insight | null
  dismissible?: boolean
}>()

const show = ref(true)

const dismiss = () => {
  if (props.dismissible !== false) {
    show.value = false
  }
}
</script>

<style scoped>
.insight-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 14px;
}

.insight-info { background: #eff6ff; color: #1e40af; }
.insight-warning { background: #fefce8; color: #a16207; }
.insight-success { background: #f0fdf4; color: #166534; }
.insight-error { background: #fef2f2; color: #991b1b; }

.insight-icon { font-size: 18px; }
.insight-content { flex: 1; }
.insight-title { font-weight: 500; }
.insight-detail { font-size: 13px; opacity: 0.9; }

.insight-action {
  background: white;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
}

.insight-dismiss {
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0.6;
  font-size: 16px;
  padding: 4px;
}

.insight-dismiss:hover { opacity: 1; }

.slide-enter-active, .slide-leave-active { transition: all 0.2s; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translateY(-10px); }
</style>
```

### 4.2 Quick Win: Missing Data Warning (Already in Personnel!)

```typescript
// composable/useMissingDataWarning.ts
import { computed } from 'vue'

export function useMissingDataWarning<T extends { id: number | string }>(
  allItems: T[],
  processedItems: T[],
  itemLabel: string
) {
  const missingItems = computed(() => {
    const processedIds = new Set(processedItems.map(i => i.id))
    return allItems.filter(i => !processedIds.has(i.id))
  })

  const warning = computed(() => {
    if (missingItems.value.length === 0) return null
    return {
      type: 'warning' as const,
      icon: '⚠️',
      title: `${missingItems.value.length} ${itemLabel} bu ay için eksik`,
      detail: missingItems.value.map(i => (i as any).name).join(', '),
      dismissible: true
    }
  })

  return { missingItems, warning }
}
```

### 4.3 Quick Win: Anomaly Detection for Expenses

```typescript
// utils/anomalyDetection.ts
export function detectExpenseAnomalies(
  expenses: Array<{ amount: number; category?: string }>,
  threshold = 2.0
) {
  if (expenses.length < 3) return []

  // Calculate average per category
  const byCategory = new Map<string, number[]>()
  expenses.forEach(e => {
    const cat = e.category || 'uncategorized'
    if (!byCategory.has(cat)) byCategory.set(cat, [])
    byCategory.get(cat)!.push(e.amount)
  })

  const anomalies: Array<{ expense: typeof expenses[0]; reason: string }> = []

  byCategory.forEach((amounts, category) => {
    const avg = amounts.reduce((a, b) => a + b, 0) / amounts.length
    expenses.forEach(e => {
      if (e.amount > avg * threshold) {
        anomalies.push({
          expense: e,
          reason: `${category} kategorisi ortalamasının ${threshold}x üzerinde`
        })
      }
    })
  })

  return anomalies
}
```

---

## Phase 5: Page Migrations (Day 3+)

### Migration Order

1. **Expenses.vue** (Simple - no tabs)
   - Replace filter section with UnifiedFilterBar
   - Add icons to summary cards
   - Test: Everything works as before

2. **Personnel.vue** (Complex - 3 tabs)
   - Add TabBar component
   - Migrate each tab's filter section
   - Preserve existing "missing payroll" warning (it's good!)
   - Test: Tab switching, filters, warnings

3. **Purchases.vue** (Simple)
4. **StaffMeals.vue** (Simple)
5. **CourierExpenses.vue** (Simple)
6. **Production.vue** (Simple)
7. **CashDifference.vue** (Simple)
8. **UnifiedSales.vue** (Simple)

---

## Files to Create

```
frontend/src/
├── icons.ts                           # Icon registry
├── components/ui/
│   ├── Icon.vue                       # Icon component
│   ├── TabBar.vue                     # Tab navigation
│   ├── EntitySelector.vue             # Entity dropdown
│   ├── QuickActions.vue               # Search/export buttons
│   ├── UnifiedFilterBar.vue           # Complete filter bar
│   └── InsightBanner.vue              # AI/Warning banner
├── composables/
│   └── useMissingDataWarning.ts       # Missing data composable
└── utils/
    └── anomalyDetection.ts            # Simple anomaly detection
```

## Files to Modify

```
frontend/src/
├── components/ui/index.ts             # Export new components
├── views/
│   ├── Expenses.vue                   # Migrate to UnifiedFilterBar
│   ├── Personnel.vue                  # Add TabBar + migrate
│   ├── Purchases.vue                  # Migrate
│   └── ... (remaining pages)
```

---

## Success Criteria (Simplified)

- [ ] Turkish locale working in datepicker ✅ (Done)
- [ ] Icon system created and exported
- [ ] TabBar works on Personnel page
- [ ] UnifiedFilterBar works on Expenses page
- [ ] EntitySelector with settings button
- [ ] InsightBanner shows warnings (real or mock)
- [ ] All pages migrated
- [ ] Build passes, no errors

---

## Mock AI Features (Document Only)

| Feature | Mock Implementation | Real Implementation Later |
|---------|---------------------|---------------------------|
| Smart Categorization | Random category suggestion | ML model based on descriptions |
| Demand Forecast | Linear extrapolation | Time-series ML model |
| Receipt OCR | Manual entry form | OCR API integration |
| Supplier Ratings | Static stars | Performance metrics calculation |

---

## Open Questions (Simplified)

1. **Tab Persistence**: Remember last tab? → Default: yes
2. **Icons**: Emojis ok? → Default: yes, simple
3. **AI Warnings**: Show all or dismissible? → Default: dismissible
