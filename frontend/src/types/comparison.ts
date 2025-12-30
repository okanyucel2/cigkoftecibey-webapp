// frontend/src/types/comparison.ts
export type ComparisonMode =
  | 'today_vs_yesterday'
  | 'this_week_vs_last_week'
  | 'this_month_vs_last_month'
  | 'last_7_vs_previous_7'
  | 'last_30_vs_previous_30'
  | 'custom'

export interface ComparisonPeriod {
  label: string
  start: string // ISO date
  end: string   // ISO date
}

export interface ComparisonConfig {
  mode: ComparisonMode
  leftPeriod: ComparisonPeriod
  rightPeriod: ComparisonPeriod
}

export interface ComparisonModeOption {
  value: ComparisonMode
  label: string
  description: string
  icon: string
}
