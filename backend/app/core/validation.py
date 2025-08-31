from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator
from fastapi import Request, HTTPException, status
import re
import html
from datetime import datetime

from app.core.exceptions import ValidationError


class RequestValidator:
    """Comprehensive request validation utilities"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
        """Sanitize string input to prevent XSS and other attacks"""
        if not isinstance(value, str):
            raise ValidationError("Value must be a string")
        
        sanitized = html.escape(value.strip())
        
        if max_length and len(sanitized) > max_length:
            raise ValidationError(f"String too long. Maximum length is {max_length}")
        
        return sanitized
    
    @staticmethod
    def validate_pagination_params(page: int, size: int) -> tuple[int, int]:
        """Validate pagination parameters"""
        if page < 1:
            raise ValidationError("Page number must be greater than 0", "page")
        
        if size < 1:
            raise ValidationError("Page size must be greater than 0", "size")
        
        if size > 100:
            raise ValidationError("Page size cannot exceed 100", "size")
        
        return page, size
    
    @staticmethod
    def validate_sort_params(order_by: str, order_direction: str, valid_fields: List[str]) -> tuple[str, str]:
        """Validate sorting parameters"""
        if order_by not in valid_fields:
            raise ValidationError(
                f"Invalid order_by field. Must be one of: {', '.join(valid_fields)}", 
                "order_by"
            )
        
        order_direction = order_direction.lower()
        if order_direction not in ["asc", "desc"]:
            raise ValidationError("Order direction must be 'asc' or 'desc'", "order_direction")
        
        return order_by, order_direction
    
    @staticmethod
    def validate_search_term(search_term: str, min_length: int = 2, max_length: int = 200) -> str:
        """Validate search term"""
        if not search_term or not search_term.strip():
            raise ValidationError("Search term cannot be empty", "search_term")
        
        sanitized = RequestValidator.sanitize_string(search_term, max_length)
        
        if len(sanitized) < min_length:
            raise ValidationError(f"Search term must be at least {min_length} characters long", "search_term")
        
        return sanitized
    
    @staticmethod
    def validate_task_title(title: str) -> str:
        """Validate task title with business rules"""
        if not title or not title.strip():
            raise ValidationError("Title cannot be empty", "title")
        
        sanitized = RequestValidator.sanitize_string(title, 200)
        
        if len(sanitized) < 1:
            raise ValidationError("Title must be at least 1 character long", "title")
        
        if re.search(r'[<>"\']', sanitized):
            raise ValidationError("Title contains invalid characters", "title")
        
        return sanitized
    
    @staticmethod
    def validate_task_description(description: Optional[str]) -> Optional[str]:
        """Validate task description"""
        if description is None:
            return None
        
        if not description.strip():
            return None
        
        sanitized = RequestValidator.sanitize_string(description, 1000)
        return sanitized
    
    @staticmethod
    def validate_id_parameter(id_value: Any, resource_name: str = "Resource") -> int:
        """Validate ID parameter"""
        try:
            id_int = int(id_value)
            if id_int <= 0:
                raise ValidationError(f"{resource_name} ID must be a positive integer", "id")
            return id_int
        except (ValueError, TypeError):
            raise ValidationError(f"{resource_name} ID must be a valid integer", "id")


def validate_request_size(request: Request, max_size: int = 1024 * 1024):  # 1MB default
    """Middleware to validate request size"""
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Request too large. Maximum size is {max_size} bytes"
        )


def validate_content_type(request: Request, allowed_types: List[str] = None):
    """Middleware to validate content type"""
    if allowed_types is None:
        allowed_types = ["application/json"]
    
    content_type = request.headers.get("content-type", "").split(";")[0]
    
    if request.method in ["POST", "PUT", "PATCH"] and content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported content type. Allowed types: {', '.join(allowed_types)}"
        )
