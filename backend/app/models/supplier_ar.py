from datetime import datetime, UTC
from decimal import Decimal
from typing import Optional
from enum import Enum
from sqlalchemy import String, Integer, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum
from app.database import Base


class PaymentType(str, Enum):
    CASH = "cash"           # Nakit
    EFT = "eft"             # EFT/Havale
    CHECK = "check"         # Çek
    PROMISSORY = "promissory"  # Senet
    PARTIAL = "partial"     # Kısmi ödeme


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TransactionType(str, Enum):
    ORDER = "order"         # Sipariş (borç artar)
    PAYMENT = "payment"     # Ödeme (borç azalır)
    RETURN = "return"       # İade (borç azalır)
    ADJUSTMENT = "adjustment"  # Düzeltme


class SupplierPayment(Base):
    __tablename__ = "supplier_payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"))

    # Payment details
    payment_type: Mapped[PaymentType] = mapped_column(SQLEnum(PaymentType))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    payment_date: Mapped[datetime] = mapped_column(DateTime)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Sipariş/makbuz numarası

    # Bank info for EFT
    bank_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    transfer_code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Check/Promissory info
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)  # Vade tarihi
    serial_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    status: Mapped[PaymentStatus] = mapped_column(
        SQLEnum(PaymentStatus),
        default=PaymentStatus.COMPLETED
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)
    )

    # Relationships
    supplier: Mapped["Supplier"] = relationship(back_populates="payments")


class SupplierTransaction(Base):
    """
    Her sipariş ve ödeme için hareket kaydı
    Bakiye hesaplama için kullanılır
    """
    __tablename__ = "supplier_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"))

    transaction_type: Mapped[TransactionType] = mapped_column(SQLEnum(TransactionType))
    reference_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # order_id veya payment_id
    reference_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 'purchase_order', 'supplier_payment'

    description: Mapped[str] = mapped_column(String(500))

    # Positive = debt (borç artar), Negative = credit (borç azalır)
    debt_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    credit_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)

    running_balance: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    transaction_date: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC)
    )

    # Relationships
    supplier: Mapped["Supplier"] = relationship(back_populates="transactions")
