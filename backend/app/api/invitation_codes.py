import secrets
import string
from fastapi import APIRouter, HTTPException, status
from app.api.deps import DBSession, CurrentUser, CurrentBranchContext
from app.models import InvitationCode, InvitationCodeUse, Organization, Branch
from app.schemas import (
    InvitationCodeCreate, InvitationCodeUpdate, InvitationCodeResponse,
    InvitationCodeValidation, BranchResponse
)

router = APIRouter(prefix="/invitation-codes", tags=["invitation-codes"])


def generate_code(length: int = 8) -> str:
    """Generate a random alphanumeric invitation code"""
    alphabet = string.ascii_uppercase + string.digits
    # Remove confusing characters
    alphabet = alphabet.replace('O', '').replace('0', '').replace('I', '').replace('1', '').replace('L', '')
    return ''.join(secrets.choice(alphabet) for _ in range(length))


@router.get("", response_model=list[InvitationCodeResponse])
def list_invitation_codes(
    db: DBSession,
    ctx: CurrentBranchContext
):
    """List invitation codes for current organization (owner only)"""
    # Get user's organization
    user = ctx.user
    if not user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kullanici bir organizasyona bagli degil"
        )

    # Only owners can manage invitation codes
    if user.role not in ["owner"] and not user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Davet kodlarini sadece sahipler yonetebilir"
        )

    codes = db.query(InvitationCode).filter(
        InvitationCode.organization_id == user.organization_id,
        InvitationCode.is_active == True
    ).order_by(InvitationCode.created_at.desc()).all()

    result = []
    for code in codes:
        branch = None
        if code.branch_id:
            branch_obj = db.query(Branch).filter(Branch.id == code.branch_id).first()
            if branch_obj:
                branch = BranchResponse.model_validate(branch_obj)

        result.append(InvitationCodeResponse(
            id=code.id,
            code=code.code,
            organization_id=code.organization_id,
            branch_id=code.branch_id,
            role=code.role,
            max_uses=code.max_uses,
            used_count=code.used_count,
            expires_at=code.expires_at,
            is_active=code.is_active,
            created_by=code.created_by,
            created_at=code.created_at,
            is_valid=code.is_valid,
            branch=branch
        ))

    return result


@router.post("", response_model=InvitationCodeResponse)
def create_invitation_code(
    data: InvitationCodeCreate,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """Create a new invitation code (owner only)"""
    user = ctx.user
    if not user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kullanici bir organizasyona bagli degil"
        )

    # Only owners can create invitation codes
    if user.role not in ["owner"] and not user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Davet kodu olusturma yetkisi yok"
        )

    # Validate branch if specified
    if data.branch_id:
        branch = db.query(Branch).filter(
            Branch.id == data.branch_id,
            Branch.organization_id == user.organization_id
        ).first()
        if not branch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sube bulunamadi veya organizasyona ait degil"
            )

    # Generate unique code
    code_str = generate_code()
    while db.query(InvitationCode).filter(InvitationCode.code == code_str).first():
        code_str = generate_code()

    code = InvitationCode(
        code=code_str,
        organization_id=user.organization_id,
        branch_id=data.branch_id,
        role=data.role,
        max_uses=data.max_uses,
        expires_at=data.expires_at,
        created_by=user.id
    )
    db.add(code)
    db.commit()
    db.refresh(code)

    branch_response = None
    if code.branch_id:
        branch_obj = db.query(Branch).filter(Branch.id == code.branch_id).first()
        if branch_obj:
            branch_response = BranchResponse.model_validate(branch_obj)

    return InvitationCodeResponse(
        id=code.id,
        code=code.code,
        organization_id=code.organization_id,
        branch_id=code.branch_id,
        role=code.role,
        max_uses=code.max_uses,
        used_count=code.used_count,
        expires_at=code.expires_at,
        is_active=code.is_active,
        created_by=code.created_by,
        created_at=code.created_at,
        is_valid=code.is_valid,
        branch=branch_response
    )


@router.get("/{code_id}", response_model=InvitationCodeResponse)
def get_invitation_code(
    code_id: int,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """Get invitation code details"""
    user = ctx.user

    code = db.query(InvitationCode).filter(
        InvitationCode.id == code_id,
        InvitationCode.organization_id == user.organization_id
    ).first()

    if not code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Davet kodu bulunamadi"
        )

    branch_response = None
    if code.branch_id:
        branch_obj = db.query(Branch).filter(Branch.id == code.branch_id).first()
        if branch_obj:
            branch_response = BranchResponse.model_validate(branch_obj)

    return InvitationCodeResponse(
        id=code.id,
        code=code.code,
        organization_id=code.organization_id,
        branch_id=code.branch_id,
        role=code.role,
        max_uses=code.max_uses,
        used_count=code.used_count,
        expires_at=code.expires_at,
        is_active=code.is_active,
        created_by=code.created_by,
        created_at=code.created_at,
        is_valid=code.is_valid,
        branch=branch_response
    )


@router.put("/{code_id}", response_model=InvitationCodeResponse)
def update_invitation_code(
    code_id: int,
    data: InvitationCodeUpdate,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """Update invitation code"""
    user = ctx.user

    if user.role not in ["owner"] and not user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Davet kodu guncelleme yetkisi yok"
        )

    code = db.query(InvitationCode).filter(
        InvitationCode.id == code_id,
        InvitationCode.organization_id == user.organization_id
    ).first()

    if not code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Davet kodu bulunamadi"
        )

    if data.max_uses is not None:
        code.max_uses = data.max_uses
    if data.expires_at is not None:
        code.expires_at = data.expires_at
    if data.is_active is not None:
        code.is_active = data.is_active

    db.commit()
    db.refresh(code)

    branch_response = None
    if code.branch_id:
        branch_obj = db.query(Branch).filter(Branch.id == code.branch_id).first()
        if branch_obj:
            branch_response = BranchResponse.model_validate(branch_obj)

    return InvitationCodeResponse(
        id=code.id,
        code=code.code,
        organization_id=code.organization_id,
        branch_id=code.branch_id,
        role=code.role,
        max_uses=code.max_uses,
        used_count=code.used_count,
        expires_at=code.expires_at,
        is_active=code.is_active,
        created_by=code.created_by,
        created_at=code.created_at,
        is_valid=code.is_valid,
        branch=branch_response
    )


@router.delete("/{code_id}")
def delete_invitation_code(
    code_id: int,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """Deactivate invitation code"""
    user = ctx.user

    if user.role not in ["owner"] and not user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Davet kodu silme yetkisi yok"
        )

    code = db.query(InvitationCode).filter(
        InvitationCode.id == code_id,
        InvitationCode.organization_id == user.organization_id
    ).first()

    if not code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Davet kodu bulunamadi"
        )

    code.is_active = False
    db.commit()

    return {"message": "Davet kodu devre disi birakildi"}


@router.post("/validate", response_model=InvitationCodeValidation)
def validate_invitation_code(
    code_str: str,
    db: DBSession
):
    """Public endpoint to validate an invitation code"""
    code = db.query(InvitationCode).filter(
        InvitationCode.code == code_str.upper()
    ).first()

    if not code:
        return InvitationCodeValidation(
            valid=False,
            message="Gecersiz davet kodu"
        )

    if not code.is_valid:
        if not code.is_active:
            message = "Bu davet kodu artik aktif degil"
        elif code.max_uses > 0 and code.used_count >= code.max_uses:
            message = "Bu davet kodu kullanim limitine ulasmis"
        else:
            message = "Bu davet kodunun suresi dolmus"

        return InvitationCodeValidation(
            valid=False,
            message=message
        )

    # Get organization and branch info
    org = db.query(Organization).filter(Organization.id == code.organization_id).first()
    branch_name = None
    if code.branch_id:
        branch = db.query(Branch).filter(Branch.id == code.branch_id).first()
        branch_name = branch.name if branch else None

    return InvitationCodeValidation(
        valid=True,
        message="Davet kodu gecerli",
        organization_name=org.name if org else None,
        branch_name=branch_name,
        role=code.role
    )
