import { ref, computed } from 'vue'

/**
 * Turkish month names for dropdowns
 */
export const MONTHS = [
  { value: 1, label: 'Ocak' },
  { value: 2, label: 'Subat' },
  { value: 3, label: 'Mart' },
  { value: 4, label: 'Nisan' },
  { value: 5, label: 'Mayis' },
  { value: 6, label: 'Haziran' },
  { value: 7, label: 'Temmuz' },
  { value: 8, label: 'Agustos' },
  { value: 9, label: 'Eylul' },
  { value: 10, label: 'Ekim' },
  { value: 11, label: 'Kasim' },
  { value: 12, label: 'Aralik' }
] as const

export type Month = (typeof MONTHS)[number]

/**
 * Composable for month/year filtering
 * Provides reactive state and helper functions for date range filtering
 */
export function useMonthYearFilter(options?: { yearsBack?: number }) {
  const currentDate = new Date()
  const yearsBack = options?.yearsBack ?? 2

  // Reactive state
  const selectedMonth = ref(currentDate.getMonth() + 1) // 1-12
  const selectedYear = ref(currentDate.getFullYear())

  // Computed years list (current year + previous years)
  const years = computed(() => {
    const currentYear = new Date().getFullYear()
    return Array.from({ length: yearsBack + 1 }, (_, i) => currentYear - i)
  })

  // Get the selected month label
  const selectedMonthLabel = computed(() => {
    return MONTHS.find(m => m.value === selectedMonth.value)?.label || ''
  })

  // Get date range for the selected month
  const dateRange = computed(() => {
    const startDate = new Date(selectedYear.value, selectedMonth.value - 1, 1)
    const endDate = new Date(selectedYear.value, selectedMonth.value, 0)

    return {
      start: startDate,
      end: endDate,
      startStr: startDate.toISOString().split('T')[0],
      endStr: endDate.toISOString().split('T')[0]
    }
  })

  // Format the period as "Ocak 2025"
  const periodLabel = computed(() => {
    return `${selectedMonthLabel.value} ${selectedYear.value}`
  })

  // Reset to current month/year
  function resetToCurrentPeriod() {
    const now = new Date()
    selectedMonth.value = now.getMonth() + 1
    selectedYear.value = now.getFullYear()
  }

  // Go to previous month
  function previousMonth() {
    if (selectedMonth.value === 1) {
      selectedMonth.value = 12
      selectedYear.value--
    } else {
      selectedMonth.value--
    }
  }

  // Go to next month
  function nextMonth() {
    if (selectedMonth.value === 12) {
      selectedMonth.value = 1
      selectedYear.value++
    } else {
      selectedMonth.value++
    }
  }

  return {
    // State
    selectedMonth,
    selectedYear,

    // Data
    months: MONTHS,
    years,

    // Computed
    selectedMonthLabel,
    dateRange,
    periodLabel,

    // Actions
    resetToCurrentPeriod,
    previousMonth,
    nextMonth
  }
}
