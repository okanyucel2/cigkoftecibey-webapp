from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import joinedload
from app.api.deps import DBSession, CurrentUser, get_password_hash
from app.models import User, Branch, UserBranch
from app.schemas import UserResponse, UserCreate
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/users", tags=["users"])


class UserBranchAssignment(BaseModel):
    user_id: int
    branch_id: int
    role: str = "owner"
    is_default: bool = False


class UserBranchResponse(BaseModel):
    id: int
    user_id: int
    branch_id: int
    role: str
    is_default: bool
    branch_name: str

    class Config:
        from_attributes = True


class UserWithBranchesResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    branch_id: Optional[int] = None  # Can be NULL for users without primary branch
    is_active: bool
    is_super_admin: bool
    branches: list[UserBranchResponse] = []

    class Config:
        from_attributes = True


def require_super_admin(current_user: User):
    """Check if current user is super admin"""
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu islemi sadece super admin yapabilir"
        )


@router.get("", response_model=list[UserWithBranchesResponse])
def get_all_users(db: DBSession, current_user: CurrentUser):
    """Get all users with their branch assignments (super_admin only)"""
    require_super_admin(current_user)

    users = db.query(User).options(
        joinedload(User.user_branches).joinedload(UserBranch.branch)
    ).all()

    result = []
    for user in users:
        user_branches = []
        for ub in user.user_branches:
            user_branches.append(UserBranchResponse(
                id=ub.id,
                user_id=ub.user_id,
                branch_id=ub.branch_id,
                role=ub.role,
                is_default=ub.is_default,
                branch_name=ub.branch.name if ub.branch else ""
            ))

        result.append(UserWithBranchesResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            branch_id=user.branch_id,
            is_active=user.is_active,
            is_super_admin=user.is_super_admin,
            branches=user_branches
        ))

    return result


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, db: DBSession, current_user: CurrentUser):
    """Create a new user (super_admin only)"""
    require_super_admin(current_user)

    # Check if email already exists
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu email adresi zaten kullaniliyor"
        )

    # Check if branch exists
    branch = db.query(Branch).filter(Branch.id == data.branch_id).first()
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sube bulunamadi"
        )

    user = User(
        email=data.email,
        name=data.name,
        role=data.role,
        branch_id=data.branch_id,
        password_hash=get_password_hash(data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create default user_branch entry
    user_branch = UserBranch(
        user_id=user.id,
        branch_id=data.branch_id,
        role=data.role,
        is_default=True
    )
    db.add(user_branch)
    db.commit()

    return user


@router.get("/{user_id}", response_model=UserWithBranchesResponse)
def get_user(user_id: int, db: DBSession, current_user: CurrentUser):
    """Get a specific user with their branch assignments (super_admin only)"""
    require_super_admin(current_user)

    user = db.query(User).options(
        joinedload(User.user_branches).joinedload(UserBranch.branch)
    ).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanici bulunamadi"
        )

    user_branches = []
    for ub in user.user_branches:
        user_branches.append(UserBranchResponse(
            id=ub.id,
            user_id=ub.user_id,
            branch_id=ub.branch_id,
            role=ub.role,
            is_default=ub.is_default,
            branch_name=ub.branch.name if ub.branch else ""
        ))

    return UserWithBranchesResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        branch_id=user.branch_id,
        is_active=user.is_active,
        is_super_admin=user.is_super_admin,
        branches=user_branches
    )


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    is_super_admin: Optional[bool] = None


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, data: UserUpdate, db: DBSession, current_user: CurrentUser):
    """Update a user (super_admin only)"""
    require_super_admin(current_user)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanici bulunamadi"
        )

    if data.name is not None:
        user.name = data.name
    if data.role is not None:
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.is_super_admin is not None:
        user.is_super_admin = data.is_super_admin

    db.commit()
    db.refresh(user)
    return user


@router.post("/{user_id}/branches", response_model=UserBranchResponse)
def assign_user_to_branch(
    user_id: int,
    data: UserBranchAssignment,
    db: DBSession,
    current_user: CurrentUser
):
    """Assign a user to a branch (super_admin only)"""
    require_super_admin(current_user)

    # Validate user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanici bulunamadi"
        )

    # Validate branch exists
    branch = db.query(Branch).filter(Branch.id == data.branch_id).first()
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sube bulunamadi"
        )

    # Check if assignment already exists
    existing = db.query(UserBranch).filter(
        UserBranch.user_id == user_id,
        UserBranch.branch_id == data.branch_id
    ).first()

    if existing:
        # Update existing assignment
        existing.role = data.role
        if data.is_default:
            # Reset other defaults
            db.query(UserBranch).filter(
                UserBranch.user_id == user_id,
                UserBranch.is_default == True
            ).update({"is_default": False})
            existing.is_default = True
        db.commit()
        db.refresh(existing)
        return UserBranchResponse(
            id=existing.id,
            user_id=existing.user_id,
            branch_id=existing.branch_id,
            role=existing.role,
            is_default=existing.is_default,
            branch_name=branch.name
        )

    # Create new assignment
    if data.is_default:
        # Reset other defaults
        db.query(UserBranch).filter(
            UserBranch.user_id == user_id,
            UserBranch.is_default == True
        ).update({"is_default": False})

    user_branch = UserBranch(
        user_id=user_id,
        branch_id=data.branch_id,
        role=data.role,
        is_default=data.is_default
    )
    db.add(user_branch)
    db.commit()
    db.refresh(user_branch)

    return UserBranchResponse(
        id=user_branch.id,
        user_id=user_branch.user_id,
        branch_id=user_branch.branch_id,
        role=user_branch.role,
        is_default=user_branch.is_default,
        branch_name=branch.name
    )


@router.delete("/{user_id}/branches/{branch_id}")
def remove_user_from_branch(
    user_id: int,
    branch_id: int,
    db: DBSession,
    current_user: CurrentUser
):
    """Remove a user from a branch (super_admin only)"""
    require_super_admin(current_user)

    user_branch = db.query(UserBranch).filter(
        UserBranch.user_id == user_id,
        UserBranch.branch_id == branch_id
    ).first()

    if not user_branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanici-sube iliskisi bulunamadi"
        )

    # Don't allow removing last branch
    count = db.query(UserBranch).filter(UserBranch.user_id == user_id).count()
    if count <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kullanicinin en az bir subesi olmali"
        )

    was_default = user_branch.is_default
    db.delete(user_branch)
    db.commit()

    # If removed branch was default, set another as default
    if was_default:
        another = db.query(UserBranch).filter(UserBranch.user_id == user_id).first()
        if another:
            another.is_default = True
            db.commit()

    return {"message": "Kullanici subeden cikarildi"}
