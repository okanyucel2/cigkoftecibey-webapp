from datetime import date, timedelta
from decimal import Decimal
from calendar import monthrange
from fastapi import APIRouter
from sqlalchemy import func, and_
from app.api.deps import DBSession, CurrentBranchContext
from app.models import Purchase, Expense, DailyProduction, StaffMeal, OnlineSale, OnlinePlatform, CourierExpense, PartTimeCost
from app.schemas import DashboardStats, BilancoStats, DaySummary

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


# Türkçe gün adları
TURKISH_DAYS = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
TURKISH_DAYS_SHORT = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
TURKISH_MONTHS = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                  "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]


def get_day_revenue(db: DBSession, branch_id: int, target_date: date) -> Decimal:
    """Belirli bir günün toplam cirosunu hesapla"""
    total = db.query(func.coalesce(func.sum(OnlineSale.amount), 0)).filter(
        OnlineSale.branch_id == branch_id,
        OnlineSale.sale_date == target_date
    ).scalar()
    return Decimal(str(total))


def get_day_expenses(db: DBSession, branch_id: int, target_date: date) -> Decimal:
    """Belirli bir günün toplam giderlerini hesapla"""
    purchases = db.query(func.coalesce(func.sum(Purchase.total), 0)).filter(
        Purchase.branch_id == branch_id,
        Purchase.purchase_date == target_date
    ).scalar()

    expenses = db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
        Expense.branch_id == branch_id,
        Expense.expense_date == target_date
    ).scalar()

    courier = db.query(func.coalesce(func.sum(CourierExpense.amount), 0)).filter(
        CourierExpense.branch_id == branch_id,
        CourierExpense.expense_date == target_date
    ).scalar()

    parttime = db.query(func.coalesce(func.sum(PartTimeCost.amount), 0)).filter(
        PartTimeCost.branch_id == branch_id,
        PartTimeCost.cost_date == target_date
    ).scalar()

    staff_meal = db.query(StaffMeal).filter(
        StaffMeal.branch_id == branch_id,
        StaffMeal.meal_date == target_date
    ).first()
    staff_cost = staff_meal.total if staff_meal else Decimal("0")

    return Decimal(str(purchases)) + Decimal(str(expenses)) + Decimal(str(courier)) + Decimal(str(parttime)) + staff_cost


def get_day_breakdown(db: DBSession, branch_id: int, target_date: date) -> dict:
    """Belirli bir günün kırılımını döndür"""
    purchases = db.query(func.coalesce(func.sum(Purchase.total), 0)).filter(
        Purchase.branch_id == branch_id,
        Purchase.purchase_date == target_date
    ).scalar()

    expenses = db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
        Expense.branch_id == branch_id,
        Expense.expense_date == target_date
    ).scalar()

    courier = db.query(func.coalesce(func.sum(CourierExpense.amount), 0)).filter(
        CourierExpense.branch_id == branch_id,
        CourierExpense.expense_date == target_date
    ).scalar()

    parttime = db.query(func.coalesce(func.sum(PartTimeCost.amount), 0)).filter(
        PartTimeCost.branch_id == branch_id,
        PartTimeCost.cost_date == target_date
    ).scalar()

    staff_meal = db.query(StaffMeal).filter(
        StaffMeal.branch_id == branch_id,
        StaffMeal.meal_date == target_date
    ).first()
    staff_cost = staff_meal.total if staff_meal else Decimal("0")

    revenue = get_day_revenue(db, branch_id, target_date)

    return {
        "online": revenue,
        "mal_alimi": Decimal(str(purchases)),
        "gider": Decimal(str(expenses)),
        "staff": staff_cost,
        "kurye": Decimal(str(courier)),
        "parttime": Decimal(str(parttime))
    }


@router.get("/bilanco", response_model=BilancoStats)
def get_bilanco_stats(db: DBSession, ctx: CurrentBranchContext):
    """Bilanço dashboard - Dün, Bu Hafta, Bu Ay özeti"""
    today = date.today()
    yesterday = today - timedelta(days=1)
    day_before_yesterday = today - timedelta(days=2)
    branch_id = ctx.current_branch_id

    # ===== DÜN =====
    yesterday_revenue = get_day_revenue(db, branch_id, yesterday)
    yesterday_expenses = get_day_expenses(db, branch_id, yesterday)
    yesterday_profit = yesterday_revenue - yesterday_expenses
    yesterday_breakdown = get_day_breakdown(db, branch_id, yesterday)

    prev_revenue = get_day_revenue(db, branch_id, day_before_yesterday)
    if prev_revenue > 0:
        yesterday_vs_previous_pct = ((yesterday_revenue - prev_revenue) / prev_revenue) * 100
    else:
        yesterday_vs_previous_pct = Decimal("0")

    yesterday_day_name = TURKISH_DAYS[yesterday.weekday()]

    # ===== BU HAFTA =====
    days_since_monday = today.weekday()
    this_week_start = today - timedelta(days=days_since_monday)
    this_week_end = yesterday

    this_week_daily = []
    this_week_total = Decimal("0")

    for i in range(7):
        day = this_week_start + timedelta(days=i)
        if day >= today:
            break
        amount = get_day_revenue(db, branch_id, day)
        this_week_daily.append(DaySummary(
            day_name=TURKISH_DAYS_SHORT[day.weekday()],
            date=day,
            amount=amount
        ))
        this_week_total += amount

    if this_week_daily:
        this_week_best = max(this_week_daily, key=lambda x: x.amount)
        this_week_worst = min(this_week_daily, key=lambda x: x.amount)
    else:
        this_week_best = None
        this_week_worst = None

    # ===== GEÇEN HAFTA =====
    last_week_start = this_week_start - timedelta(days=7)
    last_week_end = this_week_start - timedelta(days=1)

    last_week_daily = []
    last_week_total = Decimal("0")

    for i in range(7):
        day = last_week_start + timedelta(days=i)
        amount = get_day_revenue(db, branch_id, day)
        last_week_daily.append(DaySummary(
            day_name=TURKISH_DAYS_SHORT[day.weekday()],
            date=day,
            amount=amount
        ))
        last_week_total += amount

    if last_week_total > 0:
        week_vs_week_pct = ((this_week_total - last_week_total) / last_week_total) * 100
    else:
        week_vs_week_pct = Decimal("0")

    # ===== BU AY =====
    this_month_start = today.replace(day=1)
    _, days_in_month = monthrange(today.year, today.month)
    this_month_name = f"{TURKISH_MONTHS[today.month]} {today.year}"
    this_month_days_passed = (yesterday - this_month_start).days + 1
    this_month_days_total = days_in_month

    this_month_revenue = Decimal("0")
    this_month_expenses = Decimal("0")
    this_month_chart = []

    current = this_month_start
    while current < today:
        rev = get_day_revenue(db, branch_id, current)
        exp = get_day_expenses(db, branch_id, current)
        this_month_revenue += rev
        this_month_expenses += exp
        this_month_chart.append(DaySummary(
            day_name=str(current.day),
            date=current,
            amount=rev
        ))
        current += timedelta(days=1)

    this_month_profit = this_month_revenue - this_month_expenses

    if this_month_days_passed > 0:
        this_month_daily_avg = this_month_revenue / this_month_days_passed
        remaining_days = this_month_days_total - this_month_days_passed
        this_month_forecast = this_month_revenue + (this_month_daily_avg * remaining_days)
    else:
        this_month_daily_avg = Decimal("0")
        this_month_forecast = Decimal("0")

    # ===== GEÇEN AY =====
    if today.month == 1:
        last_month_year = today.year - 1
        last_month_num = 12
    else:
        last_month_year = today.year
        last_month_num = today.month - 1

    last_month_start = date(last_month_year, last_month_num, 1)
    _, last_month_days = monthrange(last_month_year, last_month_num)
    last_month_compare_end = last_month_start + timedelta(days=min(this_month_days_passed, last_month_days) - 1)

    last_month_revenue = Decimal("0")
    last_month_expenses = Decimal("0")

    current = last_month_start
    while current <= last_month_compare_end:
        last_month_revenue += get_day_revenue(db, branch_id, current)
        last_month_expenses += get_day_expenses(db, branch_id, current)
        current += timedelta(days=1)

    last_month_profit = last_month_revenue - last_month_expenses

    return BilancoStats(
        yesterday_date=yesterday,
        yesterday_day_name=yesterday_day_name,
        yesterday_revenue=yesterday_revenue,
        yesterday_expenses=yesterday_expenses,
        yesterday_profit=yesterday_profit,
        yesterday_vs_previous_pct=yesterday_vs_previous_pct,
        yesterday_breakdown=yesterday_breakdown,
        this_week_start=this_week_start,
        this_week_end=this_week_end,
        this_week_total=this_week_total,
        this_week_daily=this_week_daily,
        this_week_best_day=this_week_best,
        this_week_worst_day=this_week_worst,
        last_week_start=last_week_start,
        last_week_end=last_week_end,
        last_week_total=last_week_total,
        last_week_daily=last_week_daily,
        week_vs_week_pct=week_vs_week_pct,
        this_month_name=this_month_name,
        this_month_days_passed=this_month_days_passed,
        this_month_days_total=this_month_days_total,
        this_month_revenue=this_month_revenue,
        this_month_expenses=this_month_expenses,
        this_month_profit=this_month_profit,
        this_month_daily_avg=this_month_daily_avg,
        this_month_forecast=this_month_forecast,
        this_month_chart=this_month_chart,
        last_month_revenue=last_month_revenue,
        last_month_expenses=last_month_expenses,
        last_month_profit=last_month_profit
    )
