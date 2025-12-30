# backend/app/schemas/supplier_ar.py
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from decimal import Decimal


class PaymentTypeEnum(str):
    cash = "cash"
    eft = "eft"
    check = "check"
    promissory = "promissory"
    partial = "partial"


PaymentTypeLiteral = Literal["cash", "eft", "check", "promissory", "partial"]
PaymentStatusLiteral = Literal["pending", "completed", "cancelled"]
TransactionTypeLiteral = Literal["order", "payment", "return", "adjustment"]


# ============ Supplier AR Summary ============
class SupplierARSummary(BaseModel):
    id: int
    name: str
    balance: Decimal
    total_debt: Decimal
    total_credit: Decimal
    last_transaction_date: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ Supplier Transaction ============
class SupplierTransactionBase(BaseModel):
    transaction_type: TransactionTypeLiteral
    description: str
    debt_amount: Decimal = Field(default=0)
    credit_amount: Decimal = Field(default=0)


class SupplierTransaction(SupplierTransactionBase):
    id: int
    supplier_id: int
    reference_id: Optional[int] = None
    reference_type: Optional[str] = None
    running_balance: Decimal
    transaction_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Supplier Payment ============
class SupplierPaymentBase(BaseModel):
    supplier_id: int
    payment_type: PaymentTypeLiteral
    amount: Decimal
    payment_date: datetime
    description: Optional[str] = None
    reference: Optional[str] = None
    bank_name: Optional[str] = None
    transfer_code: Optional[str] = None
    due_date: Optional[datetime] = None
    serial_number: Optional[str] = None


class SupplierPaymentCreate(SupplierPaymentBase):
    pass


class SupplierPaymentUpdate(BaseModel):
    payment_type: Optional[PaymentTypeLiteral] = None
    amount: Optional[Decimal] = None
    payment_date: Optional[datetime] = None
    description: Optional[str] = None
    reference: Optional[str] = None
    bank_name: Optional[str] = None
    transfer_code: Optional[str] = None
    due_date: Optional[datetime] = None
    serial_number: Optional[str] = None
    status: Optional[PaymentStatusLiteral] = None


class SupplierPayment(SupplierPaymentBase):
    id: int
    status: PaymentStatusLiteral
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SupplierPaymentWithSupplier(SupplierPayment):
    supplier_name: str


# ============ Supplier AR Detail ============
class SupplierARDetail(BaseModel):
    id: int
    name: str
    balance: Decimal
    total_debt: Decimal
    total_credit: Decimal
    last_transaction_date: Optional[datetime] = None
    transactions: list[SupplierTransaction] = []

    class Config:
        from_attributes = True
