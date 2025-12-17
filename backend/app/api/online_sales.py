from datetime import date
from decimal import Decimal
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, and_
from app.api.deps import DBSession, CurrentBranchContext
from app.models import OnlinePlatform, OnlineSale
from app.schemas import (
    OnlinePlatformCreate, OnlinePlatformUpdate, OnlinePlatformResponse,
    OnlineSaleCreate, OnlineSaleResponse,
    DailySalesCreate, DailySalesResponse,
    OnlineSalesSummary
)

router = APIRouter(prefix="/online-sales", tags=["online-sales"])


# ==================== CHANNELS / PLATFORMS ====================

@router.get("/channels")
def get_channels_grouped(db: DBSession, ctx: CurrentBranchContext):
    """
    Satış kanallarını tip bazında gruplandırılmış şekilde döndür.
    Frontend'de birleşik satış girişi için kullanılır.
    """
    platforms = db.query(OnlinePlatform).filter(
        OnlinePlatform.is_active == True
    ).order_by(OnlinePlatform.display_order).all()

    pos_channels = []
    online_channels = []

    for p in platforms:
        channel_data = {
            "id": p.id,
            "name": p.name,
            "channel_type": p.channel_type,
            "is_system": p.is_system,
            "display_order": p.display_order
        }
        if p.channel_type in ('pos_salon', 'pos_telefon'):
            pos_channels.append(channel_data)
        else:
            online_channels.append(channel_data)

    return {
        "pos": pos_channels,
        "online": online_channels
    }


@router.get("/platforms", response_model=list[OnlinePlatformResponse])
def get_platforms(db: DBSession, ctx: CurrentBranchContext):
    """Tüm satış kanallarını listele (POS + Online)"""
    return db.query(OnlinePlatform).filter(
        OnlinePlatform.is_active == True
    ).order_by(OnlinePlatform.display_order).all()


@router.post("/platforms", response_model=OnlinePlatformResponse)
def create_platform(data: OnlinePlatformCreate, db: DBSession, ctx: CurrentBranchContext):
    """Yeni platform ekle"""
    platform = OnlinePlatform(**data.model_dump())
    db.add(platform)
    db.commit()
    db.refresh(platform)
    return platform


@router.put("/platforms/{platform_id}", response_model=OnlinePlatformResponse)
def update_platform(
    platform_id: int,
    data: OnlinePlatformUpdate,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """Platform güncelle"""
    platform = db.query(OnlinePlatform).filter(OnlinePlatform.id == platform_id).first()
    if not platform:
        raise HTTPException(status_code=404, detail="Platform bulunamadi")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(platform, field, value)

    db.commit()
    db.refresh(platform)
    return platform


@router.delete("/platforms/{platform_id}")
def delete_platform(platform_id: int, db: DBSession, ctx: CurrentBranchContext):
    """Platform sil (sistem kanalları ve kayıt varsa silinemez)"""
    platform = db.query(OnlinePlatform).filter(OnlinePlatform.id == platform_id).first()
    if not platform:
        raise HTTPException(status_code=404, detail="Platform bulunamadi")

    # Sistem kanalları silinemez (Salon, Telefon Paket)
    if platform.is_system:
        raise HTTPException(
            status_code=400,
            detail="Sistem kanallari silinemez (Salon, Telefon Paket)"
        )

    # Bu platforma ait satış var mı kontrol et
    sale_count = db.query(OnlineSale).filter(OnlineSale.platform_id == platform_id).count()
    if sale_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Bu platformda {sale_count} satis kaydi var. Once satislari silin."
        )

    db.delete(platform)
    db.commit()
    return {"message": "Platform silindi"}


# ==================== SALES ====================

@router.get("/today")
def get_today_sales(db: DBSession, ctx: CurrentBranchContext):
    """
    Bugünün tüm kanal satışlarını getir - birleşik giriş sayfası için.
    Her kanal için mevcut değeri döndürür.
    """
    today = date.today()
    branch_id = ctx.current_branch_id

    # Tüm aktif kanalları al
    platforms = db.query(OnlinePlatform).filter(
        OnlinePlatform.is_active == True
    ).order_by(OnlinePlatform.display_order).all()

    # Bugünün satışlarını al
    sales = db.query(OnlineSale).filter(
        OnlineSale.branch_id == branch_id,
        OnlineSale.sale_date == today
    ).all()

    # Platform ID -> Sale eşleştirmesi
    sales_by_platform = {s.platform_id: s for s in sales}

    # Her kanal için değer döndür
    entries = []
    for p in platforms:
        sale = sales_by_platform.get(p.id)
        entries.append({
            "platform_id": p.id,
            "platform_name": p.name,
            "channel_type": p.channel_type,
            "is_system": p.is_system,
            "amount": float(sale.amount) if sale else 0,
            "sale_id": sale.id if sale else None
        })

    total = sum(e["amount"] for e in entries)

    return {
        "sale_date": today.isoformat(),
        "entries": entries,
        "total": total
    }


@router.get("", response_model=list[OnlineSaleResponse])
def get_sales(
    db: DBSession,
    ctx: CurrentBranchContext,
    start_date: date | None = None,
    end_date: date | None = None,
    platform_id: int | None = None,
    limit: int = Query(default=100, le=500)
):
    """Online satışları listele"""
    query = db.query(OnlineSale).filter(OnlineSale.branch_id == ctx.current_branch_id)

    if start_date:
        query = query.filter(OnlineSale.sale_date >= start_date)
    if end_date:
        query = query.filter(OnlineSale.sale_date <= end_date)
    if platform_id:
        query = query.filter(OnlineSale.platform_id == platform_id)

    return query.order_by(OnlineSale.sale_date.desc()).limit(limit).all()


@router.get("/daily/{sale_date}", response_model=DailySalesResponse)
def get_daily_sales(sale_date: date, db: DBSession, ctx: CurrentBranchContext):
    """Belirli bir günün tüm platform satışlarını getir"""
    sales = db.query(OnlineSale).filter(
        OnlineSale.branch_id == ctx.current_branch_id,
        OnlineSale.sale_date == sale_date
    ).all()

    total = sum(s.amount for s in sales)
    return DailySalesResponse(sale_date=sale_date, entries=sales, total=total)


@router.post("/daily", response_model=DailySalesResponse)
def create_or_update_daily_sales(
    data: DailySalesCreate,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """
    Günlük satışları toplu kaydet/güncelle.
    Aynı tarih ve platform için kayıt varsa günceller, yoksa yeni oluşturur.
    """
    result_entries = []

    for entry in data.entries:
        if entry.amount <= 0:
            continue  # Boş veya negatif tutarları atla

        # Aynı gün ve platform için kayıt var mı?
        existing = db.query(OnlineSale).filter(
            OnlineSale.branch_id == ctx.current_branch_id,
            OnlineSale.sale_date == data.sale_date,
            OnlineSale.platform_id == entry.platform_id
        ).first()

        if existing:
            # Güncelle
            existing.amount = entry.amount
            existing.notes = data.notes
            db.commit()
            db.refresh(existing)
            result_entries.append(existing)
        else:
            # Yeni kayıt
            sale = OnlineSale(
                branch_id=ctx.current_branch_id,
                platform_id=entry.platform_id,
                sale_date=data.sale_date,
                amount=entry.amount,
                notes=data.notes,
                created_by=ctx.user.id
            )
            db.add(sale)
            db.commit()
            db.refresh(sale)
            result_entries.append(sale)

    total = sum(e.amount for e in result_entries)
    return DailySalesResponse(sale_date=data.sale_date, entries=result_entries, total=total)


@router.delete("/{sale_id}")
def delete_sale(sale_id: int, db: DBSession, ctx: CurrentBranchContext):
    """Tek bir satış kaydını sil"""
    sale = db.query(OnlineSale).filter(
        OnlineSale.id == sale_id,
        OnlineSale.branch_id == ctx.current_branch_id
    ).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Satis kaydi bulunamadi")

    db.delete(sale)
    db.commit()
    return {"message": "Satis silindi"}


@router.delete("/daily/{sale_date}")
def delete_daily_sales(sale_date: date, db: DBSession, ctx: CurrentBranchContext):
    """Bir günün tüm satışlarını sil"""
    deleted = db.query(OnlineSale).filter(
        OnlineSale.branch_id == ctx.current_branch_id,
        OnlineSale.sale_date == sale_date
    ).delete()
    db.commit()
    return {"message": f"{deleted} satis kaydi silindi"}


# ==================== SUMMARY ====================

@router.get("/summary", response_model=OnlineSalesSummary)
def get_sales_summary(
    db: DBSession,
    ctx: CurrentBranchContext,
    month: int | None = None,
    year: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None
):
    """Aylık veya dönemsel online satış özeti"""
    query = db.query(OnlineSale).filter(OnlineSale.branch_id == ctx.current_branch_id)

    # Tarih filtresi
    if start_date and end_date:
        query = query.filter(
            OnlineSale.sale_date >= start_date,
            OnlineSale.sale_date <= end_date
        )
    elif month and year:
        from calendar import monthrange
        start = date(year, month, 1)
        end = date(year, month, monthrange(year, month)[1])
        query = query.filter(
            OnlineSale.sale_date >= start,
            OnlineSale.sale_date <= end
        )

    sales = query.all()

    # Platform bazlı toplamlar
    platform_totals: dict[str, Decimal] = {}
    for sale in sales:
        platform_name = sale.platform.name if sale.platform else "Bilinmeyen"
        if platform_name not in platform_totals:
            platform_totals[platform_name] = Decimal("0")
        platform_totals[platform_name] += sale.amount

    # Benzersiz gün sayısı
    unique_dates = set(s.sale_date for s in sales)

    return OnlineSalesSummary(
        total_amount=sum(s.amount for s in sales),
        platform_totals=platform_totals,
        days_count=len(unique_dates)
    )
