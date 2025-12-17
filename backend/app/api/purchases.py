from datetime import date
from decimal import Decimal
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func
from app.api.deps import DBSession, CurrentBranchContext
from app.models import Purchase, PurchaseItem, Supplier, PurchaseProductGroup, PurchaseProduct
from app.schemas import (
    PurchaseCreate, PurchaseResponse,
    SupplierCreate, SupplierResponse,
    PurchaseProductGroupResponse, PurchaseProductGroupCreate,
    PurchaseProductResponse, PurchaseProductCreate
)

router = APIRouter(prefix="/purchases", tags=["purchases"])


# Suppliers
@router.get("/suppliers", response_model=list[SupplierResponse])
def get_suppliers(db: DBSession, ctx: CurrentBranchContext):
    return db.query(Supplier).filter(
        Supplier.branch_id == ctx.current_branch_id,
        Supplier.is_active == True
    ).all()


@router.post("/suppliers", response_model=SupplierResponse)
def create_supplier(data: SupplierCreate, db: DBSession, ctx: CurrentBranchContext):
    supplier = Supplier(
        branch_id=ctx.current_branch_id,
        **data.model_dump()
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.put("/suppliers/{supplier_id}", response_model=SupplierResponse)
def update_supplier(supplier_id: int, data: SupplierCreate, db: DBSession, ctx: CurrentBranchContext):
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id,
        Supplier.branch_id == ctx.current_branch_id
    ).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Tedarikci bulunamadi")

    supplier.name = data.name
    supplier.phone = data.phone
    db.commit()
    db.refresh(supplier)
    return supplier


@router.delete("/suppliers/{supplier_id}")
def delete_supplier(supplier_id: int, db: DBSession, ctx: CurrentBranchContext):
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id,
        Supplier.branch_id == ctx.current_branch_id
    ).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Tedarikci bulunamadi")

    # Alim kaydi var mi kontrol et
    has_purchases = db.query(Purchase).filter(Purchase.supplier_id == supplier_id).first()
    if has_purchases:
        # Silme yerine pasif yap
        supplier.is_active = False
        db.commit()
        return {"message": "Tedarikci pasif yapildi (alim kaydi mevcut)"}

    db.delete(supplier)
    db.commit()
    return {"message": "Tedarikci silindi"}


# Product Groups & Products
@router.get("/product-groups", response_model=list[PurchaseProductGroupResponse])
def get_product_groups(db: DBSession, ctx: CurrentBranchContext):
    """Ürün gruplarını ürünleriyle birlikte getir"""
    return db.query(PurchaseProductGroup).filter(
        PurchaseProductGroup.is_active == True
    ).order_by(PurchaseProductGroup.display_order).all()


@router.post("/product-groups", response_model=PurchaseProductGroupResponse)
def create_product_group(data: PurchaseProductGroupCreate, db: DBSession, ctx: CurrentBranchContext):
    group = PurchaseProductGroup(**data.model_dump())
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


@router.put("/product-groups/{group_id}", response_model=PurchaseProductGroupResponse)
def update_product_group(group_id: int, data: PurchaseProductGroupCreate, db: DBSession, ctx: CurrentBranchContext):
    group = db.query(PurchaseProductGroup).filter(PurchaseProductGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Grup bulunamadi")
    group.name = data.name
    group.display_order = data.display_order
    db.commit()
    db.refresh(group)
    return group


@router.delete("/product-groups/{group_id}")
def delete_product_group(group_id: int, db: DBSession, ctx: CurrentBranchContext):
    group = db.query(PurchaseProductGroup).filter(PurchaseProductGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Grup bulunamadi")
    # Ürünü varsa pasif yap
    has_products = db.query(PurchaseProduct).filter(PurchaseProduct.group_id == group_id).first()
    if has_products:
        group.is_active = False
        db.commit()
        return {"message": "Grup pasif yapildi (urun mevcut)"}
    db.delete(group)
    db.commit()
    return {"message": "Grup silindi"}


@router.post("/products", response_model=PurchaseProductResponse)
def create_product(data: PurchaseProductCreate, db: DBSession, ctx: CurrentBranchContext):
    product = PurchaseProduct(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/products/{product_id}", response_model=PurchaseProductResponse)
def update_product(product_id: int, data: PurchaseProductCreate, db: DBSession, ctx: CurrentBranchContext):
    product = db.query(PurchaseProduct).filter(PurchaseProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Urun bulunamadi")
    product.name = data.name
    product.group_id = data.group_id
    product.default_unit = data.default_unit
    product.display_order = data.display_order
    db.commit()
    db.refresh(product)
    return product


@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: DBSession, ctx: CurrentBranchContext):
    product = db.query(PurchaseProduct).filter(PurchaseProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Urun bulunamadi")
    # Alımda kullanıldıysa pasif yap
    has_items = db.query(PurchaseItem).filter(PurchaseItem.product_id == product_id).first()
    if has_items:
        product.is_active = False
        db.commit()
        return {"message": "Urun pasif yapildi (alim kaydi mevcut)"}
    db.delete(product)
    db.commit()
    return {"message": "Urun silindi"}


# Purchases
@router.post("", response_model=PurchaseResponse)
def create_purchase(data: PurchaseCreate, db: DBSession, ctx: CurrentBranchContext):
    # Tedarikciyi kontrol et
    supplier = db.query(Supplier).filter(
        Supplier.id == data.supplier_id,
        Supplier.branch_id == ctx.current_branch_id
    ).first()
    if not supplier:
        raise HTTPException(status_code=400, detail="Tedarikci bulunamadi")

    # Toplam hesapla
    total = Decimal("0")
    items_data = []

    for item in data.items:
        item_total = item.quantity * item.unit_price
        total += item_total
        items_data.append({
            "product_id": item.product_id,
            "description": item.description,
            "quantity": item.quantity,
            "unit": item.unit,
            "unit_price": item.unit_price,
            "total": item_total
        })

    # Alimi olustur
    purchase = Purchase(
        branch_id=ctx.current_branch_id,
        supplier_id=data.supplier_id,
        purchase_date=data.purchase_date,
        total=total,
        notes=data.notes,
        created_by=ctx.user.id
    )
    db.add(purchase)
    db.flush()

    # Alim kalemlerini ekle
    for item_data in items_data:
        item = PurchaseItem(purchase_id=purchase.id, **item_data)
        db.add(item)

    db.commit()
    db.refresh(purchase)
    return purchase


@router.get("", response_model=list[PurchaseResponse])
def get_purchases(
    db: DBSession,
    ctx: CurrentBranchContext,
    start_date: date | None = None,
    end_date: date | None = None,
    supplier_id: int | None = None,
    limit: int = Query(default=50, le=200)
):
    query = db.query(Purchase).filter(Purchase.branch_id == ctx.current_branch_id)

    if start_date:
        query = query.filter(Purchase.purchase_date >= start_date)
    if end_date:
        query = query.filter(Purchase.purchase_date <= end_date)
    if supplier_id:
        query = query.filter(Purchase.supplier_id == supplier_id)

    return query.order_by(Purchase.purchase_date.desc()).limit(limit).all()


@router.get("/today", response_model=list[PurchaseResponse])
def get_today_purchases(db: DBSession, ctx: CurrentBranchContext):
    today = date.today()
    return db.query(Purchase).filter(
        Purchase.branch_id == ctx.current_branch_id,
        Purchase.purchase_date == today
    ).order_by(Purchase.created_at.desc()).all()


@router.get("/{purchase_id}", response_model=PurchaseResponse)
def get_purchase(purchase_id: int, db: DBSession, ctx: CurrentBranchContext):
    purchase = db.query(Purchase).filter(
        Purchase.id == purchase_id,
        Purchase.branch_id == ctx.current_branch_id
    ).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Alim bulunamadi")
    return purchase


@router.put("/{purchase_id}", response_model=PurchaseResponse)
def update_purchase(purchase_id: int, data: PurchaseCreate, db: DBSession, ctx: CurrentBranchContext):
    """Mal alımını güncelle"""
    purchase = db.query(Purchase).filter(
        Purchase.id == purchase_id,
        Purchase.branch_id == ctx.current_branch_id
    ).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Alim bulunamadi")

    # Tedarikciyi kontrol et
    supplier = db.query(Supplier).filter(
        Supplier.id == data.supplier_id,
        Supplier.branch_id == ctx.current_branch_id
    ).first()
    if not supplier:
        raise HTTPException(status_code=400, detail="Tedarikci bulunamadi")

    # Mevcut kalemleri sil
    db.query(PurchaseItem).filter(PurchaseItem.purchase_id == purchase_id).delete()

    # Yeni toplam ve kalemler
    total = Decimal("0")
    for item in data.items:
        item_total = item.quantity * item.unit_price
        total += item_total
        purchase_item = PurchaseItem(
            purchase_id=purchase_id,
            product_id=item.product_id,
            description=item.description,
            quantity=item.quantity,
            unit=item.unit,
            unit_price=item.unit_price,
            total=item_total
        )
        db.add(purchase_item)

    # Alımı güncelle
    purchase.supplier_id = data.supplier_id
    purchase.purchase_date = data.purchase_date
    purchase.notes = data.notes
    purchase.total = total

    db.commit()
    db.refresh(purchase)
    return purchase


@router.delete("/{purchase_id}")
def delete_purchase(purchase_id: int, db: DBSession, ctx: CurrentBranchContext):
    """Mal alımını sil"""
    purchase = db.query(Purchase).filter(
        Purchase.id == purchase_id,
        Purchase.branch_id == ctx.current_branch_id
    ).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Alim bulunamadi")

    # Önce kalemleri sil
    db.query(PurchaseItem).filter(PurchaseItem.purchase_id == purchase_id).delete()

    # Sonra alımı sil
    db.delete(purchase)
    db.commit()

    return {"message": "Alim silindi"}
