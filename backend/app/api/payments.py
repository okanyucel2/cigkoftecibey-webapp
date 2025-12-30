# backend/app/api/payments.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Literal
from datetime import datetime

from app.database import get_db
from app.services.supplier_ar_service import SupplierARService
from app.services.payment_service import PaymentService
from app.schemas.supplier_ar import (
    SupplierARSummary,
    SupplierARDetail,
    SupplierTransaction,
    SupplierPaymentCreate,
    SupplierPaymentUpdate,
    SupplierPaymentWithSupplier
)

router = APIRouter(prefix="/payments", tags=["payments"])


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
