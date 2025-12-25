"""
Import History API - Track and manage import audit trail
"""
from datetime import date
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import desc
from app.api.deps import DBSession, CurrentBranchContext
from app.models import ImportHistory, ImportHistoryItem
from app.schemas import ImportHistoryResponse

router = APIRouter(prefix="/import-history", tags=["import-history"])


@router.get("", response_model=list[ImportHistoryResponse])
def get_import_history(
    db: DBSession,
    ctx: CurrentBranchContext,
    import_type: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    status: str | None = None,
    limit: int = Query(default=50, le=200)
):
    """Get import history with optional filters"""
    query = db.query(ImportHistory).filter(
        ImportHistory.branch_id == ctx.current_branch_id
    )

    if import_type:
        query = query.filter(ImportHistory.import_type == import_type)
    if start_date:
        query = query.filter(ImportHistory.import_date >= start_date)
    if end_date:
        query = query.filter(ImportHistory.import_date <= end_date)
    if status:
        query = query.filter(ImportHistory.status == status)

    return query.order_by(desc(ImportHistory.created_at)).limit(limit).all()


@router.get("/{history_id}", response_model=ImportHistoryResponse)
def get_import_history_detail(
    history_id: int,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """Get import history detail with items"""
    record = db.query(ImportHistory).filter(
        ImportHistory.id == history_id,
        ImportHistory.branch_id == ctx.current_branch_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Import history not found")

    return record


@router.post("/{history_id}/undo")
def undo_import(
    history_id: int,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """Undo an import by deleting created entities"""
    record = db.query(ImportHistory).filter(
        ImportHistory.id == history_id,
        ImportHistory.branch_id == ctx.current_branch_id,
        ImportHistory.status == "completed"
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Import not found or already undone")

    # Delete created entities (simplified - expand for each entity type)
    from app.models import Expense, CashDifference, OnlineSale

    for item in record.items:
        if item.action == "created":
            if item.entity_type == "expense":
                db.query(Expense).filter(Expense.id == item.entity_id).delete()
            elif item.entity_type == "cash_difference":
                db.query(CashDifference).filter(CashDifference.id == item.entity_id).delete()
            elif item.entity_type == "online_sale":
                db.query(OnlineSale).filter(OnlineSale.id == item.entity_id).delete()

    record.status = "undone"
    db.commit()

    return {"message": "Import undone successfully", "items_reverted": len(record.items)}
