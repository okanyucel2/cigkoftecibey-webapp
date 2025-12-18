from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import DBSession, CurrentUser, CurrentBranchContext, get_accessible_branches
from app.models import Branch, UserBranch
from app.schemas import BranchCreate, BranchResponse

router = APIRouter(prefix="/branches", tags=["branches"])


@router.get("", response_model=list[BranchResponse])
def get_accessible_branches_list(
    db: DBSession,
    current_user: CurrentUser
):
    """Get list of branches the current user can access"""
    branches = get_accessible_branches(db, current_user)
    return branches


@router.get("/{branch_id}", response_model=BranchResponse)
def get_branch(
    branch_id: int,
    db: DBSession,
    current_user: CurrentUser
):
    """Get a specific branch by ID"""
    # Verify user has access to this branch
    accessible = get_accessible_branches(db, current_user)
    accessible_ids = [b.id for b in accessible]

    if branch_id not in accessible_ids and not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu subeye erisim yetkiniz yok"
        )

    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sube bulunamadi"
        )
    return branch


@router.post("", response_model=BranchResponse, status_code=status.HTTP_201_CREATED)
def create_branch(
    data: BranchCreate,
    db: DBSession,
    current_user: CurrentUser
):
    """Create a new branch (super_admin only)"""
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu islemi sadece super admin yapabilir"
        )

    # Check if code already exists
    existing = db.query(Branch).filter(Branch.code == data.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu sube kodu zaten kullaniliyor"
        )

    branch = Branch(
        name=data.name,
        code=data.code,
        city=data.city,
        address=data.address,
        phone=data.phone
    )
    db.add(branch)
    db.commit()
    db.refresh(branch)
    return branch


@router.put("/{branch_id}", response_model=BranchResponse)
def update_branch(
    branch_id: int,
    data: BranchCreate,
    db: DBSession,
    current_user: CurrentUser
):
    """Update a branch (super_admin only)"""
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu islemi sadece super admin yapabilir"
        )

    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sube bulunamadi"
        )

    # Check if code already exists for another branch
    existing = db.query(Branch).filter(
        Branch.code == data.code,
        Branch.id != branch_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu sube kodu zaten kullaniliyor"
        )

    branch.name = data.name
    branch.code = data.code
    branch.city = data.city
    branch.address = data.address
    branch.phone = data.phone
    db.commit()
    db.refresh(branch)
    return branch


@router.delete("/{branch_id}")
def delete_branch(
    branch_id: int,
    db: DBSession,
    current_user: CurrentUser
):
    """Deactivate a branch (super_admin only)"""
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu islemi sadece super admin yapabilir"
        )

    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sube bulunamadi"
        )

    # Soft delete - just deactivate
    branch.is_active = False
    db.commit()
    return {"message": "Sube deaktif edildi"}


@router.post("/{branch_id}/activate")
def activate_branch(
    branch_id: int,
    db: DBSession,
    current_user: CurrentUser
):
    """Reactivate a branch (super_admin only)"""
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu islemi sadece super admin yapabilir"
        )

    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sube bulunamadi"
        )

    branch.is_active = True
    db.commit()
    return {"message": "Sube aktif edildi"}
