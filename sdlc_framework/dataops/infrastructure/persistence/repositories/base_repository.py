"""Base repository with common CRUD operations."""

from typing import Generic, TypeVar, Type, Optional, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import Base

T = TypeVar('T', bound=Base)


class BaseRepository(Generic[T]):
    """Base repository providing common database operations."""

    def __init__(self, session: AsyncSession, model_class: Type[T]):
        self.session = session
        self.model_class = model_class

    async def get_by_id(self, entity_id: UUID) -> Optional[T]:
        """Retrieve entity by ID."""
        result = await self.session.execute(
            select(self.model_class).where(self.model_class.id == entity_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """List all entities with pagination."""
        result = await self.session.execute(
            select(self.model_class)
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def save(self, entity: T) -> T:
        """Save entity (insert or update)."""
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity: T) -> None:
        """Delete entity."""
        await self.session.delete(entity)
        await self.session.flush()

    async def count(self) -> int:
        """Count total entities."""
        from sqlalchemy import func
        result = await self.session.execute(
            select(func.count()).select_from(self.model_class)
        )
        return result.scalar()
