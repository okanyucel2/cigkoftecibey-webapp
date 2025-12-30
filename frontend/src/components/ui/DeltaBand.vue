<!-- frontend/src/components/ui/DeltaBand.vue -->
<script setup lang="ts">
import { computed } from 'vue'
import type { BilancoPeriodData, DeltaData, DeltaMetric } from '@/types/comparison'

// Delta threshold for considering a change "neutral" (in percentage points)
const DELTA_THRESHOLD = 2

const props = defineProps<{
  leftData: BilancoPeriodData
  rightData: BilancoPeriodData
}>()

// Null safety: Ensure parent component provides valid data
// If data is missing, we show empty state rather than crash
if (!props.leftData || !props.rightData) {
  console.warn('DeltaBand: Missing required props (leftData or rightData)')
}

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

/**
 * Calculate delta metric between two periods
 * @param leftValue - Base period value
 * @param rightValue - Comparison period value
 * @param invertLogic - If true, decrease is considered positive (for expenses)
 * @param isPercentagePoints - If true, treat as percentage points, not percentage change
 */
const calculateDelta = (
  leftValue: number,
  rightValue: number,
  invertLogic: boolean = false,
  isPercentagePoints: boolean = false
): DeltaMetric => {
  const absolute = rightValue - leftValue

  let percentage: number
  if (isPercentagePoints) {
    // For percentage points, just return the absolute difference
    percentage = absolute
  } else if (leftValue === 0) {
    // Handle zero division
    percentage = rightValue > 0 ? 100 : 0
  } else {
    percentage = (absolute / leftValue) * 100
  }

  // Determine if change is positive (good) or negative (bad)
  // For normal metrics: increase is good
  // For inverted metrics (expenses): decrease is good
  let isPositive: boolean
  if (invertLogic) {
    isPositive = absolute < 0 // Expenses went down = good
  } else {
    isPositive = absolute > 0 // Revenue/profit went up = good
  }

  return {
    label: '',
    absolute,
    percentage,
    isPositive
  }
}

/**
 * Determine the color class for a delta metric
 * Green = good change
 * Red = bad change
 * Yellow = neutral change (within small threshold)
 */
const getDeltaColor = (metric: DeltaMetric, threshold: number = DELTA_THRESHOLD): string => {
  if (Math.abs(metric.percentage) < threshold) {
    return 'bg-yellow-50 border-yellow-200 text-yellow-700'
  }

  if (metric.isPositive) {
    return 'bg-green-50 border-green-200 text-green-700'
  } else {
    return 'bg-red-50 border-red-200 text-red-700'
  }
}

/**
 * Get the arrow icon and text for delta display
 */
const getDeltaDisplay = (metric: DeltaMetric, isPercentagePoints: boolean = false): string => {
  const arrow = metric.absolute > 0 ? '▲' : metric.absolute < 0 ? '▼' : '→'
  const absText = metric.absolute !== 0
    ? `${arrow} ${formatCurrency(Math.abs(metric.absolute))}`
    : '→'

  if (isPercentagePoints) {
    return `${arrow} ${metric.percentage > 0 ? '+' : ''}${metric.percentage.toFixed(1)}pp`
  }

  return `${arrow} ${metric.percentage > 0 ? '+' : ''}${metric.percentage.toFixed(1)}% (${absText})`
}

// Computed delta calculations
const revenueDelta = computed(() => {
  if (!props.leftData || !props.rightData) {
    return { label: '', absolute: 0, percentage: 0, isPositive: true }
  }
  return calculateDelta(props.leftData.total_revenue, props.rightData.total_revenue)
})

const expensesDelta = computed(() => {
  if (!props.leftData || !props.rightData) {
    return { label: '', absolute: 0, percentage: 0, isPositive: true }
  }
  return calculateDelta(
    props.leftData.total_expenses,
    props.rightData.total_expenses,
    true // Invert logic: decrease is good
  )
})

const profitDelta = computed(() => {
  if (!props.leftData || !props.rightData) {
    return { label: '', absolute: 0, percentage: 0, isPositive: true }
  }
  return calculateDelta(props.leftData.net_profit, props.rightData.net_profit)
})

const profitMarginDelta = computed(() => {
  if (!props.leftData || !props.rightData) {
    return { label: '', absolute: 0, percentage: 0, isPositive: true }
  }
  return calculateDelta(
    props.leftData.profit_margin,
    props.rightData.profit_margin,
    false,
    true // Percentage points, not percentage change
  )
})

// Computed DeltaData object
const deltaData = computed<DeltaData>(() => ({
  revenue: {
    ...revenueDelta.value,
    label: 'Ciro Farkı'
  },
  expenses: {
    ...expensesDelta.value,
    label: 'Gider Farkı'
  },
  profit: {
    ...profitDelta.value,
    label: 'Kar Farkı'
  },
  profitMargin: {
    ...profitMarginDelta.value,
    label: 'Karlılık Farkı'
  }
}))

// Computed color classes for each metric
const revenueColor = computed(() => getDeltaColor(revenueDelta.value))
const expensesColor = computed(() => getDeltaColor(expensesDelta.value))
const profitColor = computed(() => getDeltaColor(profitDelta.value))
const profitMarginColor = computed(() => getDeltaColor(profitMarginDelta.value, DELTA_THRESHOLD)) // Percentage points threshold
</script>

<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 sm:p-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
      <h3 class="text-base sm:text-lg font-semibold text-gray-800">
        Değişim Analizi
      </h3>
      <span class="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded-full w-fit">
        {{ leftData.period_label }} → {{ rightData.period_label }}
      </span>
    </div>

    <!-- Delta Cards Grid -->
    <div class="grid grid-cols-2 gap-2 sm:gap-3">
      <!-- Revenue Delta -->
      <div :class="['rounded-lg sm:rounded-xl p-3 sm:p-4 border-2', revenueColor]">
        <p class="text-xs sm:text-sm font-medium mb-1 sm:mb-2 flex items-center gap-1">
          <span class="text-sm sm:text-base">💰</span> <span class="hidden sm:inline">Ciro Farkı</span>
        </p>
        <p class="text-sm sm:text-lg font-bold leading-tight">
          {{ getDeltaDisplay(deltaData.revenue) }}
        </p>
      </div>

      <!-- Expenses Delta -->
      <div :class="['rounded-lg sm:rounded-xl p-3 sm:p-4 border-2', expensesColor]">
        <p class="text-xs sm:text-sm font-medium mb-1 sm:mb-2 flex items-center gap-1">
          <span class="text-sm sm:text-base">📦</span> <span class="hidden sm:inline">Gider Farkı</span>
        </p>
        <p class="text-sm sm:text-lg font-bold leading-tight">
          {{ getDeltaDisplay(deltaData.expenses) }}
        </p>
      </div>

      <!-- Profit Delta -->
      <div :class="['rounded-lg sm:rounded-xl p-3 sm:p-4 border-2', profitColor]">
        <p class="text-xs sm:text-sm font-medium mb-1 sm:mb-2 flex items-center gap-1">
          <span class="text-sm sm:text-base">📈</span> <span class="hidden sm:inline">Kar Farkı</span>
        </p>
        <p class="text-sm sm:text-lg font-bold leading-tight">
          {{ getDeltaDisplay(deltaData.profit) }}
        </p>
      </div>

      <!-- Profit Margin Delta -->
      <div :class="['rounded-lg sm:rounded-xl p-3 sm:p-4 border-2', profitMarginColor]">
        <p class="text-xs sm:text-sm font-medium mb-1 sm:mb-2 flex items-center gap-1">
          <span class="text-sm sm:text-base">📊</span> <span class="hidden sm:inline">Karlılık Farkı</span>
        </p>
        <p class="text-sm sm:text-lg font-bold leading-tight">
          {{ getDeltaDisplay(deltaData.profitMargin, true) }}
        </p>
      </div>
    </div>

    <!-- Legend -->
    <div class="mt-3 sm:mt-4 pt-3 sm:pt-4 border-t border-gray-100">
      <div class="flex items-center justify-center gap-3 sm:gap-6 text-xs text-gray-500 flex-wrap">
        <div class="flex items-center gap-1">
          <span class="w-3 h-3 rounded bg-green-100 border border-green-300 flex-shrink-0"></span>
          <span>İyi</span>
        </div>
        <div class="flex items-center gap-1">
          <span class="w-3 h-3 rounded bg-red-100 border border-red-300 flex-shrink-0"></span>
          <span>Kötü</span>
        </div>
        <div class="flex items-center gap-1">
          <span class="w-3 h-3 rounded bg-yellow-100 border border-yellow-300 flex-shrink-0"></span>
          <span>Nötr (±{{ DELTA_THRESHOLD }}%)</span>
        </div>
      </div>
    </div>
  </div>
</template>
