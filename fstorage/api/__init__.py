from fastapi import APIRouter

from .file import router as files_api

router = APIRouter()

router.include_router(files_api, prefix="/files", tags=["Files"])
