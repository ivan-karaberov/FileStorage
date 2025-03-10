import io
from abc import ABC, abstractmethod


class S3Storage(ABC):
    @abstractmethod
    def upload_file(
        self, file: str | io.BytesIO, bucket_name: str, object_name: str, file_size: int
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_file_link(self, bucket_name: str, object_name: str) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def delete_file(self, file: str, object_name: str) -> bool:
        raise NotImplementedError
