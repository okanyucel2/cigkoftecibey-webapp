from datetime import date
from decimal import Decimal
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, extract
from app.api.deps import DBSession, CurrentBranchContext
from app.models import CourierExpense
from app.schemas import (
    CourierExpenseCreate, CourierExpenseResponse, CourierExpenseUpdate,
    CourierExpenseSummary, CourierExpenseBulkCreate
)

router = APIRouter(prefix="/courier-expenses", tags=["courier-expenses"])


@router.post("", response_model=CourierExpenseResponse)
def create_courier_expense(data: CourierExpenseCreate, db: DBSession, ctx: CurrentBranchContext):
    """Yeni kurye gideri olustur"""
    # Ayni gun icin kayit var mi kontrol et
    existing = db.query(CourierExpense).filter(
        CourierExpense.branch_id == ctx.current_branch_id,
        CourierExpense.expense_date == data.expense_date
    ).first()

    if existing:
        # Varsa guncelle
        for field, value in data.model_dump().items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing

    # Yoksa yeni olustur
    expense = CourierExpense(
        branch_id=ctx.current_branch_id,
        created_by=ctx.user.id,
        **data.model_dump()
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.post("/bulk", response_model=list[CourierExpenseResponse])
def create_bulk_courier_expenses(data: CourierExpenseBulkCreate, db: DBSession, ctx: CurrentBranchContext):
    """Toplu kurye gideri girisi"""
    results = []

    for entry in data.entries:
        # Ayni gun icin kayit var mi kontrol et
        existing = db.query(CourierExpense).filter(
            CourierExpense.branch_id == ctx.current_branch_id,
            CourierExpense.expense_date == entry.expense_date
        ).first()

        if existing:
            # Guncelle
            existing.package_count = entry.package_count
            existing.amount = entry.amount
            existing.vat_rate = entry.vat_rate
            db.flush()
            results.append(existing)
        else:
            # Yeni olustur
            expense = CourierExpense(
                branch_id=ctx.current_branch_id,
                created_by=ctx.user.id,
                expense_date=entry.expense_date,
                package_count=entry.package_count,
                amount=entry.amount,
                vat_rate=entry.vat_rate
            )
            db.add(expense)
            db.flush()
            results.append(expense)

    db.commit()
    for r in results:
        db.refresh(r)
    return results


@router.get("", response_model=list[CourierExpenseResponse])
def get_courier_expenses(
    db: DBSession,
    ctx: CurrentBranchContext,
    start_date: date | None = None,
    end_date: date | None = None,
    year: int | None = None,
    month: int | None = None,
    limit: int = Query(default=100, le=500)
):
    """Kurye giderlerini listele"""
    query = db.query(CourierExpense).filter(CourierExpense.branch_id == ctx.current_branch_id)

    if year and month:
        query = query.filter(
            extract('year', CourierExpense.expense_date) == year,
            extract('month', CourierExpense.expense_date) == month
        )
    else:
        if start_date:
            query = query.filter(CourierExpense.expense_date >= start_date)
        if end_date:
            query = query.filter(CourierExpense.expense_date <= end_date)

    return query.order_by(CourierExpense.expense_date.desc()).limit(limit).all()


@router.get("/summary", response_model=CourierExpenseSummary)
def get_courier_expense_summary(
    db: DBSession,
    ctx: CurrentBranchContext,
    year: int | None = None,
    month: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None
):
    """Kurye gideri ozeti"""
    query = db.query(CourierExpense).filter(CourierExpense.branch_id == ctx.current_branch_id)

    if year and month:
        query = query.filter(
            extract('year', CourierExpense.expense_date) == year,
            extract('month', CourierExpense.expense_date) == month
        )
    else:
        if start_date:
            query = query.filter(CourierExpense.expense_date >= start_date)
        if end_date:
            query = query.filter(CourierExpense.expense_date <= end_date)

    expenses = query.all()

    if not expenses:
        return CourierExpenseSummary(
            total_packages=0,
            total_amount=Decimal("0"),
            total_vat=Decimal("0"),
            total_with_vat=Decimal("0"),
            days_count=0,
            avg_daily_packages=Decimal("0"),
            avg_package_cost=Decimal("0")
        )

    total_packages = sum(e.package_count for e in expenses)
    total_amount = sum(e.amount for e in expenses)
    total_vat = sum(e.vat_amount for e in expenses)
    total_with_vat = sum(e.total_with_vat for e in expenses)
    days_count = len(expenses)

    avg_daily_packages = Decimal(total_packages) / days_count if days_count > 0 else Decimal("0")
    avg_package_cost = total_with_vat / total_packages if total_packages > 0 else Decimal("0")

    return CourierExpenseSummary(
        total_packages=total_packages,
        total_amount=total_amount,
        total_vat=total_vat,
        total_with_vat=total_with_vat,
        days_count=days_count,
        avg_daily_packages=avg_daily_packages,
        avg_package_cost=avg_package_cost
    )


@router.get("/today", response_model=CourierExpenseResponse | None)
def get_today_courier_expense(db: DBSession, ctx: CurrentBranchContext):
    """Bugunun kurye giderini getir"""
    today = date.today()
    return db.query(CourierExpense).filter(
        CourierExpense.branch_id == ctx.current_branch_id,
        CourierExpense.expense_date == today
    ).first()


@router.get("/{expense_id}", response_model=CourierExpenseResponse)
def get_courier_expense(expense_id: int, db: DBSession, ctx: CurrentBranchContext):
    """Tek bir kurye gideri getir"""
    expense = db.query(CourierExpense).filter(
        CourierExpense.id == expense_id,
        CourierExpense.branch_id == ctx.current_branch_id
    ).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Kurye gideri bulunamadi")
    return expense


@router.put("/{expense_id}", response_model=CourierExpenseResponse)
def update_courier_expense(
    expense_id: int,
    data: CourierExpenseUpdate,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """Kurye gideri guncelle"""
    expense = db.query(CourierExpense).filter(
        CourierExpense.id == expense_id,
        CourierExpense.branch_id == ctx.current_branch_id
    ).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Kurye gideri bulunamadi")

    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(expense, field, value)

    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}")
def delete_courier_expense(expense_id: int, db: DBSession, ctx: CurrentBranchContext):
    """Kurye gideri sil"""
    expense = db.query(CourierExpense).filter(
        CourierExpense.id == expense_id,
        CourierExpense.branch_id == ctx.current_branch_id
    ).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Kurye gideri bulunamadi")
    db.delete(expense)
    db.commit()
    return {"message": "Kurye gideri silindi"}
