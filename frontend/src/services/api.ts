import axios from 'axios'
import type {
  User, Branch, ChannelsGrouped, TodaySalesResponse,
  Supplier, Purchase, ExpenseCategory, Expense, DashboardStats, BilancoStats,
  DailyProduction, ProductionSummary, PurchaseProductGroup,
  StaffMeal, StaffMealSummary,
  Employee, MonthlyPayroll, PayrollSummary, PartTimeCost, PartTimeCostSummary,
  OnlinePlatform, OnlineSale, DailySalesEntry, DailySalesResponse, OnlineSalesSummary,
  InvitationCode, InvitationCodeValidation, GoogleAuthResponse,
  CourierExpense, CourierExpenseSummary,
  CashDifference, CashDifferenceSummary, CashDifferencePreviewDelete, ExcelParseResult, POSParseResult
} from '@/types'
import type { ComparisonResponse } from '@/types/comparison'

// Render production URL - fallback for when env var isn't set at build time
const RENDER_BACKEND_URL = 'https://genesis-cigkofteci-bey-backend.onrender.com/api'

// Use VITE_API_URL if set, otherwise detect production by hostname
const baseURL = import.meta.env.VITE_API_URL ||
  (typeof window !== 'undefined' && window.location.hostname.includes('onrender.com')
    ? RENDER_BACKEND_URL
    : '/api')

const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Auth interceptor - adds Bearer token and X-Branch-Id header
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  // Add X-Branch-Id header for multi-branch context
  const currentBranchId = localStorage.getItem('currentBranchId')
  if (currentBranchId) {
    config.headers['X-Branch-Id'] = currentBranchId
  }

  return config
})

// Error interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      // Only redirect if we are not already on the login page
      // This allows the login page to handle 401 (wrong password) natively
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// Auth
export const authApi = {
  login: (email: string, password: string) =>
    api.post<{ access_token: string }>('/auth/login-json', { email, password }),

  me: () => api.get<User>('/auth/me'),

  switchBranch: (branchId: number) =>
    api.post<{ message: string; branch_id: number }>('/auth/switch-branch', { branch_id: branchId }),

  // Google OAuth
  googleLogin: (credential: string) =>
    api.post<GoogleAuthResponse>('/auth/google', { credential }),

  registerWithCode: (code: string, googleCredential: string) =>
    api.post<{ access_token: string }>('/auth/register-with-code', {
      code,
      google_credential: googleCredential
    })
}

// Branches
export const branchesApi = {
  getAll: () => api.get<Branch[]>('/branches'),
  getById: (id: number) => api.get<Branch>(`/branches/${id}`),
  create: (data: { name: string; code: string; address?: string; phone?: string }) =>
    api.post<Branch>('/branches', data),
  update: (id: number, data: { name: string; code: string; address?: string; phone?: string }) =>
    api.put<Branch>(`/branches/${id}`, data),
  delete: (id: number) => api.delete(`/branches/${id}`),
  activate: (id: number) => api.post(`/branches/${id}/activate`)
}

// Users (Admin only)
export interface UserBranchAssignment {
  id: number
  user_id: number
  branch_id: number
  role: string
  is_default: boolean
  branch_name: string
}

export interface UserWithBranches {
  id: number
  email: string
  name: string
  role: string
  branch_id: number
  is_active: boolean
  is_super_admin: boolean
  branches: UserBranchAssignment[]
}

export const usersApi = {
  getAll: () => api.get<UserWithBranches[]>('/users'),
  getById: (id: number) => api.get<UserWithBranches>(`/users/${id}`),
  create: (data: { email: string; password: string; name: string; role: string; branch_id: number }) =>
    api.post<User>('/users', data),
  update: (id: number, data: { name?: string; role?: string; is_active?: boolean; is_super_admin?: boolean }) =>
    api.put<User>(`/users/${id}`, data),
  assignToBranch: (userId: number, data: { user_id: number; branch_id: number; role: string; is_default?: boolean }) =>
    api.post<UserBranchAssignment>(`/users/${userId}/branches`, data),
  removeFromBranch: (userId: number, branchId: number) =>
    api.delete(`/users/${userId}/branches/${branchId}`)
}

// Unified Sales API (Birleşik Satış - POS + Online)
export const unifiedSalesApi = {
  // Get channels grouped by type (POS vs Online)
  getChannels: () => api.get<ChannelsGrouped>('/online-sales/channels'),

  // Get today's sales for all channels
  getToday: () => api.get<TodaySalesResponse>('/online-sales/today'),

  // Save daily sales (works for both POS and Online channels)
  saveDailySales: (data: { sale_date: string; entries: DailySalesEntry[]; notes?: string }) =>
    api.post<DailySalesResponse>('/online-sales/daily', data)
}

// Suppliers
export const suppliersApi = {
  getAll: () => api.get<Supplier[]>('/purchases/suppliers'),
  create: (data: { name: string; phone?: string }) =>
    api.post<Supplier>('/purchases/suppliers', data),
  update: (id: number, data: { name: string; phone?: string }) =>
    api.put<Supplier>(`/purchases/suppliers/${id}`, data),
  delete: (id: number) => api.delete(`/purchases/suppliers/${id}`)
}

// Purchase Product Groups (Ürün grupları ve ürünler)
export const purchaseProductsApi = {
  getGroups: () => api.get<PurchaseProductGroup[]>('/purchases/product-groups'),
  createGroup: (data: { name: string; display_order?: number }) =>
    api.post<PurchaseProductGroup>('/purchases/product-groups', data),
  updateGroup: (id: number, data: { name: string; display_order?: number }) =>
    api.put<PurchaseProductGroup>(`/purchases/product-groups/${id}`, data),
  deleteGroup: (id: number) => api.delete(`/purchases/product-groups/${id}`),
  createProduct: (data: { name: string; group_id: number; default_unit?: string }) =>
    api.post('/purchases/products', data),
  updateProduct: (id: number, data: { name: string; group_id: number; default_unit?: string }) =>
    api.put(`/purchases/products/${id}`, data),
  deleteProduct: (id: number) => api.delete(`/purchases/products/${id}`)
}

// Purchases
export const purchasesApi = {
  create: (data: {
    supplier_id: number
    purchase_date: string
    notes?: string
    items: { product_id?: number; description: string; quantity: number; unit: string; unit_price: number }[]
  }) => api.post<Purchase>('/purchases', data),

  getAll: (params?: { start_date?: string; end_date?: string; supplier_id?: number }) =>
    api.get<Purchase[]>('/purchases', { params }),

  getById: (id: number) => api.get<Purchase>(`/purchases/${id}`),

  update: (id: number, data: {
    supplier_id: number
    purchase_date: string
    notes?: string
    items: { product_id?: number; description: string; quantity: number; unit: string; unit_price: number }[]
  }) => api.put<Purchase>(`/purchases/${id}`, data),

  delete: (id: number) => api.delete(`/purchases/${id}`),

  getTodayPurchases: () => api.get<Purchase[]>('/purchases/today')
}

// Expense Categories
export const expenseCategoriesApi = {
  getAll: () => api.get<ExpenseCategory[]>('/expenses/categories'),
  create: (data: { name: string; is_fixed?: boolean; display_order?: number }) =>
    api.post<ExpenseCategory>('/expenses/categories', data),
  update: (id: number, data: { name: string; is_fixed?: boolean; display_order?: number }) =>
    api.put<ExpenseCategory>(`/expenses/categories/${id}`, data),
  delete: (id: number) => api.delete(`/expenses/categories/${id}`)
}

// Expenses
export const expensesApi = {
  create: (data: {
    category_id: number
    expense_date: string
    description?: string
    amount: number
  }) => api.post<Expense>('/expenses', data),

  getAll: (params?: { start_date?: string; end_date?: string; category_id?: number }) =>
    api.get<Expense[]>('/expenses', { params }),

  getTodayExpenses: () => api.get<Expense[]>('/expenses/today'),

  delete: (id: number) => api.delete(`/expenses/${id}`)
}

// Reports
export const reportsApi = {
  getDashboard: () => api.get<DashboardStats>('/reports/dashboard'),
  getBilanco: () => api.get<BilancoStats>('/reports/bilanco'),
  getDailySummary: (startDate?: string, endDate?: string) =>
    api.get('/reports/daily-summary', { params: { start_date: startDate, end_date: endDate } }),

  bilancoCompare: (params: {
    left_start: string
    left_end: string
    right_start: string
    right_end: string
  }) => api.get<ComparisonResponse>('/reports/bilanco-compare', { params })
}

// Production (Günlük Üretim/Legen Takibi)
export const productionApi = {
  create: (data: {
    production_date: string
    kneaded_kg: number
    legen_kg?: number
    legen_cost?: number
    notes?: string
  }) => api.post<DailyProduction>('/production', data),

  getAll: (params?: {
    start_date?: string
    end_date?: string
    month?: number
    year?: number
  }) => api.get<DailyProduction[]>('/production', { params }),

  getToday: () => api.get<DailyProduction | null>('/production/today'),

  getSummary: (params?: {
    start_date?: string
    end_date?: string
    month?: number
    year?: number
  }) => api.get<ProductionSummary>('/production/summary', { params }),

  update: (id: number, data: {
    production_date: string
    kneaded_kg: number
    legen_kg?: number
    legen_cost?: number
    notes?: string
  }) => api.put<DailyProduction>(`/production/${id}`, data),

  delete: (id: number) => api.delete(`/production/${id}`)
}

// Staff Meals (Personel Yemek / Tabldot)
export const staffMealsApi = {
  create: (data: {
    meal_date: string
    unit_price: number
    staff_count: number
    notes?: string
  }) => api.post<StaffMeal>('/staff-meals', data),

  getAll: (params?: {
    start_date?: string
    end_date?: string
    month?: number
    year?: number
  }) => api.get<StaffMeal[]>('/staff-meals', { params }),

  getById: (id: number) => api.get<StaffMeal>(`/staff-meals/${id}`),

  getToday: () => api.get<StaffMeal | null>('/staff-meals/today'),

  getSummary: (params?: {
    start_date?: string
    end_date?: string
    month?: number
    year?: number
  }) => api.get<StaffMealSummary>('/staff-meals/summary', { params }),

  update: (id: number, data: {
    meal_date: string
    unit_price: number
    staff_count: number
    notes?: string
  }) => api.put<StaffMeal>(`/staff-meals/${id}`, data),

  delete: (id: number) => api.delete(`/staff-meals/${id}`)
}

// Personnel (Personel Yonetimi)
export const personnelApi = {
  // Employees
  getEmployees: (includeInactive?: boolean) =>
    api.get<Employee[]>('/personnel/employees', { params: { include_inactive: includeInactive } }),

  createEmployee: (data: {
    name: string
    base_salary: number
    has_sgk?: boolean
    sgk_amount?: number
    daily_rate?: number
    hourly_rate?: number
    payment_type?: string
    is_part_time?: boolean
  }) => api.post<Employee>('/personnel/employees', data),

  getEmployee: (id: number) => api.get<Employee>(`/personnel/employees/${id}`),

  updateEmployee: (id: number, data: Partial<{
    name: string
    base_salary: number
    has_sgk: boolean
    sgk_amount: number
    daily_rate: number
    hourly_rate: number
    payment_type: string
    is_part_time: boolean
    is_active: boolean
  }>) => api.put<Employee>(`/personnel/employees/${id}`, data),

  deleteEmployee: (id: number) => api.delete(`/personnel/employees/${id}`),

  // Monthly Payroll
  getPayrolls: (params?: { year?: number; month?: number; employee_id?: number }) =>
    api.get<MonthlyPayroll[]>('/personnel/payroll', { params }),

  createPayroll: (data: {
    employee_id: number
    year: number
    month: number
    payment_date: string
    record_type: string
    base_salary?: number
    sgk_amount?: number
    bonus?: number
    premium?: number
    overtime_hours?: number
    overtime_amount?: number
    advance?: number
    absence_days?: number
    absence_deduction?: number
    notes?: string
  }) => api.post<MonthlyPayroll>('/personnel/payroll', data),

  getPayroll: (id: number) => api.get<MonthlyPayroll>(`/personnel/payroll/${id}`),

  updatePayroll: (id: number, data: Partial<{
    payment_date: string
    base_salary: number
    sgk_amount: number
    bonus: number
    premium: number
    overtime_hours: number
    overtime_amount: number
    advance: number
    absence_days: number
    absence_deduction: number
    notes: string
  }>) => api.put<MonthlyPayroll>(`/personnel/payroll/${id}`, data),

  deletePayroll: (id: number) => api.delete(`/personnel/payroll/${id}`),

  getPayrollSummary: (year: number, month: number, employeeId?: number) =>
    api.get<PayrollSummary>('/personnel/payroll/summary', { params: { year, month, employee_id: employeeId } }),

  // Part-time Costs
  getPartTimeCosts: (params?: { month?: number; year?: number; start_date?: string; end_date?: string }) =>
    api.get<PartTimeCost[]>('/personnel/part-time', { params }),

  createPartTimeCost: (data: {
    cost_date: string
    amount: number
    notes?: string
  }) => api.post<PartTimeCost>('/personnel/part-time', data),

  getPartTimeCost: (id: number) => api.get<PartTimeCost>(`/personnel/part-time/${id}`),

  updatePartTimeCost: (id: number, data: Partial<{
    cost_date: string
    amount: number
    notes: string
  }>) => api.put<PartTimeCost>(`/personnel/part-time/${id}`, data),

  deletePartTimeCost: (id: number) => api.delete(`/personnel/part-time/${id}`),

  getPartTimeSummary: (params?: { month?: number; year?: number }) =>
    api.get<PartTimeCostSummary>('/personnel/part-time/summary', { params })
}

// Online Sales (Online Platform Satislari)
export const onlineSalesApi = {
  // Platforms
  getPlatforms: () => api.get<OnlinePlatform[]>('/online-sales/platforms'),

  createPlatform: (data: { name: string; display_order?: number }) =>
    api.post<OnlinePlatform>('/online-sales/platforms', data),

  updatePlatform: (id: number, data: { name?: string; display_order?: number; is_active?: boolean }) =>
    api.put<OnlinePlatform>(`/online-sales/platforms/${id}`, data),

  deletePlatform: (id: number) => api.delete(`/online-sales/platforms/${id}`),

  // Sales
  getSales: (params?: { start_date?: string; end_date?: string; platform_id?: number }) =>
    api.get<OnlineSale[]>('/online-sales', { params }),

  getDailySales: (date: string) =>
    api.get<DailySalesResponse>(`/online-sales/daily/${date}`),

  createOrUpdateDailySales: (data: { sale_date: string; entries: DailySalesEntry[]; notes?: string }) =>
    api.post<DailySalesResponse>('/online-sales/daily', data),

  deleteSale: (id: number) => api.delete(`/online-sales/${id}`),

  deleteDailySales: (date: string) => api.delete(`/online-sales/daily/${date}`),

  // Summary
  getSummary: (params?: { month?: number; year?: number; start_date?: string; end_date?: string }) =>
    api.get<OnlineSalesSummary>('/online-sales/summary', { params })
}

// Courier Expenses (Kurye Giderleri)
export const courierExpensesApi = {
  create: (data: {
    expense_date: string
    package_count: number
    amount: number
    vat_rate?: number
    notes?: string
  }) => api.post<CourierExpense>('/courier-expenses', data),

  createBulk: (data: {
    entries: Array<{
      expense_date: string
      package_count: number
      amount: number
      vat_rate?: number
    }>
  }) => api.post<CourierExpense[]>('/courier-expenses/bulk', data),

  getAll: (params?: {
    start_date?: string
    end_date?: string
    year?: number
    month?: number
  }) => api.get<CourierExpense[]>('/courier-expenses', { params }),

  getById: (id: number) => api.get<CourierExpense>(`/courier-expenses/${id}`),

  getToday: () => api.get<CourierExpense | null>('/courier-expenses/today'),

  getSummary: (params?: {
    year?: number
    month?: number
    start_date?: string
    end_date?: string
  }) => api.get<CourierExpenseSummary>('/courier-expenses/summary', { params }),

  update: (id: number, data: {
    expense_date?: string
    package_count?: number
    amount?: number
    vat_rate?: number
    notes?: string
  }) => api.put<CourierExpense>(`/courier-expenses/${id}`, data),

  delete: (id: number) => api.delete(`/courier-expenses/${id}`)
}

// Invitation Codes
export const invitationCodesApi = {
  getAll: () => api.get<InvitationCode[]>('/invitation-codes'),

  getById: (id: number) => api.get<InvitationCode>(`/invitation-codes/${id}`),

  create: (data: { role: string; max_uses?: number; expires_at?: string; branch_id?: number }) =>
    api.post<InvitationCode>('/invitation-codes', data),

  update: (id: number, data: { max_uses?: number; expires_at?: string; is_active?: boolean }) =>
    api.put<InvitationCode>(`/invitation-codes/${id}`, data),

  delete: (id: number) => api.delete(`/invitation-codes/${id}`),

  // Public validation endpoint (no auth required)
  validate: (code: string) =>
    api.post<InvitationCodeValidation>(`/invitation-codes/validate?code_str=${code}`)
}

// AI Insights
export const aiApi = {
  getDailyBrief: (forceRefresh = false) => api.get('/ai/daily-brief', { params: { force_refresh: forceRefresh } })
}

// Cash Difference (Kasa Farki)
export const cashDifferenceApi = {
  parseExcel: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post<ExcelParseResult>('/cash-difference/parse-excel', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  parseHasilatExcel: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post<POSParseResult>('/cash-difference/parse-hasilat-excel', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  import: (data: {
    difference_date: string
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
    excel_file_url?: string
    pos_image_url?: string
    ocr_confidence_score?: number
  }, expenses?: Array<{ description: string; amount: number }>) =>
    api.post<CashDifference>('/cash-difference/import', { ...data, expenses }),

  getAll: (params?: {
    start_date?: string
    end_date?: string
    status?: string
    month?: number
    year?: number
  }) => api.get<CashDifference[]>('/cash-difference', { params }),

  getById: (id: number) => api.get<CashDifference>(`/cash-difference/${id}`),

  getSummary: (params?: { month?: number; year?: number }) =>
    api.get<CashDifferenceSummary>('/cash-difference/summary', { params }),

  update: (id: number, data: { status?: string; resolution_note?: string }) =>
    api.put<CashDifference>(`/cash-difference/${id}`, data),

  previewDelete: (id: number) =>
    api.get<CashDifferencePreviewDelete>(`/cash-difference/${id}/preview-delete`),

  delete: (id: number) => api.delete<{
    message: string
    deleted_expenses: number
    deleted_sales: number
    skipped_expenses: number
    skipped_sales: number
  }>(`/cash-difference/${id}`)
}

// Import History API
export const importHistoryApi = {
  getAll: (params?: { import_type?: string; start_date?: string; end_date?: string }) =>
    api.get<any[]>('/import-history', { params }),

  getById: (id: number) =>
    api.get<any>(`/import-history/${id}`),

  undo: (id: number) =>
    api.post(`/import-history/${id}/undo`),
}

// Categorization API
export const categorizationApi = {
  suggest: (description: string, amount?: number) =>
    api.post<any[]>('/categorization/suggest', { description, amount }),

  suggestBatch: (expenses: Array<{ description: string; amount?: number }>) =>
    api.post('/categorization/suggest-batch', { expenses }),
}

export default api
