"""
Application lifespan management
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.database import init_db
from app.core.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting up Task Management API...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
        
        from app.services.sse import sse_service
        await sse_service.start()
        logger.info("SSE service started successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
    
    yield
    
    logger.info("Shutting down Task Management API...")
    try:
        from app.services.sse import sse_service
        await sse_service.stop()
        logger.info("SSE service stopped successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")