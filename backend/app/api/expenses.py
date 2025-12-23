from datetime import date
from fastapi import APIRouter, HTTPException, Query
from app.api.deps import DBSession, CurrentBranchContext
from app.models import Expense, ExpenseCategory
from app.schemas import (
    ExpenseCreate, ExpenseResponse,
    ExpenseCategoryCreate, ExpenseCategoryResponse
)

router = APIRouter(prefix="/expenses", tags=["expenses"])


# Expense Categories
@router.get("/categories", response_model=list[ExpenseCategoryResponse])
def get_expense_categories(db: DBSession, ctx: CurrentBranchContext):
    return db.query(ExpenseCategory).order_by(ExpenseCategory.name).all()


@router.post("/categories", response_model=ExpenseCategoryResponse)
def create_expense_category(data: ExpenseCategoryCreate, db: DBSession, ctx: CurrentBranchContext):
    category = ExpenseCategory(**data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.put("/categories/{category_id}", response_model=ExpenseCategoryResponse)
def update_expense_category(
    category_id: int,
    data: ExpenseCategoryCreate,
    db: DBSession,
    ctx: CurrentBranchContext
):
    category = db.query(ExpenseCategory).filter(ExpenseCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Kategori bulunamadi")

    for field, value in data.model_dump().items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)
    return category


@router.delete("/categories/{category_id}")
def delete_expense_category(category_id: int, db: DBSession, ctx: CurrentBranchContext):
    category = db.query(ExpenseCategory).filter(ExpenseCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Kategori bulunamadi")

    # System categories cannot be deleted
    if category.is_system:
        raise HTTPException(status_code=400, detail="Sistem kategorileri silinemez")

    # Bu kategoriye ait gider var mi kontrol et
    expense_count = db.query(Expense).filter(Expense.category_id == category_id).count()
    if expense_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Bu kategoride {expense_count} gider kaydi var. Once giderleri silin veya baska kategoriye tasıyın."
        )

    db.delete(category)
    db.commit()
    return {"message": "Kategori silindi"}


# Expenses
@router.post("", response_model=ExpenseResponse)
def create_expense(data: ExpenseCreate, db: DBSession, ctx: CurrentBranchContext):
    # Kategoriyi kontrol et
    category = db.query(ExpenseCategory).filter(
        ExpenseCategory.id == data.category_id
    ).first()
    if not category:
        raise HTTPException(status_code=400, detail="Gider kategorisi bulunamadi")

    expense = Expense(
        branch_id=ctx.current_branch_id,
        created_by=ctx.user.id,
        **data.model_dump()
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("", response_model=list[ExpenseResponse])
def get_expenses(
    db: DBSession,
    ctx: CurrentBranchContext,
    start_date: date | None = None,
    end_date: date | None = None,
    category_id: int | None = None,
    limit: int = Query(default=50, le=200)
):
    query = db.query(Expense).filter(Expense.branch_id == ctx.current_branch_id)

    if start_date:
        query = query.filter(Expense.expense_date >= start_date)
    if end_date:
        query = query.filter(Expense.expense_date <= end_date)
    if category_id:
        query = query.filter(Expense.category_id == category_id)

    return query.order_by(Expense.expense_date.desc(), Expense.id.desc()).limit(limit).all()


@router.get("/today", response_model=list[ExpenseResponse])
def get_today_expenses(db: DBSession, ctx: CurrentBranchContext):
    today = date.today()
    return db.query(Expense).filter(
        Expense.branch_id == ctx.current_branch_id,
        Expense.expense_date == today
    ).order_by(Expense.created_at.desc()).all()


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: int, db: DBSession, ctx: CurrentBranchContext):
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.branch_id == ctx.current_branch_id
    ).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Gider bulunamadi")
    return expense


@router.delete("/{expense_id}")
def delete_expense(expense_id: int, db: DBSession, ctx: CurrentBranchContext):
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.branch_id == ctx.current_branch_id
    ).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Gider bulunamadi")
    db.delete(expense)
    db.commit()
    return {"message": "Gider silindi"}
