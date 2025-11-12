from pathlib import Path
from typing import Literal

from pydantic import (
    BaseModel,
    DirectoryPath,
    Field,
    FilePath,
    SecretStr,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingSettings(BaseModel):
    LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )
    DIR: DirectoryPath = Field(
        default=Path("./logs"),
        description="Path to log files directory",
    )


class IntakeQSettings(BaseModel):
    API_KEY: SecretStr = Field(description="IntakeQ API key")
    BASE_URL: str = Field(description="IntakeQ API base URL")
    EXPORT_PROFILE_ID: str = Field(
        description="IntakeQ export profile ID for patient data"
    )
    CSV_DELIMITER: str = Field(
        default=";", description="IntakeQ export profile ID for patient data"
    )


class S3Settings(BaseModel):
    BUCKET: str = Field(description="S3 bucket name for CSV uploads")
    KEY_PREFIX: str = Field(description="S3 key prefix for uploaded files")
    SIGNED_URL_EXPIRATION: int = Field(description="Signed URL expiration in seconds")


class AWSSettings(BaseModel):
    REGION: str = Field(description="AWS region")


class AppSettings(BaseModel):
    ENV: Literal["local", "production"] = Field(default="local")
    DATA_DIR: DirectoryPath = Field(
        default=Path("./data"), description="Directory for output CSV files"
    )
    INPUT_CSV: FilePath = Field(
        default=Path("./data/intakeq_migration_data.csv"),
        description="CSV file to use as input",
    )

    @property
    def is_local(self) -> bool:
        return self.ENV == "local"


class Settings(BaseSettings):
    APP: AppSettings = Field(default_factory=AppSettings)
    LOG: LoggingSettings = Field(default_factory=LoggingSettings)
    INTAKEQ: IntakeQSettings = Field(default_factory=IntakeQSettings)
    S3: S3Settings = Field(default_factory=S3Settings)
    AWS: AWSSettings = Field(default_factory=AWSSettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        frozen=True,
        extra="ignore",
        env_nested_delimiter="__",
    )


settings = Settings()
