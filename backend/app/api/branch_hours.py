"""
Branch Operating Hours CRUD API

Hybrid tenant isolation:
- branch_id=NULL: Global default hours (apply to all branches)
- branch_id=X: Branch-specific hours (override global defaults)
"""
from fastapi import APIRouter, status
from sqlalchemy import or_
from app.api.deps import DBSession, CurrentBranchContext
from app.models import BranchOperatingHours
from app.schemas import (
    BranchOperatingHoursCreate,
    BranchOperatingHoursBatchCreate,
    BranchOperatingHoursResponse
)

router = APIRouter(prefix="/v1/branch-hours", tags=["branch-hours"])


@router.get("", response_model=list[BranchOperatingHoursResponse])
def get_branch_hours(db: DBSession, ctx: CurrentBranchContext):
    """
    Get operating hours for current branch.

    Returns merged view:
    - Branch-specific hours take precedence
    - Falls back to global defaults (branch_id=NULL) for days without override
    """
    branch_id = ctx.current_branch_id

    # Get all hours (global + branch-specific)
    all_hours = (
        db.query(BranchOperatingHours)
        .filter(
            or_(
                BranchOperatingHours.branch_id == None,  # Global
                BranchOperatingHours.branch_id == branch_id  # Branch-specific
            )
        )
        .order_by(BranchOperatingHours.day_of_week)
        .all()
    )

    # Merge: branch-specific overrides global
    hours_by_day: dict[int, BranchOperatingHours] = {}
    for hours in all_hours:
        day = hours.day_of_week
        # If branch-specific, always use it
        # If global and no branch-specific exists, use global
        if hours.branch_id == branch_id:
            hours_by_day[day] = hours
        elif day not in hours_by_day:
            hours_by_day[day] = hours

    # Return sorted by day
    return sorted(hours_by_day.values(), key=lambda h: h.day_of_week)


@router.post("", response_model=BranchOperatingHoursResponse, status_code=status.HTTP_201_CREATED)
def set_branch_hours(
    data: BranchOperatingHoursCreate,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """
    Set operating hours for a specific day.

    Creates or updates branch-specific hours.
    """
    branch_id = ctx.current_branch_id

    # Check if hours exist for this day and branch
    existing = (
        db.query(BranchOperatingHours)
        .filter(
            BranchOperatingHours.branch_id == branch_id,
            BranchOperatingHours.day_of_week == data.day_of_week
        )
        .first()
    )

    if existing:
        # Update existing
        existing.open_time = data.open_time
        existing.close_time = data.close_time
        existing.is_closed = data.is_closed
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create new
        hours = BranchOperatingHours(
            branch_id=branch_id,
            day_of_week=data.day_of_week,
            open_time=data.open_time,
            close_time=data.close_time,
            is_closed=data.is_closed
        )
        db.add(hours)
        db.commit()
        db.refresh(hours)
        return hours


@router.post("/batch", response_model=list[BranchOperatingHoursResponse], status_code=status.HTTP_201_CREATED)
def set_branch_hours_batch(
    data: BranchOperatingHoursBatchCreate,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """
    Set operating hours for multiple days at once.
    """
    results = []
    for hours_data in data.hours:
        # Reuse single-day logic
        result = set_branch_hours(hours_data, db, ctx)
        results.append(result)
    return results
