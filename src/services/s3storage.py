import logging
from abc import ABC, abstractmethod

from minio.error import S3Error

logger = logging.getLogger(__name__)


class AbstractS3Storage(ABC):
    @abstractmethod
    def upload_file(self, file: str, bucket_name: str, object_name: str) -> bool:
        raise NotImplementedError


class MinioStorage(AbstractS3Storage):
    def __init__(self, minio_client) -> None:
        self.minio_client = minio_client

    def upload_file(
            self,
            file: str,
            bucket_name: str,
            object_name: str
    ) -> bool:
        try:
            if not self.minio_client.bucket_exists(bucket_name):
                self.minio_client.make_bucket(bucket_name)

            self.minio_client.fput_object(bucket_name, object_name, file)

            return True

        except S3Error as e:
            logger.error("Unsuccessful file upload to MinIO: %s", e)
            return False

        except Exception as e:
            logger.error("An unexpected error occurred: %s", e)
            return False
