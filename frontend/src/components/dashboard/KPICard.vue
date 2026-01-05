<template>
  <div
    :data-testid="testId"
    class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 transition-all duration-300"
    :class="{
      'ring-2 ring-primary-500 scale-[1.02]': isHighlighted,
      'hover:shadow-md': !isHighlighted
    }"
  >
    <!-- Header -->
    <div class="flex items-center justify-between mb-2">
      <span class="text-xs font-medium text-gray-500 uppercase tracking-wide">
        {{ label }}
      </span>
      <span
        v-if="badge"
        class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
        :class="badgeClasses"
      >
        <component
          v-if="badgeIcon"
          :is="badgeIcon"
          class="w-3 h-3 mr-1"
        />
        {{ badge }}
      </span>
    </div>

    <!-- Value -->
    <div class="text-2xl font-bold text-gray-900 tabular-nums">
      <span v-if="prefix" class="text-gray-500">{{ prefix }}</span>
      {{ formattedValue }}
      <span v-if="suffix" class="text-lg font-normal text-gray-500">{{ suffix }}</span>
    </div>

    <!-- Subtitle -->
    <div v-if="subtitle" class="mt-1 text-sm text-gray-500">
      {{ subtitle }}
    </div>

    <!-- Progress Bar (optional) -->
    <div v-if="showProgress" class="mt-3">
      <div class="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          class="h-full rounded-full transition-all duration-500"
          :class="progressColor"
          :style="{ width: `${Math.min(progressPercent, 100)}%` }"
        />
      </div>
      <div class="mt-1 text-xs text-gray-500">
        Hedef: {{ target }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, type Component } from 'vue'
import { TrendingUp, TrendingDown, Check, AlertTriangle } from 'lucide-vue-next'

interface Props {
  testId?: string
  label: string
  value: number
  prefix?: string
  suffix?: string
  badge?: string
  badgeType?: 'success' | 'warning' | 'danger' | 'info' | 'neutral'
  trend?: 'up' | 'down' | null
  subtitle?: string
  isHighlighted?: boolean
  showProgress?: boolean
  progressPercent?: number
  progressColor?: string
  target?: string
  formatAsCurrency?: boolean
  formatAsPercent?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  testId: 'kpi-card',
  badgeType: 'neutral',
  trend: null,
  isHighlighted: false,
  showProgress: false,
  progressPercent: 0,
  progressColor: 'bg-primary-500',
  formatAsCurrency: false,
  formatAsPercent: false
})

const formattedValue = computed(() => {
  if (props.formatAsPercent) {
    return `%${props.value}`
  }
  if (props.formatAsCurrency) {
    return new Intl.NumberFormat('tr-TR').format(props.value)
  }
  return new Intl.NumberFormat('tr-TR').format(props.value)
})

const badgeIcon = computed<Component | null>(() => {
  if (props.trend === 'up') return TrendingUp
  if (props.trend === 'down') return TrendingDown
  if (props.badgeType === 'success') return Check
  if (props.badgeType === 'warning' || props.badgeType === 'danger') return AlertTriangle
  return null
})

const badgeClasses = computed(() => {
  const baseClasses = {
    success: 'bg-success-100 text-success-700',
    warning: 'bg-warning-100 text-warning-700',
    danger: 'bg-danger-100 text-danger-700',
    info: 'bg-primary-100 text-primary-700',
    neutral: 'bg-gray-100 text-gray-700'
  }

  // Override based on trend
  if (props.trend === 'up') {
    return 'bg-success-100 text-success-700'
  }
  if (props.trend === 'down') {
    return 'bg-danger-100 text-danger-700'
  }

  return baseClasses[props.badgeType]
})
</script>
