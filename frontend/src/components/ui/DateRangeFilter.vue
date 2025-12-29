<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { VueDatePicker } from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'
import type { DateRangeValue, DateRangeMode } from '@/types/filters'
import { useDateRangeFilter } from '@/composables'

// Props
const props = withDefaults(
  defineProps<{
    modelValue: DateRangeValue
    availablePresets?: string[]
    format?: string
  }>(),
  {
    availablePresets: () => ['today', 'last7', 'last30', 'last90', 'thisQuarter', 'thisYear'],
    format: 'dd.MM.yyyy'
  }
)

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: DateRangeValue]
}>()

// Local state for datepicker (needs Date objects)
const pickerDates = ref<Date[]>([])

// Initialize composable with current mode
const {
  mode,
  selectedMonth,
  selectedYear,
  startDate,
  endDate,
  selectedPreset,
  presets,
  years,
  months,
  filterValue,
  displayLabel,
  setRange,
  setMonthYear,
  applyPreset,
  setMode
} = useDateRangeFilter({
  initialMode: props.modelValue.mode,
  initialMonth: props.modelValue.month,
  initialYear: props.modelValue.year
})

// Filter available presets
const availablePresets = computed(() => {
  return presets.filter(p => props.availablePresets.includes(p.key))
})

// Initialize dates from props
function initializeFromProps() {
  if (props.modelValue.start) {
    startDate.value = props.modelValue.start
  }
  if (props.modelValue.end) {
    endDate.value = props.modelValue.end
  }
  if (props.modelValue.mode) {
    mode.value = props.modelValue.mode
  }
  if (props.modelValue.preset) {
    selectedPreset.value = props.modelValue.preset
  }

  // Update picker dates
  updatePickerDates()
}

// Update picker dates from startDate/endDate
function updatePickerDates() {
  if (startDate.value && endDate.value) {
    pickerDates.value = [new Date(startDate.value), new Date(endDate.value)]
  }
}

// Sync mode from props
watch(
  () => props.modelValue.mode,
  (newMode) => {
    if (newMode !== mode.value) {
      mode.value = newMode
    }
  }
)

// Sync month/year from props
watch(
  () => [props.modelValue.month, props.modelValue.year],
  ([month, year]) => {
    if (month && year && mode.value === 'month') {
      selectedMonth.value = month
      selectedYear.value = year
    }
  }
)

// Emit changes when filterValue changes
watch(
  filterValue,
  (newValue) => {
    emit('update:modelValue', newValue)
  },
  { immediate: true }
)

// Handle mode toggle
function handleModeToggle(newMode: DateRangeMode) {
  setMode(newMode)
}

// Handle preset click
function handlePresetClick(presetKey: string) {
  applyPreset(presetKey)
}

// Handle month change
function handleMonthChange(month: number) {
  setMonthYear(month, selectedYear.value)
}

// Handle year change
function handleYearChange(year: number) {
  setMonthYear(selectedMonth.value, year)
}

// Handle datepicker change
function handleDateChange(dates: Date[]) {
  if (dates && dates.length === 2) {
    const start = dates[0].toISOString().split('T')[0]
    const end = dates[1].toISOString().split('T')[0]
    setRange(start, end)
  } else if (dates && dates.length === 1) {
    // Single date selection
    const dateStr = dates[0].toISOString().split('T')[0]
    setRange(dateStr, dateStr)
  }
}

// Format date for display
function formatDateForDisplay(dateStr: string): string {
  const date = new Date(dateStr)
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const year = date.getFullYear()
  return `${day}.${month}.${year}`
}

// Initialize on mount
initializeFromProps()
</script>

<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
    <!-- Row 1: Mode Toggle + Presets + Display Label -->
    <div class="flex flex-wrap items-center justify-between gap-3 mb-3">

      <!-- Left: Mode Toggle -->
      <div class="flex bg-gray-100 rounded-lg p-1">
        <button
          :class="[
            'px-4 py-2 rounded-md text-sm font-medium transition-colors',
            mode === 'month'
              ? 'bg-white text-red-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          ]"
          @click="handleModeToggle('month')"
        >
          Ay Bazlı
        </button>
        <button
          :class="[
            'px-4 py-2 rounded-md text-sm font-medium transition-colors',
            mode === 'range'
              ? 'bg-white text-red-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          ]"
          @click="handleModeToggle('range')"
        >
          Özel Aralık
        </button>
      </div>

      <!-- Center: Preset Buttons (range mode only) -->
      <div v-if="mode === 'range'" class="flex flex-wrap gap-2">
        <button
          v-for="preset in availablePresets"
          :key="preset.key"
          :class="[
            'px-3 py-1.5 rounded-md text-xs font-medium transition-colors',
            selectedPreset === preset.key
              ? 'bg-red-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          ]"
          @click="handlePresetClick(preset.key)"
        >
          {{ preset.label }}
        </button>
      </div>

      <!-- Right: Display Label / Spacer -->
      <div class="text-sm text-gray-600 font-medium min-w-[120px] text-right">
        {{ displayLabel }}
      </div>
    </div>

    <!-- Row 2: Input Area -->
    <div class="border-t border-gray-100 pt-3">

      <!-- Month Mode: Dropdown Selects -->
      <div v-if="mode === 'month'" class="flex items-center gap-3">
        <div class="flex items-center gap-2 bg-gray-50 rounded-lg px-3 py-2">
          <label class="text-sm text-gray-600">Ay:</label>
          <select
            :value="selectedMonth"
            @change="handleMonthChange(Number(($event.target as HTMLSelectElement).value))"
            class="bg-transparent border-none text-sm font-medium focus:ring-0 cursor-pointer"
          >
            <option v-for="month in months" :key="month.value" :value="month.value">
              {{ month.label }}
            </option>
          </select>
        </div>

        <div class="flex items-center gap-2 bg-gray-50 rounded-lg px-3 py-2">
          <label class="text-sm text-gray-600">Yıl:</label>
          <select
            :value="selectedYear"
            @change="handleYearChange(Number(($event.target as HTMLSelectElement).value))"
            class="bg-transparent border-none text-sm font-medium focus:ring-0 cursor-pointer"
          >
            <option v-for="year in years" :key="year" :value="year">
              {{ year }}
            </option>
          </select>
        </div>
      </div>

      <!-- Range Mode: Date Picker -->
      <div v-else class="flex items-center gap-3">
        <div class="flex-1">
          <VueDatePicker
            v-model="pickerDates"
            :range="true"
            :format="format"
            :enable-time-picker="false"
            :auto-apply="true"
            :max-date="new Date()"
            :text-input="true"
            :placeholder="'Başlangıç - Bitiş tarihi seçin'"
            input-class-name="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-red-500 focus:border-red-500"
            @update:model-value="handleDateChange"
          />
        </div>

        <!-- Quick Date Display -->
        <div class="flex items-center gap-2 text-sm text-gray-600 min-w-[200px]">
          <span class="bg-gray-50 px-3 py-2 rounded-lg">
            {{ startDate ? formatDateForDisplay(startDate) : '...' }}
          </span>
          <span>→</span>
          <span class="bg-gray-50 px-3 py-2 rounded-lg">
            {{ endDate ? formatDateForDisplay(endDate) : '...' }}
          </span>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* Custom styles for datepicker to match theme */
:deep(.dp__main) {
  border-radius: 0.5rem;
  border: 1px solid rgb(229 231 235);
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}

:deep(.dp__today) {
  border-color: rgb(220 38 38);
}

:deep(.dp__range_end, .dp__range_start, .dp__active_date) {
  background-color: rgb(220 38 38);
}

:deep(.dp__range_between) {
  background-color: rgb(254 226 226);
}

:deep(.dp__action_select) {
  background-color: rgb(220 38 38);
}

:deep(.dp__action_select:hover) {
  background-color: rgb(185 28 28);
}
</style>
