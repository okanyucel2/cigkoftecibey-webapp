from datetime import date, timedelta
from decimal import Decimal
from fastapi import APIRouter
from sqlalchemy import func, and_
from app.api.deps import DBSession, CurrentBranchContext
from app.models import Purchase, Expense, DailyProduction, StaffMeal, OnlineSale, OnlinePlatform, CourierExpense, PartTimeCost
from app.schemas import DashboardStats

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(db: DBSession, ctx: CurrentBranchContext):
    today = date.today()
    branch_id = ctx.current_branch_id

    # Tüm kanalları ve bugünün satışlarını çek
    channel_sales = db.query(
        OnlinePlatform.channel_type,
        OnlinePlatform.name,
        func.coalesce(func.sum(OnlineSale.amount), 0).label('total')
    ).outerjoin(
        OnlineSale,
        and_(
            OnlineSale.platform_id == OnlinePlatform.id,
            OnlineSale.branch_id == branch_id,
            OnlineSale.sale_date == today
        )
    ).filter(
        OnlinePlatform.is_active == True
    ).group_by(
        OnlinePlatform.channel_type,
        OnlinePlatform.name
    ).all()

    # Kanal tipine göre toplamlar
    today_salon = Decimal("0")
    today_telefon = Decimal("0")
    today_online = Decimal("0")
    online_breakdown = {}
    online_platform_count = 0

    for sale in channel_sales:
        amount = Decimal(str(sale.total))
        if sale.channel_type == 'pos_salon':
            today_salon = amount
        elif sale.channel_type == 'pos_telefon':
            today_telefon = amount
        elif sale.channel_type == 'online':
            if amount > 0:
                online_breakdown[sale.name] = amount
                online_platform_count += 1
            today_online += amount

    # Toplam satış
    today_total_sales = today_salon + today_telefon + today_online

    # Bugünün mal alımları
    today_purchases = db.query(func.coalesce(func.sum(Purchase.total), 0)).filter(
        Purchase.branch_id == branch_id,
        Purchase.purchase_date == today
    ).scalar()

    # Bugünün giderleri
    today_expenses = db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
        Expense.branch_id == branch_id,
        Expense.expense_date == today
    ).scalar()

    # Bugünün kurye giderleri
    today_courier_expense = db.query(func.coalesce(func.sum(CourierExpense.amount), 0)).filter(
        CourierExpense.branch_id == branch_id,
        CourierExpense.expense_date == today
    ).scalar()
    today_courier_cost = Decimal(str(today_courier_expense))

    # Bugünün part-time giderleri
    today_part_time_expense = db.query(func.coalesce(func.sum(PartTimeCost.amount), 0)).filter(
        PartTimeCost.branch_id == branch_id,
        PartTimeCost.cost_date == today
    ).scalar()
    today_part_time_cost = Decimal(str(today_part_time_expense))

    # Bugünün personel yemekleri
    today_staff_meal = db.query(StaffMeal).filter(
        StaffMeal.branch_id == branch_id,
        StaffMeal.meal_date == today
    ).first()
    today_staff_meals = today_staff_meal.total if today_staff_meal else Decimal("0")

    # Bugünün karı
    today_profit = (
        today_total_sales 
        - Decimal(str(today_purchases)) 
        - Decimal(str(today_expenses)) 
        - today_staff_meals
        - today_courier_cost
        - today_part_time_cost
    )

    # Bugünün üretimi
    today_production = db.query(DailyProduction).filter(
        DailyProduction.branch_id == branch_id,
        DailyProduction.production_date == today
    ).first()

    today_production_kg = Decimal("0")
    today_production_cost = Decimal("0")
    if today_production:
        today_production_kg = today_production.kneaded_kg or Decimal("0")
        today_production_cost = today_production.total_cost or Decimal("0")

    # Son 7 günlük satış trendi (tüm kanalların toplamı)
    week_sales = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_total = db.query(func.coalesce(func.sum(OnlineSale.amount), 0)).filter(
            OnlineSale.branch_id == branch_id,
            OnlineSale.sale_date == day
        ).scalar()
        week_sales.append({
            "date": day.isoformat(),
            "day": day.strftime("%a"),
            "sales": float(day_total)
        })

    return DashboardStats(
        today_salon=today_salon,
        today_telefon=today_telefon,
        today_online_sales=today_online,
        today_total_sales=today_total_sales,
        online_breakdown=online_breakdown,
        online_platform_count=online_platform_count,
        today_purchases=Decimal(str(today_purchases)),
        today_expenses=Decimal(str(today_expenses)),
        today_staff_meals=today_staff_meals,
        today_courier_cost=today_courier_cost,
        today_part_time_cost=today_part_time_cost,
        today_profit=today_profit,
        today_production_kg=today_production_kg,
        today_production_cost=today_production_cost,
        week_sales=week_sales
    )


@router.get("/daily-summary")
def get_daily_summary(
    db: DBSession,
    ctx: CurrentBranchContext,
    start_date: date | None = None,
    end_date: date | None = None
):
    """Günlük özet raporu - birleşik kanal modeli"""
    branch_id = ctx.current_branch_id

    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    results = []
    current = start_date

    while current <= end_date:
        # O günün satışları (kanal tipine göre)
        day_sales_query = db.query(
            OnlinePlatform.channel_type,
            func.coalesce(func.sum(OnlineSale.amount), 0).label('total')
        ).outerjoin(
            OnlineSale,
            and_(
                OnlineSale.platform_id == OnlinePlatform.id,
                OnlineSale.branch_id == branch_id,
                OnlineSale.sale_date == current
            )
        ).group_by(OnlinePlatform.channel_type).all()

        day_salon = Decimal("0")
        day_telefon = Decimal("0")
        day_online = Decimal("0")

        for row in day_sales_query:
            amount = Decimal(str(row.total))
            if row.channel_type == 'pos_salon':
                day_salon = amount
            elif row.channel_type == 'pos_telefon':
                day_telefon = amount
            elif row.channel_type == 'online':
                day_online = amount

        day_total = day_salon + day_telefon + day_online

        # O günün alımları
        day_purchases = db.query(func.coalesce(func.sum(Purchase.total), 0)).filter(
            Purchase.branch_id == branch_id,
            Purchase.purchase_date == current
        ).scalar()

        # O günün giderleri
        day_expenses = db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
            Expense.branch_id == branch_id,
            Expense.expense_date == current
        ).scalar()

        day_profit = float(day_total) - float(day_purchases) - float(day_expenses)

        results.append({
            "date": current.isoformat(),
            "sales": float(day_total),
            "salon": float(day_salon),
            "telefon": float(day_telefon),
            "online": float(day_online),
            "purchases": float(day_purchases),
            "expenses": float(day_expenses),
            "profit": day_profit
        })

        current += timedelta(days=1)

    return results
