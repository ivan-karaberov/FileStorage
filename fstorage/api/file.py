import os
import io
import uuid
import logging

from fastapi import APIRouter, File, UploadFile, status
from fastapi.exceptions import HTTPException

from config import settings
from dependencies.file import FileDependency
from schemas.file import ResponseUploadSchema
from exceptions.exceptions import APIException, IncorrectBucketName, IncorrectFileSize, \
                                    IncorrectFileFormat, FileNotUploaded

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    path="/{user_id}/{bucket_name}/upload",
    responses={
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "detail": {
                                "type": "string",
                            }
                        }
                    },
                    "examples": {
                        "IncorrectBucketName": {
                            "value": {"detail": IncorrectBucketName.detail}
                        },
                        "IncorrectFileSize": {
                            "value": {"detail": IncorrectFileSize.detail}
                        },
                        "IncorrectFileFormat": {
                            "value": {"detail": IncorrectFileFormat.detail}
                        },
                        "FileNotUploaded": {
                            "value": {"detail": FileNotUploaded.detail}
                        }
                    }
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "detail": {
                                "type": "string",
                                "example": "An unexpected error occurred. File not uploaded"
                            }
                        }
                    }
                }
            }
        }
    },
    summary="Upload file to S3 Storage",
    response_description="Object ID and Permanent link (if bucket is public)"
)
async def upload_file(
    user_id: str, bucket_name: str, file_service: FileDependency, file: UploadFile = File(...)
) -> ResponseUploadSchema:
    bucket_settings = settings.app.file_upload_validation_settings.get(bucket_name)

    # check bucket name
    if bucket_settings is None:
        raise IncorrectBucketName

    # check file size
    max_length = bucket_settings.get("max_length", 0)
    if not isinstance(max_length, int):
        raise ValueError(f"Incorrect type for max_length {type(max_length)}")
    file_size = file.size if file.size else 0
    if max_length < file_size:
        raise IncorrectFileSize

    # check file format
    _, file_format = os.path.splitext(str(file.filename))
    allowed_formats = bucket_settings.get("allowed_formats")
    if not isinstance(allowed_formats, list):
        raise ValueError(f"Incorrect type for allowed_formats {type(allowed_formats)}")
    if allowed_formats is not None and file_format not in allowed_formats:
        raise IncorrectFileFormat

    try:
        filename = str(uuid.uuid4()) + str(file_format)
        file_bytes = io.BytesIO(await file.read())
        return await file_service.upload_file(
            file=file_bytes,
            user_id=user_id,
            bucket_name=bucket_name,
            object_name=filename,
            file_size=file_size
        )
    except APIException as e:
        raise e
    except Exception as e:
        logger.error("File not uploaded | error > %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. File not uploaded"
        )
