from typing import Optional

from pydantic import BaseModel


class ResponseUploadSchema(BaseModel):
    permanent_link: Optional[str]
    object_id: str


class ResponseDeleteSchema(BaseModel):
    status: bool


class ResponseLinkSchema(BaseModel):
    link: str
