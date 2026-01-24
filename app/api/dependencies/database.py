# Database session dependency
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal


async def get_db_session() -> AsyncSession:
    """Get database session dependency"""
    async with AsyncSessionLocal() as session:
        yield session
