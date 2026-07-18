"""Operations dashboard router.

Exposes endpoints for the stadium management team to view AI-generated insights
based on real-time crowd and queue data.
"""

from fastapi import APIRouter

from app.services.ai import gemini_service

router = APIRouter(prefix="/ops", tags=["Operations"])


@router.get("/recommendations")
async def get_ops_recommendations() -> list[dict]:
    """Get AI-generated actionable recommendations based on live stadium state."""
    return await gemini_service.generate_recommendations()
