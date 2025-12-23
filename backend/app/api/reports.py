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


def fetch_daily_data(db: DBSession, branch_id: int, start_date: date, end_date: date) -> dict:
    """
    Belirli bir tarih aralığı için tüm günlük verileri tek seferde çeker.
    ~200 query yerine 6 query kullanır (batch optimization).

    Returns:
        {
            date: {
                "revenue": Decimal,
                "purchases": Decimal,
                "expenses": Decimal,
                "courier": Decimal,
                "parttime": Decimal,
                "staff": Decimal
            }
        }
    """
    result = {}

    # Initialize all dates with zeros
    current = start_date
    while current <= end_date:
        result[current] = {
            "revenue": Decimal("0"),
            "purchases": Decimal("0"),
            "expenses": Decimal("0"),
            "courier": Decimal("0"),
            "parttime": Decimal("0"),
            "staff": Decimal("0")
        }
        current += timedelta(days=1)

    # Query 1: Revenue (OnlineSale)
    revenue_rows = db.query(
        OnlineSale.sale_date,
        func.sum(OnlineSale.amount)
    ).filter(
        OnlineSale.branch_id == branch_id,
        OnlineSale.sale_date >= start_date,
        OnlineSale.sale_date <= end_date
    ).group_by(OnlineSale.sale_date).all()

    for row in revenue_rows:
        if row[0] in result:
            result[row[0]]["revenue"] = Decimal(str(row[1] or 0))

    # Query 2: Purchases
    purchase_rows = db.query(
        Purchase.purchase_date,
        func.sum(Purchase.total)
    ).filter(
        Purchase.branch_id == branch_id,
        Purchase.purchase_date >= start_date,
        Purchase.purchase_date <= end_date
    ).group_by(Purchase.purchase_date).all()

    for row in purchase_rows:
        if row[0] in result:
            result[row[0]]["purchases"] = Decimal(str(row[1] or 0))

    # Query 3: Expenses
    expense_rows = db.query(
        Expense.expense_date,
        func.sum(Expense.amount)
    ).filter(
        Expense.branch_id == branch_id,
        Expense.expense_date >= start_date,
        Expense.expense_date <= end_date
    ).group_by(Expense.expense_date).all()

    for row in expense_rows:
        if row[0] in result:
            result[row[0]]["expenses"] = Decimal(str(row[1] or 0))

    # Query 4: Courier
    courier_rows = db.query(
        CourierExpense.expense_date,
        func.sum(CourierExpense.amount)
    ).filter(
        CourierExpense.branch_id == branch_id,
        CourierExpense.expense_date >= start_date,
        CourierExpense.expense_date <= end_date
    ).group_by(CourierExpense.expense_date).all()

    for row in courier_rows:
        if row[0] in result:
            result[row[0]]["courier"] = Decimal(str(row[1] or 0))

    # Query 5: Part-time
    parttime_rows = db.query(
        PartTimeCost.cost_date,
        func.sum(PartTimeCost.amount)
    ).filter(
        PartTimeCost.branch_id == branch_id,
        PartTimeCost.cost_date >= start_date,
        PartTimeCost.cost_date <= end_date
    ).group_by(PartTimeCost.cost_date).all()

    for row in parttime_rows:
        if row[0] in result:
            result[row[0]]["parttime"] = Decimal(str(row[1] or 0))

    # Query 6: Staff meals
    staff_rows = db.query(StaffMeal).filter(
        StaffMeal.branch_id == branch_id,
        StaffMeal.meal_date >= start_date,
        StaffMeal.meal_date <= end_date
    ).all()

    for row in staff_rows:
        if row.meal_date in result:
            result[row.meal_date]["staff"] = row.total or Decimal("0")

    return result


def get_day_total_expenses(data: dict) -> Decimal:
    """Günlük toplam gideri hesapla (revenue hariç tüm alanlar)"""
    return (
        data["purchases"] + data["expenses"] +
        data["courier"] + data["parttime"] + data["staff"]
    )


@router.get("/bilanco", response_model=BilancoStats)
def get_bilanco_stats(db: DBSession, ctx: CurrentBranchContext):
    """
    Bilanço dashboard - Dün, Bu Hafta, Bu Ay özeti

    Performance: 6 batch queries (optimized from ~200 individual queries)
    """
    today = date.today()
    yesterday = today - timedelta(days=1)
    day_before_yesterday = today - timedelta(days=2)
    branch_id = ctx.current_branch_id

    # Tarih aralıklarını hesapla (Hafta: Pazartesi-Pazar)
    days_since_monday = today.weekday()

    if days_since_monday == 0:
        # Bugün Pazartesi - henüz tamamlanmış gün yok
        # "Bu Hafta" olarak geçen haftayı göster (Pzt-Paz biten dün)
        this_week_start = today - timedelta(days=7)  # Geçen Pazartesi
        this_week_end = yesterday  # Dün (Pazar)
        # "Geçen Hafta" = ondan önceki hafta
        last_week_start = this_week_start - timedelta(days=7)
        last_week_end = this_week_start - timedelta(days=1)
    else:
        # Normal durum: bu hafta Pazartesi'den düne kadar
        this_week_start = today - timedelta(days=days_since_monday)
        this_week_end = yesterday
        # Geçen hafta: önceki Pazartesi'den Pazar'a
        last_week_start = this_week_start - timedelta(days=7)
        last_week_end = this_week_start - timedelta(days=1)

    this_month_start = today.replace(day=1)
    _, days_in_month = monthrange(today.year, today.month)
    this_month_days_passed = max(0, (yesterday - this_month_start).days + 1)
    this_month_days_total = days_in_month

    # Geçen ay hesabı
    if today.month == 1:
        last_month_year = today.year - 1
        last_month_num = 12
    else:
        last_month_year = today.year
        last_month_num = today.month - 1

    last_month_start = date(last_month_year, last_month_num, 1)
    _, last_month_days = monthrange(last_month_year, last_month_num)
    last_month_compare_end = last_month_start + timedelta(days=min(this_month_days_passed, last_month_days) - 1) if this_month_days_passed > 0 else last_month_start

    # Tüm tarih aralığını kapsayan min/max tarihler
    min_date = min(last_week_start, last_month_start, day_before_yesterday)
    max_date = yesterday

    # BATCH QUERY: Tüm verileri tek seferde çek (6 query)
    daily_data = fetch_daily_data(db, branch_id, min_date, max_date)

    # ===== DÜN =====
    yesterday_data = daily_data.get(yesterday, {
        "revenue": Decimal("0"), "purchases": Decimal("0"),
        "expenses": Decimal("0"), "courier": Decimal("0"),
        "parttime": Decimal("0"), "staff": Decimal("0")
    })
    yesterday_revenue = yesterday_data["revenue"]
    yesterday_expenses = get_day_total_expenses(yesterday_data)
    yesterday_profit = yesterday_revenue - yesterday_expenses
    yesterday_breakdown = {
        "online": yesterday_data["revenue"],
        "mal_alimi": yesterday_data["purchases"],
        "gider": yesterday_data["expenses"],
        "staff": yesterday_data["staff"],
        "kurye": yesterday_data["courier"],
        "parttime": yesterday_data["parttime"]
    }

    prev_data = daily_data.get(day_before_yesterday, {"revenue": Decimal("0")})
    prev_revenue = prev_data["revenue"]
    if prev_revenue > 0:
        yesterday_vs_previous_pct = ((yesterday_revenue - prev_revenue) / prev_revenue) * 100
    else:
        yesterday_vs_previous_pct = Decimal("0")

    yesterday_day_name = TURKISH_DAYS[yesterday.weekday()]

    # ===== BU HAFTA =====
    this_week_daily = []
    this_week_total = Decimal("0")

    for i in range(7):
        day = this_week_start + timedelta(days=i)
        if day >= today:
            break
        day_data = daily_data.get(day, {"revenue": Decimal("0")})
        amount = day_data["revenue"]
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
    last_week_daily = []
    last_week_total = Decimal("0")

    for i in range(7):
        day = last_week_start + timedelta(days=i)
        day_data = daily_data.get(day, {"revenue": Decimal("0")})
        amount = day_data["revenue"]
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
    this_month_name = f"{TURKISH_MONTHS[today.month]} {today.year}"
    this_month_revenue = Decimal("0")
    this_month_expenses = Decimal("0")
    this_month_chart = []

    current = this_month_start
    while current < today:
        day_data = daily_data.get(current, {
            "revenue": Decimal("0"), "purchases": Decimal("0"),
            "expenses": Decimal("0"), "courier": Decimal("0"),
            "parttime": Decimal("0"), "staff": Decimal("0")
        })
        rev = day_data["revenue"]
        exp = get_day_total_expenses(day_data)
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
    last_month_revenue = Decimal("0")
    last_month_expenses = Decimal("0")

    if this_month_days_passed > 0:
        current = last_month_start
        while current <= last_month_compare_end:
            day_data = daily_data.get(current, {
                "revenue": Decimal("0"), "purchases": Decimal("0"),
                "expenses": Decimal("0"), "courier": Decimal("0"),
                "parttime": Decimal("0"), "staff": Decimal("0")
            })
            last_month_revenue += day_data["revenue"]
            last_month_expenses += get_day_total_expenses(day_data)
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
