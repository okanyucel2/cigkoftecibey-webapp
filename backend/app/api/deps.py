from datetime import datetime, timedelta
from typing import Annotated, Optional
from dataclasses import dataclass
from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import User, Branch, UserBranch
from app.schemas import TokenData


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


@dataclass
class TenantContext:
    """Context object containing tenant information for multi-tenant isolation"""
    tenant_id: int
    source: str  # "user", "header", or "query"
    user: User


@dataclass
class BranchContext:
    """Context object containing user and branch information"""
    user: User
    current_branch_id: int
    current_branch: Branch
    accessible_branches: list[Branch]
    is_super_admin: bool


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)]
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kimlik dogrulanamadi",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        token_data = TokenData(user_id=int(user_id_str))
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Kullanici aktif degil")
    return user


def get_accessible_branches(db: Session, user: User) -> list[Branch]:
    """Get list of branches user can access"""
    if user.is_super_admin:
        # Super admin can access all branches
        return db.query(Branch).filter(Branch.is_active == True).all()

    # Get branches from user_branches table
    user_branch_ids = db.query(UserBranch.branch_id).filter(
        UserBranch.user_id == user.id
    ).all()
    branch_ids = [ub[0] for ub in user_branch_ids]

    # Fallback to user's default branch_id if no user_branches entries
    if not branch_ids and user.branch_id:
        branch_ids = [user.branch_id]

    return db.query(Branch).filter(
        Branch.id.in_(branch_ids),
        Branch.is_active == True
    ).all()


def get_default_branch_id(db: Session, user: User) -> int:
    """Get user's default branch ID"""
    # Check for default in user_branches
    default_ub = db.query(UserBranch).filter(
        UserBranch.user_id == user.id,
        UserBranch.is_default == True
    ).first()

    if default_ub:
        return default_ub.branch_id

    # Fallback to first accessible branch
    accessible = get_accessible_branches(db, user)
    if accessible:
        return accessible[0].id

    # Final fallback to user's branch_id
    return user.branch_id


def get_branch_context(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
    x_branch_id: Annotated[Optional[int], Header(alias="X-Branch-Id")] = None
) -> BranchContext:
    """Get branch context from token and X-Branch-Id header"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kimlik dogrulanamadi",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        token_data = TokenData(user_id=int(user_id_str))
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Kullanici aktif degil")

    # Get accessible branches
    accessible_branches = get_accessible_branches(db, user)

    # Determine current branch
    if x_branch_id is not None:
        # Validate user has access to the requested branch
        if not user.is_super_admin:
            accessible_ids = [b.id for b in accessible_branches]
            if x_branch_id not in accessible_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Bu subeye erisim yetkiniz yok"
                )
        current_branch_id = x_branch_id
    else:
        # Use default branch
        current_branch_id = get_default_branch_id(db, user)

    # Get current branch object
    current_branch = db.query(Branch).filter(Branch.id == current_branch_id).first()
    if current_branch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sube bulunamadi"
        )

    return BranchContext(
        user=user,
        current_branch_id=current_branch_id,
        current_branch=current_branch,
        accessible_branches=accessible_branches,
        is_super_admin=user.is_super_admin
    )


def get_current_tenant(
    request: Request,
    db: Session,
    user: User
) -> TenantContext:
    """
    Extract tenant context for multi-tenant isolation.

    Priority for super_admin:
    1. X-Tenant-ID header (API/dev use)
    2. ?tenant= query param (dev only)
    3. User's organization_id

    Regular users always use their organization_id.

    Also sets PostgreSQL session variable for RLS policies.
    """
    tenant_id: Optional[int] = None
    source: str = "user"

    # Super admins can override tenant via header or query param
    if user.is_super_admin:
        # Try header first
        header_val = request.headers.get("x-tenant-id")
        if header_val and header_val.isdigit():
            tenant_id = int(header_val)
            source = "header"

        # Try query param if no header
        if tenant_id is None:
            query_val = request.query_params.get("tenant")
            if query_val and query_val.isdigit():
                tenant_id = int(query_val)
                source = "query"

    # Default to user's organization
    if tenant_id is None:
        tenant_id = user.organization_id
        source = "user"

    # Validate tenant exists
    if tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant context missing. User has no organization."
        )

    # Set PostgreSQL session variable for RLS
    db.execute(
        text("SELECT set_config('app.current_tenant', :tid, false)"),
        {"tid": str(tenant_id)}
    )

    return TenantContext(
        tenant_id=tenant_id,
        source=source,
        user=user
    )


CurrentUser = Annotated[User, Depends(get_current_user)]
DBSession = Annotated[Session, Depends(get_db)]
CurrentBranchContext = Annotated[BranchContext, Depends(get_branch_context)]
CurrentTenantContext = Annotated[TenantContext, Depends(get_current_tenant)]
