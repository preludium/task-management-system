"""
Application factory for creating FastAPI instances
"""
from fastapi import FastAPI

from app.core.config import settings
from app.core.lifespan import lifespan
from app.core.middleware import setup_middleware
from app.core.exception_handlers import setup_exception_handlers
from app.api.routes import setup_routes


def create_app(config_override: dict = None) -> FastAPI:
    """
    Create and configure the FastAPI application
    
    Args:
        config_override: Optional configuration overrides for testing
    """
    
    if config_override:
        for key, value in config_override.items():
            setattr(settings, key, value)
    
    app = FastAPI(
        title="Task Management API",
        description="A FastAPI backend for task management with real-time updates",
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    setup_middleware(app)
    setup_exception_handlers(app)
    setup_routes(app)
    
    return app