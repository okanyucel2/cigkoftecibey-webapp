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
  today_profit: number
  today_production_kg: number
  today_production_cost: number
  week_sales: { date: string; day: string; sales: number }[]
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
  record_type: 'salary' | 'advance' | 'weekly'
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
