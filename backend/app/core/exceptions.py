from fastapi import HTTPException, status
from typing import Any, Dict, Optional, List


class TaskManagementException(Exception):
    """Base exception for task management application"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(TaskManagementException):
    """Raised when validation fails"""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.field = field


class NotFoundError(TaskManagementException):
    """Raised when a resource is not found"""
    
    def __init__(self, resource: str, resource_id: Any, details: Optional[Dict[str, Any]] = None):
        message = f"{resource} with id {resource_id} not found"
        super().__init__(message, details)
        self.resource = resource
        self.resource_id = resource_id


class ConflictError(TaskManagementException):
    """Raised when there's a conflict with existing data"""
    
    def __init__(self, message: str, conflicting_field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.conflicting_field = conflicting_field


class DatabaseError(TaskManagementException):
    """Raised when database operations fail"""
    
    def __init__(self, message: str, operation: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.operation = operation


class BusinessLogicError(TaskManagementException):
    """Raised when business logic rules are violated"""
    
    def __init__(self, message: str, rule: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.rule = rule


# HTTP Exception helpers
class HTTPExceptions:
    """Helper class for common HTTP exceptions"""
    
    @staticmethod
    def not_found(resource: str, resource_id: Any) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"{resource} not found",
                "resource_id": resource_id,
                "type": "not_found_error"
            }
        )
    
    @staticmethod
    def validation_error(message: str, field: Optional[str] = None) -> HTTPException:
        detail = {
            "message": message,
            "type": "validation_error"
        }
        if field:
            detail["field"] = field
            
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )
    
    @staticmethod
    def conflict_error(message: str) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": message,
                "type": "conflict_error"
            }
        )
    
    @staticmethod
    def internal_error(message: str = "Internal server error") -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": message,
                "type": "internal_error"
            }
        )