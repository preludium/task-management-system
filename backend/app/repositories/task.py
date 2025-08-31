from typing import List, Optional, Dict, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc, and_, or_, text
from sqlalchemy.orm import selectinload
from app.models.task import Task, TaskStatus
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task, dict, dict]):
    def __init__(self, db: AsyncSession):
        super().__init__(Task, db)
        
    VALID_ORDER_FIELDS = ["id", "title", "status", "created_at", "updated_at"]
    
    DEFAULT_PAGE_SIZE = 12
    MAX_PAGE_SIZE = 100

    async def search_by_title(
        self, 
        search_term: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Task]:
        """Search tasks by title (case-insensitive)"""
        query = select(self.model).where(
            self.model.title.ilike(f"%{search_term}%")
        ).order_by(desc(self.model.created_at))
        
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_tasks_with_advanced_filtering(
        self,
        filters: Dict[str, Any],
        page: int = 1,
        size: int = DEFAULT_PAGE_SIZE,
        order_by: str = "created_at",
        order_direction: str = "desc"
    ) -> tuple[List[Task], int]:
        """
        Advanced filtering method that returns both tasks and total count in a single optimized call.
        This reduces database round trips for better performance on large datasets.
        """
        status = filters.get("status")
        statuses = filters.get("statuses")
        title_contains = filters.get("title_contains")
        
        page = max(1, page)
        size = min(max(1, size), self.MAX_PAGE_SIZE)
        skip = (page - 1) * size
        
        conditions = []
        
        if status is not None:
            conditions.append(self.model.status == status)
        elif statuses is not None and len(statuses) > 0:
            conditions.append(self.model.status.in_(statuses))
        
        if title_contains is not None and title_contains.strip():
            conditions.append(
                self.model.title.ilike(f"%{title_contains.strip()}%")
            )
        
        where_clause = and_(*conditions) if conditions else None
        
        count_query = select(func.count(self.model.id))
        if where_clause is not None:
            count_query = count_query.where(where_clause)
        
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        if total == 0:
            return [], 0
        
        data_query = select(self.model)
        if where_clause is not None:
            data_query = data_query.where(where_clause)
        
        if order_by in self.VALID_ORDER_FIELDS:
            order_column = getattr(self.model, order_by)
            if order_direction.lower() == "desc":
                data_query = data_query.order_by(desc(order_column))
            else:
                data_query = data_query.order_by(asc(order_column))
        else:
            data_query = data_query.order_by(desc(self.model.created_at))
        
        data_query = data_query.offset(skip).limit(size)
        
        data_result = await self.db.execute(data_query)
        tasks = data_result.scalars().all()
        
        return tasks, total
    
    async def get_status_distribution(self) -> Dict[str, int]:
        """
        Optimized method to get task count distribution by status.
        Uses a single query with GROUP BY for better performance.
        """
        query = select(
            self.model.status,
            func.count(self.model.id).label('count')
        ).group_by(self.model.status)
        
        result = await self.db.execute(query)
        
        distribution = {status.value: 0 for status in TaskStatus}
        
        for status, count in result.fetchall():
            distribution[status.value] = count
        
        return distribution
