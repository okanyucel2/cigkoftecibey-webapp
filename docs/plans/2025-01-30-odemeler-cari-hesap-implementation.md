# Ödemeler - Tedarikçi Cari Hesap Sistemi Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Build a supplier accounts receivable (cari hesap) system with payment tracking, transaction history, and reporting.

**Architecture:**
- Backend: FastAPI routes + SQLAlchemy models for payments and transactions
- Frontend: Vue 3 components with tabbed interface for Cari List and Payment Records
- Integration: Payment creation triggers transaction records with running balance calculation

**Tech Stack:**
- Backend: Python 3.12, FastAPI, SQLAlchemy, AsyncIO
- Frontend: Vue 3 Composition API, TypeScript, Pinia
- Database: PostgreSQL (existing schema)

---

## Task 1: Backend - Create Payment Models

**Files:**
- Create: `backend/models/supplier_ar.py`
- Modify: `backend/models/__init__.py` (add import)

**Step 1: Create the models file**

```python
# backend/models/supplier_ar.py
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from backend.core.database import Base
import enum
from datetime import datetime


class PaymentType(str, enum.Enum):
    CASH = "cash"           # Nakit
    EFT = "eft"             # EFT/Havale
    CHECK = "check"         # Çek
    PROMISSORY = "promissory"  # Senet
    PARTIAL = "partial"     # Kısmi ödeme


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TransactionType(str, enum.Enum):
    ORDER = "order"         # Sipariş (borç artar)
    PAYMENT = "payment"     # Ödeme (borç azalır)
    RETURN = "return"       # İade (borç azalır)
    ADJUSTMENT = "adjustment"  # Düzeltme


class SupplierPayment(Base):
    __tablename__ = "supplier_payments"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)

    # Payment details
    payment_type = Column(SQLEnum(PaymentType), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(DateTime, nullable=False)
    description = Column(String(500))
    reference = Column(String(100))  # Sipariş/makbuz numarası

    # Bank info for EFT
    bank_name = Column(String(100))
    transfer_code = Column(String(100))

    # Check/Promissory info
    due_date = Column(DateTime)  # Vade tarihi
    serial_number = Column(String(50))

    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.COMPLETED)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship
    supplier = relationship("Supplier", back_populates="payments")


class SupplierTransaction(Base):
    """
    Her sipariş ve ödeme için hareket kaydı
    Bakiye hesaplama için kullanılır
    """
    __tablename__ = "supplier_transactions"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)

    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    reference_id = Column(Integer)  # order_id veya payment_id
    reference_type = Column(String(50))  # 'purchase_order', 'supplier_payment'

    description = Column(String(500), nullable=False)

    # Positive = debt (borç artar), Negative = credit (borç azalır)
    debt_amount = Column(Numeric(10, 2), default=0)
    credit_amount = Column(Numeric(10, 2), default=0)

    running_balance = Column(Numeric(10, 2), nullable=False)

    transaction_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    supplier = relationship("Supplier", back_populates="transactions")
```

**Step 2: Update models __init__.py**

Add to `backend/models/__init__.py`:
```python
from .supplier_ar import (
    SupplierPayment,
    SupplierTransaction,
    PaymentType,
    PaymentStatus,
    TransactionType
)
```

**Step 3: Create migration**

```bash
cd /Users/okan.yucel/cigkoftecibey-webapp/backend
alembic revision --autogenerate -m "Add supplier payment and transaction models"
```

**Step 4: Run migration**

```bash
alembic upgrade head
```

**Step 5: Commit**

```bash
git add backend/models/supplier_ar.py backend/models/__init__.py alembic/versions/
git commit -m "feat: add supplier payment and transaction models"
```

---

## Task 2: Backend - Update Supplier Model Relationships

**Files:**
- Modify: `backend/models/supplier.py`

**Step 1: Add relationships to Supplier model**

Add these relationships to the Supplier class:
```python
from sqlalchemy.orm import relationship
from .supplier_ar import SupplierPayment, SupplierTransaction

# In Supplier class, add:
payments = relationship("SupplierPayment", back_populates="supplier", cascade="all, delete-orphan")
transactions = relationship("SupplierTransaction", back_populates="supplier", cascade="all, delete-orphan")
```

**Step 2: Commit**

```bash
git add backend/models/supplier.py
git commit -m "feat: add payment and transaction relationships to Supplier"
```

---

## Task 3: Backend - Create Pydantic Schemas

**Files:**
- Create: `backend/schemas/supplier_ar.py`

**Step 1: Create schemas file**

```python
# backend/schemas/supplier_ar.py
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
```

**Step 2: Update schemas __init__.py**

```python
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
```

**Step 3: Commit**

```bash
git add backend/schemas/supplier_ar.py backend/schemas/__init__.py
git commit -m "feat: add supplier AR schemas"
```

---

## Task 4: Backend - Create Supplier AR Service

**Files:**
- Create: `backend/services/supplier_ar_service.py`

**Step 1: Create service file**

```python
# backend/services/supplier_ar_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from typing import Optional
from datetime import datetime
from decimal import Decimal

from backend.models.supplier import Supplier
from backend.models.supplier_ar import (
    SupplierPayment,
    SupplierTransaction,
    PaymentType,
    PaymentStatus,
    TransactionType
)
from backend.schemas.supplier_ar import (
    SupplierARSummary,
    SupplierARDetail,
    SupplierTransaction as TransactionSchema,
    SupplierPaymentCreate,
    SupplierPayment as PaymentSchema,
    SupplierPaymentUpdate
)


class SupplierARService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_supplier_ar(self) -> list[SupplierARSummary]:
        """
        Tüm tedarikçilerin cari hesap özetini getirir.
        Hesaplamalar transaction tablosundan yapılır.
        """
        # Son transaction kayıtlarını her tedarikçi için
        subq = (
            select(
                SupplierTransaction.supplier_id,
                func.max(SupplierTransaction.id).label('last_trans_id')
            )
            .group_by(SupplierTransaction.supplier_id)
            .subquery()
        )

        # Son transaction bilgileri
        last_trans = select(SupplierTransaction).where(
            SupplierTransaction.id == subq.c.last_trans_id
        ).subquery()

        # Son ödeme tarihi (payments tablosundan)
        last_payment_dates = (
            select(
                SupplierPayment.supplier_id,
                func.max(SupplierPayment.payment_date).label('last_payment_date')
            )
            .group_by(SupplierPayment.supplier_id)
            .subquery()
        )

        # Tedarikçilerle birleştir
        query = (
            select(
                Supplier.id,
                Supplier.name,
                func.coalesce(last_trans.c.running_balance, 0).label('balance'),
                func.coalesce(last_trans.c.total_debt, 0).label('total_debt'),
                func.coalesce(last_trans.c.total_credit, 0).label('total_credit'),
                func.coalesce(last_payment_dates.c.last_payment_date, last_trans.c.transaction_date).label('last_transaction_date')
            )
            .outerjoin(last_trans, Supplier.id == last_trans.c.supplier_id)
            .outerjoin(last_payment_dates, Supplier.id == last_payment_dates.c.supplier_id)
            .order_by(desc(func.coalesce(last_trans.c.running_balance, 0)))
        )

        result = await self.db.execute(query)
        rows = result.all()

        return [
            SupplierARSummary(
                id=row.id,
                name=row.name,
                balance=row.balance or Decimal('0'),
                total_debt=row.total_debt or Decimal('0'),
                total_credit=row.total_credit or Decimal('0'),
                last_transaction_date=row.last_transaction_date
            )
            for row in rows
        ]

    async def get_supplier_ar_detail(self, supplier_id: int) -> Optional[SupplierARDetail]:
        """
        Tek tedarikçinin detaylı cari hesap bilgisini getirir.
        """
        # Tedarikçi bilgisi
        supplier_result = await self.db.execute(
            select(Supplier).where(Supplier.id == supplier_id)
        )
        supplier = supplier_result.scalar_one_or_none()

        if not supplier:
            return None

        # Hareket geçmişi
        trans_result = await self.db.execute(
            select(SupplierTransaction)
            .where(SupplierTransaction.supplier_id == supplier_id)
            .order_by(desc(SupplierTransaction.transaction_date))
        )
        transactions = trans_result.scalars().all()

        # Son hareketten bakiye bilgisi
        last_trans = transactions[0] if transactions else None

        return SupplierARDetail(
            id=supplier.id,
            name=supplier.name,
            balance=last_trans.running_balance if last_trans else Decimal('0'),
            total_debt=last_trans.total_debt if last_trans else Decimal('0'),  # Needs aggregation
            total_credit=last_trans.total_credit if last_trans else Decimal('0'),
            last_transaction_date=last_trans.transaction_date if last_trans else None,
            transactions=[TransactionSchema.model_validate(t) for t in transactions]
        )

    async def create_transaction(
        self,
        supplier_id: int,
        transaction_type: TransactionType,
        description: str,
        debt_amount: Decimal = Decimal('0'),
        credit_amount: Decimal = Decimal('0'),
        reference_id: Optional[int] = None,
        reference_type: Optional[str] = None,
        transaction_date: Optional[datetime] = None
    ) -> SupplierTransaction:
        """
        Yeni hareket kaydı oluşturur. Running balance hesaplar.
        """
        # Son bakiyeyi bul
        last_balance_result = await self.db.execute(
            select(SupplierTransaction.running_balance)
            .where(SupplierTransaction.supplier_id == supplier_id)
            .order_by(desc(SupplierTransaction.transaction_date))
            .limit(1)
        )
        last_balance = last_balance_result.scalar() or Decimal('0')

        # Yeni bakiye hesapla
        new_balance = last_balance + debt_amount - credit_amount

        transaction = SupplierTransaction(
            supplier_id=supplier_id,
            transaction_type=transaction_type,
            description=description,
            debt_amount=debt_amount,
            credit_amount=credit_amount,
            running_balance=new_balance,
            reference_id=reference_id,
            reference_type=reference_type,
            transaction_date=transaction_date or datetime.utcnow()
        )

        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)

        return transaction
```

**Step 2: Commit**

```bash
git add backend/services/supplier_ar_service.py
git commit -m "feat: add supplier AR service with transaction logic"
```

---

## Task 5: Backend - Create Payment Service

**Files:**
- Create: `backend/services/payment_service.py`

**Step 1: Create payment service**

```python
# backend/services/payment_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from typing import Optional
from datetime import datetime

from backend.models.supplier_ar import (
    SupplierPayment,
    SupplierTransaction,
    PaymentType,
    PaymentStatus,
    TransactionType
)
from backend.models.purchase_order import PurchaseOrder
from backend.schemas.supplier_ar import (
    SupplierPaymentCreate,
    SupplierPaymentUpdate,
    SupplierPaymentWithSupplier,
    SupplierPayment as PaymentSchema
)
from backend.services.supplier_ar_service import SupplierARService


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ar_service = SupplierARService(db)

    async def create_payment(self, data: SupplierPaymentCreate) -> SupplierPaymentWithSupplier:
        """
        Yeni ödeme kaydı oluşturur ve transaction kaydı ekler.
        """
        # Tedarikçi adını al
        from backend.models.supplier import Supplier
        supplier_result = await self.db.execute(
            select(Supplier.name).where(Supplier.id == data.supplier_id)
        )
        supplier_name = supplier_result.scalar_one_or_none()
        if not supplier_name:
            raise ValueError("Supplier not found")

        # Ödeme kaydı oluştur
        payment = SupplierPayment(**data.model_dump())
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)

        # Transaction kaydı oluştur (borç azalır)
        await self.ar_service.create_transaction(
            supplier_id=data.supplier_id,
            transaction_type=TransactionType.PAYMENT,
            description=f"Ödeme - {self._get_payment_type_label(data.payment_type)}",
            debt_amount=Decimal('0'),
            credit_amount=data.amount,
            reference_id=payment.id,
            reference_type='supplier_payment',
            transaction_date=data.payment_date
        )

        return SupplierPaymentWithSupplier(
            id=payment.id,
            supplier_id=payment.supplier_id,
            supplier_name=supplier_name,
            payment_type=payment.payment_type,
            amount=payment.amount,
            payment_date=payment.payment_date,
            description=payment.description,
            reference=payment.reference,
            bank_name=payment.bank_name,
            transfer_code=payment.transfer_code,
            due_date=payment.due_date,
            serial_number=payment.serial_number,
            status=payment.status,
            created_at=payment.created_at,
            updated_at=payment.updated_at
        )

    async def get_payments(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        supplier_id: Optional[int] = None,
        payment_type: Optional[PaymentType] = None,
        search: Optional[str] = None
    ) -> list[SupplierPaymentWithSupplier]:
        """
        Ödeme listesini filtrelerle birlikte getirir.
        """
        from backend.models.supplier import Supplier

        query = (
            select(SupplierPayment, Supplier.name)
            .join(Supplier, SupplierPayment.supplier_id == Supplier.id)
        )

        # Filtreleri uygula
        conditions = []
        if start_date:
            conditions.append(SupplierPayment.payment_date >= start_date)
        if end_date:
            conditions.append(SupplierPayment.payment_date <= end_date)
        if supplier_id:
            conditions.append(SupplierPayment.supplier_id == supplier_id)
        if payment_type:
            conditions.append(SupplierPayment.payment_type == payment_type)
        if search:
            conditions.append(
                (Supplier.name.ilike(f"%{search}%")) |
                (SupplierPayment.description.ilike(f"%{search}%")) |
                (SupplierPayment.reference.ilike(f"%{search}%"))
            )

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(desc(SupplierPayment.payment_date))

        result = await self.db.execute(query)
        rows = result.all()

        return [
            SupplierPaymentWithSupplier(
                id=payment.id,
                supplier_id=payment.supplier_id,
                supplier_name=supplier_name,
                payment_type=payment.payment_type,
                amount=payment.amount,
                payment_date=payment.payment_date,
                description=payment.description,
                reference=payment.reference,
                bank_name=payment.bank_name,
                transfer_code=payment.transfer_code,
                due_date=payment.due_date,
                serial_number=payment.serial_number,
                status=payment.status,
                created_at=payment.created_at,
                updated_at=payment.updated_at
            )
            for payment, supplier_name in rows
        ]

    async def get_payment(self, payment_id: int) -> Optional[SupplierPaymentWithSupplier]:
        """Tek ödeme kaydı getirir."""
        from backend.models.supplier import Supplier

        result = await self.db.execute(
            select(SupplierPayment, Supplier.name)
            .join(Supplier, SupplierPayment.supplier_id == Supplier.id)
            .where(SupplierPayment.id == payment_id)
        )
        row = result.first()

        if not row:
            return None

        payment, supplier_name = row

        return SupplierPaymentWithSupplier(
            id=payment.id,
            supplier_id=payment.supplier_id,
            supplier_name=supplier_name,
            payment_type=payment.payment_type,
            amount=payment.amount,
            payment_date=payment.payment_date,
            description=payment.description,
            reference=payment.reference,
            bank_name=payment.bank_name,
            transfer_code=payment.transfer_code,
            due_date=payment.due_date,
            serial_number=payment.serial_number,
            status=payment.status,
            created_at=payment.created_at,
            updated_at=payment.updated_at
        )

    async def update_payment(
        self,
        payment_id: int,
        data: SupplierPaymentUpdate
    ) -> Optional[SupplierPaymentWithSupplier]:
        """Ödeme kaydı günceller."""
        result = await self.db.execute(
            select(SupplierPayment).where(SupplierPayment.id == payment_id)
        )
        payment = result.scalar_one_or_none()

        if not payment:
            return None

        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(payment, field, value)

        await self.db.commit()
        await self.db.refresh(payment)

        # Get supplier name
        from backend.models.supplier import Supplier
        supplier_result = await self.db.execute(
            select(Supplier.name).where(Supplier.id == payment.supplier_id)
        )
        supplier_name = supplier_result.scalar_one()

        return SupplierPaymentWithSupplier(
            id=payment.id,
            supplier_id=payment.supplier_id,
            supplier_name=supplier_name,
            payment_type=payment.payment_type,
            amount=payment.amount,
            payment_date=payment.payment_date,
            description=payment.description,
            reference=payment.reference,
            bank_name=payment.bank_name,
            transfer_code=payment.transfer_code,
            due_date=payment.due_date,
            serial_number=payment.serial_number,
            status=payment.status,
            created_at=payment.created_at,
            updated_at=payment.updated_at
        )

    async def delete_payment(self, payment_id: int) -> bool:
        """Ödeme kaydı siler."""
        result = await self.db.execute(
            select(SupplierPayment).where(SupplierPayment.id == payment_id)
        )
        payment = result.scalar_one_or_none()

        if not payment:
            return False

        # İlgili transaction kaydını da sil
        await self.db.execute(
            select(SupplierTransaction)
            .where(
                and_(
                    SupplierTransaction.reference_id == payment_id,
                    SupplierTransaction.reference_type == 'supplier_payment'
                )
            )
        )

        await self.db.delete(payment)
        await self.db.commit()

        return True

    def _get_payment_type_label(self, payment_type: PaymentType) -> str:
        labels = {
            PaymentType.CASH: "Nakit",
            PaymentType.EFT: "EFT",
            PaymentType.CHECK: "Çek",
            PaymentType.PROMISSORY: "Senet",
            PaymentType.PARTIAL: "Kısmi Ödeme"
        }
        return labels.get(payment_type, str(payment_type))
```

**Step 2: Commit**

```bash
git add backend/services/payment_service.py
git commit -m "feat: add payment service with CRUD operations"
```

---

## Task 6: Backend - Create API Routes

**Files:**
- Create: `backend/api/routes/payments.py`

**Step 1: Create payment routes**

```python
# backend/api/routes/payments.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Literal
from datetime import datetime

from backend.core.database import get_db
from backend.services.supplier_ar_service import SupplierARService
from backend.services.payment_service import PaymentService
from backend.schemas.supplier_ar import (
    SupplierARSummary,
    SupplierARDetail,
    SupplierTransaction,
    SupplierPaymentCreate,
    SupplierPaymentUpdate,
    SupplierPaymentWithSupplier
)

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])


# ============ Dependency ============
async def get_payment_service(db: AsyncSession = Depends(get_db)) -> PaymentService:
    return PaymentService(db)


async def get_ar_service(db: AsyncSession = Depends(get_db)) -> SupplierARService:
    return SupplierARService(db)


# ============ Supplier AR Endpoints ============
@router.get("/supplier/ar", response_model=list[SupplierARSummary])
async def get_all_supplier_ar(
    service: SupplierARService = Depends(get_ar_service)
):
    """
    Tüm tedarikçilerin cari hesap özetini getirir.
    """
    return await service.get_all_supplier_ar()


@router.get("/supplier/ar/{supplier_id}", response_model=SupplierARDetail)
async def get_supplier_ar_detail(
    supplier_id: int,
    service: SupplierARService = Depends(get_ar_service)
):
    """
    Tek tedarikçinin detaylı cari hesap bilgisini getirir.
    """
    result = await service.get_supplier_ar_detail(supplier_id)
    if not result:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return result


@router.get("/supplier/ar/{supplier_id}/transactions", response_model=list[SupplierTransaction])
async def get_supplier_transactions(
    supplier_id: int,
    limit: int = Query(100, ge=1, le=500),
    service: SupplierARService = Depends(get_ar_service)
):
    """
    Tedarikçinin hareket geçmişini getirir.
    """
    detail = await service.get_supplier_ar_detail(supplier_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return detail.transactions[:limit]


# ============ Payment Endpoints ============
@router.get("/supplier", response_model=list[SupplierPaymentWithSupplier])
async def get_payments(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    supplier_id: Optional[int] = None,
    payment_type: Optional[Literal["cash", "eft", "check", "promissory", "partial"]] = None,
    search: Optional[str] = None,
    service: PaymentService = Depends(get_payment_service)
):
    """
    Ödeme listesini filtrelerle birlikte getirir.
    """
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None

    return await service.get_payments(
        start_date=start_dt,
        end_date=end_dt,
        supplier_id=supplier_id,
        payment_type=payment_type,
        search=search
    )


@router.post("/supplier", response_model=SupplierPaymentWithSupplier)
async def create_payment(
    data: SupplierPaymentCreate,
    service: PaymentService = Depends(get_payment_service)
):
    """
    Yeni ödeme kaydı oluşturur.
    """
    try:
        return await service.create_payment(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/supplier/{payment_id}", response_model=SupplierPaymentWithSupplier)
async def get_payment(
    payment_id: int,
    service: PaymentService = Depends(get_payment_service)
):
    """
    Tek ödeme kaydı getirir.
    """
    result = await service.get_payment(payment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Payment not found")
    return result


@router.put("/supplier/{payment_id}", response_model=SupplierPaymentWithSupplier)
async def update_payment(
    payment_id: int,
    data: SupplierPaymentUpdate,
    service: PaymentService = Depends(get_payment_service)
):
    """
    Ödeme kaydı günceller.
    """
    result = await service.update_payment(payment_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Payment not found")
    return result


@router.delete("/supplier/{payment_id}")
async def delete_payment(
    payment_id: int,
    service: PaymentService = Depends(get_payment_service)
):
    """
    Ödeme kaydı siler.
    """
    success = await service.delete_payment(payment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"message": "Payment deleted successfully"}
```

**Step 2: Register router in main.py**

Add to `backend/main.py`:
```python
from .api.routes.payments import router as payments_router
app.include_router(payments_router)
```

**Step 3: Commit**

```bash
git add backend/api/routes/payments.py backend/main.py
git commit -m "feat: add payment API routes"
```

---

## Task 7: Frontend - Add Types

**Files:**
- Modify: `frontend/src/types/index.ts`

**Step 1: Add payment types**

Add to `frontend/src/types/index.ts`:

```typescript
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
```

**Step 2: Commit**

```bash
cd /Users/okan.yucel/cigkoftecibey-webapp/frontend
git add src/types/index.ts
git commit -m "feat: add payment types"
```

---

## Task 8: Frontend - Add API Service

**Files:**
- Create: `frontend/src/services/paymentsApi.ts`

**Step 1: Create payments API service**

```typescript
// frontend/src/services/paymentsApi.ts
import axios from './axios'
import type {
  SupplierARSummary,
  SupplierARDetail,
  SupplierTransaction,
  SupplierPayment,
  CreatePaymentDTO,
  PaymentFilters
} from '@/types'

export const paymentsApi = {
  // ============ Supplier AR ============
  getSupplierAR: () =>
    axios.get<SupplierARSummary[]>('/payments/supplier/ar'),

  getSupplierARDetail: (id: number) =>
    axios.get<SupplierARDetail>(`/payments/supplier/ar/${id}`),

  getSupplierTransactions: (id: number, limit = 100) =>
    axios.get<SupplierTransaction[]>(`/payments/supplier/ar/${id}/transactions`, {
      params: { limit }
    }),

  // ============ Payments ============
  getPayments: (filters?: PaymentFilters) =>
    axios.get<SupplierPayment[]>('/payments/supplier', { params: filters }),

  createPayment: (data: CreatePaymentDTO) =>
    axios.post<SupplierPayment>('/payments/supplier', data),

  getPayment: (id: number) =>
    axios.get<SupplierPayment>(`/payments/supplier/${id}`),

  updatePayment: (id: number, data: Partial<CreatePaymentDTO>) =>
    axios.put<SupplierPayment>(`/payments/supplier/${id}`, data),

  deletePayment: (id: number) =>
    axios.delete(`/payments/supplier/${id}`)
}
```

**Step 2: Export from services/index.ts**

Add to `frontend/src/services/index.ts`:
```typescript
export * from './paymentsApi'
```

**Step 3: Commit**

```bash
git add src/services/paymentsApi.ts src/services/index.ts
git commit -m "feat: add payments API service"
```

---

## Task 9: Frontend - Create Main Odemeler View

**Files:**
- Create: `frontend/src/views/Odemeler.vue`

**Step 1: Create Odemeler view**

```vue
<!-- frontend/src/views/Odemeler.vue -->
<script setup lang="ts">
import { ref } from 'vue'
import SupplierARList from '@/components/payments/SupplierARList.vue'
import PaymentRecordsList from '@/components/payments/PaymentRecordsList.vue'

const activeTab = ref<'cari' | 'records'>('cari')

const tabs = [
  { id: 'cari' as const, label: 'Tedarikçi Cari', icon: '🏪' },
  { id: 'records' as const, label: 'Ödeme Kayıtları', icon: '📋' }
]
</script>

<template>
  <div class="max-w-7xl mx-auto space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-display font-bold text-gray-900">💳 Ödemeler</h1>
    </div>

    <!-- Tabs -->
    <div class="bg-white rounded-lg shadow">
      <div class="border-b">
        <nav class="flex -mb-px">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'px-6 py-4 text-sm font-medium border-b-2 transition-colors',
              activeTab === tab.id
                ? 'border-brand-red text-brand-red'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            ]"
          >
            <span class="mr-2">{{ tab.icon }}</span>
            {{ tab.label }}
          </button>
        </nav>
      </div>

      <!-- Tab Content -->
      <div class="p-6">
        <SupplierARList v-if="activeTab === 'cari'" />
        <PaymentRecordsList v-else />
      </div>
    </div>
  </div>
</template>
```

**Step 2: Commit**

```bash
git add src/views/Odemeler.vue
git commit -m "feat: add Odemeler view with tabs"
```

---

## Task 10: Frontend - Create SupplierARList Component

**Files:**
- Create: `frontend/src/components/payments/SupplierARList.vue`

**Step 1: Create component**

```vue
<!-- frontend/src/components/payments/SupplierARList.vue -->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { paymentsApi } from '@/services'
import type { SupplierARSummary } from '@/types'

const router = useRouter()
const suppliers = ref<SupplierARSummary[]>([])
const loading = ref(true)
const error = ref('')
const filter = ref<'all' | 'debtors' | 'creditors'>('all')

const filteredSuppliers = computed(() => {
  switch (filter.value) {
    case 'debtors':
      return suppliers.value.filter(s => s.balance > 0)
    case 'creditors':
      return suppliers.value.filter(s => s.balance < 0)
    default:
      return suppliers.value
  }
})

const summary = computed(() => ({
  totalBalance: suppliers.value.reduce((sum, s) => sum + Number(s.balance), 0),
  totalDebt: suppliers.value.reduce((sum, s) => sum + Number(s.total_debt), 0),
  totalCredit: suppliers.value.reduce((sum, s) => sum + Number(s.total_credit), 0),
  debtorCount: suppliers.value.filter(s => s.balance > 0).length
}))

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await paymentsApi.getSupplierAR()
    suppliers.value = data.sort((a, b) => Number(b.balance) - Number(a.balance))
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Veri yüklenemedi'
  } finally {
    loading.value = false
  }
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY'
  }).format(amount)
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('tr-TR')
}

onMounted(loadData)
</script>

<template>
  <div class="space-y-6">
    <!-- Error -->
    <div v-if="error" class="bg-red-100 text-red-700 p-4 rounded-lg">
      {{ error }}
      <button @click="error = ''" class="ml-2 font-bold">x</button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-8 text-gray-500">
      Yükleniyor...
    </div>

    <template v-else>
      <!-- Summary Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="bg-white rounded-lg shadow p-4">
          <p class="text-sm text-gray-500">Toplam Bakiye</p>
          <p class="text-2xl font-bold" :class="summary.totalBalance > 0 ? 'text-red-600' : 'text-green-600'">
            {{ formatCurrency(summary.totalBalance) }}
          </p>
        </div>
        <div class="bg-white rounded-lg shadow p-4">
          <p class="text-sm text-gray-500">Toplam Borç</p>
          <p class="text-2xl font-bold text-red-600">
            {{ formatCurrency(summary.totalDebt) }}
          </p>
        </div>
        <div class="bg-white rounded-lg shadow p-4">
          <p class="text-sm text-gray-500">Toplam Alacak</p>
          <p class="text-2xl font-bold text-green-600">
            {{ formatCurrency(summary.totalCredit) }}
          </p>
        </div>
        <div class="bg-white rounded-lg shadow p-4">
          <p class="text-sm text-gray-500">Borçlu Tedarikçi</p>
          <p class="text-2xl font-bold text-gray-900">
            {{ summary.debtorCount }}
          </p>
        </div>
      </div>

      <!-- Filters -->
      <div class="flex items-center gap-3">
        <span class="text-sm text-gray-600">Filtre:</span>
        <button
          v-for="f in [
            { id: 'all', label: 'Tümü' },
            { id: 'debtors', label: 'Sadece Borçlu' },
            { id: 'creditors', label: 'Sadece Alacaklı' }
          ]"
          :key="f.id"
          @click="filter = f.id"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
            filter === f.id
              ? 'bg-brand-red text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          ]"
        >
          {{ f.label }}
        </button>
      </div>

      <!-- Table -->
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <div v-if="filteredSuppliers.length === 0" class="p-8 text-center text-gray-500">
          Kayıt bulunamadı
        </div>

        <table v-else class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tedarikçi</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Bakiye</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Son Hareket</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Borç</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Alacak</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr
              v-for="supplier in filteredSuppliers"
              :key="supplier.id"
              class="hover:bg-gray-50 cursor-pointer"
              @click="/* Navigate to detail - to be implemented */"
            >
              <td class="px-6 py-4 text-sm font-medium text-gray-900">
                🏪 {{ supplier.name }}
              </td>
              <td class="px-6 py-4 text-sm font-medium" :class="{
                'text-red-600': supplier.balance > 0,
                'text-green-600': supplier.balance < 0,
                'text-gray-500': supplier.balance === 0
              }">
                {{ formatCurrency(Number(supplier.balance)) }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-500">
                {{ formatDate(supplier.last_transaction_date) }}
              </td>
              <td class="px-6 py-4 text-sm text-right text-gray-900">
                {{ formatCurrency(Number(supplier.total_debt)) }}
              </td>
              <td class="px-6 py-4 text-sm text-right text-gray-900">
                {{ formatCurrency(Number(supplier.total_credit)) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>
```

**Step 2: Commit**

```bash
git add src/components/payments/SupplierARList.vue
git commit -m "feat: add SupplierARList component"
```

---

## Task 11: Frontend - Create PaymentRecordsList Component

**Files:**
- Create: `frontend/src/components/payments/PaymentRecordsList.vue`

**Step 1: Create component**

```vue
<!-- frontend/src/components/payments/PaymentRecordsList.vue -->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { paymentsApi } from '@/services'
import type { SupplierPayment, PaymentFilters, PaymentType } from '@/types'

const payments = ref<SupplierPayment[]>([])
const loading = ref(true)
const error = ref('')

const filters = ref<PaymentFilters>({
  start_date: new Date().toISOString().split('T')[0],
  end_date: new Date().toISOString().split('T')[0]
})

const paymentTypeLabels: Record<PaymentType, string> = {
  cash: 'Nakit',
  eft: 'EFT',
  check: 'Çek',
  promissory: 'Senet',
  partial: 'Kısmi'
}

const summary = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  return {
    today: payments.value
      .filter(p => p.payment_date.startsWith(today))
      .reduce((sum, p) => sum + Number(p.amount), 0),
    total: payments.value.reduce((sum, p) => sum + Number(p.amount), 0)
  }
})

async function loadPayments() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await paymentsApi.getPayments(filters.value)
    payments.value = data
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Veri yüklenemedi'
  } finally {
    loading.value = false
  }
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY'
  }).format(amount)
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('tr-TR')
}

onMounted(loadPayments)
</script>

<template>
  <div class="space-y-6">
    <!-- Error -->
    <div v-if="error" class="bg-red-100 text-red-700 p-4 rounded-lg">
      {{ error }}
      <button @click="error = ''" class="ml-2 font-bold">x</button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-8 text-gray-500">
      Yükleniyor...
    </div>

    <template v-else>
      <!-- Summary Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-white rounded-lg shadow p-4">
          <p class="text-sm text-gray-500">Bugün</p>
          <p class="text-2xl font-bold text-brand-red">
            {{ formatCurrency(summary.today) }}
          </p>
        </div>
        <div class="bg-white rounded-lg shadow p-4">
          <p class="text-sm text-gray-500">Toplam</p>
          <p class="text-2xl font-bold text-gray-900">
            {{ formatCurrency(summary.total) }}
          </p>
        </div>
      </div>

      <!-- Table -->
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <div v-if="payments.length === 0" class="p-8 text-center text-gray-500">
          Ödeme kaydı bulunamadı
        </div>

        <table v-else class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tarih</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tedarikçi</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tür</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Tutar</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Açıklama</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="payment in payments" :key="payment.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 text-sm text-gray-900">
                {{ formatDate(payment.payment_date) }}
              </td>
              <td class="px-6 py-4 text-sm font-medium text-gray-900">
                🏪 {{ payment.supplier_name }}
              </td>
              <td class="px-6 py-4">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  {{ paymentTypeLabels[payment.payment_type] }}
                </span>
              </td>
              <td class="px-6 py-4 text-sm text-right font-semibold text-gray-900">
                {{ formatCurrency(Number(payment.amount)) }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                {{ payment.description || '-' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>
```

**Step 2: Commit**

```bash
git add src/components/payments/PaymentRecordsList.vue
git commit -m "feat: add PaymentRecordsList component"
```

---

## Task 12: Frontend - Add Router Entry

**Files:**
- Modify: `frontend/src/router/index.ts`

**Step 1: Add route**

Add to the routes array in `frontend/src/router/index.ts`:

```typescript
{
  path: 'odemeler',
  name: 'odemeler',
  component: () => import('@/views/Odemeler.vue'),
  meta: {
    icon: '💳',
    title: 'Ödemeler',
    requiredPermission: null
  }
}
```

Place it in the main routes array, preferably after 'gelirler' route.

**Step 2: Commit**

```bash
git add src/router/index.ts
git commit -m "feat: add odemeler route"
```

---

## Task 13: Frontend - Update Navigation Menu

**Files:**
- Modify: `frontend/src/components/NavigationSidebar.vue` (or equivalent nav component)

**Step 1: Add menu item**

Add to the navigation menu items:

```typescript
{
  id: 'odemeler',
  label: 'Ödemeler',
  icon: '💳',
  route: '/odemeler'
}
```

**Step 2: Commit**

```bash
git add src/components/NavigationSidebar.vue
git commit -m "feat: add odemeler to navigation menu"
```

---

## Testing Checklist

After implementation, verify:

1. **Backend**
   - [ ] Migration applied successfully
   - [ ] `/api/v1/payments/supplier/ar` returns supplier list with balances
   - [ ] `/api/v1/payments/supplier/ar/{id}` returns supplier detail with transactions
   - [ ] POST `/api/v1/payments/supplier` creates payment and transaction
   - [ ] Payment types saved correctly (cash, eft, check, promissory, partial)

2. **Frontend**
   - [ ] Odemeler page loads with tabs
   - [ ] Tedarikçi Cari tab shows supplier list
   - [ ] Filters work (Tümü, Sadece Borçlu, Sadece Alacaklı)
   - [ ] Ödeme Kayıtları tab shows payment list
   - [ ] Summary cards display correct totals
   - [ ] Navigation menu shows Ödemeler item

3. **Integration**
   - [ ] Creating payment updates supplier balance
   - [ ] Transaction history shows correct running balance
   - [ ] Date filters work correctly
