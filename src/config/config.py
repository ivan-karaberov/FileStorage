from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="config/.env", env_file_encoding="utf-8", extra="ignore"
    )


class KafkaConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix="kafka_")

    host: str = "localhost"
    port: int = 9092


class MinioConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix="minio_")


class Config(BaseSettings):
    kafka: KafkaConfig = Field(default_factory=KafkaConfig)
    minio: MinioConfig = Field(default_factory=MinioConfig)
