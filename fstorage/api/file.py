import os
import io
import uuid
import logging
from datetime import timedelta

from fastapi import APIRouter, File, Body, UploadFile, status
from fastapi.exceptions import HTTPException

from config import settings
from dependencies.file import FileDependency
from schemas.file import ResponseUploadSchema, ResponseDeleteSchema, ResponseLinkSchema
from exceptions.exceptions import APIException, IncorrectBucketName, IncorrectFileSize, \
                                    IncorrectFileFormat, FileNotUploaded, FileNotFound, \
                                    FileNotDeleted, FailedLinkGeneration

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    path="/{bucket_name}/upload",
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
    bucket_name: str,
    file_service: FileDependency,
    user_id: str = Body(embed=True),
    file: UploadFile = File(...)
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


@router.get(
    path="/{bucket_name}/{object_id}",
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
                        "FailedLinkGeneration": {
                            "value": {"detail": FailedLinkGeneration.detail}
                        },
                        "FileNotFound": {
                            "value": {"detail": FileNotFound.detail}
                        },
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
                                "example": "An unexpected error occurred. Failed generation link"
                            }
                        }
                    }
                }
            }
        }
    },
    summary="Generate temporary link",
    response_description="Temporary link"
)
async def get_file_link(
    bucket_name: str,
    object_id: str,
    file_service: FileDependency
) -> ResponseLinkSchema:
    bucket_settings = settings.app.file_upload_validation_settings.get(bucket_name)

    # check bucket name
    if bucket_settings is None:
        raise IncorrectBucketName

    try:
        link = await file_service.get_file_link(
            bucket_name,
            object_id,
            ttl=timedelta(hours=settings.app.temporary_link_ttl)
        )
        return ResponseLinkSchema(link=link)
    except APIException as e:
        raise e
    except Exception as e:
        logger.error("Failed generation link | error > %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Failed generation link"
        )


@router.delete(
    path="/{bucket_name}/{object_id}",
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
                        "FileNotFound": {
                            "value": {"detail": FileNotFound.detail}
                        },
                        "FileNotDeleted": {
                            "value": {"detail": FileNotDeleted.detail}
                        },
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
                                "example": "An unexpected error occurred. File not deleted"
                            }
                        }
                    }
                }
            }
        }
    },
    summary="Delete file from S3 Storage",
    response_description="Operation status"
)
async def delete_file(
    bucket_name: str,
    object_id: str,
    file_service: FileDependency,
    user_id: str = Body(embed=True)
) -> ResponseDeleteSchema:
    try:
        delete_status = await file_service.delete_file(user_id, bucket_name, object_id)
        return ResponseDeleteSchema(status=delete_status)
    except APIException as e:
        raise e
    except Exception as e:
        logger.error("File not deleted | error > %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. File not deleted"
        )
