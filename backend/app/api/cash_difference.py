"""
Cash Difference API - Kasa Farki Takibi
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Header
from sqlalchemy import func, and_
from app.api.deps import DBSession, CurrentBranchContext
from app.models import CashDifference, Expense, ExpenseCategory, OnlineSale, OnlinePlatform, ImportHistory, ImportHistoryItem
from app.schemas import (
    CashDifferenceCreate, CashDifferenceUpdate, CashDifferenceResponse,
    CashDifferenceSummary, ExcelParseResult, POSParseResult,
    CashDifferenceImportRequest
)
from app.utils.excel_parser import parse_kasa_raporu, parse_hasilat_raporu
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


@router.post("/parse-hasilat-excel", response_model=POSParseResult)
async def parse_hasilat_excel_file(
    file: UploadFile = File(...),
    ctx: CurrentBranchContext = None
):
    """Parse Şefim Hasılat Raporu Excel"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Sadece Excel dosyalari kabul edilir")

    content = await file.read()

    try:
        data = parse_hasilat_raporu(content)
        return POSParseResult(
            date=data["date"],
            visa=data["visa"],
            nakit=data["nakit"],
            trendyol=data["trendyol"],
            getir=data["getir"],
            yemeksepeti=data["yemeksepeti"],
            migros=data["migros"],
            total=data["total"],
            confidence_score=Decimal("1.0")  # Excel parsing is 100% confident
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Hasılat Excel parse hatasi: {str(e)}")


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
    db.flush()  # Flush to get record.id

    if import_expenses and request.expenses:
        uncategorized = db.query(ExpenseCategory).filter(
            ExpenseCategory.name == "Kategorize Edilmemis"
        ).first()

        if uncategorized:
            for exp in request.expenses:
                if exp.amount > 0:
                    # Use user-selected category_id from import UI, fallback to uncategorized
                    category_id = exp.category_id if exp.category_id is not None else uncategorized.id
                    expense = Expense(
                        branch_id=ctx.current_branch_id,
                        category_id=category_id,
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

    # Track import in history
    history = ImportHistory(
        branch_id=ctx.current_branch_id,
        import_type="kasa_raporu",
        import_date=request.difference_date,
        source_filename=None,  # Could be added from request if available
        status="completed",
        import_metadata={
            "ocr_confidence": float(request.ocr_confidence_score) if request.ocr_confidence_score else None,
            "kasa_total": float(request.kasa_total),
            "pos_total": float(request.pos_total),
            "diff_total": float(request.pos_total - request.kasa_total)
        },
        created_by=ctx.user.id
    )
    db.add(history)
    db.flush()  # Get the history.id

    # Track the cash difference record
    db.add(ImportHistoryItem(
        import_history_id=history.id,
        entity_type="cash_difference",
        entity_id=record.id,
        action="created",
        data={"difference_date": str(request.difference_date)}
    ))

    # Track any expenses that were created during the import
    if import_expenses and request.expenses:
        # Get the expenses we just created for this date
        created_expenses = db.query(Expense).filter(
            Expense.branch_id == ctx.current_branch_id,
            Expense.expense_date == request.difference_date,
            Expense.created_by == ctx.user.id
        ).order_by(Expense.id.desc()).limit(len(request.expenses)).all()

        for expense in created_expenses:
            db.add(ImportHistoryItem(
                import_history_id=history.id,
                entity_type="expense",
                entity_id=expense.id,
                action="created",
                data={
                    "description": expense.description,
                    "amount": float(expense.amount)
                }
            ))

    # Track online sales that were synced
    if sync_to_sales:
        # Track the sales we just created/updated
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
                    sale = db.query(OnlineSale).filter(
                        OnlineSale.branch_id == ctx.current_branch_id,
                        OnlineSale.sale_date == request.difference_date,
                        OnlineSale.platform_id == platform.id
                    ).first()

                    if sale:
                        db.add(ImportHistoryItem(
                            import_history_id=history.id,
                            entity_type="online_sale",
                            entity_id=sale.id,
                            action="created",  # We track both creates and updates as 'created' for import context
                            data={
                                "platform": platform_name,
                                "amount": float(amount)
                            }
                        ))

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
    """Delete cash difference record and all related entities (cascade delete).

    This will delete:
    - Related expenses created during import (ONLY if not modified after import)
    - Related online_sales synced during import (ONLY if not modified after import)
    - Import history tracking records

    SAFETY: Expenses and online_sales that were modified AFTER import will NOT be deleted.

    WARNING: This action cannot be undone.
    """
    try:
        # Get the record
        record = db.query(CashDifference).filter(
            CashDifference.id == record_id,
            CashDifference.branch_id == ctx.current_branch_id
        ).first()

        if not record:
            raise HTTPException(status_code=404, detail="Kayit bulunamadi")

        # Find all import history items that created this cash_difference record
        import_history_items = db.query(ImportHistoryItem).filter(
            ImportHistoryItem.entity_type == "cash_difference",
            ImportHistoryItem.entity_id == record_id
        ).all()

        deleted_expenses = 0
        deleted_sales = 0
        skipped_expenses = 0
        skipped_sales = 0
        history_ids_to_check = set()

        for item in import_history_items:
            history_ids_to_check.add(item.import_history_id)

            # Find all related items from the same import (expenses, online_sales)
            related_items = db.query(ImportHistoryItem).filter(
                ImportHistoryItem.import_history_id == item.import_history_id,
                ImportHistoryItem.entity_type.in_(["expense", "online_sale"])
            ).all()

            for related in related_items:
                if related.entity_type == "expense":
                    # Check if expense exists and hasn't been modified
                    expense = db.query(Expense).filter(
                        Expense.id == related.entity_id,
                        Expense.branch_id == ctx.current_branch_id
                    ).first()
                    if expense:
                        # Check if expense was modified after import (updated_at exists and > created_at)
                        if hasattr(expense, 'updated_at') and expense.updated_at and expense.updated_at > expense.created_at:
                            # Skip deleting modified expenses
                            skipped_expenses += 1
                        else:
                            db.delete(expense)
                            deleted_expenses += 1

                elif related.entity_type == "online_sale":
                    # Check if sale exists and hasn't been modified
                    sale = db.query(OnlineSale).filter(
                        OnlineSale.id == related.entity_id,
                        OnlineSale.branch_id == ctx.current_branch_id
                    ).first()
                    if sale:
                        # Check if sale was modified after import
                        if hasattr(sale, 'updated_at') and sale.updated_at and sale.updated_at > sale.created_at:
                            # Skip deleting modified sales
                            skipped_sales += 1
                        else:
                            db.delete(sale)
                            deleted_sales += 1

                # Delete the import history item
                db.delete(related)

            # Delete the cash_difference import history item itself
            db.delete(item)

        # Clean up empty import history records (no items left)
        for history_id in history_ids_to_check:
            remaining_items = db.query(ImportHistoryItem).filter(
                ImportHistoryItem.import_history_id == history_id
            ).count()
            if remaining_items == 0:
                history = db.query(ImportHistory).filter(
                    ImportHistory.id == history_id
                ).first()
                if history:
                    db.delete(history)

        # Finally, delete the cash_difference record
        db.delete(record)

        # Commit transaction
        db.commit()

        result_message = "Kayit silindi"
        if deleted_expenses > 0 or deleted_sales > 0:
            result_message += f" ({deleted_expenses} gider, {deleted_sales} satış)"
        if skipped_expenses > 0 or skipped_sales > 0:
            result_message += f" - {skipped_expenses} gider, {skipped_sales} satış değiştirildiği için atlandı"

        return {
            "message": result_message,
            "deleted_expenses": deleted_expenses,
            "deleted_sales": deleted_sales,
            "skipped_expenses": skipped_expenses,
            "skipped_sales": skipped_sales
        }

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Rollback on any other error
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Silme sırasında hata oluştu: {str(e)}. İşlem geri alındı."
        )


@router.get("/{record_id}/preview-delete")
def preview_delete_cash_difference(record_id: int, db: DBSession, ctx: CurrentBranchContext):
    """Preview what will be deleted when deleting a cash difference record.

    Returns a list of related entities that will be cascade deleted.
    Use this to show the user what will be affected before confirming deletion.

    NOTE: Expenses and online_sales that were modified AFTER import will NOT be deleted.
    """
    record = db.query(CashDifference).filter(
        CashDifference.id == record_id,
        CashDifference.branch_id == ctx.current_branch_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Kayit bulunamadi")

    # Find all import history items that created this cash_difference record
    import_history_items = db.query(ImportHistoryItem).filter(
        ImportHistoryItem.entity_type == "cash_difference",
        ImportHistoryItem.entity_id == record_id
    ).all()

    expenses_to_delete = []
    expenses_to_skip = []
    sales_to_delete = []
    sales_to_skip = []
    history_ids_to_check = set()

    for item in import_history_items:
        history_ids_to_check.add(item.import_history_id)

        # Find all related items from the same import
        related_items = db.query(ImportHistoryItem).filter(
            ImportHistoryItem.import_history_id == item.import_history_id,
            ImportHistoryItem.entity_type.in_(["expense", "online_sale"])
        ).all()

        for related in related_items:
            if related.entity_type == "expense":
                expense = db.query(Expense).filter(
                    Expense.id == related.entity_id,
                    Expense.branch_id == ctx.current_branch_id
                ).first()
                if expense:
                    # Check if expense was modified after import
                    is_modified = (
                        hasattr(expense, 'updated_at') and
                        expense.updated_at and
                        expense.updated_at > expense.created_at
                    )
                    expense_info = {
                        "id": expense.id,
                        "description": expense.description,
                        "amount": float(expense.amount),
                        "expense_date": str(expense.expense_date),
                        "reason": "modified_after_import" if is_modified else None
                    }
                    if is_modified:
                        expenses_to_skip.append(expense_info)
                    else:
                        expenses_to_delete.append(expense_info)

            elif related.entity_type == "online_sale":
                sale = db.query(OnlineSale).filter(
                    OnlineSale.id == related.entity_id,
                    OnlineSale.branch_id == ctx.current_branch_id
                ).first()
                if sale:
                    # Check if sale was modified after import
                    is_modified = (
                        hasattr(sale, 'updated_at') and
                        sale.updated_at and
                        sale.updated_at > sale.created_at
                    )
                    # Get platform name
                    platform = db.query(OnlinePlatform).filter(
                        OnlinePlatform.id == sale.platform_id
                    ).first()
                    sale_info = {
                        "id": sale.id,
                        "platform": platform.name if platform else "Bilinmiyor",
                        "amount": float(sale.amount),
                        "sale_date": str(sale.sale_date),
                        "reason": "modified_after_import" if is_modified else None
                    }
                    if is_modified:
                        sales_to_skip.append(sale_info)
                    else:
                        sales_to_delete.append(sale_info)

    return {
        "cash_difference": {
            "id": record.id,
            "difference_date": str(record.difference_date),
            "kasa_total": float(record.kasa_total),
            "pos_total": float(record.pos_total)
        },
        "related_entities": {
            "expenses": expenses_to_delete,
            "online_sales": sales_to_delete
        },
        "skipped_entities": {
            "expenses": expenses_to_skip,
            "online_sales": sales_to_skip
        },
        "summary": {
            "total_expenses": len(expenses_to_delete),
            "total_sales": len(sales_to_delete),
            "skipped_expenses": len(expenses_to_skip),
            "skipped_sales": len(sales_to_skip)
        }
    }
