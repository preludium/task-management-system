"""
Exception handlers for the FastAPI application
"""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import (
    TaskManagementException, ValidationError, NotFoundError, 
    ConflictError, DatabaseError
)
from app.core.logging import logger


def setup_exception_handlers(app: FastAPI):
    """Configure all exception handlers for the application"""

    @app.exception_handler(TaskManagementException)
    async def task_management_exception_handler(request: Request, exc: TaskManagementException):
        """Handle custom task management exceptions"""
        logger.warning(f"Task management exception on {request.method} {request.url}: {exc.message}")
        
        status_code_map = {
            ValidationError: 422,
            NotFoundError: 404,
            ConflictError: 409,
            DatabaseError: 500,
        }
        
        status_code = status_code_map.get(type(exc), 500)
        
        return JSONResponse(
            status_code=status_code,
            content={
                "detail": exc.message,
                "type": type(exc).__name__.lower().replace("error", "_error"),
                "details": exc.details
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle FastAPI request validation errors with detailed messages"""
        logger.warning(f"Validation error on {request.method} {request.url}: {exc}")
        
        formatted_errors = []
        for error in exc.errors():
            field_path = " -> ".join(str(loc) for loc in error["loc"])
            formatted_errors.append({
                "field": field_path,
                "message": error["msg"],
                "type": error["type"],
                "input": error.get("input")
            })
        
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Validation failed",
                "type": "validation_error",
                "errors": formatted_errors
            }
        )

    @app.exception_handler(PydanticValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: PydanticValidationError):
        """Handle Pydantic validation errors"""
        logger.warning(f"Pydantic validation error on {request.method} {request.url}: {exc}")
        
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Data validation failed",
                "type": "validation_error",
                "errors": exc.errors()
            }
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        """Handle SQLAlchemy database errors"""
        logger.error(f"Database error on {request.method} {request.url}: {exc}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Database operation failed",
                "type": "database_error"
            }
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler for unhandled errors"""
        logger.error(f"Unhandled exception on {request.method} {request.url}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "type": "internal_error",
                "request_id": getattr(request.state, "request_id", None)
            }
        )