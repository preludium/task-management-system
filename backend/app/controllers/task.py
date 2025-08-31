from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.task import TaskService
from app.services.sse import get_sse_service
from app.schemas.task import (
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse, TaskStatus
)
from app.core.exceptions import (
    ValidationError, DatabaseError
)
from app.core.validation import (
    RequestValidator, validate_request_size, validate_content_type
)

router = APIRouter()


async def get_task_service(
    db: AsyncSession = Depends(get_db),
    sse_service = Depends(get_sse_service)
) -> TaskService:
    """Dependency to get task service instance"""
    return TaskService(db, sse_service)


@router.get("/tasks", response_model=TaskListResponse)
async def get_tasks(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    size: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    title_contains: Optional[str] = Query(None, description="Filter by title containing text"),
    order_by: str = Query("created_at", description="Field to order by"),
    order_direction: str = Query("desc", description="Order direction (asc/desc)"),
    task_service: TaskService = Depends(get_task_service)
):
    """
    Get tasks with pagination and filtering.
    
    - **page**: Page number (1-based, default: 1)
    - **size**: Items per page (1-100, default: 10)
    - **status**: Filter by task status (OPEN, IN_PROGRESS, DONE)
    - **title_contains**: Filter by title containing text
    - **order_by**: Field to order by (id, title, status, created_at, updated_at)
    - **order_direction**: Order direction (asc, desc)
    """
    try:
        page, size = RequestValidator.validate_pagination_params(page, size)
        
        valid_order_fields = ["id", "title", "status", "created_at", "updated_at"]
        order_by, order_direction = RequestValidator.validate_sort_params(
            order_by, order_direction, valid_order_fields
        )
        
        if title_contains:
            title_contains = RequestValidator.validate_search_term(title_contains)
        
        return await task_service.get_tasks_with_pagination(
            page=page,
            size=size,
            status=status,
            title_contains=title_contains,
            order_by=order_by,
            order_direction=order_direction
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": str(e),
                "field": getattr(e, 'field', None),
                "type": "validation_error"
            }
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Database error occurred",
                "type": "database_error"
            }
        )

@router.get("/tasks/counts")
async def get_task_counts(
    task_service: TaskService = Depends(get_task_service)
):
    try:
        return await task_service.get_tasks_counts()
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Database error occurred",
                "type": "database_error"
            }
        )


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: Request,
    task_data: TaskCreate,
    task_service: TaskService = Depends(get_task_service)
):
    """
    Create a new task.
    
    - **title**: Task title (required, 1-200 characters)
    - **description**: Task description (optional, max 1000 characters)
    - **status**: Task status (optional, default: todo)
    """
    try:
        validate_request_size(request)
        validate_content_type(request)
        
        if hasattr(task_data, 'title'):
            task_data.title = RequestValidator.validate_task_title(task_data.title)
        
        if hasattr(task_data, 'description') and task_data.description:
            task_data.description = RequestValidator.validate_task_description(task_data.description)
        
        return await task_service.create_task(task_data)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": str(e),
                "field": getattr(e, 'field', None),
                "type": "validation_error"
            }
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Failed to create task",
                "type": "database_error"
            }
        )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    task_service: TaskService = Depends(get_task_service)
):
    """
    Get a specific task by ID.
    
    - **task_id**: The ID of the task to retrieve
    """
    try:
        task_id = RequestValidator.validate_id_parameter(task_id, "Task")
        
        return await task_service.get_task_by_id(task_id)
    except HTTPException:
        raise
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": str(e),
                "field": getattr(e, 'field', None),
                "type": "validation_error"
            }
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Database error occurred",
                "type": "database_error"
            }
        )


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    task_service: TaskService = Depends(get_task_service)
):
    """
    Update an existing task with partial updates support.
    
    - **task_id**: The ID of the task to update
    - **title**: New task title (optional)
    - **description**: New task description (optional)
    - **status**: New task status (optional)
    
    Only provided fields will be updated.
    """
    try:
        return await task_service.update_task(task_id, task_data)
    except HTTPException:
        raise
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task"
        )


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    task_service: TaskService = Depends(get_task_service)
):
    """
    Delete a task by ID.
    
    - **task_id**: The ID of the task to delete
    """
    try:
        success = await task_service.delete_task(task_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete task"
            )
    except HTTPException:
        raise
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete task"
        )
