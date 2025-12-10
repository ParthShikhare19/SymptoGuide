"""API v1 router"""

from fastapi import APIRouter
from app.api.v1.endpoints import health, analysis

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(analysis.router, tags=["analysis"])
