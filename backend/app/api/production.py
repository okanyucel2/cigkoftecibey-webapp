from datetime import date
from decimal import Decimal
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func
from app.api.deps import DBSession, CurrentBranchContext
from app.models import DailyProduction
from app.schemas import DailyProductionCreate, DailyProductionResponse, ProductionSummary

router = APIRouter(prefix="/production", tags=["production"])


@router.post("", response_model=DailyProductionResponse)
def create_production(data: DailyProductionCreate, db: DBSession, ctx: CurrentBranchContext):
    """Günlük üretim girişi"""
    # Aynı tarihte ve aynı tipte kayıt var mı kontrol et
    existing = db.query(DailyProduction).filter(
        DailyProduction.branch_id == ctx.current_branch_id,
        DailyProduction.production_date == data.production_date,
        DailyProduction.production_type == data.production_type
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"{data.production_date} tarihinde {data.production_type} tipinde zaten üretim kaydı var"
        )

    production = DailyProduction(
        branch_id=ctx.current_branch_id,
        production_date=data.production_date,
        production_type=data.production_type,
        kneaded_kg=data.kneaded_kg,
        legen_kg=data.legen_kg,
        legen_cost=data.legen_cost,
        notes=data.notes,
        created_by=ctx.user.id
    )
    db.add(production)
    db.commit()
    db.refresh(production)

    return DailyProductionResponse(
        id=production.id,
        branch_id=production.branch_id,
        production_date=production.production_date,
        production_type=production.production_type,
        kneaded_kg=production.kneaded_kg,
        legen_kg=production.legen_kg,
        legen_cost=production.legen_cost,
        legen_count=production.legen_count,
        total_cost=production.total_cost,
        notes=production.notes,
        created_by=production.created_by,
        created_at=production.created_at
    )


@router.get("", response_model=list[DailyProductionResponse])
def get_productions(
    db: DBSession,
    ctx: CurrentBranchContext,
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    month: int | None = Query(None, ge=1, le=12),
    year: int | None = Query(None, ge=2020, le=2100)
):
    """Günlük üretim listesi"""
    query = db.query(DailyProduction).filter(
        DailyProduction.branch_id == ctx.current_branch_id
    )

    if start_date:
        query = query.filter(DailyProduction.production_date >= start_date)
    if end_date:
        query = query.filter(DailyProduction.production_date <= end_date)

    # Ay/yıl filtresi
    if month and year:
        from sqlalchemy import extract
        query = query.filter(
            extract('month', DailyProduction.production_date) == month,
            extract('year', DailyProduction.production_date) == year
        )
    elif year:
        from sqlalchemy import extract
        query = query.filter(extract('year', DailyProduction.production_date) == year)

    productions = query.order_by(DailyProduction.production_date.desc()).all()

    return [
        DailyProductionResponse(
            id=p.id,
            branch_id=p.branch_id,
            production_date=p.production_date,
            production_type=p.production_type,
            kneaded_kg=p.kneaded_kg,
            legen_kg=p.legen_kg,
            legen_cost=p.legen_cost,
            legen_count=p.legen_count,
            total_cost=p.total_cost,
            notes=p.notes,
            created_by=p.created_by,
            created_at=p.created_at
        ) for p in productions
    ]


@router.get("/today", response_model=DailyProductionResponse | None)
def get_today_production(db: DBSession, ctx: CurrentBranchContext):
    """Bugünün üretimi"""
    production = db.query(DailyProduction).filter(
        DailyProduction.branch_id == ctx.current_branch_id,
        DailyProduction.production_date == date.today()
    ).first()

    if not production:
        return None

    return DailyProductionResponse(
        id=production.id,
        branch_id=production.branch_id,
        production_date=production.production_date,
        production_type=production.production_type,
        kneaded_kg=production.kneaded_kg,
        legen_kg=production.legen_kg,
        legen_cost=production.legen_cost,
        legen_count=production.legen_count,
        total_cost=production.total_cost,
        notes=production.notes,
        created_by=production.created_by,
        created_at=production.created_at
    )


@router.get("/summary", response_model=ProductionSummary)
def get_production_summary(
    db: DBSession,
    ctx: CurrentBranchContext,
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    month: int | None = Query(None, ge=1, le=12),
    year: int | None = Query(None, ge=2020, le=2100)
):
    """Dönemsel üretim özeti"""
    query = db.query(DailyProduction).filter(
        DailyProduction.branch_id == ctx.current_branch_id
    )

    if start_date:
        query = query.filter(DailyProduction.production_date >= start_date)
    if end_date:
        query = query.filter(DailyProduction.production_date <= end_date)

    if month and year:
        from sqlalchemy import extract
        query = query.filter(
            extract('month', DailyProduction.production_date) == month,
            extract('year', DailyProduction.production_date) == year
        )
    elif year:
        from sqlalchemy import extract
        query = query.filter(extract('year', DailyProduction.production_date) == year)

    productions = query.all()

    if not productions:
        return ProductionSummary(
            total_kneaded_kg=Decimal("0"),
            total_legen_count=Decimal("0"),
            total_cost=Decimal("0"),
            avg_daily_kg=Decimal("0"),
            days_count=0
        )

    total_kg = sum(p.kneaded_kg for p in productions)
    total_legen = sum(p.legen_count for p in productions)
    total_cost = sum(p.total_cost for p in productions)
    days = len(productions)

    return ProductionSummary(
        total_kneaded_kg=total_kg,
        total_legen_count=total_legen,
        total_cost=total_cost,
        avg_daily_kg=total_kg / days if days > 0 else Decimal("0"),
        days_count=days
    )


@router.put("/{production_id}", response_model=DailyProductionResponse)
def update_production(
    production_id: int,
    data: DailyProductionCreate,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """Üretim kaydını güncelle"""
    production = db.query(DailyProduction).filter(
        DailyProduction.id == production_id,
        DailyProduction.branch_id == ctx.current_branch_id
    ).first()

    if not production:
        raise HTTPException(status_code=404, detail="Üretim kaydı bulunamadı")

    production.production_date = data.production_date
    production.production_type = data.production_type
    production.kneaded_kg = data.kneaded_kg
    production.legen_kg = data.legen_kg
    production.legen_cost = data.legen_cost
    production.notes = data.notes

    db.commit()
    db.refresh(production)

    return DailyProductionResponse(
        id=production.id,
        branch_id=production.branch_id,
        production_date=production.production_date,
        production_type=production.production_type,
        kneaded_kg=production.kneaded_kg,
        legen_kg=production.legen_kg,
        legen_cost=production.legen_cost,
        legen_count=production.legen_count,
        total_cost=production.total_cost,
        notes=production.notes,
        created_by=production.created_by,
        created_at=production.created_at
    )


@router.delete("/{production_id}")
def delete_production(production_id: int, db: DBSession, ctx: CurrentBranchContext):
    """Üretim kaydını sil"""
    production = db.query(DailyProduction).filter(
        DailyProduction.id == production_id,
        DailyProduction.branch_id == ctx.current_branch_id
    ).first()

    if not production:
        raise HTTPException(status_code=404, detail="Üretim kaydı bulunamadı")

    db.delete(production)
    db.commit()

    return {"message": "Üretim kaydı silindi"}
