from datetime import date
from decimal import Decimal
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.orm import joinedload
from app.api.deps import DBSession, CurrentBranchContext
from app.models import Employee, MonthlyPayroll, PartTimeCost
from app.schemas import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse,
    MonthlyPayrollCreate, MonthlyPayrollUpdate, MonthlyPayrollResponse, PayrollSummary,
    PartTimeCostCreate, PartTimeCostUpdate, PartTimeCostResponse, PartTimeCostSummary
)

router = APIRouter(prefix="/personnel", tags=["personnel"])


# ==================== EMPLOYEES ====================

@router.get("/employees", response_model=list[EmployeeResponse])
def get_employees(
    db: DBSession,
    ctx: CurrentBranchContext,
    include_inactive: bool = False
):
    """Tum personeli getir"""
    query = db.query(Employee).filter(Employee.branch_id == ctx.current_branch_id)
    if not include_inactive:
        query = query.filter(Employee.is_active == True)
    return query.order_by(Employee.name).all()


@router.post("/employees", response_model=EmployeeResponse)
def create_employee(data: EmployeeCreate, db: DBSession, ctx: CurrentBranchContext):
    """Yeni personel olustur"""
    employee = Employee(
        branch_id=ctx.current_branch_id,
        name=data.name,
        base_salary=data.base_salary,
        has_sgk=data.has_sgk,
        sgk_amount=data.sgk_amount,
        daily_rate=data.daily_rate,
        hourly_rate=data.hourly_rate,
        payment_type=data.payment_type,
        is_part_time=data.is_part_time
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


@router.get("/employees/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: int, db: DBSession, ctx: CurrentBranchContext):
    """Tekil personel getir"""
    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.branch_id == ctx.current_branch_id
    ).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Personel bulunamadi")
    return employee


@router.put("/employees/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    data: EmployeeUpdate,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """Personel guncelle"""
    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.branch_id == ctx.current_branch_id
    ).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Personel bulunamadi")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(employee, field, value)

    db.commit()
    db.refresh(employee)
    return employee


@router.delete("/employees/{employee_id}")
def delete_employee(employee_id: int, db: DBSession, ctx: CurrentBranchContext):
    """Personeli pasif yap (soft delete)"""
    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.branch_id == ctx.current_branch_id
    ).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Personel bulunamadi")

    employee.is_active = False
    db.commit()
    return {"message": "Personel pasif yapildi"}


# ==================== MONTHLY PAYROLL ====================

@router.get("/payroll", response_model=list[MonthlyPayrollResponse])
def get_payrolls(
    db: DBSession,
    ctx: CurrentBranchContext,
    year: int | None = None,
    month: int | None = Query(default=None, ge=1, le=12),
    employee_id: int | None = None
):
    """Maas bordrolarina getir"""
    query = db.query(MonthlyPayroll).filter(
        MonthlyPayroll.branch_id == ctx.current_branch_id
    ).options(joinedload(MonthlyPayroll.employee))

    if year:
        query = query.filter(MonthlyPayroll.year == year)
    if month:
        query = query.filter(MonthlyPayroll.month == month)
    if employee_id:
        query = query.filter(MonthlyPayroll.employee_id == employee_id)

    return query.order_by(
        MonthlyPayroll.payment_date.desc(),
        MonthlyPayroll.employee_id
    ).all()


@router.post("/payroll", response_model=MonthlyPayrollResponse)
def create_payroll(data: MonthlyPayrollCreate, db: DBSession, ctx: CurrentBranchContext):
    """Yeni maas bordrosu olustur - haftalik odemeler icin ayni personele birden fazla kayit olabilir"""
    # Personeli kontrol et
    employee = db.query(Employee).filter(
        Employee.id == data.employee_id,
        Employee.branch_id == ctx.current_branch_id
    ).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Personel bulunamadi")

    # Ayni tarih + ayni tip icin ayni personele kayit var mi kontrol et (duplicate onleme)
    # Farkli tipler ayni tarihte girilebilir (ornegin maas + avans)
    existing = db.query(MonthlyPayroll).filter(
        MonthlyPayroll.branch_id == ctx.current_branch_id,
        MonthlyPayroll.employee_id == data.employee_id,
        MonthlyPayroll.payment_date == data.payment_date,
        MonthlyPayroll.record_type == data.record_type
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu personel icin bu tarihte ayni tipte zaten kayit var")

    payroll = MonthlyPayroll(
        branch_id=ctx.current_branch_id,
        employee_id=data.employee_id,
        year=data.year,
        month=data.month,
        payment_date=data.payment_date,
        record_type=data.record_type,
        base_salary=data.base_salary,
        sgk_amount=data.sgk_amount,
        bonus=data.bonus,
        premium=data.premium,
        overtime_hours=data.overtime_hours,
        overtime_amount=data.overtime_amount,
        advance=data.advance,
        absence_days=data.absence_days,
        absence_deduction=data.absence_deduction,
        notes=data.notes,
        created_by=ctx.user.id
    )
    db.add(payroll)
    db.commit()
    db.refresh(payroll)
    return payroll


@router.get("/payroll/summary", response_model=PayrollSummary)
def get_payroll_summary(
    db: DBSession,
    ctx: CurrentBranchContext,
    year: int,
    month: int = Query(ge=1, le=12),
    employee_id: int | None = None
):
    """Aylik maas ozeti"""
    query = db.query(MonthlyPayroll).filter(
        MonthlyPayroll.branch_id == ctx.current_branch_id,
        MonthlyPayroll.year == year,
        MonthlyPayroll.month == month
    )
    if employee_id:
        query = query.filter(MonthlyPayroll.employee_id == employee_id)
    payrolls = query.all()

    if not payrolls:
        return PayrollSummary(
            total_base_salary=Decimal("0"),
            total_sgk=Decimal("0"),
            total_bonus=Decimal("0"),
            total_premium=Decimal("0"),
            total_overtime=Decimal("0"),
            total_advance=Decimal("0"),
            total_deduction=Decimal("0"),
            total_payroll=Decimal("0"),
            employee_count=0
        )

    return PayrollSummary(
        total_base_salary=sum(p.base_salary for p in payrolls),
        total_sgk=sum(p.sgk_amount for p in payrolls),
        total_bonus=sum(p.bonus for p in payrolls),
        total_premium=sum(p.premium for p in payrolls),
        total_overtime=sum(p.overtime_amount for p in payrolls),
        total_advance=sum(p.advance for p in payrolls),
        total_deduction=sum(p.absence_deduction for p in payrolls),
        total_payroll=sum(p.total for p in payrolls),
        employee_count=len(payrolls)
    )


@router.get("/payroll/{payroll_id}", response_model=MonthlyPayrollResponse)
def get_payroll(payroll_id: int, db: DBSession, ctx: CurrentBranchContext):
    """Tekil bordro getir"""
    payroll = db.query(MonthlyPayroll).filter(
        MonthlyPayroll.id == payroll_id,
        MonthlyPayroll.branch_id == ctx.current_branch_id
    ).options(joinedload(MonthlyPayroll.employee)).first()
    if not payroll:
        raise HTTPException(status_code=404, detail="Bordro bulunamadi")
    return payroll


@router.put("/payroll/{payroll_id}", response_model=MonthlyPayrollResponse)
def update_payroll(
    payroll_id: int,
    data: MonthlyPayrollUpdate,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """Bordro guncelle"""
    payroll = db.query(MonthlyPayroll).filter(
        MonthlyPayroll.id == payroll_id,
        MonthlyPayroll.branch_id == ctx.current_branch_id
    ).first()
    if not payroll:
        raise HTTPException(status_code=404, detail="Bordro bulunamadi")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(payroll, field, value)

    db.commit()
    db.refresh(payroll)
    return payroll


@router.delete("/payroll/{payroll_id}")
def delete_payroll(payroll_id: int, db: DBSession, ctx: CurrentBranchContext):
    """Bordro sil"""
    payroll = db.query(MonthlyPayroll).filter(
        MonthlyPayroll.id == payroll_id,
        MonthlyPayroll.branch_id == ctx.current_branch_id
    ).first()
    if not payroll:
        raise HTTPException(status_code=404, detail="Bordro bulunamadi")

    db.delete(payroll)
    db.commit()
    return {"message": "Bordro silindi"}


# ==================== PART-TIME COSTS ====================

@router.get("/part-time", response_model=list[PartTimeCostResponse])
def get_part_time_costs(
    db: DBSession,
    ctx: CurrentBranchContext,
    month: int | None = Query(default=None, ge=1, le=12),
    year: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = Query(default=50, le=200)
):
    """Part-time personel giderlerini getir"""
    query = db.query(PartTimeCost).filter(PartTimeCost.branch_id == ctx.current_branch_id)

    # Ay/yil filtresi
    if month and year:
        from calendar import monthrange
        first_day = date(year, month, 1)
        last_day = date(year, month, monthrange(year, month)[1])
        query = query.filter(
            PartTimeCost.cost_date >= first_day,
            PartTimeCost.cost_date <= last_day
        )
    else:
        if start_date:
            query = query.filter(PartTimeCost.cost_date >= start_date)
        if end_date:
            query = query.filter(PartTimeCost.cost_date <= end_date)

    return query.order_by(PartTimeCost.cost_date.desc()).limit(limit).all()


@router.post("/part-time", response_model=PartTimeCostResponse)
def create_part_time_cost(data: PartTimeCostCreate, db: DBSession, ctx: CurrentBranchContext):
    """Yeni part-time gideri olustur"""
    # Ayni tarihte kayit var mi kontrol et
    existing = db.query(PartTimeCost).filter(
        PartTimeCost.branch_id == ctx.current_branch_id,
        PartTimeCost.cost_date == data.cost_date
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu tarihte zaten kayit var")

    cost = PartTimeCost(
        branch_id=ctx.current_branch_id,
        cost_date=data.cost_date,
        amount=data.amount,
        notes=data.notes,
        created_by=ctx.user.id
    )
    db.add(cost)
    db.commit()
    db.refresh(cost)
    return cost


@router.get("/part-time/summary", response_model=PartTimeCostSummary)
def get_part_time_summary(
    db: DBSession,
    ctx: CurrentBranchContext,
    month: int | None = Query(default=None, ge=1, le=12),
    year: int | None = None
):
    """Part-time gider ozeti"""
    query = db.query(PartTimeCost).filter(PartTimeCost.branch_id == ctx.current_branch_id)

    if month and year:
        from calendar import monthrange
        first_day = date(year, month, 1)
        last_day = date(year, month, monthrange(year, month)[1])
        query = query.filter(
            PartTimeCost.cost_date >= first_day,
            PartTimeCost.cost_date <= last_day
        )

    costs = query.all()

    if not costs:
        return PartTimeCostSummary(
            total_cost=Decimal("0"),
            days_count=0,
            avg_daily_cost=Decimal("0")
        )

    total_cost = sum(c.amount for c in costs)
    return PartTimeCostSummary(
        total_cost=total_cost,
        days_count=len(costs),
        avg_daily_cost=total_cost / len(costs)
    )


@router.get("/part-time/{cost_id}", response_model=PartTimeCostResponse)
def get_part_time_cost(cost_id: int, db: DBSession, ctx: CurrentBranchContext):
    """Tekil part-time gideri getir"""
    cost = db.query(PartTimeCost).filter(
        PartTimeCost.id == cost_id,
        PartTimeCost.branch_id == ctx.current_branch_id
    ).first()
    if not cost:
        raise HTTPException(status_code=404, detail="Kayit bulunamadi")
    return cost


@router.put("/part-time/{cost_id}", response_model=PartTimeCostResponse)
def update_part_time_cost(
    cost_id: int,
    data: PartTimeCostUpdate,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """Part-time gideri guncelle"""
    cost = db.query(PartTimeCost).filter(
        PartTimeCost.id == cost_id,
        PartTimeCost.branch_id == ctx.current_branch_id
    ).first()
    if not cost:
        raise HTTPException(status_code=404, detail="Kayit bulunamadi")

    # Tarih degistiyse kontrol et
    if data.cost_date and data.cost_date != cost.cost_date:
        existing = db.query(PartTimeCost).filter(
            PartTimeCost.branch_id == ctx.current_branch_id,
            PartTimeCost.cost_date == data.cost_date,
            PartTimeCost.id != cost_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Bu tarihte zaten kayit var")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cost, field, value)

    db.commit()
    db.refresh(cost)
    return cost


@router.delete("/part-time/{cost_id}")
def delete_part_time_cost(cost_id: int, db: DBSession, ctx: CurrentBranchContext):
    """Part-time gideri sil"""
    cost = db.query(PartTimeCost).filter(
        PartTimeCost.id == cost_id,
        PartTimeCost.branch_id == ctx.current_branch_id
    ).first()
    if not cost:
        raise HTTPException(status_code=404, detail="Kayit bulunamadi")

    db.delete(cost)
    db.commit()
    return {"message": "Kayit silindi"}
