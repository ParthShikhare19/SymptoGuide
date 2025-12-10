"""Health check endpoint"""

from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.services.ml.model_manager import get_model_manager
from app.core.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    
    model_manager = get_model_manager()
    metadata = model_manager.get_metadata()
    
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        model_loaded=model_manager.is_loaded(),
        model_version=metadata.get("version")
    )
