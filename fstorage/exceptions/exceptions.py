from typing import Optional

from fastapi import status


class APIException(Exception):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: Optional[str] = None

    def __str__(self):
        return f"{self.detail}"


class IncorrectBucketName(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Incorrect bucket name"


class IncorrectFileSize(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "File size exceeds the maximum limit"


class IncorrectFileFormat(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Incorrect file format."


class FileNotUploaded(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "File not uploaded"


class FileNotDeleted(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "File not deleted"


class FileNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "File not found"
