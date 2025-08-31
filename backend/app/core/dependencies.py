from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db


class PaginationParams:
    """Pagination parameters for list endpoints"""
    
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number (1-based)"),
        size: int = Query(10, ge=1, le=100, description="Items per page")
    ):
        self.page = page
        self.size = size
        self.skip = (page - 1) * size
        self.limit = size


async def get_pagination(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    size: int = Query(10, ge=1, le=100, description="Items per page")
) -> PaginationParams:
    """Dependency for pagination parameters"""
    return PaginationParams(page=page, size=size)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency with proper error handling"""
    session = None
    try:
        async for session in get_db():
            yield session
    except Exception as e:
        if session:
            await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        ) from e


CommonDeps = {
    "db": Depends(get_db_session),
    "pagination": Depends(get_pagination)
}