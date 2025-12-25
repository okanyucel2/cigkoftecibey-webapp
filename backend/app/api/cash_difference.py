"""
Cash Difference API - Kasa Farki Takibi
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Header
from sqlalchemy import func, and_
from app.api.deps import DBSession, CurrentBranchContext
from app.models import CashDifference, Expense, ExpenseCategory, OnlineSale, OnlinePlatform
from app.schemas import (
    CashDifferenceCreate, CashDifferenceUpdate, CashDifferenceResponse,
    CashDifferenceSummary, ExcelParseResult, POSParseResult,
    CashDifferenceImportRequest
)
from app.utils.excel_parser import parse_kasa_raporu
from app.utils.pos_ocr import parse_pos_image
from app.idempotency import check_idempotency, save_idempotency

router = APIRouter(prefix="/cash-difference", tags=["cash-difference"])


def calculate_severity(diff_total: Decimal) -> str:
    abs_diff = abs(diff_total)
    if abs_diff <= 50:
        return "ok"
    elif abs_diff <= 200:
        return "warning"
    else:
        return "critical"


@router.post("/parse-excel", response_model=ExcelParseResult)
async def parse_excel_file(
    file: UploadFile = File(...),
    ctx: CurrentBranchContext = None
):
    """Parse Excel Kasa Raporu and return extracted data for preview"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Sadece Excel dosyalari kabul edilir")

    content = await file.read()

    try:
        data = parse_kasa_raporu(content)
        return ExcelParseResult(
            date=data["date"],
            visa=data["visa"],
            nakit=data["nakit"],
            trendyol=data["trendyol"],
            getir=data["getir"],
            yemeksepeti=data["yemeksepeti"],
            migros=data["migros"],
            total=data["total"],
            expenses=data["expenses"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Excel parse hatasi: {str(e)}")


@router.post("/parse-pos-image", response_model=POSParseResult)
async def parse_pos_image_file(
    file: UploadFile = File(...),
    ctx: CurrentBranchContext = None
):
    """Parse POS image using OCR"""
    allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Sadece JPEG ve PNG kabul edilir")

    content = await file.read()

    try:
        data = parse_pos_image(content, file.content_type)
        return POSParseResult(
            date=data["date"],
            visa=data["visa"],
            nakit=data["nakit"],
            trendyol=data["trendyol"],
            getir=data["getir"],
            yemeksepeti=data["yemeksepeti"],
            migros=data["migros"],
            total=data["total"],
            confidence_score=data["confidence_score"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OCR hatasi: {str(e)}")


@router.post("/import", response_model=CashDifferenceResponse)
def import_cash_difference(
    request: CashDifferenceImportRequest,
    db: DBSession,
    ctx: CurrentBranchContext,
    import_expenses: bool = Query(default=True),
    sync_to_sales: bool = Query(default=True),
    x_idempotency_key: str | None = Header(default=None, alias="X-Idempotency-Key")
):
    """Import parsed data and create CashDifference record.

    Also syncs POS values to online_sales table for dashboard counters.
    """
    # Check idempotency cache first
    if x_idempotency_key:
        cached = check_idempotency(x_idempotency_key)
        if cached:
            return cached

    existing = db.query(CashDifference).filter(
        CashDifference.branch_id == ctx.current_branch_id,
        CashDifference.difference_date == request.difference_date
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail=f"{request.difference_date} icin zaten kayit var")

    diff_total = request.pos_total - request.kasa_total
    severity = calculate_severity(diff_total)

    record = CashDifference(
        branch_id=ctx.current_branch_id,
        difference_date=request.difference_date,
        kasa_visa=request.kasa_visa,
        kasa_nakit=request.kasa_nakit,
        kasa_trendyol=request.kasa_trendyol,
        kasa_getir=request.kasa_getir,
        kasa_yemeksepeti=request.kasa_yemeksepeti,
        kasa_migros=request.kasa_migros,
        kasa_total=request.kasa_total,
        pos_visa=request.pos_visa,
        pos_nakit=request.pos_nakit,
        pos_trendyol=request.pos_trendyol,
        pos_getir=request.pos_getir,
        pos_yemeksepeti=request.pos_yemeksepeti,
        pos_migros=request.pos_migros,
        pos_total=request.pos_total,
        status="pending",
        severity=severity,
        excel_file_url=request.excel_file_url,
        pos_image_url=request.pos_image_url,
        ocr_confidence_score=request.ocr_confidence_score,
        created_by=ctx.user.id
    )

    db.add(record)

    if import_expenses and request.expenses:
        uncategorized = db.query(ExpenseCategory).filter(
            ExpenseCategory.name == "Kategorize Edilmemis"
        ).first()

        if uncategorized:
            for exp in request.expenses:
                if exp.amount > 0:
                    expense = Expense(
                        branch_id=ctx.current_branch_id,
                        category_id=uncategorized.id,
                        expense_date=request.difference_date,
                        description=exp.description or "Excel'den aktarildi",
                        amount=exp.amount,
                        created_by=ctx.user.id
                    )
                    db.add(expense)

    # Sync POS values to online_sales table
    if sync_to_sales:
        platform_mapping = {
            'pos_visa': 'Visa',
            'pos_nakit': 'Nakit',
            'pos_trendyol': 'Trendyol',
            'pos_getir': 'Getir',
            'pos_yemeksepeti': 'Yemek Sepeti',
            'pos_migros': 'Migros Yemek',
        }

        for field, platform_name in platform_mapping.items():
            amount = getattr(request, field, None)
            if amount and amount > 0:
                platform = db.query(OnlinePlatform).filter(
                    OnlinePlatform.name == platform_name
                ).first()

                if platform:
                    # Upsert: update existing or create new
                    existing_sale = db.query(OnlineSale).filter(
                        OnlineSale.branch_id == ctx.current_branch_id,
                        OnlineSale.sale_date == request.difference_date,
                        OnlineSale.platform_id == platform.id
                    ).first()

                    if existing_sale:
                        existing_sale.amount = amount
                        existing_sale.notes = "Kasa Farki'ndan guncellendi"
                    else:
                        sale = OnlineSale(
                            branch_id=ctx.current_branch_id,
                            platform_id=platform.id,
                            sale_date=request.difference_date,
                            amount=amount,
                            notes="Kasa Farki'ndan aktarildi",
                            created_by=ctx.user.id
                        )
                        db.add(sale)

    db.commit()
    db.refresh(record)

    # Convert to response model for caching
    response = CashDifferenceResponse.model_validate(record)

    # Save to idempotency cache
    if x_idempotency_key:
        save_idempotency(x_idempotency_key, response)

    return response


@router.get("", response_model=list[CashDifferenceResponse])
def get_cash_differences(
    db: DBSession,
    ctx: CurrentBranchContext,
    start_date: date | None = None,
    end_date: date | None = None,
    status: str | None = None,
    month: int | None = None,
    year: int | None = None,
    limit: int = Query(default=50, le=200)
):
    """Get cash difference records with filters"""
    query = db.query(CashDifference).filter(
        CashDifference.branch_id == ctx.current_branch_id
    )

    if start_date:
        query = query.filter(CashDifference.difference_date >= start_date)
    if end_date:
        query = query.filter(CashDifference.difference_date <= end_date)
    if status:
        query = query.filter(CashDifference.status == status)
    if month and year:
        from calendar import monthrange
        start = date(year, month, 1)
        end = date(year, month, monthrange(year, month)[1])
        query = query.filter(
            CashDifference.difference_date >= start,
            CashDifference.difference_date <= end
        )

    return query.order_by(CashDifference.difference_date.desc()).limit(limit).all()


@router.get("/summary", response_model=CashDifferenceSummary)
def get_cash_difference_summary(
    db: DBSession,
    ctx: CurrentBranchContext,
    month: int | None = None,
    year: int | None = None
):
    """Get summary statistics"""
    from calendar import monthrange

    if not month or not year:
        today = date.today()
        month = month or today.month
        year = year or today.year

    start = date(year, month, 1)
    end = date(year, month, monthrange(year, month)[1])

    records = db.query(CashDifference).filter(
        CashDifference.branch_id == ctx.current_branch_id,
        CashDifference.difference_date >= start,
        CashDifference.difference_date <= end
    ).all()

    total_diff = sum(r.diff_total for r in records)

    return CashDifferenceSummary(
        total_records=len(records),
        pending_count=sum(1 for r in records if r.status == "pending"),
        resolved_count=sum(1 for r in records if r.status == "resolved"),
        critical_count=sum(1 for r in records if r.severity == "critical"),
        total_diff=total_diff,
        period_start=start,
        period_end=end
    )


@router.get("/{record_id}", response_model=CashDifferenceResponse)
def get_cash_difference(record_id: int, db: DBSession, ctx: CurrentBranchContext):
    record = db.query(CashDifference).filter(
        CashDifference.id == record_id,
        CashDifference.branch_id == ctx.current_branch_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Kayit bulunamadi")

    return record


@router.put("/{record_id}", response_model=CashDifferenceResponse)
def update_cash_difference(
    record_id: int,
    data: CashDifferenceUpdate,
    db: DBSession,
    ctx: CurrentBranchContext
):
    record = db.query(CashDifference).filter(
        CashDifference.id == record_id,
        CashDifference.branch_id == ctx.current_branch_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Kayit bulunamadi")

    if data.status:
        record.status = data.status
        if data.status == "resolved":
            record.resolved_by = ctx.user.id
            record.resolved_at = datetime.utcnow()

    if data.resolution_note is not None:
        record.resolution_note = data.resolution_note

    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}")
def delete_cash_difference(record_id: int, db: DBSession, ctx: CurrentBranchContext):
    record = db.query(CashDifference).filter(
        CashDifference.id == record_id,
        CashDifference.branch_id == ctx.current_branch_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Kayit bulunamadi")

    db.delete(record)
    db.commit()
    return {"message": "Kayit silindi"}
