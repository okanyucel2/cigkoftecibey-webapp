from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import DBSession, CurrentUser
from app.services.prediction_service import PredictionService
from app.services.ai_service import AIService
from datetime import datetime

router = APIRouter(prefix="/ai", tags=["ai"])

# Singleton instances (or can be dependency injected)
prediction_service = PredictionService()
ai_service = AIService()

@router.get("/daily-brief")
async def get_daily_brief(
    current_user: CurrentUser,
    db: DBSession
):
    """
    Get AI-powered daily briefing and stats.
    """
    # 1. Get Statistical Prediction
    today = datetime.now()
    stats = await prediction_service.get_daily_sales_prediction(today, current_user.branch_id)
    
    # 2. Get AI Narrative (Insight)
    insight_text = await ai_service.generate_daily_brief(stats)
    
    return {
        "stats": stats,
        "insight": insight_text,
        "generated_at": datetime.now().isoformat()
    }
