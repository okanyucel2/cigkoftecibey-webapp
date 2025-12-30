/**
 * Date utility functions for formatting
 */

const TURKISH_MONTHS_SHORT = [
  'Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz',
  'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara'
]

/**
 * Format Date to 'YYYY-MM-DD' string (ISO format)
 */
export function formatDateToISO(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

/**
 * Format Date to display string (DD.MM.YYYY)
 */
export function formatDateToDisplay(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date
  const day = String(d.getDate()).padStart(2, '0')
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const year = d.getFullYear()
  return `${day}.${month}.${year}`
}

/**
 * Format Date to Turkish display (DD Mon YYYY)
 */
export function formatDateToTurkish(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date
  const day = d.getDate()
  const month = TURKISH_MONTHS_SHORT[d.getMonth()]
  const year = d.getFullYear()
  return `${day} ${month} ${year}`
}

/**
 * Format a date range to compact display string
 * Examples:
 *   - Same day: "29 Ara 2025"
 *   - Same month: "29-30 Ara 2025"
 *   - Same year: "29 Ara - 15 Oca 2025"
 *   - Different years: "29 Ara 2024 - 15 Oca 2025"
 */
export function formatDateRangeCompact(start: Date | string, end: Date | string): string {
  const s = typeof start === 'string' ? new Date(start) : start
  const e = typeof end === 'string' ? new Date(end) : end

  const sDay = s.getDate()
  const eDay = e.getDate()
  const sMonth = TURKISH_MONTHS_SHORT[s.getMonth()]
  const eMonth = TURKISH_MONTHS_SHORT[e.getMonth()]
  const sYear = s.getFullYear()
  const eYear = e.getFullYear()

  // Same date
  if (s.getTime() === e.getTime()) {
    return `${sDay} ${sMonth} ${sYear}`
  }

  // Same day and month (shouldn't happen with different dates, but handle it)
  if (sDay === eDay && sMonth === eMonth && sYear === eYear) {
    return `${sDay} ${sMonth} ${sYear}`
  }

  // Same month and year
  if (sMonth === eMonth && sYear === eYear) {
    return `${sDay}-${eDay} ${sMonth} ${sYear}`
  }

  // Same year, different month
  if (sYear === eYear) {
    return `${sDay} ${sMonth} - ${eDay} ${eMonth} ${sYear}`
  }

  // Different years
  return `${sDay} ${sMonth} ${sYear} - ${eDay} ${eMonth} ${eYear}`
}
