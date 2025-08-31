from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from pydantic import BaseModel

from app.repositories.base import BaseRepository

ModelType = TypeVar("ModelType", bound=DeclarativeBase)
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, RepositoryType, CreateSchemaType, UpdateSchemaType]):
    """Base service class with common business logic operations"""
    
    def __init__(
        self,
        repository_class: Type[RepositoryType],
        model_class: Type[ModelType],
        db: AsyncSession
    ):
        self.repository = repository_class(model_class, db)
        self.db = db
    
    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get a single record by ID"""
        return await self.repository.get(id)
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count total records with optional filtering"""
        return await self.repository.count(filters=filters)
    
    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record with business logic validation"""
        # Subclasses can override this method to add business logic
        await self._validate_create(obj_in)
        return await self.repository.create(obj_in)
    
    async def update(self, id: int, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        """Update an existing record with business logic validation"""
        # Check if record exists
        existing = await self.repository.get(id)
        if not existing:
            return None
        
        # Subclasses can override this method to add business logic
        await self._validate_update(id, obj_in, existing)
        return await self.repository.update(id, obj_in)
    
    async def delete(self, id: int) -> bool:
        """Delete a record by ID with business logic validation"""
        # Check if record exists
        existing = await self.repository.get(id)
        if not existing:
            return False
        
        # Subclasses can override this method to add business logic
        await self._validate_delete(id, existing)
        return await self.repository.delete(id)
    
    async def _validate_create(self, obj_in: CreateSchemaType) -> None:
        """Override in subclasses to add create validation logic"""
        pass
    
    async def _validate_update(self, id: int, obj_in: UpdateSchemaType, existing: ModelType) -> None:
        """Override in subclasses to add update validation logic"""
        pass
    
    async def _validate_delete(self, id: int, existing: ModelType) -> None:
        """Override in subclasses to add delete validation logic"""
        pass