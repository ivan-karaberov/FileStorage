import io
import logging
from datetime import timedelta

from minio.error import S3Error

from .storage import S3Storage


logger = logging.getLogger(__name__)


class MinioS3Storage(S3Storage):
    def __init__(self, minio_client) -> None:
        self.minio_client = minio_client

    def upload_file(
        self, file: str | io.BytesIO, bucket_name: str, object_name: str, file_size: int
    ) -> bool:
        try:
            if not self.minio_client.bucket_exists(bucket_name):
                self.minio_client.make_bucket(bucket_name)

            if isinstance(file, str):
                self.minio_client.fput_obect(bucket_name, object_name, file)
            else:
                self.minio_client.put_object(bucket_name, object_name, file, file_size)

            return True

        except S3Error as e:
            logger.error("Unsuccessful file upload to MinIO: %s", e)
            return False

        except Exception as e:
            logger.error("An unexpected error occurred: %s", e)
            return False

    def get_file_link(self, bucket_name: str, object_name: str, ttl: timedelta) -> str | None:
        try:
            link = self.minio_client.presigned_get_object(
                bucket_name=bucket_name,
                object_name=object_name,
                expires=ttl
            )
            return link

        except S3Error as e:
            logger.error("Unsuccessful getting file from MinIO: %s", e)
            return None

        except Exception as e:
            logger.error("An unexpected error occured: %s", e)
            return None

    def delete_file(self, bucket_name: str, object_name: str) -> bool:
        try:
            self.minio_client.remove_object(bucket_name, object_name)
            return True

        except S3Error as e:
            logger.error("Unsuccessful file delete in MinIO: %s", e)
            return False

        except Exception as e:
            logger.error("An unexpected error occurred: %s", e)
            return False
