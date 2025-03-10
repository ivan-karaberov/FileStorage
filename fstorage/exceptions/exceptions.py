from typing import Optional

from fastapi import status


class APIException(Exception):
    status_code: Optional[int] = None
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
