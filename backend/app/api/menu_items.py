"""
Menu Item CRUD API

Hybrid tenant isolation:
- branch_id=NULL: Global items (visible to all branches)
- branch_id=X: Branch-specific items (visible only to that branch)
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Response, Query
from sqlalchemy import or_
from app.api.deps import DBSession, CurrentBranchContext
from app.models import MenuItem, MenuCategory
from app.schemas import MenuItemCreate, MenuItemUpdate, MenuItemResponse

router = APIRouter(prefix="/v1/menu-items", tags=["menu-items"])


@router.get("", response_model=list[MenuItemResponse])
def get_menu_items(
    db: DBSession,
    ctx: CurrentBranchContext,
    category_id: Optional[int] = Query(None, description="Filter by category ID")
):
    """
    Get menu items for current branch.
    Returns global (branch_id=NULL) + branch-specific items.
    Optionally filter by category_id.
    """
    query = (
        db.query(MenuItem)
        .filter(
            MenuItem.is_active == True,
            or_(
                MenuItem.branch_id == None,  # Global
                MenuItem.branch_id == ctx.current_branch_id
            )
        )
    )

    if category_id is not None:
        query = query.filter(MenuItem.category_id == category_id)

    return query.order_by(MenuItem.display_order).all()


@router.get("/{item_id}", response_model=MenuItemResponse)
def get_menu_item(
    item_id: int,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """
    Get a single menu item by ID.
    Only accessible items (global or current branch) can be retrieved.
    """
    item = (
        db.query(MenuItem)
        .filter(
            MenuItem.id == item_id,
            or_(
                MenuItem.branch_id == None,
                MenuItem.branch_id == ctx.current_branch_id
            )
        )
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ürün bulunamadı"
        )
    return item


@router.post("", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
def create_menu_item(
    data: MenuItemCreate,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """
    Create a new menu item.
    is_global=True creates global item (branch_id=NULL).
    is_global=False creates branch-specific item.
    """
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kategori bulunamadı veya erişim yetkiniz yok"
        )

    # Determine branch_id
    branch_id = None if data.is_global else ctx.current_branch_id

    # Check for duplicate name in same category and scope
    existing = (
        db.query(MenuItem)
        .filter(
            MenuItem.name == data.name,
            MenuItem.category_id == data.category_id,
            MenuItem.branch_id == branch_id
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
        price=data.price,
        display_order=data.display_order,
        is_available=data.is_available,
        branch_id=branch_id,
        created_by=ctx.user.id
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=MenuItemResponse)
def update_menu_item(
    item_id: int,
    data: MenuItemUpdate,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """
    Update an existing menu item.
    Only items accessible to current branch can be updated.
    """
    # Find item with tenant isolation
    item = (
        db.query(MenuItem)
        .filter(
            MenuItem.id == item_id,
            or_(
                MenuItem.branch_id == None,
                MenuItem.branch_id == ctx.current_branch_id
            )
        )
        .first()
    )
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
                status_code=status.HTTP_404_NOT_FOUND,
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
                MenuItem.branch_id == item.branch_id,
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
    if data.price is not None:
        item.price = data.price
    if data.display_order is not None:
        item.display_order = data.display_order
    if data.is_active is not None:
        item.is_active = data.is_active
    if data.is_available is not None:
        item.is_available = data.is_available

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(
    item_id: int,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """
    Delete a menu item.
    Only items accessible to current branch can be deleted.
    """
    # Find item with tenant isolation
    item = (
        db.query(MenuItem)
        .filter(
            MenuItem.id == item_id,
            or_(
                MenuItem.branch_id == None,
                MenuItem.branch_id == ctx.current_branch_id
            )
        )
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ürün bulunamadı"
        )

    db.delete(item)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
