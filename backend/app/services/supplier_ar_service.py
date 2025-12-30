# backend/app/services/supplier_ar_service.py
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, desc
from typing import Optional
from datetime import datetime, UTC
from decimal import Decimal

from app.models import Supplier
from app.models.supplier_ar import (
    SupplierPayment,
    SupplierTransaction,
    PaymentType,
    PaymentStatus,
    TransactionType
)
from app.schemas.supplier_ar import (
    SupplierARSummary,
    SupplierARDetail,
    SupplierTransaction as TransactionSchema,
    SupplierPaymentCreate,
    SupplierPayment as PaymentSchema,
    SupplierPaymentUpdate
)


class SupplierARService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_supplier_ar(self) -> list[SupplierARSummary]:
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

        result = self.db.execute(query)
        rows = result.all()

        return [
            SupplierARSummary(
                id=row.id,
                name=row.name,
                balance=Decimal(str(row.balance)) if row.balance else Decimal('0'),
                total_debt=Decimal(str(row.total_debt)) if row.total_debt else Decimal('0'),
                total_credit=Decimal(str(row.total_credit)) if row.total_credit else Decimal('0'),
                last_transaction_date=row.last_transaction_date
            )
            for row in rows
        ]

    def get_supplier_ar_detail(self, supplier_id: int) -> Optional[SupplierARDetail]:
        """
        Tek tedarikçinin detaylı cari hesap bilgisini getirir.
        """
        # Tedarikçi bilgisi
        supplier_result = self.db.execute(
            select(Supplier).where(Supplier.id == supplier_id)
        )
        supplier = supplier_result.scalar_one_or_none()

        if not supplier:
            return None

        # Hareket geçmişi
        trans_result = self.db.execute(
            select(SupplierTransaction)
            .where(SupplierTransaction.supplier_id == supplier_id)
            .order_by(desc(SupplierTransaction.transaction_date))
        )
        transactions = trans_result.scalars().all()

        # Son hareketten bakiye bilgisi
        last_trans = transactions[0] if transactions else None

        # Toplam borç/alacak hesapla
        total_debt = sum((t.debt_amount or Decimal('0')) for t in transactions)
        total_credit = sum((t.credit_amount or Decimal('0')) for t in transactions)

        return SupplierARDetail(
            id=supplier.id,
            name=supplier.name,
            balance=last_trans.running_balance if last_trans else Decimal('0'),
            total_debt=total_debt,
            total_credit=total_credit,
            last_transaction_date=last_trans.transaction_date if last_trans else None,
            transactions=[TransactionSchema.model_validate(t) for t in transactions]
        )

    def create_transaction(
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
        last_balance_result = self.db.execute(
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
            transaction_date=transaction_date or datetime.now(UTC)
        )

        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)

        return transaction
