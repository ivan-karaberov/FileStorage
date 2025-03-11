import logging
from typing import Union
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent.parent
ENV_FILE = BASE_DIR / "config" / ".env"


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore"
    )


class DatabaseConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix="db_")

    host: str
    port: int
    name: str
    user: str
    passwd: str
    echo: bool = False

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.passwd}@{self.host}:{self.port}/{self.name}"


class MinioConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix="minio_")

    host: str
    port: int
    access_key: str
    secret_key: str
    secure: bool = False

    @property
    def minio_url(self) -> str:
        return f"{self.host}:{self.port}"


class AppConfig(BaseSettings):
    file_upload_validation_settings: dict[str, dict[str, Union[int, list[str], bool]]] = {
        "avatar": {
            "max_length": 5 * 1024 * 1024,  # 5 MB
            "allowed_formats": [".jpg", ".png"],
            "is_public": True  # Affects permalink generation, not affect container settings
        },
        "video": {
            "max_length": 100 * 1024 * 1024,  # 100 MB
            "allowed_formats": [".mp4", ".mkv", ".mov", ".avi"],
            "is_public": False  # Affects permalink generation, not affect container settings
        }
    }

    temporary_link_ttl: int = 12  # hours


class LoggingConfig(BaseSettings):
    logging_level: int = logging.INFO

    def configure_logging(self):
        logging.basicConfig(
            level=self.logging_level,
            datefmt="%Y-%m-%d %H:%M:%S",
            format="[%(asctime)s.%(msecs)03d] %(module)s:%(lineno)d %(levelname)s - %(message)s",
        )


class Config(BaseSettings):
    app: AppConfig = AppConfig()
    logger: LoggingConfig = LoggingConfig()
    minio: MinioConfig = Field(default_factory=MinioConfig)
    db: DatabaseConfig = Field(default_factory=DatabaseConfig)
