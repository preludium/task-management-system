"""
API routes configuration
"""
from fastapi import FastAPI

from app.core.config import settings
from app.controllers.task import router as task_router
from app.controllers.sse import router as sse_router
from app.controllers.test import router as test_router
from app.api.health import router as health_router


def setup_routes(app: FastAPI):
    """Configure all API routes"""
    
    # Health check routes (no prefix)
    app.include_router(health_router)
    
    # API v1 routes
    app.include_router(task_router, prefix=settings.API_V1_STR, tags=["tasks"])
    app.include_router(sse_router, prefix=settings.API_V1_STR, tags=["sse"])
    app.include_router(test_router, prefix=settings.TEST_V1_STR, tags=["test"])