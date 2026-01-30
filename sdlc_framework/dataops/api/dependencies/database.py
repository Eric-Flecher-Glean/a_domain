"""Database session dependency."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from ...infrastructure.persistence.database import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency.

    Usage in route:
        async def my_route(db: AsyncSession = Depends(get_db)):
            # Use db session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
