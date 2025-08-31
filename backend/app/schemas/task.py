from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, computed_field

from app.models.task import TaskStatus


class TaskBase(BaseModel):
    """Base schema for task with common fields"""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    status: TaskStatus = Field(default=TaskStatus.OPEN, description="Task status")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Validate title is not empty or just whitespace"""
        if not v or not v.strip():
            raise ValueError('Title cannot be empty or just whitespace')
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        """Validate description if provided"""
        if v is not None:
            return v.strip() if v.strip() else None
        return v

    model_config = {"use_enum_values": True}


class TaskCreate(TaskBase):
    """Schema for creating a new task"""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating an existing task - all fields optional"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    status: Optional[TaskStatus] = Field(None, description="Task status")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Validate title is not empty or just whitespace if provided"""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Title cannot be empty or just whitespace')
            return v.strip()
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        """Validate description if provided"""
        if v is not None:
            return v.strip() if v.strip() else None
        return v

    model_config = {"use_enum_values": True}


class TaskResponse(TaskBase):
    """Schema for task response with all fields including metadata"""
    id: int = Field(..., description="Task ID")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime = Field(..., description="Task last update timestamp")

    model_config = {"from_attributes": True, "use_enum_values": True}


class TaskListResponse(BaseModel):
    """Schema for paginated task list response"""
    items: List[TaskResponse] = Field(..., description="List of tasks")
    total: int = Field(..., ge=0, description="Total number of tasks")
    page: int = Field(..., ge=1, description="Current page number")
    size: int = Field(..., ge=1, description="Items per page")

    @computed_field
    @property
    def pages(self) -> int:
        """Calculate total pages based on total and size"""
        return (self.total + self.size - 1) // self.size if self.total > 0 else 0

    model_config = {"from_attributes": True}


class TaskFilter(BaseModel):
    """Schema for task filtering parameters"""
    status: Optional[TaskStatus] = Field(None, description="Filter by single task status")
    title_contains: Optional[str] = Field(None, description="Filter by title containing text")

    @field_validator('title_contains')
    @classmethod
    def validate_title_contains(cls, v):
        """Validate title search term"""
        if v is not None:
            stripped = v.strip()
            if len(stripped) < 2:
                raise ValueError('Search term must be at least 2 characters long')
            return stripped
        return v

    model_config = {"use_enum_values": True}


class PaginationParams(BaseModel):
    """Schema for pagination parameters with validation"""
    page: int = Field(1, ge=1, description="Page number (1-based)")
    size: int = Field(10, ge=1, le=100, description="Items per page (max 100)")
    order_by: str = Field("created_at", description="Field to order by")
    order_direction: str = Field("desc", description="Order direction (asc/desc)")

    @field_validator('order_by')
    @classmethod
    def validate_order_by(cls, v):
        """Validate order_by field"""
        valid_fields = ["id", "title", "status", "created_at", "updated_at"]
        if v not in valid_fields:
            raise ValueError(f'order_by must be one of: {", ".join(valid_fields)}')
        return v

    @field_validator('order_direction')
    @classmethod
    def validate_order_direction(cls, v):
        """Validate and normalize order direction"""
        normalized = v.lower()
        if normalized not in ["asc", "desc"]:
            raise ValueError('order_direction must be "asc" or "desc"')
        return normalized

    model_config = {"use_enum_values": True}


class TaskSearchParams(BaseModel):
    """Schema for task search parameters"""
    search_term: str = Field(..., min_length=2, max_length=200, description="Search term for task titles")
    status: Optional[TaskStatus] = Field(None, description="Filter search results by status")

    @field_validator('search_term')
    @classmethod
    def validate_search_term(cls, v):
        """Validate and sanitize search term"""
        if not v or not v.strip():
            raise ValueError('Search term cannot be empty')
        stripped = v.strip()
        if len(stripped) < 2:
            raise ValueError('Search term must be at least 2 characters long')
        return stripped

    model_config = {"use_enum_values": True}