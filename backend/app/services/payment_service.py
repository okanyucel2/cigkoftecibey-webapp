# backend/app/services/payment_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, delete
from typing import Optional
from datetime import datetime, UTC
from decimal import Decimal

from backend.app.models.supplier_ar import (
    SupplierPayment,
    SupplierTransaction,
    PaymentType,
    PaymentStatus,
    TransactionType
)
from backend.app.schemas.supplier_ar import (
    SupplierPaymentCreate,
    SupplierPaymentUpdate,
    SupplierPaymentWithSupplier
)
from backend.app.services.supplier_ar_service import SupplierARService


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ar_service = SupplierARService(db)

    async def create_payment(self, data: SupplierPaymentCreate) -> SupplierPaymentWithSupplier:
        """
        Yeni ödeme kaydı oluşturur ve transaction kaydı ekler.
        """
        # Tedarikçi adını al
        from backend.app.models.supplier import Supplier
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
        from backend.app.models.supplier import Supplier

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
        from backend.app.models.supplier import Supplier

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
        from backend.app.models.supplier import Supplier
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
            delete(SupplierTransaction).where(
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
