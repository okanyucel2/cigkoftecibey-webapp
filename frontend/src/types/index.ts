export interface User {
  id: number
  branch_id: number | null
  organization_id: number | null
  email: string
  name: string
  role: string
  is_active: boolean
  is_super_admin: boolean
  google_id?: string
  avatar_url?: string
  auth_provider: 'email' | 'google'
  created_at: string
  current_branch_id: number | null
  accessible_branches: Branch[]
}

export interface Branch {
  id: number
  name: string
  code: string
  city?: string
  address?: string
  phone?: string
  is_active: boolean
}

// Sales Channel (Birleşik satış kanalları)
export interface SalesChannel {
  id: number
  name: string
  channel_type: 'pos_salon' | 'pos_telefon' | 'online'
  is_system: boolean
  display_order: number
}

export interface ChannelsGrouped {
  pos: SalesChannel[]
  online: SalesChannel[]
}

export interface TodaySalesEntry {
  platform_id: number
  platform_name: string
  channel_type: string
  is_system: boolean
  amount: number
  sale_id: number | null
}

export interface TodaySalesResponse {
  sale_date: string
  entries: TodaySalesEntry[]
  total: number
}

export interface Supplier {
  id: number
  branch_id: number
  name: string
  phone?: string
  is_active: boolean
}

export interface PurchaseProduct {
  id: number
  group_id: number
  name: string
  default_unit: string
  display_order: number
  is_active: boolean
}

export interface PurchaseProductGroup {
  id: number
  name: string
  display_order: number
  is_active: boolean
  products: PurchaseProduct[]
}

export interface PurchaseItem {
  id?: number
  product_id?: number
  description: string
  quantity: number
  unit: string
  unit_price: number
  total?: number
  product?: PurchaseProduct
}

export interface Purchase {
  id: number
  branch_id: number
  supplier_id: number
  purchase_date: string
  total: number
  notes?: string
  created_by: number
  created_at: string
  items: PurchaseItem[]
  supplier?: Supplier
}

export interface ExpenseCategory {
  id: number
  name: string
  is_fixed: boolean
  display_order: number
}

export interface Expense {
  id: number
  branch_id: number
  category_id: number
  expense_date: string
  description?: string
  amount: number
  created_by: number
  created_at: string
  category?: ExpenseCategory
}

export interface DashboardStats {
  today_salon: number  // Salon satışları
  today_telefon: number  // Telefon paket satışları
  today_online_sales: number  // Online platform satışları toplamı
  today_total_sales: number  // Salon + Telefon + Online
  online_breakdown: Record<string, number>  // Platform bazlı: {"Trendyol": 1500, "Getir": 800}
  online_platform_count: number  // Satış yapılan online platform sayısı
  today_purchases: number
  today_expenses: number
  today_staff_meals: number
  today_courier_cost: number
  today_part_time_cost: number
  today_profit: number
  today_production_kg: number
  today_production_cost: number
  week_sales: { date: string; day: string; sales: number }[]
}

// Bilanço Dashboard Types
export interface DaySummary {
  day_name: string  // "Pzt", "Sal", etc.
  date: string
  amount: number
}

export interface BilancoStats {
  // Bugün (şu ana kadar)
  today_date: string
  today_day_name: string  // "Pazartesi"
  today_revenue: number
  today_expenses: number
  today_profit: number
  today_breakdown: {
    visa: number
    nakit: number
    online: number
    mal_alimi: number
    gider: number
    staff: number
    kurye: number
    parttime: number
    uretim: number
  }

  // Dün
  yesterday_date: string
  yesterday_day_name: string  // "Pazartesi"
  yesterday_revenue: number
  yesterday_expenses: number
  yesterday_profit: number
  yesterday_vs_previous_pct: number
  yesterday_breakdown: {
    visa: number
    nakit: number
    online: number
    mal_alimi: number
    gider: number
    staff: number
    kurye: number
    parttime: number
    uretim: number
  }

  // Bu Hafta
  this_week_start: string
  this_week_end: string
  this_week_total: number
  this_week_daily: DaySummary[]
  this_week_best_day: DaySummary | null
  this_week_worst_day: DaySummary | null
  this_week_breakdown: {
    visa: number
    nakit: number
    online: number
    mal_alimi: number
    gider: number
    staff: number
    kurye: number
    parttime: number
    uretim: number
  }

  // Geçen Hafta
  last_week_start: string
  last_week_end: string
  last_week_total: number
  last_week_daily: DaySummary[]
  week_vs_week_pct: number
  last_week_breakdown: {
    visa: number
    nakit: number
    online: number
    mal_alimi: number
    gider: number
    staff: number
    kurye: number
    parttime: number
    uretim: number
  }

  // Bu Ay
  this_month_name: string  // "Aralık 2025"
  this_month_days_passed: number
  this_month_days_total: number
  this_month_revenue: number
  this_month_expenses: number
  this_month_profit: number
  this_month_daily_avg: number
  this_month_forecast: number
  this_month_chart: DaySummary[]
  this_month_breakdown: {
    visa: number
    nakit: number
    online: number
    mal_alimi: number
    gider: number
    staff: number
    kurye: number
    parttime: number
    uretim: number
  }

  // Geçen Ay
  last_month_revenue: number
  last_month_expenses: number
  last_month_profit: number
  last_month_breakdown: {
    visa: number
    nakit: number
    online: number
    mal_alimi: number
    gider: number
    staff: number
    kurye: number
    parttime: number
    uretim: number
  }
}

export interface StaffMeal {
  id: number
  branch_id: number
  meal_date: string
  unit_price: number
  staff_count: number
  total: number
  notes?: string
  created_by: number
  created_at: string
}

export interface StaffMealSummary {
  total_staff_count: number
  total_cost: number
  avg_daily_staff: number
  avg_unit_price: number
  days_count: number
}

export interface DailyProduction {
  id: number
  branch_id: number
  production_date: string
  production_type: string  // 'etli' or 'etsiz'
  kneaded_kg: number
  legen_kg: number
  legen_cost: number
  legen_count: number
  total_cost: number
  notes?: string
  created_by: number
  created_at: string
}

export interface ProductionSummary {
  total_kneaded_kg: number
  total_legen_count: number
  total_cost: number
  avg_daily_kg: number
  days_count: number
}


// Personnel Types
export interface Employee {
  id: number
  branch_id: number
  name: string
  base_salary: number
  has_sgk: boolean
  sgk_amount: number
  daily_rate: number
  hourly_rate: number
  payment_type: 'monthly' | 'weekly'
  is_part_time: boolean
  is_active: boolean
  created_at: string
}

export interface MonthlyPayroll {
  id: number
  branch_id: number
  employee_id: number
  year: number
  month: number
  payment_date: string
  record_type: 'salary' | 'advance' | 'weekly' | 'sgk' | 'prim'
  base_salary: number
  sgk_amount: number
  bonus: number
  premium: number
  overtime_hours: number
  overtime_amount: number
  advance: number
  absence_days: number
  absence_deduction: number
  total: number
  notes?: string
  created_by: number
  created_at: string
  employee?: Employee
}

export interface PayrollSummary {
  total_base_salary: number
  total_sgk: number
  total_bonus: number
  total_premium: number
  total_overtime: number
  total_advance: number
  total_deduction: number
  total_payroll: number
  employee_count: number
}

export interface PartTimeCost {
  id: number
  branch_id: number
  cost_date: string
  amount: number
  notes?: string
  created_by: number
  created_at: string
}

export interface PartTimeCostSummary {
  total_cost: number
  days_count: number
  avg_daily_cost: number
}

// Online Sales Types
export interface OnlinePlatform {
  id: number
  name: string
  channel_type: 'pos_salon' | 'pos_telefon' | 'online'
  is_system: boolean
  display_order: number
  is_active: boolean
}

export interface OnlineSale {
  id: number
  branch_id: number
  platform_id: number
  sale_date: string
  amount: number
  notes?: string
  created_by: number
  created_at: string
  updated_at?: string
  platform?: OnlinePlatform
}

export interface DailySalesEntry {
  platform_id: number
  amount: number
}

export interface DailySalesResponse {
  sale_date: string
  entries: OnlineSale[]
  total: number
}

export interface OnlineSalesSummary {
  total_amount: number
  platform_totals: Record<string, number>
  days_count: number
}

// Invitation Code Types
export interface InvitationCode {
  id: number
  code: string
  organization_id: number
  branch_id: number | null
  role: string
  max_uses: number
  used_count: number
  expires_at: string | null
  is_active: boolean
  created_by: number
  created_at: string
  is_valid: boolean
  branch?: Branch
}

export interface InvitationCodeValidation {
  valid: boolean
  message: string
  organization_name?: string
  branch_name?: string
  role?: string
}

// Google Auth Types
export interface GoogleAuthResponse {
  access_token: string
  token_type: string
  requires_onboarding: boolean
  user?: User
}

// Courier Expense Types
export interface CourierExpense {
  id: number
  branch_id: number
  expense_date: string
  package_count: number
  amount: number  // KDV haric
  vat_rate: number  // KDV orani (%)
  vat_amount: number  // KDV tutari
  total_with_vat: number  // KDV dahil toplam
  notes?: string
  created_by: number
  created_at: string
}

export interface CourierExpenseSummary {
  total_packages: number
  total_amount: number  // KDV haric toplam
  total_vat: number  // Toplam KDV
  total_with_vat: number  // KDV dahil genel toplam
  days_count: number
  avg_daily_packages: number
  avg_package_cost: number  // Paket basina ortalama maliyet
}

// Cash Difference (Kasa Farki) Types
export interface CashDifference {
  id: number
  branch_id: number
  difference_date: string
  // Kasa Raporu
  kasa_visa: number
  kasa_nakit: number
  kasa_trendyol: number
  kasa_getir: number
  kasa_yemeksepeti: number
  kasa_migros: number
  kasa_total: number
  // POS Hasilat
  pos_visa: number
  pos_nakit: number
  pos_trendyol: number
  pos_getir: number
  pos_yemeksepeti: number
  pos_migros: number
  pos_total: number
  // Diffs
  diff_visa: number
  diff_nakit: number
  diff_trendyol: number
  diff_getir: number
  diff_yemeksepeti: number
  diff_migros: number
  diff_total: number
  // Meta
  status: 'pending' | 'reviewed' | 'resolved' | 'flagged'
  severity: 'ok' | 'warning' | 'critical'
  resolution_note?: string
  resolved_by?: number
  resolved_at?: string
  // Files
  excel_file_url?: string
  pos_image_url?: string
  ocr_confidence_score?: number
  // Audit
  created_by: number
  created_at: string
}

export interface CashDifferenceSummary {
  total_records: number
  pending_count: number
  resolved_count: number
  critical_count: number
  total_diff: number
  period_start: string
  period_end: string
}

export interface CashDifferencePreviewDelete {
  cash_difference: {
    id: number
    difference_date: string
    kasa_total: number
    pos_total: number
  }
  related_entities: {
    expenses: Array<{
      id: number
      description: string
      amount: number
      expense_date: string
      reason?: string
    }>
    online_sales: Array<{
      id: number
      platform: string
      amount: number
      sale_date: string
      reason?: string
    }>
  }
  skipped_entities: {
    expenses: Array<{
      id: number
      description: string
      amount: number
      expense_date: string
      reason: string
    }>
    online_sales: Array<{
      id: number
      platform: string
      amount: number
      sale_date: string
      reason: string
    }>
  }
  summary: {
    total_expenses: number
    total_sales: number
    skipped_expenses: number
    skipped_sales: number
  }
}

export interface ExcelParseResult {
  date: string
  visa: number
  nakit: number
  trendyol: number
  getir: number
  yemeksepeti: number
  migros: number
  total: number
  expenses: Array<{
    description: string
    amount: number
    category_id?: number
    suggested_category?: string
    suggested_category_id?: number
  }>
}

export interface POSParseResult {
  date: string
  visa: number
  nakit: number
  trendyol: number
  getir: number
  yemeksepeti: number
  migros: number
  total: number
  confidence_score: number
}

// Re-export filter types for convenience
export type { DateRangeMode, DateRangeValue, PresetOption, DateRange, DateRangeLocale, DateFormat } from './filters'

// Re-export UI component types for convenience
export type { NavItem } from '@/components/ui/VerticalNav.vue'

// ============ Payment Types ============
export type PaymentType = 'cash' | 'eft' | 'check' | 'promissory' | 'partial'
export type PaymentStatus = 'pending' | 'completed' | 'cancelled'
export type TransactionType = 'order' | 'payment' | 'return' | 'adjustment'

// ============ Supplier AR ============
export interface SupplierARSummary {
  id: number
  name: string
  balance: number
  total_debt: number
  total_credit: number
  last_transaction_date: string | null
}

export interface SupplierARDetail extends SupplierARSummary {
  transactions: SupplierTransaction[]
}

export interface SupplierTransaction {
  id: number
  supplier_id: number
  transaction_type: TransactionType
  description: string
  debt_amount: number
  credit_amount: number
  running_balance: number
  reference_id: number | null
  reference_type: string | null
  transaction_date: string
  created_at: string
}

// ============ Payments ============
export interface SupplierPayment {
  id: number
  supplier_id: number
  supplier_name: string
  payment_type: PaymentType
  amount: number
  payment_date: string
  description: string | null
  reference: string | null
  bank_name: string | null
  transfer_code: string | null
  due_date: string | null
  serial_number: string | null
  status: PaymentStatus
  created_at: string
  updated_at: string
}

export interface CreatePaymentDTO {
  supplier_id: number
  payment_type: PaymentType
  amount: number
  payment_date: string
  description?: string
  reference?: string
  bank_name?: string
  transfer_code?: string
  due_date?: string
  serial_number?: string
}

export interface PaymentFilters {
  start_date?: string
  end_date?: string
  supplier_id?: number
  payment_type?: PaymentType
  search?: string
}

export interface PaymentSummary {
  today: number
  thisWeek: number
  thisMonth: number
  total: number
}

// Dashboard Comparison (for trend badges)
export interface ComparisonMetric {
  current: number
  previous: number
  diff: number
  diff_percent: number
}

export interface DashboardComparison {
  current_date: string
  compare_date: string
  sales: ComparisonMetric
  expenses: ComparisonMetric
}

// Daily Sales Analytics - AnalyticsEnvelope
export interface AnalyticsMeta {
  period_start: string
  period_end: string
  branch_id: number
  generated_at: string
  record_count: number
}

export interface AnalyticsSummary {
  total_kasa: number
  total_pos: number
  total_diff: number
  avg_daily_kasa: number
  avg_daily_pos: number
}

export interface DailySalesRecord {
  date: string
  kasa_visa: number
  kasa_nakit: number
  kasa_trendyol: number
  kasa_getir: number
  kasa_yemeksepeti: number
  kasa_migros: number
  kasa_total: number
  pos_visa: number
  pos_nakit: number
  pos_trendyol: number
  pos_getir: number
  pos_yemeksepeti: number
  pos_migros: number
  pos_total: number
  diff_total: number
  status: string
}

export interface AnalyticsData {
  daily_breakdown: DailySalesRecord[]
}

export interface AnalyticsEnvelope {
  meta: AnalyticsMeta
  data: AnalyticsData
  summary: AnalyticsSummary
}

// Error handling utilities
export * from './errors'
