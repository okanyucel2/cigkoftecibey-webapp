from datetime import datetime, date, UTC
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, Integer, Numeric, Boolean, DateTime, Date, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Organization(Base):
    """Organization/Company for multi-tenant support"""
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    branches: Mapped[list["Branch"]] = relationship(back_populates="organization")
    users: Mapped[list["User"]] = relationship(back_populates="organization")
    invitation_codes: Mapped[list["InvitationCode"]] = relationship(back_populates="organization")


class Branch(Base):
    __tablename__ = "branches"

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[Optional[int]] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(100))
    code: Mapped[str] = mapped_column(String(20), unique=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship(back_populates="branches")
    users: Mapped[list["User"]] = relationship(back_populates="branch")
    purchases: Mapped[list["Purchase"]] = relationship(back_populates="branch")
    expenses: Mapped[list["Expense"]] = relationship(back_populates="branch")
    suppliers: Mapped[list["Supplier"]] = relationship(back_populates="branch")
    user_branches: Mapped[list["UserBranch"]] = relationship(back_populates="branch", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[Optional[int]] = mapped_column(ForeignKey("branches.id"), nullable=True)
    organization_id: Mapped[Optional[int]] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Nullable for Google users
    name: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(50), default="owner")  # owner, manager, cashier
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_super_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    # Google Auth fields
    google_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    auth_provider: Mapped[str] = mapped_column(String(20), default="email")  # email, google

    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship(back_populates="users")
    branch: Mapped[Optional["Branch"]] = relationship(back_populates="users")
    user_branches: Mapped[list["UserBranch"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    branch: Mapped["Branch"] = relationship(back_populates="suppliers")
    purchases: Mapped[list["Purchase"]] = relationship(back_populates="supplier")
    payments: Mapped[list["SupplierPayment"]] = relationship(back_populates="supplier")
    transactions: Mapped[list["SupplierTransaction"]] = relationship(back_populates="supplier")


class Purchase(Base):
    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"))
    purchase_date: Mapped[date] = mapped_column(Date)
    total: Mapped[Decimal] = mapped_column(Numeric(14, 5))  # 14,5 for more precision (was 12,2)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    branch: Mapped["Branch"] = relationship(back_populates="purchases")
    supplier: Mapped["Supplier"] = relationship(back_populates="purchases")
    items: Mapped[list["PurchaseItem"]] = relationship(back_populates="purchase", cascade="all, delete-orphan")


class PurchaseProductGroup(Base):
    """Mal alımı ürün grupları (Manav, Lavaş, Kuru Gıda, vb.)"""
    __tablename__ = "purchase_product_groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[Optional[int]] = mapped_column(ForeignKey("branches.id"), nullable=True)  # NULL = global
    name: Mapped[str] = mapped_column(String(100))
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    products: Mapped[list["PurchaseProduct"]] = relationship(back_populates="group")


class PurchaseProduct(Base):
    """Mal alımı ürünleri (Marul, Nane, Çınar Lavaş, vb.)"""
    __tablename__ = "purchase_products"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[Optional[int]] = mapped_column(ForeignKey("branches.id"), nullable=True)  # NULL = global
    group_id: Mapped[int] = mapped_column(ForeignKey("purchase_product_groups.id"))
    name: Mapped[str] = mapped_column(String(100))
    default_unit: Mapped[str] = mapped_column(String(20), default="kg")  # kg, adet, koli, lt
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    group: Mapped["PurchaseProductGroup"] = relationship(back_populates="products")


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    purchase_id: Mapped[int] = mapped_column(ForeignKey("purchases.id"))
    product_id: Mapped[Optional[int]] = mapped_column(ForeignKey("purchase_products.id"), nullable=True)
    description: Mapped[str] = mapped_column(String(200))
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 3))
    unit: Mapped[str] = mapped_column(String(20))  # kg, adet, koli, lt
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    total: Mapped[Decimal] = mapped_column(Numeric(14, 5))  # 14,5 for more precision (was 12,2)

    # Relationships
    purchase: Mapped["Purchase"] = relationship(back_populates="items")
    product: Mapped[Optional["PurchaseProduct"]] = relationship()


class ExpenseCategory(Base):
    __tablename__ = "expense_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[Optional[int]] = mapped_column(ForeignKey("branches.id"), nullable=True)  # NULL = global
    name: Mapped[str] = mapped_column(String(100))
    is_fixed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)  # System categories cannot be deleted
    display_order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    expenses: Mapped[list["Expense"]] = relationship(back_populates="category")


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("expense_categories.id"))
    expense_date: Mapped[date] = mapped_column(Date)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    branch: Mapped["Branch"] = relationship(back_populates="expenses")
    category: Mapped["ExpenseCategory"] = relationship(back_populates="expenses")


class DailySummary(Base):
    __tablename__ = "daily_summaries"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    summary_date: Mapped[date] = mapped_column(Date)
    total_sales: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total_purchases: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total_expenses: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    order_count: Mapped[int] = mapped_column(Integer, default=0)
    salon_orders: Mapped[int] = mapped_column(Integer, default=0)
    paket_orders: Mapped[int] = mapped_column(Integer, default=0)


class DailyProduction(Base):
    """Günlük üretim/legen takibi - Excel'deki gibi"""
    __tablename__ = "daily_productions"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    production_date: Mapped[date] = mapped_column(Date, index=True)
    kneaded_kg: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # Yoğrulan Kilo
    legen_kg: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=11.2)  # 1 Legenin Kilosu
    legen_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=1040)  # 1 Legenin Maliyeti
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    # Hesaplanan alanlar (property olarak)
    @property
    def legen_count(self) -> Decimal:
        """Legen Sayısı = Yoğrulan Kilo / 1 Legenin Kilosu"""
        if self.legen_kg and self.legen_kg > 0:
            return self.kneaded_kg / self.legen_kg
        return Decimal(0)

    @property
    def total_cost(self) -> Decimal:
        """Toplam Maliyet = Legen Sayısı × 1 Legenin Maliyeti"""
        return self.legen_count * self.legen_cost


class StaffMeal(Base):
    """Günlük personel yemek takibi (Tabldot)"""
    __tablename__ = "staff_meals"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    meal_date: Mapped[date] = mapped_column(Date, index=True)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # Birim fiyat (₺145 gibi)
    staff_count: Mapped[int] = mapped_column(Integer)  # Personel adedi
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    @property
    def total(self) -> Decimal:
        """Toplam = Birim Fiyat × Personel Adedi"""
        return self.unit_price * self.staff_count


class Employee(Base):
    """Personel kartı"""
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    name: Mapped[str] = mapped_column(String(100))
    base_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2))  # Baz maaş
    has_sgk: Mapped[bool] = mapped_column(Boolean, default=True)  # SGK durumu
    sgk_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=7524.46)  # SGK tutarı
    daily_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)  # Günlük ücret (kesinti için)
    hourly_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=110)  # Saatlik ücret (mesai için)
    payment_type: Mapped[str] = mapped_column(String(20), default="monthly")  # monthly/weekly
    is_part_time: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    payrolls: Mapped[list["MonthlyPayroll"]] = relationship(back_populates="employee")


class MonthlyPayroll(Base):
    """Aylık bordro - haftalık ödemeler için birden fazla kayıt olabilir"""
    __tablename__ = "monthly_payrolls"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    year: Mapped[int] = mapped_column(Integer)
    month: Mapped[int] = mapped_column(Integer)  # 1-12
    payment_date: Mapped[date] = mapped_column(Date, index=True)  # Ödeme tarihi
    record_type: Mapped[str] = mapped_column(String(20), default="salary")  # salary, advance, weekly

    # Gelirler
    base_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)  # Maaş
    sgk_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)  # SGK
    bonus: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)  # Ek ödenek
    premium: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)  # Prim
    overtime_hours: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=0)  # Mesai saati
    overtime_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)  # Mesai tutarı

    # Kesintiler
    advance: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)  # Avans
    absence_days: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=0)  # Eksik gün
    absence_deduction: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)  # Eksik gün kesintisi

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    employee: Mapped["Employee"] = relationship(back_populates="payrolls")

    @property
    def total(self) -> Decimal:
        """Toplam ödeme tutarı - kayıt tipine göre hesaplanır"""
        if self.record_type == "advance":
            # Avans ödemesi - sadece avans tutarı
            return self.advance
        elif self.record_type == "sgk":
            # Sadece SGK ödemesi
            return self.sgk_amount
        elif self.record_type == "prim":
            # Sadece Prim ödemesi
            return self.premium
        else:
            # Maaş veya haftalık ödeme
            return (self.base_salary + self.sgk_amount + self.bonus +
                    self.premium + self.overtime_amount - self.advance - self.absence_deduction)


class PartTimeCost(Base):
    """Part-time günlük gider"""
    __tablename__ = "part_time_costs"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    cost_date: Mapped[date] = mapped_column(Date, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class OnlinePlatform(Base):
    """Satış kanalları (Salon, Telefon Paket, Trendyol, Getir, vb.)"""
    __tablename__ = "online_platforms"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[Optional[int]] = mapped_column(ForeignKey("branches.id"), nullable=True)  # NULL = global
    name: Mapped[str] = mapped_column(String(100))
    channel_type: Mapped[str] = mapped_column(String(20), default="online")  # pos_visa, pos_nakit, online
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)  # True for Visa/Nakit (cannot be deleted)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    sales: Mapped[list["OnlineSale"]] = relationship(back_populates="platform")


class OnlineSale(Base):
    """Günlük online satış kayıtları"""
    __tablename__ = "online_sales"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    platform_id: Mapped[int] = mapped_column(ForeignKey("online_platforms.id"))
    sale_date: Mapped[date] = mapped_column(Date, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, onupdate=datetime.utcnow)

    # Relationships
    platform: Mapped["OnlinePlatform"] = relationship(back_populates="sales")


class UserBranch(Base):
    """Kullanıcı-Şube ilişkisi (Many-to-Many)"""
    __tablename__ = "user_branches"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(50), default="owner")  # owner, manager, cashier
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    user: Mapped["User"] = relationship(back_populates="user_branches")
    branch: Mapped["Branch"] = relationship(back_populates="user_branches")


class InvitationCode(Base):
    """Invitation codes for user onboarding"""
    __tablename__ = "invitation_codes"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    branch_id: Mapped[Optional[int]] = mapped_column(ForeignKey("branches.id"), nullable=True)  # NULL = all branches
    role: Mapped[str] = mapped_column(String(20))  # owner, manager, cashier
    max_uses: Mapped[int] = mapped_column(Integer, default=1)
    used_count: Mapped[int] = mapped_column(Integer, default=0)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="invitation_codes")
    branch: Mapped[Optional["Branch"]] = relationship()
    creator: Mapped["User"] = relationship()
    uses: Mapped[list["InvitationCodeUse"]] = relationship(back_populates="invitation_code")

    @property
    def is_valid(self) -> bool:
        """Check if code is still valid"""
        if not self.is_active:
            return False
        if self.max_uses > 0 and self.used_count >= self.max_uses:
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        return True


class InvitationCodeUse(Base):
    """Track invitation code usage"""
    __tablename__ = "invitation_code_uses"

    id: Mapped[int] = mapped_column(primary_key=True)
    code_id: Mapped[int] = mapped_column(ForeignKey("invitation_codes.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    used_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    invitation_code: Mapped["InvitationCode"] = relationship(back_populates="uses")
    user: Mapped["User"] = relationship()


class CourierExpense(Base):
    """Kurye firması hakedişleri - günlük teslimat giderleri"""
    __tablename__ = "courier_expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    expense_date: Mapped[date] = mapped_column(Date, index=True)
    package_count: Mapped[int] = mapped_column(Integer)  # Günlük atılan paket sayısı
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))  # TL değeri (KDV hariç)
    vat_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=20)  # KDV oranı (%)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    @property
    def vat_amount(self) -> Decimal:
        """KDV tutarı"""
        return self.amount * (self.vat_rate / 100)

    @property
    def total_with_vat(self) -> Decimal:
        """KDV dahil toplam"""
        return self.amount + self.vat_amount


class CashDifference(Base):
    """Kasa farki takibi - Excel vs POS karsilastirmasi"""
    __tablename__ = "cash_differences"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    difference_date: Mapped[date] = mapped_column(Date, index=True)

    # Kasa Raporu (Excel)
    kasa_visa: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    kasa_nakit: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    kasa_trendyol: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    kasa_getir: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    kasa_yemeksepeti: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    kasa_migros: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    kasa_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)

    # POS Hasilat (Gorsel)
    pos_visa: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    pos_nakit: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    pos_trendyol: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    pos_getir: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    pos_yemeksepeti: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    pos_migros: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    pos_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)

    # Meta
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, reviewed, resolved, flagged
    severity: Mapped[str] = mapped_column(String(20), default="ok")  # ok, warning, critical
    resolution_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolved_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Files
    excel_file_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pos_image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ocr_confidence_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)

    # Audit
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, onupdate=datetime.utcnow)

    # Computed properties for diffs
    @property
    def diff_visa(self) -> Decimal:
        return self.pos_visa - self.kasa_visa

    @property
    def diff_nakit(self) -> Decimal:
        return self.pos_nakit - self.kasa_nakit

    @property
    def diff_trendyol(self) -> Decimal:
        return self.pos_trendyol - self.kasa_trendyol

    @property
    def diff_getir(self) -> Decimal:
        return self.pos_getir - self.kasa_getir

    @property
    def diff_yemeksepeti(self) -> Decimal:
        return self.pos_yemeksepeti - self.kasa_yemeksepeti

    @property
    def diff_migros(self) -> Decimal:
        return self.pos_migros - self.kasa_migros

    @property
    def diff_total(self) -> Decimal:
        return self.pos_total - self.kasa_total

    # Relationships
    items: Mapped[list["CashDifferenceItem"]] = relationship(
        back_populates="cash_difference",
        cascade="all, delete-orphan"
    )


class CashDifferenceItem(Base):
    """Normalized cash difference amounts per platform"""
    __tablename__ = "cash_difference_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    cash_difference_id: Mapped[int] = mapped_column(ForeignKey("cash_differences.id", ondelete="CASCADE"))
    platform_id: Mapped[int] = mapped_column(ForeignKey("online_platforms.id"))
    source_type: Mapped[str] = mapped_column(String(10))  # 'kasa' or 'pos'
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)

    # Relationships
    cash_difference: Mapped["CashDifference"] = relationship(back_populates="items")
    platform: Mapped["OnlinePlatform"] = relationship()


class DailyInsight(Base):
    """Günlük AI içgörüleri - Caching için"""
    __tablename__ = "daily_insights"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    date: Mapped[date] = mapped_column(Date)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    # Unique constraint on (branch_id, date) is handled at DB level


class ImportHistory(Base):
    """Track all imports with audit trail"""
    __tablename__ = "import_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    import_type: Mapped[str] = mapped_column(String(50))  # kasa_raporu, pos_image, expenses, etc
    import_date: Mapped[date] = mapped_column(Date)  # The date the data is for
    source_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, completed, failed, undone
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    import_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Extra info like OCR confidence
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    items: Mapped[list["ImportHistoryItem"]] = relationship(
        back_populates="import_history",
        cascade="all, delete-orphan"
    )
    branch: Mapped["Branch"] = relationship()
    creator: Mapped["User"] = relationship()


class ImportHistoryItem(Base):
    """Individual entities created/modified by an import"""
    __tablename__ = "import_history_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    import_history_id: Mapped[int] = mapped_column(ForeignKey("import_history.id", ondelete="CASCADE"))
    entity_type: Mapped[str] = mapped_column(String(50))  # expense, cash_difference, online_sale, etc
    entity_id: Mapped[int] = mapped_column(Integer)  # ID of the created/modified entity
    action: Mapped[str] = mapped_column(String(20))  # created, updated, deleted
    data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Snapshot of data for undo

    # Relationships
    import_history: Mapped["ImportHistory"] = relationship(back_populates="items")


# Import Supplier AR (Accounts Receivable) models
from .supplier_ar import (
    SupplierPayment,
    SupplierTransaction,
    PaymentType,
    PaymentStatus,
    TransactionType
)

