from datetime import date
from decimal import Decimal
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func
from app.api.deps import DBSession, CurrentBranchContext
from app.models import StaffMeal
from app.schemas import StaffMealCreate, StaffMealResponse, StaffMealSummary

router = APIRouter(prefix="/staff-meals", tags=["staff-meals"])


@router.post("", response_model=StaffMealResponse)
def create_staff_meal(data: StaffMealCreate, db: DBSession, ctx: CurrentBranchContext):
    """Yeni personel yemek kaydı oluştur"""
    # Aynı tarihte kayıt var mı kontrol et
    existing = db.query(StaffMeal).filter(
        StaffMeal.branch_id == ctx.current_branch_id,
        StaffMeal.meal_date == data.meal_date
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu tarihte zaten kayit var")

    staff_meal = StaffMeal(
        branch_id=ctx.current_branch_id,
        meal_date=data.meal_date,
        unit_price=data.unit_price,
        staff_count=data.staff_count,
        notes=data.notes,
        created_by=ctx.user.id
    )
    db.add(staff_meal)
    db.commit()
    db.refresh(staff_meal)
    return staff_meal


@router.get("", response_model=list[StaffMealResponse])
def get_staff_meals(
    db: DBSession,
    ctx: CurrentBranchContext,
    start_date: date | None = None,
    end_date: date | None = None,
    month: int | None = Query(default=None, ge=1, le=12),
    year: int | None = None,
    limit: int = Query(default=50, le=200)
):
    """Personel yemek kayıtlarını getir"""
    query = db.query(StaffMeal).filter(StaffMeal.branch_id == ctx.current_branch_id)

    # Ay/yıl filtresi
    if month and year:
        from calendar import monthrange
        first_day = date(year, month, 1)
        last_day = date(year, month, monthrange(year, month)[1])
        query = query.filter(
            StaffMeal.meal_date >= first_day,
            StaffMeal.meal_date <= last_day
        )
    else:
        # Tarih aralığı filtresi
        if start_date:
            query = query.filter(StaffMeal.meal_date >= start_date)
        if end_date:
            query = query.filter(StaffMeal.meal_date <= end_date)

    return query.order_by(StaffMeal.meal_date.desc()).limit(limit).all()


@router.get("/today", response_model=StaffMealResponse | None)
def get_today_staff_meal(db: DBSession, ctx: CurrentBranchContext):
    """Bugünün personel yemek kaydını getir"""
    today = date.today()
    return db.query(StaffMeal).filter(
        StaffMeal.branch_id == ctx.current_branch_id,
        StaffMeal.meal_date == today
    ).first()


@router.get("/summary", response_model=StaffMealSummary)
def get_staff_meal_summary(
    db: DBSession,
    ctx: CurrentBranchContext,
    month: int | None = Query(default=None, ge=1, le=12),
    year: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None
):
    """Personel yemek özeti"""
    query = db.query(StaffMeal).filter(StaffMeal.branch_id == ctx.current_branch_id)

    # Ay/yıl filtresi
    if month and year:
        from calendar import monthrange
        first_day = date(year, month, 1)
        last_day = date(year, month, monthrange(year, month)[1])
        query = query.filter(
            StaffMeal.meal_date >= first_day,
            StaffMeal.meal_date <= last_day
        )
    elif start_date and end_date:
        query = query.filter(
            StaffMeal.meal_date >= start_date,
            StaffMeal.meal_date <= end_date
        )

    meals = query.all()

    if not meals:
        return StaffMealSummary(
            total_staff_count=0,
            total_cost=Decimal("0"),
            avg_daily_staff=Decimal("0"),
            avg_unit_price=Decimal("0"),
            days_count=0
        )

    total_staff = sum(m.staff_count for m in meals)
    total_cost = sum(m.total for m in meals)
    avg_unit_price = sum(m.unit_price for m in meals) / len(meals)

    return StaffMealSummary(
        total_staff_count=total_staff,
        total_cost=total_cost,
        avg_daily_staff=Decimal(str(total_staff / len(meals))),
        avg_unit_price=avg_unit_price,
        days_count=len(meals)
    )


@router.get("/{meal_id}", response_model=StaffMealResponse)
def get_staff_meal(meal_id: int, db: DBSession, ctx: CurrentBranchContext):
    """Tekil personel yemek kaydı getir"""
    meal = db.query(StaffMeal).filter(
        StaffMeal.id == meal_id,
        StaffMeal.branch_id == ctx.current_branch_id
    ).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Kayit bulunamadi")
    return meal


@router.put("/{meal_id}", response_model=StaffMealResponse)
def update_staff_meal(meal_id: int, data: StaffMealCreate, db: DBSession, ctx: CurrentBranchContext):
    """Personel yemek kaydını güncelle"""
    meal = db.query(StaffMeal).filter(
        StaffMeal.id == meal_id,
        StaffMeal.branch_id == ctx.current_branch_id
    ).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Kayit bulunamadi")

    # Tarih değiştiyse, yeni tarihte başka kayıt var mı kontrol et
    if data.meal_date != meal.meal_date:
        existing = db.query(StaffMeal).filter(
            StaffMeal.branch_id == ctx.current_branch_id,
            StaffMeal.meal_date == data.meal_date,
            StaffMeal.id != meal_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Bu tarihte zaten kayit var")

    meal.meal_date = data.meal_date
    meal.unit_price = data.unit_price
    meal.staff_count = data.staff_count
    meal.notes = data.notes

    db.commit()
    db.refresh(meal)
    return meal


@router.delete("/{meal_id}")
def delete_staff_meal(meal_id: int, db: DBSession, ctx: CurrentBranchContext):
    """Personel yemek kaydını sil"""
    meal = db.query(StaffMeal).filter(
        StaffMeal.id == meal_id,
        StaffMeal.branch_id == ctx.current_branch_id
    ).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Kayit bulunamadi")

    db.delete(meal)
    db.commit()
    return {"message": "Kayit silindi"}
