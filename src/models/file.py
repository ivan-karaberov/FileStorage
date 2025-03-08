import uuid

from sqlalchemy import String, DateTime, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class File(Base):
    id: Mapped[str] = mapped_column(
        String(36), unique=True, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    object_id: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, index=True
    )
    object_name: Mapped[str] = mapped_column(
        String(40), unique=True, nullable=False
    )
    backet_name: Mapped[str] = mapped_column(String(40), nullable=False)
    upload_at: Mapped[DateTime] = mapped_column(
        TIMESTAMP(timezone=True), default=func.now(), server_default=func.now()
    )
