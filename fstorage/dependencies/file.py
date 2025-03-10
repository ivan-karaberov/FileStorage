from typing import Annotated

from minio import Minio
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings, db_helper
from services.file import FileService
from repositories.file import FileRepository
from storage.minio import MinioS3Storage


def get_minio_client() -> Minio:
    return Minio(
        endpoint=settings.minio.minio_url,
        access_key=settings.minio.access_key,
        secret_key=settings.minio.secret_key,
        secure=settings.minio.secure
    )


DBSessionDependency = Annotated[AsyncSession, Depends(db_helper.get_session_dependency)]
MinioDependecy = Annotated[Minio, Depends(get_minio_client)]


def file_service(session: DBSessionDependency, minio: MinioDependecy) -> FileService:
    return FileService(FileRepository(session), MinioS3Storage(minio))


FileDependency = Annotated[FileService, Depends(file_service)]
