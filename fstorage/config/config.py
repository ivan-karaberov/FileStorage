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


class Config(BaseSettings):
    minio: MinioConfig = Field(default_factory=MinioConfig)
    db: DatabaseConfig = Field(default_factory=DatabaseConfig)
