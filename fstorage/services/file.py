import io
import logging
from datetime import timedelta

from config import settings
from repositories.file import FileRepository
from models.file import File
from storage.storage import S3Storage
from schemas.file import ResponseUploadSchema
from exceptions.exceptions import FileNotUploaded, FileNotFound, FileNotDeleted, \
                                    FailedLinkGeneration

logger = logging.getLogger(__name__)


class FileService:
    def __init__(self, file_repository: FileRepository, storage_client: S3Storage) -> None:
        self.storage_client = storage_client
        self.file_repository = file_repository

    async def upload_file(
        self,
        file: str | io.BytesIO,
        user_id: str,
        bucket_name: str,
        object_name: str,
        file_size: int
    ) -> ResponseUploadSchema:
        status = self.storage_client.upload_file(file, bucket_name, object_name, file_size)

        if status:
            permanent_link = None
            object_id = object_name.split(".")[0]

            file_metadata = File(
                user_id=user_id,
                object_id=object_id,
                object_name=object_name,
                bucket_name=bucket_name
            )

            if not await self.file_repository.add_one(file_metadata):
                self.storage_client.delete_file(bucket_name, object_name)
                logger.error(
                    "Failed writing metadata to db: \
                    user_id > %s | object_id > %s | obejct_name > %s",
                    user_id, object_id, object_name
                )
                raise FileNotUploaded

            bucket_settings = settings.app.file_upload_validation_settings.get(bucket_name)
            if bucket_settings and bucket_settings.get("is_public", False):
                permanent_link = f"{settings.minio.minio_url}/{bucket_name}/{object_name}"

            logger.info(
                "user -> %s | loaded file to bucket -> %s | object_id -> %s",
                user_id, bucket_name, object_id
            )

            return ResponseUploadSchema(
                permanent_link=permanent_link,
                object_id=object_id
            )
        else:
            raise FileNotUploaded

    async def get_file_link(self, bucket_name: str, object_id: str, ttl: timedelta):
        file_obj = await self.file_repository.fetch_one(object_id=object_id)

        if file_obj is None:
            raise FileNotFound

        link = self.storage_client.get_file_link(
            bucket_name=bucket_name,
            object_name=file_obj.object_name,
            ttl=ttl
        )

        if link is None:
            raise FailedLinkGeneration

        return link

    async def delete_file(self, user_id: str, bucket_name: str, object_id: str) -> bool:
        file_obj = await self.file_repository.fetch_one(object_id=object_id)

        if file_obj is None:
            raise FileNotFound

        if await self.file_repository.delete_one(file_obj):
            delete_status = self.storage_client.delete_file(bucket_name, file_obj.object_name)
            if not delete_status:
                logger.error("File Delete from db, but not delete from minio > %s", )
                raise FileNotDeleted
            logger.info(
                "user -> %s | delete file from bucket -> %s | object_id -> %s",
                user_id, bucket_name, object_id
            )
            return True
        else:
            logger.error(
                "Failed delete metadata from db: \
                user_id > %s | object_id > %s | obejct_name > %s",
                user_id, object_id, file_obj.object_name
            )
            return False
