"""
Branch Holidays CRUD API

Hybrid tenant isolation:
- branch_id=NULL: Global holidays (apply to all branches)
- branch_id=X: Branch-specific holidays (override global)
"""
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import or_
from app.api.deps import DBSession, CurrentBranchContext
from app.models import BranchHoliday
from app.schemas import (
    BranchHolidayCreate,
    BranchHolidayUpdate,
    BranchHolidayResponse
)

router = APIRouter(prefix="/v1/branch-holidays", tags=["branch-holidays"])


@router.get("", response_model=list[BranchHolidayResponse])
def list_holidays(db: DBSession, ctx: CurrentBranchContext):
    """
    List holidays for current branch.

    Returns merged view:
    - Branch-specific holidays take precedence
    - Falls back to global holidays (branch_id=NULL) for dates without override
    """
    branch_id = ctx.current_branch_id

    # Get all holidays (global + branch-specific)
    all_holidays = (
        db.query(BranchHoliday)
        .filter(
            or_(
                BranchHoliday.branch_id == None,  # Global
                BranchHoliday.branch_id == branch_id  # Branch-specific
            )
        )
        .order_by(BranchHoliday.date)
        .all()
    )

    # Merge: branch-specific overrides global
    holidays_by_date: dict = {}
    for holiday in all_holidays:
        holiday_date = holiday.date
        # If branch-specific, always use it
        # If global and no branch-specific exists, use global
        if holiday.branch_id == branch_id:
            holidays_by_date[holiday_date] = holiday
        elif holiday_date not in holidays_by_date:
            holidays_by_date[holiday_date] = holiday

    # Return sorted by date
    return sorted(holidays_by_date.values(), key=lambda h: h.date)


@router.post("", response_model=BranchHolidayResponse, status_code=status.HTTP_201_CREATED)
def create_holiday(
    data: BranchHolidayCreate,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """
    Create or update a branch-specific holiday.

    If a holiday already exists for this date and branch, it updates the existing one.
    """
    branch_id = ctx.current_branch_id

    # Check if holiday exists for this date and branch
    existing = (
        db.query(BranchHoliday)
        .filter(
            BranchHoliday.branch_id == branch_id,
            BranchHoliday.date == data.date
        )
        .first()
    )

    if existing:
        # Update existing
        existing.name = data.name
        existing.is_closed = data.is_closed
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create new
        holiday = BranchHoliday(
            branch_id=branch_id,
            date=data.date,
            name=data.name,
            is_closed=data.is_closed
        )
        db.add(holiday)
        db.commit()
        db.refresh(holiday)
        return holiday


@router.put("/{holiday_id}", response_model=BranchHolidayResponse)
def update_holiday(
    holiday_id: int,
    data: BranchHolidayUpdate,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """
    Update an existing holiday.
    """
    branch_id = ctx.current_branch_id

    holiday = (
        db.query(BranchHoliday)
        .filter(
            BranchHoliday.id == holiday_id,
            or_(
                BranchHoliday.branch_id == branch_id,
                BranchHoliday.branch_id == None  # Allow updating global
            )
        )
        .first()
    )

    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")

    # Update fields if provided
    if data.date is not None:
        holiday.date = data.date
    if data.name is not None:
        holiday.name = data.name
    if data.is_closed is not None:
        holiday.is_closed = data.is_closed

    db.commit()
    db.refresh(holiday)
    return holiday


@router.delete("/{holiday_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_holiday(
    holiday_id: int,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """
    Delete a holiday.
    """
    branch_id = ctx.current_branch_id

    holiday = (
        db.query(BranchHoliday)
        .filter(
            BranchHoliday.id == holiday_id,
            or_(
                BranchHoliday.branch_id == branch_id,
                BranchHoliday.branch_id == None  # Allow deleting global
            )
        )
        .first()
    )

    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")

    db.delete(holiday)
    db.commit()
    return None
