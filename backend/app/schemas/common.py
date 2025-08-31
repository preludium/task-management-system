from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    """Standard success response schema"""
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Optional response data")


class ErrorResponse(BaseModel):
    """Standard error response schema"""
    success: bool = Field(False, description="Operation success status")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class HealthResponse(BaseModel):
    """Health check response schema"""
    status: str = Field(..., description="Health status")
    timestamp: float = Field(..., description="Response timestamp")
    environment: str = Field(..., description="Application environment")
    version: Optional[str] = Field(None, description="Application version")


class PaginationMeta(BaseModel):
    """Pagination metadata schema"""
    page: int = Field(..., ge=1, description="Current page number")
    size: int = Field(..., ge=1, description="Items per page")
    total: int = Field(..., ge=0, description="Total number of items")
    pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")

    @property
    def has_next(self) -> bool:
        return self.page < self.pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1