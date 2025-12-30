<!-- frontend/src/components/ui/ComparisonModeSelector.vue -->
<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import type { ComparisonMode, ComparisonModeOption, ComparisonPeriod, ComparisonConfig } from '@/types/comparison'

const props = defineProps<{
  modelValue: ComparisonConfig
}>()

const emit = defineEmits<{
  'update:modelValue': [value: ComparisonConfig]
}>()

const isOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

const modes: ComparisonModeOption[] = [
  { value: 'today_vs_yesterday', label: 'Bugün vs Dün', description: 'Son iki günün karşılaştırması', icon: '⏰' },
  { value: 'this_week_vs_last_week', label: 'Bu Hafta vs Geçen Hafta', description: 'Haftalık trend comparison', icon: '📊' },
  { value: 'this_month_vs_last_month', label: 'Bu Ay vs Geçen Ay', description: 'Aylık performans karşılaştırması', icon: '📆' },
  { value: 'last_7_vs_previous_7', label: 'Son 7 Gün vs Önceki 7 Gün', description: 'İki haftalık periyot comparison', icon: '📅' },
  { value: 'last_30_vs_previous_30', label: 'Son 30 Gün vs Önceki 30 Gün', description: 'Aylık periyot comparison', icon: '📈' },
  { value: 'custom', label: 'Özel Karşılaştırma', description: 'Kendi tarih aralıklarını seç', icon: '🎯' }
]

// Custom range inputs
const customLeftStart = ref('')
const customLeftEnd = ref('')
const customRightStart = ref('')
const customRightEnd = ref('')

// Validation error state
const validationError = ref('')

// Initialize custom inputs from props
onMounted(() => {
  if (props.modelValue.mode === 'custom') {
    customLeftStart.value = props.modelValue.leftPeriod.start
    customLeftEnd.value = props.modelValue.leftPeriod.end
    customRightStart.value = props.modelValue.rightPeriod.start
    customRightEnd.value = props.modelValue.rightPeriod.end
  }
})

// Click-outside handler
function handleClickOutside(event: MouseEvent) {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

function getPeriodForMode(mode: ComparisonMode): { left: ComparisonPeriod, right: ComparisonPeriod } {
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  // Helper: Format date as local YYYY-MM-DD (timezone-safe)
  const formatDate = (date: Date): string => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }

  // Immutable week range calculation
  const getWeekRange = (date: Date) => {
    const d = new Date(date) // Create copy to avoid mutation
    const day = d.getDay()
    const diff = d.getDate() - day + (day === 0 ? -6 : 1)
    const monday = new Date(d)
    monday.setDate(diff)
    const sunday = new Date(monday)
    sunday.setDate(monday.getDate() + 6)
    return {
      start: formatDate(monday),
      end: formatDate(sunday)
    }
  }

  const getMonthRange = (date: Date) => {
    return {
      start: formatDate(new Date(date.getFullYear(), date.getMonth(), 1)),
      end: formatDate(new Date(date.getFullYear(), date.getMonth() + 1, 0))
    }
  }

  const getLastNDays = (n: number) => {
    const end = new Date(today)
    const start = new Date(today)
    start.setDate(start.getDate() - n + 1)
    return {
      start: formatDate(start),
      end: formatDate(end)
    }
  }

  const getPreviousNDays = (n: number) => {
    const end = new Date(today)
    end.setDate(end.getDate() - n)
    const start = new Date(end)
    start.setDate(start.getDate() - n + 1)
    return {
      start: formatDate(start),
      end: formatDate(end)
    }
  }

  switch (mode) {
    case 'today_vs_yesterday':
      return {
        left: { label: 'Bugün', start: formatDate(today), end: formatDate(today) },
        right: { label: 'Dün', start: formatDate(yesterday), end: formatDate(yesterday) }
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
  if (mode === 'custom') {
    // Switch to custom mode but keep dropdown open to show date inputs
    updateConfig('custom')
  } else {
    // For predefined modes, update and close dropdown
    updateConfig(mode)
    isOpen.value = false
  }
}

function applyCustomRange() {
  // Clear previous validation errors
  validationError.value = ''

  // Validate all fields are filled
  if (!customLeftStart.value || !customLeftEnd.value || !customRightStart.value || !customRightEnd.value) {
    validationError.value = 'Tüm tarih alanlarını doldurun'
    return
  }

  // Validate dates are valid
  const leftStart = new Date(customLeftStart.value)
  const leftEnd = new Date(customLeftEnd.value)
  const rightStart = new Date(customRightStart.value)
  const rightEnd = new Date(customRightEnd.value)

  if (isNaN(leftStart.getTime()) || isNaN(leftEnd.getTime()) ||
      isNaN(rightStart.getTime()) || isNaN(rightEnd.getTime())) {
    validationError.value = 'Geçerli tarihler girin'
    return
  }

  // Validate start <= end for both periods
  if (leftStart > leftEnd) {
    validationError.value = 'Sol aralık: başlangıç tarihi bitiş tarihinden önce olmalı'
    return
  }

  if (rightStart > rightEnd) {
    validationError.value = 'Sağ aralık: başlangıç tarihi bitiş tarihinden önce olmalı'
    return
  }

  // All validations passed
  updateConfig('custom')
  isOpen.value = false
}
</script>

<template>
  <div class="relative" ref="dropdownRef">
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
          @click="selectMode('custom')"
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

        <!-- Validation error message -->
        <div v-if="validationError && modelValue.mode === 'custom'" class="mt-2 text-xs text-red-600">
          {{ validationError }}
        </div>

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
