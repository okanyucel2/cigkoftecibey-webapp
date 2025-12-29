/**
 * Date Range Filter Types
 * Used for DateRangeFilter component and useDateRangeFilter composable
 */

/**
 * Filter mode: month-based (dropdown) or custom date range (picker)
 */
export type DateRangeMode = 'month' | 'range'

/**
 * Date range value structure
 */
export interface DateRangeValue {
  mode: DateRangeMode
  start: string        // 'YYYY-MM-DD' format
  end: string          // 'YYYY-MM-DD' format
  month?: number       // 1-12 (only for mode='month')
  year?: number        // e.g., 2025 (only for mode='month')
  preset?: string      // Preset key if a preset is selected
}

/**
 * Preset option for quick date range selection
 */
export interface PresetOption {
  key: string                    // Unique identifier (e.g., 'today', 'last7')
  label: string                  // Display label (e.g., 'Bugün', 'Son 7 Gün')
  getRange: () => DateRange      // Function that returns the date range
}

/**
 * Date range pair
 */
export interface DateRange {
  start: Date
  end: Date
}

/**
 * Available locale options
 */
export type DateRangeLocale = 'tr' | 'en'

/**
 * Date format options
 */
export type DateFormat = 'DD.MM.YYYY' | 'MM/DD/YYYY' | 'YYYY-MM-DD'
