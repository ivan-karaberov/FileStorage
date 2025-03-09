import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class Repository[T](ABC):
    @abstractmethod
    async def add_one(self, obj: T) -> str | None:
        raise NotImplementedError

    @abstractmethod
    async def fetch_one(self, **filters) -> T | None:
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, obj: T) -> bool:
        raise NotImplementedError


class SQLAlchemyRepository[T](Repository):
    def __init__(self, session: AsyncSession, model: type[T]) -> None:
        self.session = session
        self.model = model

    async def add_one(self, obj: T) -> str | None:
        try:
            self.session.add(obj)
            await self.session.commit()
            return obj.id if hasattr(obj, "id") else ""
        except Exception as e:
            await self.session.rollback()
            logger.error("SQLAlchemyRepository failed add_one > %s", e)
            return None

    async def fetch_one(self, **filters) -> T | None:
        try:
            query = select(self.model).filter_by(**filters).limit(1)
            obj = await self.session.execute(query)
        except Exception as e:
            await self.session.rollback()
            logger.error("SQLAlchemyRepository failed fetch_one > %s", e)

        return obj.scalar_one_or_none()

    async def delete_one(self, obj: T) -> bool:
        try:
            await self.session.delete(obj)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error("SQLAlchemyRepository failed delete_one > %s", e)
            return False
