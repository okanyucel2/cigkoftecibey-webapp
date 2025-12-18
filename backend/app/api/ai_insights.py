from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from app.api.deps import DBSession, CurrentUser
from app.services.prediction_service import PredictionService
from app.services.ai_service import AIService
from app.models import DailyInsight, Branch
from datetime import date, datetime

router = APIRouter(prefix="/ai", tags=["ai"])

# Singleton instances
prediction_service = PredictionService()
ai_service = AIService()

@router.get("/daily-brief")
async def get_daily_brief(
    current_user: CurrentUser,
    db: DBSession
):
    """
    Get AI-powered daily briefing.
    Uses cached 'DailyInsight' if available for today, otherwise generates and saves it.
    """
    today = date.today()
    branch_id = current_user.branch_id

    # 1. Check Cache
    cached_insight = db.query(DailyInsight).filter(
        and_(
            DailyInsight.branch_id == branch_id,
            DailyInsight.date == today
        )
    ).first()

    if cached_insight:
        # Return cached stats if possible (or re-fetch stats, but use cached text)
        # For simplicity, we re-calculate numerical stats but use cached narrative.
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

    # 5. Save to Cache
    try:
        new_insight = DailyInsight(
            branch_id=branch_id,
            date=today,
            content=insight_text
        )
        db.add(new_insight)
        db.commit()
    except Exception as e:
        # Ignore duplicate key error if race condition occurs
        db.rollback()

    return {
        "stats": stats,
        "insight": insight_text,
        "generated_at": datetime.now().isoformat(),
        "source": "generated"
    }
