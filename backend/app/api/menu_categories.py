"""
Menu Category CRUD API

Hybrid tenant isolation:
- branch_id=NULL: Global categories (visible to all branches)
- branch_id=X: Branch-specific categories (visible only to that branch)
"""
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import or_
from app.api.deps import DBSession, CurrentBranchContext
from app.models import MenuCategory
from app.schemas import MenuCategoryCreate, MenuCategoryResponse

router = APIRouter(prefix="/v1/menu-categories", tags=["menu-categories"])


@router.get("", response_model=list[MenuCategoryResponse])
def get_menu_categories(db: DBSession, ctx: CurrentBranchContext):
    """
    Get menu categories for current branch.
    Returns global (branch_id=NULL) + branch-specific categories.
    """
    return (
        db.query(MenuCategory)
        .filter(
            MenuCategory.is_active == True,
            or_(
                MenuCategory.branch_id == None,  # Global
                MenuCategory.branch_id == ctx.current_branch_id  # Branch-specific
            )
        )
        .order_by(MenuCategory.display_order)
        .all()
    )


@router.post("", response_model=MenuCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_menu_category(
    data: MenuCategoryCreate,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """
    Create a new menu category.
    is_global=True creates global category (branch_id=NULL).
    is_global=False creates branch-specific category.
    """
    # Determine branch_id
    branch_id = None if data.is_global else ctx.current_branch_id

    # Check for duplicate name in same scope
    existing = (
        db.query(MenuCategory)
        .filter(
            MenuCategory.name == data.name,
            MenuCategory.branch_id == branch_id
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu isimde kategori zaten mevcut"
        )

    category = MenuCategory(
        name=data.name,
        description=data.description,
        display_order=data.display_order,
        branch_id=branch_id,
        created_by=ctx.user.id
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category
