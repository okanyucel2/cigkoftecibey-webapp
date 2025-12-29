<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import type { DateRangeValue, PresetOption } from '@/types/filters'
import { formatDateToISO, formatDateToDisplay } from '@/utils/dateUtils'
import CustomRangeModal from './CustomRangeModal.vue'

// Preset definitions with icons
const PRESETS: PresetOption[] = [
  { key: 'today', label: 'Bugün', getRange: () => {
    const today = new Date()
    return { start: today, end: today }
  }},
  { key: 'yesterday', label: 'Dün', getRange: () => {
    const yesterday = new Date()
    yesterday.setDate(yesterday.getDate() - 1)
    return { start: yesterday, end: yesterday }
  }},
  { key: 'thisMonth', label: 'Bu Ay', getRange: () => {
    const now = new Date()
    const start = new Date(now.getFullYear(), now.getMonth(), 1)
    const end = new Date(now.getFullYear(), now.getMonth() + 1, 0)
    return { start, end }
  }},
  { key: 'lastMonth', label: 'Geçen Ay', getRange: () => {
    const now = new Date()
    const start = new Date(now.getFullYear(), now.getMonth() - 1, 1)
    const end = new Date(now.getFullYear(), now.getMonth(), 0)
    return { start, end }
  }},
  { key: 'last7', label: 'Son 7 Gün', getRange: () => {
    const end = new Date()
    const start = new Date()
    start.setDate(start.getDate() - 6)
    return { start, end }
  }},
  { key: 'last30', label: 'Son 30 Gün', getRange: () => {
    const end = new Date()
    const start = new Date()
    start.setDate(start.getDate() - 29)
    return { start, end }
  }},
  { key: 'last90', label: 'Son 90 Gün', getRange: () => {
    const end = new Date()
    const start = new Date()
    start.setDate(start.getDate() - 89)
    return { start, end }
  }},
  { key: 'thisQuarter', label: 'Bu Çeyrek', getRange: () => {
    const now = new Date()
    const quarterStart = Math.floor(now.getMonth() / 3) * 3
    const start = new Date(now.getFullYear(), quarterStart, 1)
    const end = new Date(now.getFullYear(), quarterStart + 3, 0)
    return { start, end }
  }},
  { key: 'thisYear', label: 'Bu Yıl', getRange: () => {
    const now = new Date()
    const start = new Date(now.getFullYear(), 0, 1)
    const end = new Date(now.getFullYear(), 11, 31)
    return { start, end }
  }}
]

// Icons for presets
const PRESET_ICONS: Record<string, string> = {
  today: '📅',
  yesterday: '📆',
  thisMonth: '📊',
  lastMonth: '📊',
  last7: '📈',
  last30: '📉',
  last90: '📉',
  thisQuarter: '📊',
  thisYear: '📊',
  custom: '✏️'
}

// Props
const props = withDefaults(
  defineProps<{
    modelValue: DateRangeValue
    maxDate?: Date
  }>(),
  {
    maxDate: () => new Date()
  }
)

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: DateRangeValue]
}>()

// State
const isDropdownOpen = ref(false)
const showCustomModal = ref(false)
const currentPreset = ref<string>('thisMonth')
const startDate = ref<string>(props.modelValue.start)
const endDate = ref<string>(props.modelValue.end)
const dropdownRef = ref<HTMLElement | null>(null)

// Computed: Current label for dropdown button
const currentLabel = computed(() => {
  if (currentPreset.value === 'custom') {
    return 'Özel Tarih'
  }
  const preset = PRESETS.find(p => p.key === currentPreset.value)
  return preset?.label || 'Bu Ay'
})

// Computed: Current icon
const currentIcon = computed(() => {
  return PRESET_ICONS[currentPreset.value] || '📊'
})

// Computed: Display date range (right side)
const displayRange = computed(() => {
  if (startDate.value === endDate.value) {
    return formatDateToDisplay(startDate.value)
  }
  return `${formatDateToDisplay(startDate.value)} - ${formatDateToDisplay(endDate.value)}`
})

// Detect which preset matches current date range
function detectPreset(): string {
  for (const preset of PRESETS) {
    const range = preset.getRange()
    const presetStart = formatDateToISO(range.start)
    const presetEnd = formatDateToISO(range.end)
    if (startDate.value === presetStart && endDate.value === presetEnd) {
      return preset.key
    }
  }
  return 'custom'
}

// Initialize
onMounted(() => {
  currentPreset.value = detectPreset()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// Watch modelValue changes from parent
watch(() => props.modelValue, (newValue) => {
  startDate.value = newValue.start
  endDate.value = newValue.end
  currentPreset.value = detectPreset()
}, { deep: true })

// Emit changes when dates change
watch([startDate, endDate], () => {
  emit('update:modelValue', {
    mode: 'range',
    start: startDate.value,
    end: endDate.value,
    preset: currentPreset.value === 'custom' ? undefined : currentPreset.value
  })
})

// Handle preset selection
function selectPreset(presetKey: string) {
  if (presetKey === 'custom') {
    // Open custom range modal
    showCustomModal.value = true
  } else {
    const preset = PRESETS.find(p => p.key === presetKey)
    if (preset) {
      const range = preset.getRange()
      startDate.value = formatDateToISO(range.start)
      endDate.value = formatDateToISO(range.end)
      currentPreset.value = presetKey
    }
  }
  isDropdownOpen.value = false
}

// Handle custom range applied from modal
function handleCustomRangeApply(range: { start: Date; end: Date }) {
  startDate.value = formatDateToISO(range.start)
  endDate.value = formatDateToISO(range.end)
  currentPreset.value = 'custom'
  showCustomModal.value = false
}

// Toggle dropdown
function toggleDropdown() {
  isDropdownOpen.value = !isDropdownOpen.value
}

// Close dropdown
function closeDropdown() {
  isDropdownOpen.value = false
}

// Handle click outside
function handleClickOutside(event: MouseEvent) {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    closeDropdown()
  }
}
</script>

<template>
  <div class="single-row-date-filter" ref="dropdownRef">
    <!-- Main Row -->
    <div class="flex items-center justify-between bg-white rounded-lg border border-gray-200 px-4 py-2 h-[42px]">
      <!-- Left: Preset Dropdown -->
      <div class="relative">
        <button
          @click="toggleDropdown"
          class="flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <span class="text-lg">{{ currentIcon }}</span>
          <span class="text-sm font-medium text-gray-900">{{ currentLabel }}</span>
          <svg
            class="w-4 h-4 text-gray-500 transition-transform"
            :class="{ 'rotate-180': isDropdownOpen }"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        <!-- Dropdown Menu -->
        <div
          v-if="isDropdownOpen"
          class="absolute top-full left-0 mt-1 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50"
          @click.stop
        >
          <button
            v-for="preset in PRESETS"
            :key="preset.key"
            @click="selectPreset(preset.key)"
            class="w-full flex items-center gap-3 px-4 py-2.5 text-sm hover:bg-gray-100 transition-colors text-left"
            :class="{ 'bg-red-50 text-red-700': currentPreset === preset.key }"
          >
            <span class="text-base">{{ PRESET_ICONS[preset.key] }}</span>
            <span>{{ preset.label }}</span>
            <svg
              v-if="currentPreset === preset.key"
              class="w-4 h-4 ml-auto text-red-600"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fill-rule="evenodd"
                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                clip-rule="evenodd"
              />
            </svg>
          </button>

          <!-- Separator -->
          <div class="my-2 border-t border-gray-200"></div>

          <!-- Custom Range Option -->
          <button
            @click="selectPreset('custom')"
            class="w-full flex items-center gap-3 px-4 py-2.5 text-sm hover:bg-gray-100 transition-colors text-left"
            :class="{ 'bg-red-50 text-red-700': currentPreset === 'custom' }"
          >
            <span class="text-base">✏️</span>
            <span>Özel Tarih Belirle...</span>
          </button>
        </div>
      </div>

      <!-- Right: Date Range Display (Readonly) -->
      <div class="text-sm text-gray-600 font-medium">
        {{ displayRange }}
      </div>
    </div>

    <!-- Custom Range Modal -->
    <CustomRangeModal
      :show="showCustomModal"
      :initial-start="startDate"
      :initial-end="endDate"
      :max-date="maxDate"
      @close="showCustomModal = false"
      @apply="handleCustomRangeApply"
    />
  </div>
</template>

<style scoped>
.single-row-date-filter {
  position: relative;
}
</style>
