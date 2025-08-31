from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import uuid
from datetime import datetime

from app.models.task import Task, TaskStatus
from app.repositories.task import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from app.schemas.sse import SSEEvent, SSEEventType
from app.services.base import BaseService
from app.core.exceptions import NotFoundError, ValidationError, DatabaseError, HTTPExceptions


class TaskService(BaseService[Task, TaskRepository, TaskCreate, TaskUpdate]):
    """Service layer for task management with business logic"""
    
    def __init__(self, db: AsyncSession, sse_service=None):
        self.db = db
        self.repository = TaskRepository(db)
        self.sse_service = sse_service
    
    async def create_task(self, task_data: TaskCreate) -> TaskResponse:
        """Create a new task with validation and error handling"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f"Creating task with data: {task_data}")
            
            # Additional business logic validation
            await self._validate_create(task_data)
            logger.info("Validation passed")
            
            # Create the task (this handles its own transaction)
            task = await self.repository.create(task_data.model_dump())
            logger.info(f"Task created in database: {task}")
            
            # Convert to response model
            task_response = TaskResponse.model_validate(task)
            logger.info(f"Task response model created: {task_response}")
            
            # Broadcast SSE event after successful creation (don't let this fail the main operation)
            try:
                await self._broadcast_task_created(task_response)
                logger.info("SSE event broadcasted successfully")
            except Exception as sse_error:
                # Log SSE error but don't fail the task creation
                logger.error(f"Failed to broadcast task created event: {sse_error}")
            
            return task_response
            
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error: {e}")
            raise DatabaseError(f"Failed to create task: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise ValidationError(f"Task creation failed: {str(e)}")
    
    async def get_task_by_id(self, task_id: int) -> TaskResponse:
        """Get a task by ID with proper error handling"""
        try:
            task = await self.repository.get(task_id)
            if not task:
                raise HTTPExceptions.not_found("Task", task_id)
            
            return TaskResponse.model_validate(task)
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to retrieve task: {str(e)}")
    
    async def get_tasks_with_pagination(
        self,
        page: int = 1,
        size: int = 12,
        status: Optional[TaskStatus] = None,
        statuses: Optional[List[TaskStatus]] = None,
        title_contains: Optional[str] = None,
        order_by: str = "created_at",
        order_direction: str = "desc"
    ) -> TaskListResponse:
        """
        Get tasks with enhanced pagination and filtering capabilities.
        Supports multiple status filtering, title search, and optimized queries.
        """
        try:
            # Validate pagination parameters with enhanced limits
            page = self._validate_page_number(page)
            size = self._validate_page_size(size)
            
            # Validate sorting parameters
            order_by = self._validate_order_by(order_by)
            order_direction = self._validate_order_direction(order_direction)
            
            # Validate filter parameters
            if status is not None and statuses is not None:
                raise ValidationError("Cannot specify both 'status' and 'statuses' parameters")
            
            # Use optimized repository method for better performance
            filters = {
                "status": status,
                "statuses": statuses,
                "title_contains": title_contains
            }
            
            tasks, total = await self.repository.get_tasks_with_advanced_filtering(
                filters=filters,
                page=page,
                size=size,
                order_by=order_by,
                order_direction=order_direction
            )
            
            # Convert to response models
            task_responses = [TaskResponse.model_validate(task) for task in tasks]
            
            return TaskListResponse(
                items=task_responses,
                total=total,
                page=page,
                size=size
            )
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to retrieve tasks: {str(e)}")
    
    def _validate_page_number(self, page: int) -> int:
        """Validate and sanitize page number"""
        if page < 1:
            raise ValidationError("Page number must be greater than 0")
        return page
    
    def _validate_page_size(self, size: int) -> int:
        """Validate and sanitize page size with configurable limits"""
        min_size = 1
        max_size = 100  # Configurable maximum for performance
        
        if size < min_size:
            raise ValidationError(f"Page size must be at least {min_size}")
        if size > max_size:
            raise ValidationError(f"Page size cannot exceed {max_size}")
        
        return size
    
    def _validate_order_by(self, order_by: str) -> str:
        """Validate order_by field against allowed fields"""
        valid_order_fields = ["id", "title", "status", "created_at", "updated_at"]
        if order_by not in valid_order_fields:
            raise ValidationError(f"Invalid order_by field. Must be one of: {valid_order_fields}")
        return order_by
    
    def _validate_order_direction(self, order_direction: str) -> str:
        """Validate and normalize order direction"""
        normalized = order_direction.lower()
        if normalized not in ["asc", "desc"]:
            raise ValidationError("Order direction must be 'asc' or 'desc'")
        return normalized
    
    async def update_task(self, task_id: int, task_data: TaskUpdate) -> TaskResponse:
        """Update a task with partial updates support and validation"""
        try:
            # Check if task exists
            existing_task = await self.repository.get(task_id)
            if not existing_task:
                raise HTTPExceptions.not_found("Task", task_id)
            
            # Validate update data
            await self._validate_update(task_id, task_data, existing_task)
            
            # Only update fields that are provided (not None)
            update_data = task_data.model_dump(exclude_unset=True)
            
            if not update_data:
                # No fields to update, return existing task
                return TaskResponse.model_validate(existing_task)
            
            # Store original task data for change detection
            original_task_response = TaskResponse.model_validate(existing_task)
            
            # Update the task
            updated_task = await self.repository.update(task_id, update_data)
            
            # Convert to response model
            updated_task_response = TaskResponse.model_validate(updated_task)
            
            # Broadcast SSE event after successful update
            await self._broadcast_task_updated(updated_task_response, original_task_response, update_data)
            
            return updated_task_response
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to update task: {str(e)}")
    
    async def delete_task(self, task_id: int) -> bool:
        """Delete a task with proper error handling"""
        try:
            # Check if task exists
            existing_task = await self.repository.get(task_id)
            if not existing_task:
                raise HTTPExceptions.not_found("Task", task_id)
            
            # Store task data for SSE event before deletion
            deleted_task_response = TaskResponse.model_validate(existing_task)
            
            # Additional business logic validation for deletion
            await self._validate_delete(task_id, existing_task)
            
            # Delete the task
            success = await self.repository.delete(task_id)
            
            if success:
                # Broadcast SSE event after successful deletion
                await self._broadcast_task_deleted(deleted_task_response)
            
            return success
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to delete task: {str(e)}")
    
    async def get_tasks_counts(self) -> Dict[str, int]:
      try:
        return {
          **await self.repository.get_status_distribution(),
          "total": await self.repository.count()
        }
      except SQLAlchemyError as e:
        raise DatabaseError(f"Failed to get status distribution: {str(e)}")

    def _validate_pagination_params(self, page: int, size: int) -> None:
        """Validate pagination parameters"""
        if page < 1:
            raise ValidationError("Page number must be greater than 0")
        if size < 1 or size > 100:
            raise ValidationError("Page size must be between 1 and 100")
    
    def _validate_sorting_params(self, order_by: str, order_direction: str) -> None:
        """Validate sorting parameters"""
        valid_order_fields = ["id", "title", "status", "created_at", "updated_at"]
        if order_by not in valid_order_fields:
            raise ValidationError(f"Invalid order_by field. Must be one of: {valid_order_fields}")
        
        if order_direction.lower() not in ["asc", "desc"]:
            raise ValidationError("Order direction must be 'asc' or 'desc'")
    
    # Override base service validation methods with task-specific logic
    async def _validate_create(self, task_data: TaskCreate) -> None:
        """Validate task creation data"""
        # Check for duplicate titles (business rule example)
        # This is optional - you might not want to enforce unique titles
        pass
    
    async def _validate_update(self, task_id: int, task_data: TaskUpdate, existing_task: Task) -> None:
        """Validate task update data"""
        # Add any business logic validation for updates
        # For example, you might prevent certain status transitions
        if task_data.status and existing_task.status == TaskStatus.DONE:
            # Example business rule: prevent changing completed tasks
            # Uncomment if you want this behavior
            # raise ValidationError("Cannot modify completed tasks")
            pass
    
    async def _validate_delete(self, task_id: int, existing_task: Task) -> None:
        """Validate task deletion"""
        # Add any business logic validation for deletion
        # For example, you might prevent deleting tasks in certain states
        pass
    
    # SSE Broadcasting Methods
    async def _broadcast_task_created(self, task: TaskResponse) -> None:
        """Broadcast task creation event via SSE"""
        if not self.sse_service:
            return
        
        try:
            # Use mode='json' to ensure proper serialization of datetime fields
            event = SSEEvent(
                event=SSEEventType.TASK_CREATED,
                data={
                    "task": task.model_dump(mode='json'),
                    "timestamp": datetime.utcnow().isoformat(),
                    "action": "created"
                },
                id=str(uuid.uuid4())
            )
            
            await self.sse_service.broadcast_event(event)
            
        except Exception as e:
            # Log error but don't fail the main operation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to broadcast task created event: {e}")
    
    async def _broadcast_task_updated(
        self, 
        updated_task: TaskResponse, 
        original_task: TaskResponse, 
        changed_fields: Dict[str, Any]
    ) -> None:
        """Broadcast task update event via SSE"""
        if not self.sse_service:
            return
        
        try:
            event = SSEEvent(
                event=SSEEventType.TASK_UPDATED,
                data={
                    "task": updated_task.model_dump(mode='json'),
                    "original_task": original_task.model_dump(mode='json'),
                    "changed_fields": changed_fields,
                    "timestamp": datetime.utcnow().isoformat(),
                    "action": "updated"
                },
                id=str(uuid.uuid4())
            )
            
            await self.sse_service.broadcast_event(event)
            
        except Exception as e:
            # Log error but don't fail the main operation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to broadcast task updated event: {e}")
    
    async def _broadcast_task_deleted(self, deleted_task: TaskResponse) -> None:
        """Broadcast task deletion event via SSE"""
        if not self.sse_service:
            return
        
        try:
            event = SSEEvent(
                event=SSEEventType.TASK_DELETED,
                data={
                    "task": deleted_task.model_dump(mode='json'),
                    "timestamp": datetime.utcnow().isoformat(),
                    "action": "deleted"
                },
                id=str(uuid.uuid4())
            )
            
            await self.sse_service.broadcast_event(event)
            
        except Exception as e:
            # Log error but don't fail the main operation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to broadcast task deleted event: {e}")