from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from app.api.deps import DBSession, CurrentBranchContext
from app.services.prediction_service import PredictionService
from app.services.ai_service import AIService
from app.models import DailyInsight, Branch
from datetime import date, datetime

from datetime import date, datetime, timedelta

router = APIRouter(prefix="/ai", tags=["ai"])

# Singleton instances
prediction_service = PredictionService()
ai_service = AIService()

@router.get("/daily-brief")
async def get_daily_brief(
    ctx: CurrentBranchContext,
    db: DBSession,
    force_refresh: bool = False
):
    """
    Get AI-powered daily briefing.
    Uses cached 'DailyInsight' if available for today, unless force_refresh is True.
    """
    today = date.today()
    branch_id = ctx.current_branch_id
    current_user = ctx.user
    now = datetime.utcnow()

    # 1. Check Cache
    cached_insight = db.query(DailyInsight).filter(
        and_(
            DailyInsight.branch_id == branch_id,
            DailyInsight.date == today
        )
    ).first()

    # If cache exists and is fresh (less than 1 hour old), use it (unless forced)
    if cached_insight and not force_refresh:
        is_fresh = (now - cached_insight.created_at) < timedelta(hours=1)
        if is_fresh:
            # Stats might change slightly, but we use cached insight for stability + speed
            # Re-fetch stats to be somewhat fresh on numbers, but keep narrative stable
            stats = await prediction_service.get_daily_sales_prediction(datetime.now(), branch_id)
            return {
                "stats": stats,
                "insight": cached_insight.content,
                "generated_at": cached_insight.created_at.isoformat(),
                "source": "cache"
            }

    # 2. Get Branch Info (Location)
    branch = db.query(Branch).filter(Branch.id == branch_id).first()

    city_name = branch.city if branch and branch.city else "İstanbul"

    # 3. Get Statistical Prediction
    stats = await prediction_service.get_daily_sales_prediction(datetime.now(), branch_id)
    
    # Add location to stats context for AI
    stats['city'] = city_name

    # 4. Generate AI Narrative
    insight_text = await ai_service.generate_daily_brief(stats)

    # 5. Save/Update Cache
    try:
        if cached_insight:
            # Update existing record
            cached_insight.content = insight_text
            cached_insight.created_at = now
        else:
            # Create new record
            new_insight = DailyInsight(
                branch_id=branch_id,
                date=today,
                content=insight_text,
                created_at=now
            )
            db.add(new_insight)
        
        db.commit()
    except Exception as e:
        # Ignore duplicate key error if race condition occurs
        db.rollback()

    return {
        "stats": stats,
        "insight": insight_text,
        "generated_at": now.isoformat(),
        "source": "generated"
    }
