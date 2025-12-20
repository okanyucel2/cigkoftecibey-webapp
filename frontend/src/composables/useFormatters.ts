/**
 * Composable for formatting utilities
 * Provides consistent formatting for currency, dates, and numbers across the app
 */
export function useFormatters() {
  /**
   * Format a number as Turkish Lira currency
   */
  function formatCurrency(value: number | string, options?: { decimals?: number }): string {
    const num = typeof value === 'string' ? parseFloat(value) : value
    return new Intl.NumberFormat('tr-TR', {
      style: 'currency',
      currency: 'TRY',
      minimumFractionDigits: options?.decimals ?? 0,
      maximumFractionDigits: options?.decimals ?? 2
    }).format(num || 0)
  }

  /**
   * Format a date string to Turkish locale
   */
  function formatDate(
    dateStr: string | Date,
    options?: {
      format?: 'short' | 'medium' | 'long'
      showWeekday?: boolean
    }
  ): string {
    const date = typeof dateStr === 'string' ? new Date(dateStr) : dateStr

    const formatOptions: Intl.DateTimeFormatOptions = {
      day: '2-digit'
    }

    switch (options?.format) {
      case 'short':
        formatOptions.month = '2-digit'
        formatOptions.year = 'numeric'
        break
      case 'long':
        formatOptions.month = 'long'
        formatOptions.year = 'numeric'
        if (options?.showWeekday) formatOptions.weekday = 'long'
        break
      case 'medium':
      default:
        formatOptions.month = 'long'
        if (options?.showWeekday) formatOptions.weekday = 'short'
        break
    }

    return date.toLocaleDateString('tr-TR', formatOptions)
  }

  /**
   * Format a number with Turkish locale grouping
   */
  function formatNumber(value: number | string, options?: { decimals?: number }): string {
    const num = typeof value === 'string' ? parseFloat(value) : value
    return new Intl.NumberFormat('tr-TR', {
      minimumFractionDigits: options?.decimals ?? 0,
      maximumFractionDigits: options?.decimals ?? 2
    }).format(num || 0)
  }

  /**
   * Format a percentage value
   */
  function formatPercent(value: number, options?: { decimals?: number }): string {
    return new Intl.NumberFormat('tr-TR', {
      style: 'percent',
      minimumFractionDigits: options?.decimals ?? 0,
      maximumFractionDigits: options?.decimals ?? 1
    }).format(value / 100)
  }

  /**
   * Safely convert a value to number
   */
  function toNumber(value: unknown): number {
    if (typeof value === 'number') return value
    if (typeof value === 'string') return parseFloat(value) || 0
    return 0
  }

  return {
    formatCurrency,
    formatDate,
    formatNumber,
    formatPercent,
    toNumber
  }
}
