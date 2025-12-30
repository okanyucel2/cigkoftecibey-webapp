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

export interface RevenueBreakdown {
  visa: number
  nakit: number
  online: number
  trendyol?: number
  getir?: number
  yemeksepeti?: number
  migros?: number
}

export interface ExpenseBreakdown {
  mal_alimi: number
  gider: number
  staff: number
  kurye: number
  parttime: number
  uretim: number
}

export interface BilancoPeriodData {
  period_label: string
  start_date: string
  end_date: string
  revenue_breakdown: RevenueBreakdown
  total_revenue: number
  expense_breakdown: ExpenseBreakdown
  total_expenses: number
  net_profit: number
  profit_margin: number
}

export interface DeltaMetric {
  label: string        // Human-readable label (e.g., "Ciro Farkı")
  absolute: number     // Absolute difference (right - left)
  percentage: number   // Percentage change
  isPositive: boolean  // true = good change, false = bad change
  // Note: For expenses, "positive" means decrease (costs went down)
}

export interface DeltaData {
  revenue: DeltaMetric
  expenses: DeltaMetric
  profit: DeltaMetric
  profitMargin: DeltaMetric  // In percentage points (pp)
}
