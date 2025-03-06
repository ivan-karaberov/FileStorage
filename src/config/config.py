from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="config/.env", env_file_encoding="utf-8", extra="ignore"
    )


class MinioConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix="minio_")

    host: str
    port: int
    access_key: str
    secret_key: str


class Config(BaseSettings):
    minio: MinioConfig = Field(default_factory=MinioConfig)
