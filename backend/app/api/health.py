"""
Health check endpoints
"""
import time
from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Task Management API is running",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "environment": settings.ENVIRONMENT
    }
