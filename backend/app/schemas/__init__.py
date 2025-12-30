from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


# Auth
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# User
class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: str = "owner"


class UserCreate(UserBase):
    password: str
    branch_id: int


class UserResponse(UserBase):
    id: int
    branch_id: Optional[int] = None
    organization_id: Optional[int] = None
    is_active: bool
    is_super_admin: bool = False
    google_id: Optional[str] = None
    avatar_url: Optional[str] = None
    auth_provider: str = "email"
    created_at: datetime

    class Config:
        from_attributes = True


class UserWithBranchesResponse(UserBase):
    """Extended user response with accessible branches"""
    id: int
    branch_id: Optional[int] = None
    organization_id: Optional[int] = None
    is_active: bool
    is_super_admin: bool = False
    google_id: Optional[str] = None
    avatar_url: Optional[str] = None
    auth_provider: str = "email"
    created_at: datetime
    current_branch_id: Optional[int] = None
    accessible_branches: list["BranchResponse"] = []

    class Config:
        from_attributes = True


# Branch
class BranchBase(BaseModel):
    name: str
    code: str
    city: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None


class BranchCreate(BranchBase):
    pass


class BranchUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None


class BranchResponse(BranchBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


# UserBranch (Many-to-Many User <-> Branch)
class UserBranchBase(BaseModel):
    user_id: int
    branch_id: int
    role: str = "owner"
    is_default: bool = False


class UserBranchCreate(UserBranchBase):
    pass


class UserBranchResponse(UserBranchBase):
    id: int
    created_at: datetime
    branch: Optional[BranchResponse] = None

    class Config:
        from_attributes = True


# Supplier
class SupplierBase(BaseModel):
    name: str
    phone: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierResponse(SupplierBase):
    id: int
    branch_id: int
    is_active: bool

    class Config:
        from_attributes = True


# Purchase Product Group & Product
class PurchaseProductGroupBase(BaseModel):
    name: str
    display_order: int = 0


class PurchaseProductGroupCreate(PurchaseProductGroupBase):
    pass


class PurchaseProductBase(BaseModel):
    name: str
    group_id: int
    default_unit: str = "kg"
    display_order: int = 0


class PurchaseProductCreate(PurchaseProductBase):
    pass


class PurchaseProductResponse(BaseModel):
    id: int
    group_id: int
    name: str
    default_unit: str
    display_order: int
    is_active: bool

    class Config:
        from_attributes = True


class PurchaseProductGroupResponse(PurchaseProductGroupBase):
    id: int
    is_active: bool
    products: list[PurchaseProductResponse] = []

    class Config:
        from_attributes = True


# Purchase
class PurchaseItemCreate(BaseModel):
    product_id: Optional[int] = None
    description: str
    quantity: Decimal
    unit: str
    unit_price: Decimal


class PurchaseItemResponse(BaseModel):
    id: int
    product_id: Optional[int] = None
    description: str
    quantity: Decimal
    unit: str
    unit_price: Decimal
    total: Decimal
    product: Optional[PurchaseProductResponse] = None

    class Config:
        from_attributes = True


class PurchaseCreate(BaseModel):
    supplier_id: int
    purchase_date: date
    notes: Optional[str] = None
    items: list[PurchaseItemCreate]


class PurchaseResponse(BaseModel):
    id: int
    branch_id: int
    supplier_id: int
    purchase_date: date
    total: Decimal
    notes: Optional[str]
    created_by: int
    created_at: datetime
    items: list[PurchaseItemResponse] = []
    supplier: Optional[SupplierResponse] = None

    class Config:
        from_attributes = True


# Expense Category
class ExpenseCategoryBase(BaseModel):
    name: str
    is_fixed: bool = False
    display_order: int = 0


class ExpenseCategoryCreate(ExpenseCategoryBase):
    branch_id: Optional[int] = None  # NULL = global


class ExpenseCategoryResponse(ExpenseCategoryBase):
    id: int
    branch_id: Optional[int] = None
    is_system: bool = False

    class Config:
        from_attributes = True


# Expense
class ExpenseCreate(BaseModel):
    category_id: int
    expense_date: date
    description: Optional[str] = None
    amount: Decimal


class ExpenseResponse(BaseModel):
    id: int
    branch_id: int
    category_id: int
    expense_date: date
    description: Optional[str]
    amount: Decimal
    created_by: int
    created_at: datetime
    category: Optional[ExpenseCategoryResponse] = None

    class Config:
        from_attributes = True


# Daily Summary
class DailySummaryResponse(BaseModel):
    id: int
    branch_id: int
    summary_date: date
    total_sales: Decimal
    total_purchases: Decimal
    total_expenses: Decimal
    order_count: int
    salon_orders: int
    paket_orders: int
    net_profit: Decimal = Decimal("0")

    class Config:
        from_attributes = True


# Dashboard
class DashboardStats(BaseModel):
    today_salon: Decimal = Decimal("0")  # Salon satışları
    today_telefon: Decimal = Decimal("0")  # Telefon paket satışları
    today_online_sales: Decimal = Decimal("0")  # Online platform satışları toplamı
    today_total_sales: Decimal = Decimal("0")  # Salon + Telefon + Online
    online_breakdown: dict[str, Decimal] = {}  # Platform bazlı: {"Trendyol": 1500, "Getir": 800}
    online_platform_count: int = 0  # Satış yapılan online platform sayısı
    today_purchases: Decimal
    today_expenses: Decimal
    today_staff_meals: Decimal = Decimal("0")  # Personel yemek masrafı
    today_courier_cost: Decimal = Decimal("0") # Kurye giderleri
    today_part_time_cost: Decimal = Decimal("0") # Part-time giderleri
    today_profit: Decimal
    today_production_kg: Decimal = Decimal("0")
    today_production_cost: Decimal = Decimal("0")
    week_sales: list[dict]


# Bilanço Dashboard
class DaySummary(BaseModel):
    day_name: str  # "Pzt", "Sal", etc.
    date: date
    amount: Decimal = Decimal("0")

class BilancoStats(BaseModel):
    # Bugün (şu ana kadar)
    today_date: date
    today_day_name: str  # "Pazartesi"
    today_revenue: Decimal = Decimal("0")
    today_expenses: Decimal = Decimal("0")
    today_profit: Decimal = Decimal("0")
    today_breakdown: dict[str, Decimal] = {}  # {"visa": x, "nakit": y, "online": z, ...}

    # Dün
    yesterday_date: date
    yesterday_day_name: str  # "Pazartesi"
    yesterday_revenue: Decimal = Decimal("0")
    yesterday_expenses: Decimal = Decimal("0")
    yesterday_profit: Decimal = Decimal("0")
    yesterday_vs_previous_pct: Decimal = Decimal("0")  # % değişim
    yesterday_breakdown: dict[str, Decimal] = {}  # {"online": x, "mal_alimi": y, ...}

    # Bu Hafta
    this_week_start: date
    this_week_end: date
    this_week_total: Decimal = Decimal("0")
    this_week_daily: list[DaySummary] = []
    this_week_best_day: Optional[DaySummary] = None
    this_week_worst_day: Optional[DaySummary] = None
    this_week_breakdown: dict[str, Decimal] = {}  # {"visa": x, "nakit": y, "online": z}

    # Geçen Hafta
    last_week_start: date
    last_week_end: date
    last_week_total: Decimal = Decimal("0")
    last_week_daily: list[DaySummary] = []
    week_vs_week_pct: Decimal = Decimal("0")  # % değişim
    last_week_breakdown: dict[str, Decimal] = {}  # {"visa": x, "nakit": y, "online": z}

    # Bu Ay
    this_month_name: str  # "Aralık 2025"
    this_month_days_passed: int
    this_month_days_total: int
    this_month_revenue: Decimal = Decimal("0")
    this_month_expenses: Decimal = Decimal("0")
    this_month_profit: Decimal = Decimal("0")
    this_month_daily_avg: Decimal = Decimal("0")
    this_month_forecast: Decimal = Decimal("0")
    this_month_chart: list[DaySummary] = []
    this_month_breakdown: dict[str, Decimal] = {}  # {"visa": x, "nakit": y, "online": z}

    # Geçen Ay (aynı dönem karşılaştırması için)
    last_month_revenue: Decimal = Decimal("0")
    last_month_expenses: Decimal = Decimal("0")
    last_month_profit: Decimal = Decimal("0")
    last_month_breakdown: dict[str, Decimal] = {}  # {"visa": x, "nakit": y, "online": z}


# Daily Production (Günlük Üretim/Legen Takibi)
class DailyProductionCreate(BaseModel):
    production_date: date
    kneaded_kg: Decimal  # Yoğrulan Kilo
    legen_kg: Decimal = Decimal("11.2")  # 1 Legenin Kilosu
    legen_cost: Decimal = Decimal("1040")  # 1 Legenin Maliyeti
    notes: Optional[str] = None


class DailyProductionResponse(BaseModel):
    id: int
    branch_id: int
    production_date: date
    kneaded_kg: Decimal
    legen_kg: Decimal
    legen_cost: Decimal
    legen_count: Decimal  # Hesaplanan
    total_cost: Decimal  # Hesaplanan
    notes: Optional[str]
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class ProductionSummary(BaseModel):
    """Aylık/dönemsel üretim özeti"""
    total_kneaded_kg: Decimal
    total_legen_count: Decimal
    total_cost: Decimal
    avg_daily_kg: Decimal
    days_count: int


# Staff Meal (Personel Yemek / Tabldot)
class StaffMealCreate(BaseModel):
    meal_date: date
    unit_price: Decimal
    staff_count: int
    notes: Optional[str] = None


class StaffMealResponse(BaseModel):
    id: int
    branch_id: int
    meal_date: date
    unit_price: Decimal
    staff_count: int
    total: Decimal  # Hesaplanan
    notes: Optional[str]
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class StaffMealSummary(BaseModel):
    """Aylık personel yemek özeti"""
    total_staff_count: int
    total_cost: Decimal
    avg_daily_staff: Decimal
    avg_unit_price: Decimal
    days_count: int


# Employee (Personel)
class EmployeeBase(BaseModel):
    name: str
    base_salary: Decimal
    has_sgk: bool = True
    sgk_amount: Decimal = Decimal("7524.46")
    daily_rate: Decimal = Decimal("0")
    hourly_rate: Decimal = Decimal("110")
    payment_type: str = "monthly"  # monthly, weekly
    is_part_time: bool = False


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    base_salary: Optional[Decimal] = None
    has_sgk: Optional[bool] = None
    sgk_amount: Optional[Decimal] = None
    daily_rate: Optional[Decimal] = None
    hourly_rate: Optional[Decimal] = None
    payment_type: Optional[str] = None
    is_part_time: Optional[bool] = None
    is_active: Optional[bool] = None


class EmployeeResponse(EmployeeBase):
    id: int
    branch_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Monthly Payroll (Aylık Maaş Bordrosu)
class MonthlyPayrollCreate(BaseModel):
    employee_id: int
    year: int
    month: int
    payment_date: date  # Ödeme tarihi
    record_type: str = "salary"  # salary, advance, weekly
    base_salary: Decimal = Decimal("0")
    sgk_amount: Decimal = Decimal("0")
    bonus: Decimal = Decimal("0")  # Ek ödenek
    premium: Decimal = Decimal("0")  # Prim
    overtime_hours: Decimal = Decimal("0")  # Mesai saati
    overtime_amount: Decimal = Decimal("0")  # Mesai tutarı (saat * hourly_rate)
    advance: Decimal = Decimal("0")  # Avans
    absence_days: Decimal = Decimal("0")  # Devamsızlık günü
    absence_deduction: Decimal = Decimal("0")  # Kesinti (TL)
    notes: Optional[str] = None


class MonthlyPayrollUpdate(BaseModel):
    payment_date: Optional[date] = None
    base_salary: Optional[Decimal] = None
    sgk_amount: Optional[Decimal] = None
    bonus: Optional[Decimal] = None
    premium: Optional[Decimal] = None
    overtime_hours: Optional[Decimal] = None
    overtime_amount: Optional[Decimal] = None
    advance: Optional[Decimal] = None
    absence_days: Optional[Decimal] = None
    absence_deduction: Optional[Decimal] = None
    notes: Optional[str] = None


class MonthlyPayrollResponse(BaseModel):
    id: int
    branch_id: int
    employee_id: int
    year: int
    month: int
    payment_date: date
    record_type: str
    base_salary: Decimal
    sgk_amount: Decimal
    bonus: Decimal
    premium: Decimal
    overtime_hours: Decimal
    overtime_amount: Decimal
    advance: Decimal
    absence_days: Decimal
    absence_deduction: Decimal
    total: Decimal  # Hesaplanan
    notes: Optional[str]
    created_by: int
    created_at: datetime
    employee: Optional[EmployeeResponse] = None

    class Config:
        from_attributes = True


class PayrollSummary(BaseModel):
    """Aylık maaş özeti"""
    total_base_salary: Decimal
    total_sgk: Decimal
    total_bonus: Decimal
    total_premium: Decimal
    total_overtime: Decimal
    total_advance: Decimal
    total_deduction: Decimal
    total_payroll: Decimal
    employee_count: int


# Part Time Cost (Part-time Personel Gideri)
class PartTimeCostCreate(BaseModel):
    cost_date: date
    amount: Decimal
    notes: Optional[str] = None


class PartTimeCostUpdate(BaseModel):
    cost_date: Optional[date] = None
    amount: Optional[Decimal] = None
    notes: Optional[str] = None


class PartTimeCostResponse(BaseModel):
    id: int
    branch_id: int
    cost_date: date
    amount: Decimal
    notes: Optional[str]
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class PartTimeCostSummary(BaseModel):
    """Aylık part-time özeti"""
    total_cost: Decimal
    days_count: int
    avg_daily_cost: Decimal


# Online Platform (Online Satış Platformları)
class OnlinePlatformBase(BaseModel):
    name: str
    display_order: int = 0


class OnlinePlatformCreate(OnlinePlatformBase):
    branch_id: Optional[int] = None  # NULL = global


class OnlinePlatformUpdate(BaseModel):
    name: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class OnlinePlatformResponse(OnlinePlatformBase):
    id: int
    branch_id: Optional[int] = None
    channel_type: str = "online"  # pos_visa, pos_nakit, online
    is_system: bool = False  # True for Visa/Nakit (cannot be deleted)
    is_active: bool

    class Config:
        from_attributes = True


# Online Sale (Online Satış Kayıtları)
class OnlineSaleCreate(BaseModel):
    platform_id: int
    sale_date: date
    amount: Decimal
    notes: Optional[str] = None


class OnlineSaleResponse(BaseModel):
    id: int
    branch_id: int
    platform_id: int
    sale_date: date
    amount: Decimal
    notes: Optional[str]
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]
    platform: Optional[OnlinePlatformResponse] = None

    class Config:
        from_attributes = True


# Günlük toplu giriş için
class DailySalesEntry(BaseModel):
    platform_id: int
    amount: Decimal


class DailySalesCreate(BaseModel):
    sale_date: date
    entries: list[DailySalesEntry]
    notes: Optional[str] = None


class DailySalesResponse(BaseModel):
    sale_date: date
    entries: list[OnlineSaleResponse]
    total: Decimal


class OnlineSalesSummary(BaseModel):
    """Aylık online satış özeti"""
    total_amount: Decimal
    platform_totals: dict[str, Decimal]  # platform_name -> total
    days_count: int


# Unified Sales Summary (Tüm kanallar için)
class UnifiedSalesSummary(BaseModel):
    """Birleşik satış özeti - tüm kanallar"""
    total_salon: Decimal = Decimal("0")
    total_telefon: Decimal = Decimal("0")
    total_online: Decimal = Decimal("0")
    total_all: Decimal = Decimal("0")
    online_breakdown: dict[str, Decimal] = {}  # platform_name -> total
    days_count: int = 0
    avg_daily_sales: Decimal = Decimal("0")


# Organization (Multi-tenant support)
class OrganizationBase(BaseModel):
    name: str
    code: str


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    is_active: Optional[bool] = None


class OrganizationResponse(OrganizationBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Invitation Code (User onboarding)
class InvitationCodeBase(BaseModel):
    role: str  # owner, manager, cashier
    max_uses: int = 1
    expires_at: Optional[datetime] = None


class InvitationCodeCreate(InvitationCodeBase):
    branch_id: Optional[int] = None  # NULL = all branches in organization


class InvitationCodeUpdate(BaseModel):
    max_uses: Optional[int] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class InvitationCodeResponse(InvitationCodeBase):
    id: int
    code: str
    organization_id: int
    branch_id: Optional[int] = None
    used_count: int
    is_active: bool
    created_by: int
    created_at: datetime
    is_valid: bool  # Computed property
    branch: Optional[BranchResponse] = None

    class Config:
        from_attributes = True


class InvitationCodeValidation(BaseModel):
    """Response for code validation"""
    valid: bool
    message: str
    organization_name: Optional[str] = None
    branch_name: Optional[str] = None
    role: Optional[str] = None


# Google Auth
class GoogleAuthRequest(BaseModel):
    """Request for Google OAuth login"""
    credential: str  # Google ID token


class GoogleAuthResponse(BaseModel):
    """Response for Google OAuth"""
    access_token: str
    token_type: str = "bearer"
    requires_onboarding: bool = False
    user: Optional["UserResponse"] = None


class RegisterWithCodeRequest(BaseModel):
    """Request to complete registration with invitation code"""
    code: str
    google_credential: str  # Google ID token


# Channels grouped by type (for unified sales UI)
class ChannelsGrouped(BaseModel):
    """Satış kanalları gruplu listesi"""
    pos_channels: list[OnlinePlatformResponse] = []  # Salon, Telefon
    online_channels: list[OnlinePlatformResponse] = []  # Trendyol, Getir, etc.


class TodaySalesResponse(BaseModel):
    """Bugünün satış verisi"""
    sale_date: date
    entries: list[OnlineSaleResponse]
    pos_total: Decimal = Decimal("0")
    online_total: Decimal = Decimal("0")
    grand_total: Decimal = Decimal("0")


# Courier Expense (Kurye Giderleri)
class CourierExpenseBase(BaseModel):
    expense_date: date
    package_count: int  # Günlük paket sayısı
    amount: Decimal  # KDV hariç tutar
    vat_rate: Decimal = Decimal("20")  # KDV oranı (%)
    notes: Optional[str] = None


class CourierExpenseCreate(CourierExpenseBase):
    pass


class CourierExpenseUpdate(BaseModel):
    expense_date: Optional[date] = None
    package_count: Optional[int] = None
    amount: Optional[Decimal] = None
    vat_rate: Optional[Decimal] = None
    notes: Optional[str] = None


class CourierExpenseResponse(CourierExpenseBase):
    id: int
    branch_id: int
    vat_amount: Decimal  # Hesaplanan KDV tutarı
    total_with_vat: Decimal  # KDV dahil toplam
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class CourierExpenseSummary(BaseModel):
    """Aylık kurye gideri özeti"""
    total_packages: int
    total_amount: Decimal  # KDV hariç toplam
    total_vat: Decimal  # Toplam KDV
    total_with_vat: Decimal  # KDV dahil genel toplam
    days_count: int
    avg_daily_packages: Decimal
    avg_package_cost: Decimal  # Paket başına ortalama maliyet


# Toplu kurye gideri girişi için
class CourierExpenseBulkEntry(BaseModel):
    expense_date: date
    package_count: int
    amount: Decimal
    vat_rate: Decimal = Decimal("20")


class CourierExpenseBulkCreate(BaseModel):
    entries: list[CourierExpenseBulkEntry]


# Cash Difference (Kasa Farki)
class CashDifferenceBase(BaseModel):
    difference_date: date
    kasa_visa: Decimal = Decimal("0")
    kasa_nakit: Decimal = Decimal("0")
    kasa_trendyol: Decimal = Decimal("0")
    kasa_getir: Decimal = Decimal("0")
    kasa_yemeksepeti: Decimal = Decimal("0")
    kasa_migros: Decimal = Decimal("0")
    kasa_total: Decimal = Decimal("0")
    pos_visa: Decimal = Decimal("0")
    pos_nakit: Decimal = Decimal("0")
    pos_trendyol: Decimal = Decimal("0")
    pos_getir: Decimal = Decimal("0")
    pos_yemeksepeti: Decimal = Decimal("0")
    pos_migros: Decimal = Decimal("0")
    pos_total: Decimal = Decimal("0")


class CashDifferenceCreate(CashDifferenceBase):
    excel_file_url: Optional[str] = None
    pos_image_url: Optional[str] = None
    ocr_confidence_score: Optional[Decimal] = None


class ExpenseItem(BaseModel):
    """Single expense item from Excel import"""
    description: str
    amount: Decimal
    category_id: Optional[int] = None  # User-selected category from import UI


class CashDifferenceImportRequest(CashDifferenceCreate):
    """Request body for import endpoint - includes expenses"""
    expenses: list[ExpenseItem] = []


class CashDifferenceUpdate(BaseModel):
    status: Optional[str] = None
    resolution_note: Optional[str] = None


class CashDifferenceResponse(CashDifferenceBase):
    id: int
    branch_id: int
    status: str
    severity: str
    resolution_note: Optional[str] = None
    resolved_by: Optional[int] = None
    resolved_at: Optional[datetime] = None
    excel_file_url: Optional[str] = None
    pos_image_url: Optional[str] = None
    ocr_confidence_score: Optional[Decimal] = None
    created_by: int
    created_at: datetime
    # Computed diffs
    diff_visa: Decimal
    diff_nakit: Decimal
    diff_trendyol: Decimal
    diff_getir: Decimal
    diff_yemeksepeti: Decimal
    diff_migros: Decimal
    diff_total: Decimal

    class Config:
        from_attributes = True


class CashDifferenceSummary(BaseModel):
    total_records: int
    pending_count: int
    resolved_count: int
    critical_count: int
    total_diff: Decimal
    period_start: date
    period_end: date


class ExcelParseResult(BaseModel):
    """Result of parsing Excel Kasa Raporu"""
    date: date
    visa: Decimal
    nakit: Decimal
    trendyol: Decimal
    getir: Decimal
    yemeksepeti: Decimal
    migros: Decimal
    total: Decimal
    expenses: list[dict]  # [{description: str, amount: Decimal}]


class POSParseResult(BaseModel):
    """Result of parsing POS image via OCR"""
    date: date
    visa: Decimal
    nakit: Decimal
    trendyol: Decimal
    getir: Decimal
    yemeksepeti: Decimal
    migros: Decimal
    total: Decimal
    confidence_score: Decimal


# Import History
class ImportHistoryItemResponse(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    action: str
    data: dict | None = None

    model_config = ConfigDict(from_attributes=True)


class ImportHistoryResponse(BaseModel):
    id: int
    branch_id: int
    import_type: str
    import_date: date
    source_filename: str | None = None
    status: str
    error_message: str | None = None
    import_metadata: dict | None = None  # Note: matches model field name
    created_at: datetime
    items: list[ImportHistoryItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ImportHistoryCreate(BaseModel):
    import_type: str
    import_date: date
    source_filename: str | None = None
    import_metadata: dict | None = None

    model_config = ConfigDict(from_attributes=True)


# Bilanco Comparison
class RevenueBreakdown(BaseModel):
    visa: float
    nakit: float
    online: float
    trendyol: float = 0
    getir: float = 0
    yemeksepeti: float = 0
    migros: float = 0


class ExpenseBreakdown(BaseModel):
    mal_alimi: float
    gider: float
    staff: float
    kurye: float
    parttime: float
    uretim: float


class BilancoPeriodData(BaseModel):
    period_label: str
    start_date: str
    end_date: str
    revenue_breakdown: RevenueBreakdown
    total_revenue: float
    expense_breakdown: ExpenseBreakdown
    total_expenses: float
    net_profit: float
    profit_margin: float


class ComparisonResponse(BaseModel):
    left: BilancoPeriodData
    right: BilancoPeriodData


class ComparisonRequest(BaseModel):
    left_start: str  # ISO date string
    left_end: str    # ISO date string
    right_start: str  # ISO date string
    right_end: str   # ISO date string


# Supplier AR (Supplier Accounts Receivable)
from .supplier_ar import (
    SupplierARSummary,
    SupplierARDetail,
    SupplierTransaction,
    SupplierPayment,
    SupplierPaymentCreate,
    SupplierPaymentUpdate,
    SupplierPaymentWithSupplier,
    PaymentTypeLiteral,
    PaymentStatusLiteral,
    TransactionTypeLiteral
)