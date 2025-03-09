from sqlalchemy.ext.asyncio import AsyncSession

from .repository import SQLAlchemyRepository
from models.file import File


class FileRepository(SQLAlchemyRepository[File]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model=File)
