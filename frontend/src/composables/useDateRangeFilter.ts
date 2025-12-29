import { ref, computed } from 'vue'
import type { DateRangeMode, DateRangeValue, PresetOption, DateRange } from '@/types/filters'
import { MONTHS } from './useMonthYearFilter'

/**
 * Preset label mappings (Turkish)
 */
const PRESET_LABELS: Record<string, string> = {
  today: 'Bugün',
  last7: 'Son 7 Gün',
  last30: 'Son 30 Gün',
  last90: 'Son 90 Gün',
  thisQuarter: 'Bu Çeyrek',
  thisYear: 'Bu Yıl'
}

/**
 * Get today's date range (same day)
 */
function getTodayRange(): DateRange {
  const today = new Date()
  return { start: today, end: today }
}

/**
 * Get last N days range
 */
function getLastDaysRange(days: number): DateRange {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - days + 1)
  return { start, end }
}

/**
 * Get current quarter range
 */
function getQuarterRange(): DateRange {
  const now = new Date()
  const currentMonth = now.getMonth() // 0-11
  const quarterStart = Math.floor(currentMonth / 3) * 3
  const start = new Date(now.getFullYear(), quarterStart, 1)
  const end = new Date(now.getFullYear(), quarterStart + 3, 0)
  return { start, end }
}

/**
 * Get current year range
 */
function getYearRange(): DateRange {
  const now = new Date()
  const start = new Date(now.getFullYear(), 0, 1)
  const end = new Date(now.getFullYear(), 11, 31)
  return { start, end }
}

/**
 * Get current month range
 */
function getCurrentMonthRange(): DateRange {
  const now = new Date()
  const start = new Date(now.getFullYear(), now.getMonth(), 1)
  const end = new Date(now.getFullYear(), now.getMonth() + 1, 0)
  return { start, end }
}

/**
 * Available preset options
 */
export const PRESETS: PresetOption[] = [
  { key: 'today', label: 'Bugün', getRange: getTodayRange },
  { key: 'last7', label: 'Son 7 Gün', getRange: () => getLastDaysRange(7) },
  { key: 'last30', label: 'Son 30 Gün', getRange: () => getLastDaysRange(30) },
  { key: 'last90', label: 'Son 90 Gün', getRange: () => getLastDaysRange(90) },
  { key: 'thisQuarter', label: 'Bu Çeyrek', getRange: getQuarterRange },
  { key: 'thisYear', label: 'Bu Yıl', getRange: getYearRange }
]

/**
 * Format Date to 'YYYY-MM-DD' string
 */
function formatDateToISO(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

/**
 * Format Date to display string (DD.MM.YYYY)
 */
function formatDateToDisplay(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date
  const day = String(d.getDate()).padStart(2, '0')
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const year = d.getFullYear()
  return `${day}.${month}.${year}`
}

/**
 * Composable for date range filtering
 * Provides reactive state and helper functions for date range selection
 *
 * @param options - Configuration options
 * @returns Reactive state and methods
 */
export function useDateRangeFilter(options?: {
  initialMode?: DateRangeMode
  initialMonth?: number
  initialYear?: number
}) {
  const currentDate = new Date()
  const initialMode = options?.initialMode ?? 'month'

  // Reactive state
  const mode = ref<DateRangeMode>(initialMode)
  const selectedMonth = ref(options?.initialMonth ?? currentDate.getMonth() + 1)
  const selectedYear = ref(options?.initialYear ?? currentDate.getFullYear())
  const startDate = ref<string>(formatDateToISO(getCurrentMonthRange().start))
  const endDate = ref<string>(formatDateToISO(getCurrentMonthRange().end))
  const selectedPreset = ref<string | null>(null)

  // Computed: Month label for display
  const selectedMonthLabel = computed(() => {
    return MONTHS.find(m => m.value === selectedMonth.value)?.label || ''
  })

  // Computed: Filter value (for v-model)
  const filterValue = computed((): DateRangeValue => {
    if (mode.value === 'month') {
      // Calculate month start/end
      const start = new Date(selectedYear.value, selectedMonth.value - 1, 1)
      const end = new Date(selectedYear.value, selectedMonth.value, 0)
      return {
        mode: 'month',
        start: formatDateToISO(start),
        end: formatDateToISO(end),
        month: selectedMonth.value,
        year: selectedYear.value
      }
    } else {
      return {
        mode: 'range',
        start: startDate.value,
        end: endDate.value,
        preset: selectedPreset.value || undefined
      }
    }
  })

  // Computed: Display label (for UI)
  const displayLabel = computed(() => {
    if (mode.value === 'month') {
      return `${selectedMonthLabel.value} ${selectedYear.value}`
    }
    if (selectedPreset.value && PRESET_LABELS[selectedPreset.value]) {
      return PRESET_LABELS[selectedPreset.value]
    }
    if (startDate.value === endDate.value) {
      return formatDateToDisplay(startDate.value)
    }
    return `${formatDateToDisplay(startDate.value)} - ${formatDateToDisplay(endDate.value)}`
  })

  // Computed: Years list for dropdown
  const years = computed(() => {
    const currentYear = new Date().getFullYear()
    return Array.from({ length: 4 }, (_, i) => currentYear - i)
  })

  /**
   * Set date range directly
   */
  function setRange(start: string, end: string, preset?: string) {
    // Ensure start <= end
    const startDateObj = new Date(start)
    const endDateObj = new Date(end)

    if (startDateObj > endDateObj) {
      // Swap if start is after end
      startDate.value = end
      endDate.value = start
    } else {
      startDate.value = start
      endDate.value = end
    }

    selectedPreset.value = preset || null
  }

  /**
   * Set month and year (for month mode)
   */
  function setMonthYear(month: number, year: number) {
    selectedMonth.value = month
    selectedYear.value = year

    // Also update date range for consistency
    const start = new Date(year, month - 1, 1)
    const end = new Date(year, month, 0)
    startDate.value = formatDateToISO(start)
    endDate.value = formatDateToISO(end)
  }

  /**
   * Apply a preset range
   */
  function applyPreset(presetKey: string) {
    const preset = PRESETS.find(p => p.key === presetKey)
    if (preset) {
      const range = preset.getRange()
      setRange(
        formatDateToISO(range.start),
        formatDateToISO(range.end),
        presetKey
      )
    }
  }

  /**
   * Reset to current period
   */
  function resetToCurrent() {
    const now = new Date()
    selectedMonth.value = now.getMonth() + 1
    selectedYear.value = now.getFullYear()

    const currentRange = getCurrentMonthRange()
    startDate.value = formatDateToISO(currentRange.start)
    endDate.value = formatDateToISO(currentRange.end)
    selectedPreset.value = null
  }

  /**
   * Switch between modes
   */
  function setMode(newMode: DateRangeMode) {
    mode.value = newMode

    // When switching to month mode, sync dates to selected month/year
    if (newMode === 'month') {
      const start = new Date(selectedYear.value, selectedMonth.value - 1, 1)
      const end = new Date(selectedYear.value, selectedMonth.value, 0)
      startDate.value = formatDateToISO(start)
      endDate.value = formatDateToISO(end)
      selectedPreset.value = null
    } else {
      // When switching to range mode, clear preset
      selectedPreset.value = null
    }
  }

  return {
    // State
    mode,
    selectedMonth,
    selectedYear,
    startDate,
    endDate,
    selectedPreset,

    // Data
    presets: PRESETS,
    presetLabels: PRESET_LABELS,
    years,
    months: MONTHS,

    // Computed
    filterValue,
    displayLabel,
    selectedMonthLabel,

    // Actions
    setRange,
    setMonthYear,
    applyPreset,
    resetToCurrent,
    setMode
  }
}

export type UseDateRangeFilterReturn = ReturnType<typeof useDateRangeFilter>
