"""
Menu Item CRUD API with branch-specific pricing

MenuItem: Product info (name, description, category, image)
MenuItemPrice: Branch-specific pricing (NULL branch_id = default price)
"""
from typing import Optional
from decimal import Decimal
from fastapi import APIRouter, HTTPException, status, Response, Query
from sqlalchemy import or_
from app.api.deps import DBSession, CurrentBranchContext
from app.models import MenuItem, MenuItemPrice, MenuCategory
from app.schemas import (
    MenuItemCreate, MenuItemUpdate, MenuItemResponse,
    MenuItemPriceSet, MenuItemPriceResponse
)

router = APIRouter(prefix="/v1/menu-items", tags=["menu-items"])


def _resolve_price(item: MenuItem, branch_id: int, db: DBSession) -> tuple[Optional[Decimal], Optional[bool]]:
    """Resolve price for a menu item in a specific branch.

    Returns (price, is_default):
    - Branch-specific price if exists -> (price, False)
    - Default price if exists -> (price, True)
    - No price -> (None, None)
    """
    # First try branch-specific price
    branch_price = (
        db.query(MenuItemPrice)
        .filter(
            MenuItemPrice.menu_item_id == item.id,
            MenuItemPrice.branch_id == branch_id
        )
        .first()
    )
    if branch_price:
        return branch_price.price, False

    # Fall back to default price (branch_id=NULL)
    default_price = (
        db.query(MenuItemPrice)
        .filter(
            MenuItemPrice.menu_item_id == item.id,
            MenuItemPrice.branch_id == None
        )
        .first()
    )
    if default_price:
        return default_price.price, True

    return None, None


def _item_to_response(item: MenuItem, branch_id: int, db: DBSession) -> dict:
    """Convert MenuItem to response dict with resolved price."""
    price, is_default = _resolve_price(item, branch_id, db)
    return {
        "id": item.id,
        "category_id": item.category_id,
        "name": item.name,
        "description": item.description,
        "image_url": item.image_url,
        "display_order": item.display_order,
        "is_active": item.is_active,
        "price": price,
        "price_is_default": is_default,
        "created_at": item.created_at
    }


@router.get("", response_model=list[MenuItemResponse])
def get_menu_items(
    db: DBSession,
    ctx: CurrentBranchContext,
    category_id: Optional[int] = Query(None, description="Filter by category ID")
):
    """
    Get menu items with resolved prices for current branch.
    Returns items from accessible categories (global + branch-specific).
    """
    # Get accessible category IDs
    accessible_categories = (
        db.query(MenuCategory.id)
        .filter(
            MenuCategory.is_active == True,
            or_(
                MenuCategory.branch_id == None,
                MenuCategory.branch_id == ctx.current_branch_id
            )
        )
    )

    query = (
        db.query(MenuItem)
        .filter(
            MenuItem.is_active == True,
            MenuItem.category_id.in_(accessible_categories)
        )
    )

    if category_id is not None:
        query = query.filter(MenuItem.category_id == category_id)

    items = query.order_by(MenuItem.display_order).all()

    return [_item_to_response(item, ctx.current_branch_id, db) for item in items]


@router.get("/{item_id}", response_model=MenuItemResponse)
def get_menu_item(
    item_id: int,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """Get a single menu item with resolved price."""
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ürün bulunamadı"
        )

    # Verify category is accessible
    category = (
        db.query(MenuCategory)
        .filter(
            MenuCategory.id == item.category_id,
            or_(
                MenuCategory.branch_id == None,
                MenuCategory.branch_id == ctx.current_branch_id
            )
        )
        .first()
    )
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ürün bulunamadı"
        )

    return _item_to_response(item, ctx.current_branch_id, db)


@router.post("", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
def create_menu_item(
    data: MenuItemCreate,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """Create a new menu item with optional default price."""
    # Verify category exists and is accessible
    category = (
        db.query(MenuCategory)
        .filter(
            MenuCategory.id == data.category_id,
            or_(
                MenuCategory.branch_id == None,
                MenuCategory.branch_id == ctx.current_branch_id
            )
        )
        .first()
    )
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kategori bulunamadı veya erişim yetkiniz yok"
        )

    # Check for duplicate name in same category
    existing = (
        db.query(MenuItem)
        .filter(
            MenuItem.name == data.name,
            MenuItem.category_id == data.category_id
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu kategoride aynı isimde ürün zaten mevcut"
        )

    item = MenuItem(
        category_id=data.category_id,
        name=data.name,
        description=data.description,
        image_url=data.image_url,
        display_order=data.display_order,
        created_by=ctx.user.id
    )
    db.add(item)
    db.flush()  # Get item.id

    # Create default price if provided
    if data.default_price is not None:
        default_price = MenuItemPrice(
            menu_item_id=item.id,
            branch_id=None,  # Default price
            price=data.default_price
        )
        db.add(default_price)

    db.commit()
    db.refresh(item)

    return _item_to_response(item, ctx.current_branch_id, db)


@router.put("/{item_id}", response_model=MenuItemResponse)
def update_menu_item(
    item_id: int,
    data: MenuItemUpdate,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """Update an existing menu item."""
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ürün bulunamadı"
        )

    # If changing category, verify new category is accessible
    if data.category_id is not None and data.category_id != item.category_id:
        category = (
            db.query(MenuCategory)
            .filter(
                MenuCategory.id == data.category_id,
                or_(
                    MenuCategory.branch_id == None,
                    MenuCategory.branch_id == ctx.current_branch_id
                )
            )
            .first()
        )
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kategori bulunamadı veya erişim yetkiniz yok"
            )

    # Check for duplicate name if name is being updated
    if data.name and data.name != item.name:
        check_category_id = data.category_id if data.category_id is not None else item.category_id
        existing = (
            db.query(MenuItem)
            .filter(
                MenuItem.name == data.name,
                MenuItem.category_id == check_category_id,
                MenuItem.id != item_id
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bu kategoride aynı isimde ürün zaten mevcut"
            )

    # Update only provided fields
    if data.category_id is not None:
        item.category_id = data.category_id
    if data.name is not None:
        item.name = data.name
    if data.description is not None:
        item.description = data.description
    if data.image_url is not None:
        item.image_url = data.image_url
    if data.display_order is not None:
        item.display_order = data.display_order
    if data.is_active is not None:
        item.is_active = data.is_active

    db.commit()
    db.refresh(item)

    return _item_to_response(item, ctx.current_branch_id, db)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(
    item_id: int,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """Delete a menu item and all its prices."""
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ürün bulunamadı"
        )

    db.delete(item)  # Cascade deletes prices
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ==================== Price Management Endpoints ====================

@router.get("/{item_id}/prices", response_model=list[MenuItemPriceResponse])
def get_menu_item_prices(
    item_id: int,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """Get all prices for a menu item (default and branch-specific)."""
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ürün bulunamadı"
        )

    return (
        db.query(MenuItemPrice)
        .filter(MenuItemPrice.menu_item_id == item_id)
        .order_by(MenuItemPrice.branch_id.nullsfirst())
        .all()
    )


@router.put("/{item_id}/prices", response_model=MenuItemPriceResponse)
def set_menu_item_price(
    item_id: int,
    data: MenuItemPriceSet,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """Set or update price for a menu item (default or branch-specific)."""
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ürün bulunamadı"
        )

    # Find existing price for this branch (or default)
    existing = (
        db.query(MenuItemPrice)
        .filter(
            MenuItemPrice.menu_item_id == item_id,
            MenuItemPrice.branch_id == data.branch_id
        )
        .first()
    )

    if existing:
        # Update existing price
        existing.price = data.price
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create new price
        price = MenuItemPrice(
            menu_item_id=item_id,
            branch_id=data.branch_id,
            price=data.price
        )
        db.add(price)
        db.commit()
        db.refresh(price)
        return price


@router.delete("/{item_id}/prices/{branch_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item_price(
    item_id: int,
    branch_id: int,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """Delete a branch-specific price override.

    Use branch_id=0 to delete the default price.
    """
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ürün bulunamadı"
        )

    # branch_id=0 means delete default price (NULL in database)
    actual_branch_id = None if branch_id == 0 else branch_id

    price = (
        db.query(MenuItemPrice)
        .filter(
            MenuItemPrice.menu_item_id == item_id,
            MenuItemPrice.branch_id == actual_branch_id
        )
        .first()
    )
    if not price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fiyat bulunamadı"
        )

    db.delete(price)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
