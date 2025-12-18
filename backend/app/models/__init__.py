from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, Integer, Numeric, Boolean, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Organization(Base):
    """Organization/Company for multi-tenant support"""
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

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
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

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


class Purchase(Base):
    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"))
    purchase_date: Mapped[date] = mapped_column(Date)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

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
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    # Relationships
    purchase: Mapped["Purchase"] = relationship(back_populates="items")
    product: Mapped[Optional["PurchaseProduct"]] = relationship()


class ExpenseCategory(Base):
    __tablename__ = "expense_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[Optional[int]] = mapped_column(ForeignKey("branches.id"), nullable=True)  # NULL = global
    name: Mapped[str] = mapped_column(String(100))
    is_fixed: Mapped[bool] = mapped_column(Boolean, default=False)
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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class OnlinePlatform(Base):
    """Satış kanalları (Salon, Telefon Paket, Trendyol, Getir, vb.)"""
    __tablename__ = "online_platforms"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[Optional[int]] = mapped_column(ForeignKey("branches.id"), nullable=True)  # NULL = global
    name: Mapped[str] = mapped_column(String(100))
    channel_type: Mapped[str] = mapped_column(String(20), default="online")  # pos_salon, pos_telefon, online
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)  # True for Salon/Telefon (cannot be deleted)
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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    @property
    def vat_amount(self) -> Decimal:
        """KDV tutarı"""
        return self.amount * (self.vat_rate / 100)

    @property
    def total_with_vat(self) -> Decimal:
        """KDV dahil toplam"""
        return self.amount + self.vat_amount


