from fastapi import APIRouter, Request, Depends
from typing import Optional
import logging
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/reset-database")
async def reset_database(db: AsyncSession = Depends(get_db)):
    """
    Endpoint to reset the database state for testing.
    This should be disabled in production.

    Ideally e2e tests should be in a separate package with e.g. pg library handling database operations.
    """
    async with db as session:
        await session.execute(text("TRUNCATE TABLE tasks RESTART IDENTITY CASCADE;"))
        await session.commit()

    logger.info("Database has been purged")

    return {"message": "Database reset successful"}