# Bilanco Comparison View Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform Bilanco page from chronological vertical scroll to side-by-side comparison view with unified date picker and delta indicators.

**Architecture:** Frontend-first approach. Create new Vue components (ComparisonModeSelector, ComparisonCard, DeltaBand), refactor Bilanco.vue to use them. Backend API endpoint will be added to support comparison data fetching.

**Tech Stack:** Vue 3 Composition API, TypeScript, Tailwind CSS, FastAPI (Python), SQLAlchemy

---

## Task 1: Create ComparisonModeSelector Component

**Files:**
- Create: `frontend/src/components/ui/ComparisonModeSelector.vue`
- Create: `frontend/src/types/comparison.ts` (new types)

**Step 1: Create comparison types**

```typescript
// frontend/src/types/comparison.ts
export type ComparisonMode =
  | 'today_vs_yesterday'
  | 'this_week_vs_last_week'
  | 'this_month_vs_last_month'
  | 'last_7_vs_previous_7'
  | 'last_30_vs_previous_30'
  | 'custom'

export interface ComparisonPeriod {
  label: string
  start: string // ISO date
  end: string   // ISO date
}

export interface ComparisonConfig {
  mode: ComparisonMode
  leftPeriod: ComparisonPeriod
  rightPeriod: ComparisonPeriod
}

export interface ComparisonModeOption {
  value: ComparisonMode
  label: string
  description: string
  icon: string
}
```

**Step 2: Create ComparisonModeSelector component**

```vue
<!-- frontend/src/components/ui/ComparisonModeSelector.vue -->
<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { ComparisonMode, ComparisonModeOption, ComparisonPeriod, ComparisonConfig } from '@/types/comparison'

const props = defineProps<{
  modelValue: ComparisonConfig
}>()

const emit = defineEmits<{
  'update:modelValue': [value: ComparisonConfig]
}>()

const isOpen = ref(false)

const modes: ComparisonModeOption[] = [
  { value: 'today_vs_yesterday', label: 'Bugün vs Dün', description: 'Son iki günün karşılaştırması', icon: '⏰' },
  { value: 'this_week_vs_last_week', label: 'Bu Hafta vs Geçen Hafta', description: 'Haftalık trend comparison', icon: '📊' },
  { value: 'this_month_vs_last_month', label: 'Bu Ay vs Geçen Ay', description: 'Aylık performans karşılaştırması', icon: '📆' },
  { value: 'last_7_vs_previous_7', label: 'Son 7 Gün vs Önceki 7 Gün', description: 'İki haftalık periyot comparison', icon: '📅' },
  { value: 'last_30_vs_previous_30', label: 'Son 30 Gün vs Önceki 30 Gün', description: 'Aylık periyot comparison', icon: '📈' },
  { value: 'custom', label: 'Özel Karşılaştırma', description: 'Kendi tarih aralıklarını seç', icon: '🎯' }
]

const selectedMode = computed<ComparisonMode>({
  get: () => props.modelValue.mode,
  set: (mode) => updateConfig(mode)
})

// Custom range inputs
const customLeftStart = ref('')
const customLeftEnd = ref('')
const customRightStart = ref('')
const customRightEnd = ref('')

function getPeriodForMode(mode: ComparisonMode): { left: ComparisonPeriod, right: ComparisonPeriod } {
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  const getWeekRange = (date: Date) => {
    const d = new Date(date)
    const day = d.getDay()
    const diff = d.getDate() - day + (day === 0 ? -6 : 1)
    const monday = new Date(d.setDate(diff))
    const sunday = new Date(monday)
    sunday.setDate(sunday.getDate() + 6)
    return {
      start: monday.toISOString().split('T')[0],
      end: sunday.toISOString().split('T')[0]
    }
  }

  const getMonthRange = (date: Date) => {
    return {
      start: new Date(date.getFullYear(), date.getMonth(), 1).toISOString().split('T')[0],
      end: new Date(date.getFullYear(), date.getMonth() + 1, 0).toISOString().split('T')[0]
    }
  }

  const getLastNDays = (n: number) => {
    const end = new Date(today)
    const start = new Date(today)
    start.setDate(start.getDate() - n + 1)
    return {
      start: start.toISOString().split('T')[0],
      end: end.toISOString().split('T')[0]
    }
  }

  const getPreviousNDays = (n: number) => {
    const end = new Date(today)
    end.setDate(end.getDate() - n)
    const start = new Date(end)
    start.setDate(start.getDate() - n + 1)
    return {
      start: start.toISOString().split('T')[0],
      end: end.toISOString().split('T')[0]
    }
  }

  switch (mode) {
    case 'today_vs_yesterday':
      return {
        left: { label: 'Bugün', start: today.toISOString().split('T')[0], end: today.toISOString().split('T')[0] },
        right: { label: 'Dün', start: yesterday.toISOString().split('T')[0], end: yesterday.toISOString().split('T')[0] }
      }
    case 'this_week_vs_last_week':
      const thisWeek = getWeekRange(today)
      const lastWeekStart = new Date(today)
      lastWeekStart.setDate(lastWeekStart.getDate() - 7)
      const lastWeek = getWeekRange(lastWeekStart)
      return {
        left: { label: 'Bu Hafta', ...thisWeek },
        right: { label: 'Geçen Hafta', ...lastWeek }
      }
    case 'this_month_vs_last_month':
      const thisMonth = getMonthRange(today)
      const lastMonthDate = new Date(today.getFullYear(), today.getMonth() - 1, 1)
      const lastMonth = getMonthRange(lastMonthDate)
      return {
        left: { label: 'Bu Ay', ...thisMonth },
        right: { label: 'Geçen Ay', ...lastMonth }
      }
    case 'last_7_vs_previous_7':
      const last7 = getLastNDays(7)
      const prev7 = getPreviousNDays(7)
      return {
        left: { label: 'Son 7 Gün', ...last7 },
        right: { label: 'Önceki 7 Gün', ...prev7 }
      }
    case 'last_30_vs_previous_30':
      const last30 = getLastNDays(30)
      const prev30 = getPreviousNDays(30)
      return {
        left: { label: 'Son 30 Gün', ...last30 },
        right: { label: 'Önceki 30 Gün', ...prev30 }
      }
    case 'custom':
      return {
        left: { label: 'Özel Aralık (Sol)', start: customLeftStart.value, end: customLeftEnd.value },
        right: { label: 'Özel Aralık (Sağ)', start: customRightStart.value, end: customRightEnd.value }
      }
    default:
      return {
        left: { label: '-', start: '', end: '' },
        right: { label: '-', start: '', end: '' }
      }
  }
}

function updateConfig(mode: ComparisonMode) {
  const periods = getPeriodForMode(mode)
  emit('update:modelValue', {
    mode,
    leftPeriod: periods.left,
    rightPeriod: periods.right
  })
}

const selectedModeLabel = computed(() => {
  return modes.find(m => m.value === props.modelValue.mode)?.label || ''
})

function selectMode(mode: ComparisonMode) {
  selectedMode.value = mode
  isOpen.value = false
}

function applyCustomRange() {
  if (customLeftStart.value && customLeftEnd.value && customRightStart.value && customRightEnd.value) {
    updateConfig('custom')
    isOpen.value = false
  }
}
</script>

<template>
  <div class="relative">
    <button
      @click="isOpen = !isOpen"
      class="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
    >
      <span class="text-lg">📅</span>
      <span class="font-medium text-gray-700">{{ selectedModeLabel }}</span>
      <span class="text-gray-400">{{ isOpen ? '▲' : '▼' }}</span>
    </button>

    <div
      v-if="isOpen"
      class="absolute z-50 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-lg max-h-96 overflow-y-auto"
    >
      <!-- Predefined modes -->
      <div class="p-2">
        <button
          v-for="mode in modes.slice(0, -1)"
          :key="mode.value"
          @click="selectMode(mode.value)"
          class="w-full text-left px-3 py-2 hover:bg-gray-50 rounded-lg transition-colors"
          :class="{ 'bg-gray-100': modelValue.mode === mode.value }"
        >
          <div class="flex items-center gap-2">
            <span class="text-lg">{{ mode.icon }}</span>
            <div>
              <p class="font-medium text-gray-900">{{ mode.label }}</p>
              <p class="text-xs text-gray-500">{{ mode.description }}</p>
            </div>
          </div>
        </button>
      </div>

      <div class="border-t border-gray-200"></div>

      <!-- Custom range -->
      <div class="p-3">
        <button
          @click="() => { /* open custom picker */ }"
          class="w-full text-left px-3 py-2 hover:bg-gray-50 rounded-lg transition-colors"
          :class="{ 'bg-gray-100': modelValue.mode === 'custom' }"
        >
          <div class="flex items-center gap-2">
            <span class="text-lg">{{ modes[5].icon }}</span>
            <div>
              <p class="font-medium text-gray-900">{{ modes[5].label }}</p>
              <p class="text-xs text-gray-500">{{ modes[5].description }}</p>
            </div>
          </div>
        </button>

        <!-- Custom date inputs (shown when custom is selected) -->
        <div v-if="modelValue.mode === 'custom'" class="mt-3 space-y-2">
          <div class="flex items-center gap-2">
            <span class="text-xs font-medium text-gray-600 w-16">Sol:</span>
            <input
              v-model="customLeftStart"
              type="date"
              class="flex-1 border rounded px-2 py-1 text-sm"
            />
            <span class="text-gray-400">-</span>
            <input
              v-model="customLeftEnd"
              type="date"
              class="flex-1 border rounded px-2 py-1 text-sm"
            />
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs font-medium text-gray-600 w-16">Sağ:</span>
            <input
              v-model="customRightStart"
              type="date"
              class="flex-1 border rounded px-2 py-1 text-sm"
            />
            <span class="text-gray-400">-</span>
            <input
              v-model="customRightEnd"
              type="date"
              class="flex-1 border rounded px-2 py-1 text-sm"
            />
          </div>
          <button
            @click="applyCustomRange"
            class="w-full mt-2 px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
          >
            Karşılaştır
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
```

**Step 3: Add export to barrel index**

```typescript
// frontend/src/components/ui/index.ts
export { default as ComparisonModeSelector } from './ComparisonModeSelector.vue'
export type { ComparisonMode, ComparisonPeriod, ComparisonConfig } from '@/types/comparison'
```

**Step 4: Commit**

```bash
git add frontend/src/components/ui/ComparisonModeSelector.vue frontend/src/types/comparison.ts frontend/src/components/ui/index.ts
git commit -m "feat(comparison): add ComparisonModeSelector component with predefined modes"
```

---

## Task 2: Create ComparisonCard Component

**Files:**
- Create: `frontend/src/components/ui/ComparisonCard.vue`
- Modify: `frontend/src/types/comparison.ts` (add BilancoPeriodData type)

**Step 1: Add BilancoPeriodData type**

```typescript
// frontend/src/types/comparison.ts - add to existing file

export interface RevenueBreakdown {
  visa: number
  nakit: number
  online: number
  trendyol?: number
  getir?: number
  yemeksepeti?: number
  migros?: number
}

export interface ExpenseBreakdown {
  mal_alimi: number
  gider: number
  staff: number
  kurye: number
  parttime: number
  uretim: number
}

export interface BilancoPeriodData {
  period_label: string
  start_date: string
  end_date: string
  revenue_breakdown: RevenueBreakdown
  total_revenue: number
  expense_breakdown: ExpenseBreakdown
  total_expenses: number
  net_profit: number
  profit_margin: number
}
```

**Step 2: Create ComparisonCard component**

```vue
<!-- frontend/src/components/ui/ComparisonCard.vue -->
<script setup lang="ts">
import { computed } from 'vue'
import type { BilancoPeriodData } from '@/types/comparison'

const props = defineProps<{
  data: BilancoPeriodData
  position: 'left' | 'right'
}>()

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

const totalRevenue = computed(() => props.data.total_revenue)

const profitMarginColor = computed(() => {
  return props.data.profit_margin >= 50 ? 'text-green-600' : props.data.profit_margin >= 30 ? 'text-yellow-600' : 'text-red-600'
})

const profitCardBackground = computed(() => {
  return props.data.net_profit >= 0
    ? 'bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200'
    : 'bg-gradient-to-br from-red-50 to-red-100 border-red-200'
})
</script>

<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-800">
        {{ data.period_label }}
      </h3>
      <span class="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded-full">
        {{ data.start_date === data.end_date
          ? new Date(data.start_date).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' })
          : `${new Date(data.start_date).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' })} - ${new Date(data.end_date).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' })}`
        }}
      </span>
    </div>

    <!-- Revenue Channels -->
    <p class="text-xs text-gray-500 font-medium mb-2">💳 Ciro Kanalları</p>
    <div class="grid grid-cols-3 gap-2 mb-4">
      <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-2 border border-blue-200">
        <p class="text-xs text-blue-600 flex items-center gap-1">
          <span>💳</span> Visa
        </p>
        <p class="text-sm font-bold text-blue-700">{{ formatCurrency(data.revenue_breakdown.visa) }}</p>
      </div>
      <div class="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-lg p-2 border border-emerald-200">
        <p class="text-xs text-emerald-600 flex items-center gap-1">
          <span>💵</span> Nakit
        </p>
        <p class="text-sm font-bold text-emerald-700">{{ formatCurrency(data.revenue_breakdown.nakit) }}</p>
      </div>
      <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-2 border border-purple-200">
        <p class="text-xs text-purple-600 flex items-center gap-1">
          <span>📱</span> Online
        </p>
        <p class="text-sm font-bold text-purple-700">{{ formatCurrency(data.revenue_breakdown.online) }}</p>
      </div>
    </div>

    <!-- Total Revenue -->
    <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-3 border border-green-200 mb-4">
      <p class="text-sm text-green-600 font-medium flex items-center gap-1">
        <span>💰</span> Toplam Ciro
      </p>
      <p class="text-xl font-bold text-green-700">{{ formatCurrency(totalRevenue) }}</p>
    </div>

    <!-- Expense Breakdown -->
    <p class="text-xs text-gray-500 font-medium mb-2">📦 Gider Detayları</p>
    <div class="grid grid-cols-2 gap-x-4 gap-y-1 text-sm text-gray-600 mb-3">
      <span>Mal Alımı {{ formatCurrency(data.expense_breakdown.mal_alimi) }}</span>
      <span>İşletme Giderleri {{ formatCurrency(data.expense_breakdown.gider) }}</span>
      <span>Personel Yemekleri {{ formatCurrency(data.expense_breakdown.staff) }}</span>
      <span>Kurye {{ formatCurrency(data.expense_breakdown.kurye) }}</span>
      <span>Part-Time {{ formatCurrency(data.expense_breakdown.parttime) }}</span>
      <span>Üretim {{ formatCurrency(data.expense_breakdown.uretim) }}</span>
    </div>

    <!-- Total Expenses -->
    <div class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-3 border border-orange-200 mb-4">
      <p class="text-sm text-orange-600 font-medium flex items-center gap-1">
        <span>📦</span> Toplam Gider
      </p>
      <p class="text-xl font-bold text-orange-700">{{ formatCurrency(data.total_expenses) }}</p>
    </div>

    <!-- Net Profit -->
    <div :class="['rounded-xl p-3 border', profitCardBackground]">
      <p :class="['text-sm font-medium flex items-center gap-1', props.data.net_profit >= 0 ? 'text-blue-600' : 'text-red-600']">
        <span>📈</span> Net Kâr
      </p>
      <p :class="['text-xl font-bold', props.data.net_profit >= 0 ? 'text-blue-700' : 'text-red-700']">
        {{ formatCurrency(data.net_profit) }}
      </p>
      <p :class="['text-xs mt-1', profitMarginColor]">
        Karlılık: %{{ data.profit_margin.toFixed(0) }}
      </p>
    </div>
  </div>
</template>
```

**Step 3: Add export to barrel index**

```typescript
// frontend/src/components/ui/index.ts
export { default as ComparisonCard } from './ComparisonCard.vue'
export type { BilancoPeriodData, RevenueBreakdown, ExpenseBreakdown } from '@/types/comparison'
```

**Step 4: Commit**

```bash
git add frontend/src/components/ui/ComparisonCard.vue frontend/src/types/comparison.ts frontend/src/components/ui/index.ts
git commit -m "feat(comparison): add ComparisonCard component with revenue, expenses, profit display"
```

---

## Task 3: Create DeltaBand Component

**Files:**
- Create: `frontend/src/components/ui/DeltaBand.vue`
- Modify: `frontend/src/types/comparison.ts` (add DeltaData type)

**Step 1: Add DeltaData type**

```typescript
// frontend/src/types/comparison.ts - add to existing file

export interface DeltaMetric {
  label: string
  leftValue: number
  rightValue: number
  absoluteDelta: number
  percentageDelta: number
  isInverted: boolean // true if lower is better (like expenses)
}

export interface DeltaData {
  revenue: DeltaMetric
  expenses: DeltaMetric
  profit: DeltaMetric
  profitMargin: number // percentage points difference
}
```

**Step 2: Create DeltaBand component**

```vue
<!-- frontend/src/components/ui/DeltaBand.vue -->
<script setup lang="ts">
import { computed } from 'vue'
import type { BilancoPeriodData } from '@/types/comparison'

const props = defineProps<{
  leftData: BilancoPeriodData
  rightData: BilancoPeriodData
}>()

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

function calculateDelta(left: number, right: number, isInverted = false) {
  const absoluteDelta = left - right
  const percentageDelta = right !== 0 ? ((left - right) / Math.abs(right)) * 100 : 0

  return {
    absoluteDelta,
    percentageDelta,
    direction: absoluteDelta > 0 ? 'up' : absoluteDelta < 0 ? 'down' : 'neutral'
  }
}

const revenueDelta = computed(() => calculateDelta(props.leftData.total_revenue, props.rightData.total_revenue))
const expensesDelta = computed(() => calculateDelta(props.leftData.total_expenses, props.rightData.total_expenses, true))
const profitDelta = computed(() => calculateDelta(props.leftData.net_profit, props.rightData.net_profit))
const marginDelta = computed(() => props.leftData.profit_margin - props.rightData.profit_margin)

function getDeltaColor(delta: ReturnType<typeof calculateDelta>, isInverted = false) {
  if (delta.direction === 'neutral') return 'text-yellow-600 bg-yellow-50'

  const isPositive = delta.direction === 'up'
  const isInversionGood = isInverted && !isPositive // expenses going down is good
  const isNormalGood = !isInverted && isPositive // revenue/profit going up is good

  if (isInversionGood || isNormalGood) {
    return 'text-green-600 bg-green-50'
  }
  return 'text-red-600 bg-red-50'
}

const revenueColor = computed(() => getDeltaColor(revenueDelta.value))
const expensesColor = computed(() => getDeltaColor(expensesDelta.value, true))
const profitColor = computed(() => getDeltaColor(profitDelta.value))
const marginColor = computed(() => {
  if (Math.abs(marginDelta.value) < 2) return 'text-yellow-600 bg-yellow-50'
  return marginDelta.value > 0 ? 'text-green-600 bg-green-50' : 'text-red-600 bg-red-50'
})
</script>

<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
    <h4 class="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
      <span>∆</span> Karşılaştırma Farkları
    </h4>

    <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
      <!-- Revenue Delta -->
      <div :class="['rounded-lg p-3 border', revenueColor]">
        <p class="text-xs font-medium mb-1">💰 Ciro</p>
        <p class="text-lg font-bold">
          {{ revenueDelta.direction === 'up' ? '▲' : revenueDelta.direction === 'down' ? '▼' : '→' }}
          %{{ Math.abs(revenueDelta.percentageDelta).toFixed(1) }}
        </p>
        <p class="text-xs opacity-75">
          {{ revenueDelta.absoluteDelta > 0 ? '+' : '' }}{{ formatCurrency(revenueDelta.absoluteDelta) }}
        </p>
      </div>

      <!-- Expenses Delta -->
      <div :class="['rounded-lg p-3 border', expensesColor]">
        <p class="text-xs font-medium mb-1">📦 Gider</p>
        <p class="text-lg font-bold">
          {{ expensesDelta.direction === 'up' ? '▼' : expensesDelta.direction === 'down' ? '▲' : '→' }}
          %{{ Math.abs(expensesDelta.percentageDelta).toFixed(1) }}
        </p>
        <p class="text-xs opacity-75">
          {{ expensesDelta.absoluteDelta > 0 ? '+' : '' }}{{ formatCurrency(expensesDelta.absoluteDelta) }}
        </p>
      </div>

      <!-- Profit Delta -->
      <div :class="['rounded-lg p-3 border', profitColor]">
        <p class="text-xs font-medium mb-1">📈 Kar</p>
        <p class="text-lg font-bold">
          {{ profitDelta.direction === 'up' ? '▲' : profitDelta.direction === 'down' ? '▼' : '→' }}
          %{{ Math.abs(profitDelta.percentageDelta).toFixed(1) }}
        </p>
        <p class="text-xs opacity-75">
          {{ profitDelta.absoluteDelta > 0 ? '+' : '' }}{{ formatCurrency(profitDelta.absoluteDelta) }}
        </p>
      </div>

      <!-- Margin Delta -->
      <div :class="['rounded-lg p-3 border', marginColor]">
        <p class="text-xs font-medium mb-1">📊 Karlılık</p>
        <p class="text-lg font-bold">
          {{ marginDelta > 0 ? '↑' : marginDelta < 0 ? '↓' : '→' }}
          {{ Math.abs(marginDelta).toFixed(1) }}pp
        </p>
        <p class="text-xs opacity-75">
          %{{ leftData.profit_margin.toFixed(0) }} → %{{ rightData.profit_margin.toFixed(0) }}
        </p>
      </div>
    </div>
  </div>
</template>
```

**Step 3: Add export to barrel index**

```typescript
// frontend/src/components/ui/index.ts
export { default as DeltaBand } from './DeltaBand.vue'
export type { DeltaData, DeltaMetric } from '@/types/comparison'
```

**Step 4: Commit**

```bash
git add frontend/src/components/ui/DeltaBand.vue frontend/src/types/comparison.ts frontend/src/components/ui/index.ts
git commit -m "feat(comparison): add DeltaBand component with color-coded delta indicators"
```

---

## Task 4: Create Backend API Endpoint

**Files:**
- Create: `backend/api/routes/reports_comparison.py`
- Modify: `backend/api/routes/reports.py` (register new router)
- Modify: `backend/services/reports_service.py` (add comparison logic)

**Step 1: Create comparison service method**

```python
# backend/services/reports_service.py - add to existing file

from datetime import date, timedelta
from typing import Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.sale import Sale
from backend.models.expense import Expense
from backend.models.production import DailyProduction


async def get_comparison_data(
    db: AsyncSession,
    left_start: date,
    left_end: date,
    right_start: date,
    right_end: date,
    branch_id: int | None = None
) -> Dict[str, Any]:
    """
    Get bilanco comparison data for two date ranges.
    """
    async def get_period_data(start_date: date, end_date: date, period_label: str) -> Dict[str, Any]:
        # Build base query with branch filter
        def add_branch_filter(query):
            if branch_id is not None:
                return query.where(Sale.branch_id == branch_id)
            return query

        # Revenue breakdown
        revenue_query = select(
            func.sum(Sale.visa).label('visa'),
            func.sum(Sale.nakit).label('nakit'),
            func.sum(Sale.trendyol).label('trendyol'),
            func.sum(Sale.getir).label('getir'),
            func.sum(Sale.yemeksepeti).label('yemeksepeti'),
            func.sum(Sale.migros).label('migros')
        ).where(
            func.date(Sale.sale_date) >= start_date,
            func.date(Sale.sale_date) <= end_date
        )
        revenue_query = add_branch_filter(revenue_query)

        result = await db.execute(revenue_query)
        revenue_row = result.first()

        total_revenue = (
            (revenue_row.visa or 0) +
            (revenue_row.nakit or 0) +
            (revenue_row.trendyol or 0) +
            (revenue_row.getir or 0) +
            (revenue_row.yemeksepeti or 0) +
            (revenue_row.migros or 0)
        )

        online_revenue = (
            (revenue_row.trendyol or 0) +
            (revenue_row.getir or 0) +
            (revenue_row.yemeksepeti or 0) +
            (revenue_row.migros or 0)
        )

        # Expense breakdown
        expense_query = select(
            func.sum(Expense.amount).label('total'),
            Expense.category_id
        ).where(
            func.date(Expense.expense_date) >= start_date,
            func.date(Expense.expense_date) <= end_date
        )
        # if branch_id:
        #     expense_query = expense_query.where(Expense.branch_id == branch_id)

        result = await db.execute(expense_query)
        expense_rows = result.all()

        # Initialize expense categories
        expenses = {
            'mal_alimi': 0,
            'gider': 0,
            'staff': 0,  # staff_meals
            'kurye': 0,  # courier_expenses
            'parttime': 0,
            'uretim': 0
        }

        # TODO: Map expense categories to breakdown
        # For now, use total from a simple query
        total_expenses_result = await db.execute(
            select(func.sum(Expense.amount)).where(
                func.date(Expense.expense_date) >= start_date,
                func.date(Expense.expense_date) <= end_date
            )
        )
        total_expenses = total_expenses_result.scalar() or 0

        # Calculate profit
        net_profit = total_revenue - total_expenses
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0

        return {
            'period_label': period_label,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'revenue_breakdown': {
                'visa': revenue_row.visa or 0,
                'nakit': revenue_row.nakit or 0,
                'online': online_revenue,
                'trendyol': revenue_row.trendyol or 0,
                'getir': revenue_row.getir or 0,
                'yemeksepeti': revenue_row.yemeksepeti or 0,
                'migros': revenue_row.migros or 0
            },
            'total_revenue': total_revenue,
            'expense_breakdown': expenses,
            'total_expenses': total_expenses,
            'net_profit': net_profit,
            'profit_margin': profit_margin
        }

    left_data = await get_period_data(left_start, left_end, "Sol Dönem")
    right_data = await get_period_data(right_start, right_end, "Sağ Dönem")

    return {
        'left': left_data,
        'right': right_data
    }
```

**Step 2: Create comparison router**

```python
# backend/api/routes/reports_comparison.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.services.reports_service import get_comparison_data
from backend.schemas.reports import ComparisonRequest, ComparisonResponse

router = APIRouter(prefix="/api/v1/reports", tags=["reports-comparison"])


@router.get("/bilanco-compare", response_model=ComparisonResponse)
async def get_bilanco_comparison(
    left_start: str,
    left_end: str,
    right_start: str,
    right_end: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get bilanco comparison data for two date ranges.

    Query parameters:
    - left_start: Start date for left period (ISO format)
    - left_end: End date for left period (ISO format)
    - right_start: Start date for right period (ISO format)
    - right_end: End date for right period (ISO format)
    """
    from datetime import datetime

    left_start_date = datetime.fromisoformat(left_start).date()
    left_end_date = datetime.fromisoformat(left_end).date()
    right_start_date = datetime.fromisoformat(right_start).date()
    right_end_date = datetime.fromisoformat(right_end).date()

    result = await get_comparison_data(
        db,
        left_start_date,
        left_end_date,
        right_start_date,
        right_end_date
    )

    return result
```

**Step 3: Add comparison schemas**

```python
# backend/schemas/reports.py - add to existing file

from pydantic import BaseModel
from typing import Dict, Any


class RevenueBreakdown(BaseModel):
    visa: float
    nakit: float
    online: float
    trendyol: float = 0
    getir: float = 0
    yemeksepeti: float = 0
    migros: float = 0


class ExpenseBreakdown(BaseModel):
    mal_alimi: float
    gider: float
    staff: float
    kurye: float
    parttime: float
    uretim: float


class BilancoPeriodDataSchema(BaseModel):
    period_label: str
    start_date: str
    end_date: str
    revenue_breakdown: RevenueBreakdown
    total_revenue: float
    expense_breakdown: ExpenseBreakdown
    total_expenses: float
    net_profit: float
    profit_margin: float


class ComparisonResponse(BaseModel):
    left: BilancoPeriodDataSchema
    right: BilancoPeriodDataSchema
```

**Step 4: Register router in main app**

```python
# backend/main.py - add to imports and router registration

from backend.api.routes.reports_comparison import router as reports_comparison_router

# Add to router registrations
app.include_router(reports_comparison_router)
```

**Step 5: Test the endpoint**

```bash
# Test the endpoint
curl "http://localhost:5000/api/v1/reports/bilanco-compare?left_start=2025-01-28&left_end=2025-01-28&right_start=2025-01-27&right_end=2025-01-27"
```

Expected: JSON response with left and right period data

**Step 6: Commit**

```bash
git add backend/api/routes/reports_comparison.py backend/services/reports_service.py backend/schemas/reports.py backend/main.py
git commit -m "feat(reports): add bilanco comparison API endpoint"
```

---

## Task 5: Add API Service Method

**Files:**
- Modify: `frontend/src/services/api.ts`

**Step 1: Add comparison API method**

```typescript
// frontend/src/services/api.ts - add to reportsApi object

interface BilancoComparisonParams {
  left_start: string
  left_end: string
  right_start: string
  right_end: string
}

interface BilancoComparisonResponse {
  left: BilancoPeriodData
  right: BilancoPeriodData
}

// In reportsApi object:
bilancoCompare: {
  get: async (params: BilancoComparisonParams) => {
    return axios.get<BilancoComparisonResponse>('/reports/bilanco-compare', { params })
  }
}
```

**Step 2: Commit**

```bash
git add frontend/src/services/api.ts
git commit -m "feat(api): add bilanco comparison API service method"
```

---

## Task 6: Refactor Bilanco.vue

**Files:**
- Modify: `frontend/src/views/Bilanco.vue`

**Step 1: Replace script section**

```vue
<!-- frontend/src/views/Bilanco.vue - new script section -->
<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import type { BilancoPeriodData, ComparisonConfig } from '@/types/comparison'
import { reportsApi } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { ComparisonModeSelector, ComparisonCard, DeltaBand } from '@/components/ui'
import SmartInsightCard from '@/components/dashboard/SmartInsightCard.vue'
import { LoadingState, ErrorAlert } from '@/components/ui'

const router = useRouter()
const authStore = useAuthStore()

// Comparison config
const comparisonConfig = ref<ComparisonConfig>({
  mode: 'today_vs_yesterday',
  leftPeriod: {
    label: 'Bugün',
    start: new Date().toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  },
  rightPeriod: {
    label: 'Dün',
    start: new Date(Date.now() - 86400000).toISOString().split('T')[0],
    end: new Date(Date.now() - 86400000).toISOString().split('T')[0]
  }
})

// Data
const leftData = ref<BilancoPeriodData | null>(null)
const rightData = ref<BilancoPeriodData | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

async function fetchComparisonData() {
  if (!comparisonConfig.value.leftPeriod.start || !comparisonConfig.value.leftPeriod.end ||
      !comparisonConfig.value.rightPeriod.start || !comparisonConfig.value.rightPeriod.end) {
    return
  }

  loading.value = true
  error.value = null

  try {
    const { data } = await reportsApi.bilancoCompare.get({
      left_start: comparisonConfig.value.leftPeriod.start,
      left_end: comparisonConfig.value.leftPeriod.end,
      right_start: comparisonConfig.value.rightPeriod.start,
      right_end: comparisonConfig.value.rightPeriod.end
    })

    leftData.value = data.left
    rightData.value = data.right
  } catch (err: any) {
    console.error('Failed to load comparison data:', err)
    error.value = 'Veriler yüklenemedi. Lütfen sayfayı yenileyin.'
  } finally {
    loading.value = false
  }
}

// Fetch data when comparison config changes
watch(() => comparisonConfig.value, () => {
  fetchComparisonData()
}, { deep: true })

// Refresh when branch changes
watch(() => authStore.currentBranchId, () => {
  fetchComparisonData()
})

onMounted(() => {
  fetchComparisonData()
})

function formatCurrency(value: number) {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}
</script>
```

**Step 2: Replace template section**

```vue
<!-- frontend/src/views/Bilanco.vue - new template section -->
<template>
  <div class="space-y-6">
    <!-- Quick Actions -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <span class="text-xl">🚀</span>
        Hızlı İşlemler
      </h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <button @click="router.push('/sales')" class="btn btn-primary flex items-center justify-center gap-2">
          <span>💳</span>
          <span>Kasa Girişi</span>
        </button>
        <button @click="router.push('/purchases/new')" class="btn btn-secondary flex items-center justify-center gap-2">
          <span>📦</span>
          <span>Mal Alımı</span>
        </button>
        <button @click="router.push('/expenses/new')" class="btn btn-secondary flex items-center justify-center gap-2">
          <span>💸</span>
          <span>Gider Ekle</span>
        </button>
        <button @click="router.push('/production')" class="btn btn-secondary flex items-center justify-center gap-2">
          <span>🥙</span>
          <span>Üretim Gir</span>
        </button>
      </div>
    </div>

    <!-- Error Alert -->
    <ErrorAlert v-if="error" :message="error" @dismiss="error = null" />

    <!-- Comparison Mode Selector -->
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-semibold text-gray-800 flex items-center gap-2">
        <span class="text-xl">📊</span>
        Karşılaştırma
      </h2>
      <ComparisonModeSelector v-model="comparisonConfig" />
    </div>

    <!-- Loading State -->
    <LoadingState v-if="loading" />

    <!-- Comparison Cards -->
    <template v-else-if="leftData && rightData">
      <!-- Delta Band -->
      <DeltaBand :left-data="leftData" :right-data="rightData" />

      <!-- Side by Side Cards -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ComparisonCard :data="leftData" position="left" />
        <ComparisonCard :data="rightData" position="right" />
      </div>
    </template>

    <!-- AI Asistan -->
    <SmartInsightCard />
  </div>
</template>
```

**Step 3: Run build to check for errors**

```bash
cd frontend && npm run build
```

Expected: Build successful with no errors

**Step 4: Commit**

```bash
git add frontend/src/views/Bilanco.vue
git commit -m "feat(bilanco): refactor to use comparison view with side-by-side cards"
```

---

## Task 7: Testing

**Files:**
- Create: `frontend/src/components/__tests__/ComparisonModeSelector.spec.ts`
- Create: `frontend/src/components/__tests__/ComparisonCard.spec.ts`
- Create: `frontend/src/components/__tests__/DeltaBand.spec.ts`

**Step 1: Create ComparisonModeSelector test**

```typescript
// frontend/src/components/__tests__/ComparisonModeSelector.spec.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ComparisonModeSelector from '@/components/ui/ComparisonModeSelector.vue'
import type { ComparisonConfig } from '@/types/comparison'

describe('ComparisonModeSelector', () => {
  it('renders with default today_vs_yesterday mode', () => {
    const wrapper = mount(ComparisonModeSelector, {
      props: {
        modelValue: {
          mode: 'today_vs_yesterday',
          leftPeriod: { label: 'Bugün', start: '2025-01-29', end: '2025-01-29' },
          rightPeriod: { label: 'Dün', start: '2025-01-28', end: '2025-01-28' }
        }
      }
    })

    expect(wrapper.find('button').text()).toContain('Bugün vs Dün')
  })

  it('emits update when mode is selected', async () => {
    const wrapper = mount(ComparisonModeSelector, {
      props: {
        modelValue: {
          mode: 'today_vs_yesterday',
          leftPeriod: { label: 'Bugün', start: '2025-01-29', end: '2025-01-29' },
          rightPeriod: { label: 'Dün', start: '2025-01-28', end: '2025-01-28' }
        }
      }
    })

    // Open dropdown
    await wrapper.find('button').trigger('click')
    await wrapper.vm.$nextTick()

    // Click on week mode
    const weekOption = wrapper.findAll('button')[1] // Second button is week mode
    await weekOption.trigger('click')
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
  })
})
```

**Step 2: Create ComparisonCard test**

```typescript
// frontend/src/components/__tests__/ComparisonCard.spec.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ComparisonCard from '@/components/ui/ComparisonCard.vue'
import type { BilancoPeriodData } from '@/types/comparison'

describe('ComparisonCard', () => {
  const mockData: BilancoPeriodData = {
    period_label: 'Bugün',
    start_date: '2025-01-29',
    end_date: '2025-01-29',
    revenue_breakdown: {
      visa: 45000,
      nakit: 12000,
      online: 8500,
      trendyol: 0,
      getir: 0,
      yemeksepeti: 0,
      migros: 0
    },
    total_revenue: 65500,
    expense_breakdown: {
      mal_alimi: 18000,
      gider: 3500,
      staff: 2100,
      kurye: 800,
      parttime: 600,
      uretim: 4200
    },
    total_expenses: 29200,
    net_profit: 36300,
    profit_margin: 55
  }

  it('renders period data correctly', () => {
    const wrapper = mount(ComparisonCard, {
      props: {
        data: mockData,
        position: 'left'
      }
    })

    expect(wrapper.text()).toContain('Bugün')
    expect(wrapper.text()).toContain('65.500 ₺') // Total revenue
    expect(wrapper.text()).toContain('%55') // Profit margin
  })

  it('shows green color for positive profit', () => {
    const wrapper = mount(ComparisonCard, {
      props: {
        data: mockData,
        position: 'left'
      }
    })

    expect(wrapper.find('.bg-gradient-to-br.from-blue-50').exists()).toBe(true)
  })
})
```

**Step 3: Create DeltaBand test**

```typescript
// frontend/src/components/__tests__/DeltaBand.spec.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DeltaBand from '@/components/ui/DeltaBand.vue'
import type { BilancoPeriodData } from '@/types/comparison'

describe('DeltaBand', () => {
  const leftData: BilancoPeriodData = {
    period_label: 'Bugün',
    start_date: '2025-01-29',
    end_date: '2025-01-29',
    revenue_breakdown: { visa: 45000, nakit: 12000, online: 8500 },
    total_revenue: 65500,
    expense_breakdown: { mal_alimi: 18000, gider: 3500, staff: 2100, kurye: 800, parttime: 600, uretim: 4200 },
    total_expenses: 29200,
    net_profit: 36300,
    profit_margin: 55
  }

  const rightData: BilancoPeriodData = {
    period_label: 'Dün',
    start_date: '2025-01-28',
    end_date: '2025-01-28',
    revenue_breakdown: { visa: 38000, nakit: 10500, online: 7200 },
    total_revenue: 55700,
    expense_breakdown: { mal_alimi: 15200, gider: 4200, staff: 1900, kurye: 750, parttime: 550, uretim: 3800 },
    total_expenses: 25400,
    net_profit: 30300,
    profit_margin: 54
  }

  it('calculates revenue delta correctly', () => {
    const wrapper = mount(DeltaBand, {
      props: { leftData, rightData }
    })

    // 65500 - 55700 = 9800 (17.6% increase)
    expect(wrapper.text()).toContain('%')
  })

  it('shows green for revenue increase', () => {
    const wrapper = mount(DeltaBand, {
      props: { leftData, rightData }
    })

    expect(wrapper.html()).toContain('text-green-600')
  })
})
```

**Step 4: Run tests**

```bash
cd frontend && npm run test
```

Expected: All tests pass

**Step 5: Commit**

```bash
git add frontend/src/components/__tests__/
git commit -m "test(comparison): add unit tests for comparison components"
```

---

## Task 8: Polish and Responsive Design

**Files:**
- Modify: `frontend/src/components/ui/ComparisonCard.vue`
- Modify: `frontend/src/components/ui/DeltaBand.vue`
- Modify: `frontend/src/views/Bilanco.vue`

**Step 1: Add responsive classes**

Update ComparisonCard to use responsive grid:
- On mobile: Stack vertically
- On tablet+: Side by side

**Step 2: Add loading skeletons**

Add skeleton loading state for comparison cards while data is fetching.

**Step 3: Add error boundaries**

Wrap comparison section in error boundary to handle API failures gracefully.

**Step 4: Commit**

```bash
git add frontend/src/components/ui/ComparisonCard.vue frontend/src/components/ui/DeltaBand.vue frontend/src/views/Bilanco.vue
git commit -m "style(comparison): add responsive design and loading states"
```

---

## Summary

After completing all tasks, the Bilanco page will have:

1. ✅ ComparisonModeSelector - Dropdown with predefined comparison modes
2. ✅ ComparisonCard - Displays period data with revenue, expenses, profit
3. ✅ DeltaBand - Shows color-coded differences between periods
4. ✅ Backend API - `/api/v1/reports/bilanco-compare` endpoint
5. ✅ Refactored Bilanco.vue - Side-by-side comparison view
6. ✅ Tests - Unit tests for all new components
7. ✅ Responsive design - Mobile-friendly layout

**Total estimated time:** 3-4 hours

**Key files created:**
- `frontend/src/components/ui/ComparisonModeSelector.vue`
- `frontend/src/components/ui/ComparisonCard.vue`
- `frontend/src/components/ui/DeltaBand.vue`
- `frontend/src/types/comparison.ts`
- `backend/api/routes/reports_comparison.py`

**Key files modified:**
- `frontend/src/views/Bilanco.vue`
- `frontend/src/services/api.ts`
- `backend/services/reports_service.py`
- `backend/main.py`
