"""Configuration settings for the Data Analytics Dashboard API."""

import json
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Data Analytics Dashboard API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Business Intelligence Dashboard with ETL and Analytics"

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    # Logging
    LOG_LEVEL: str = "INFO"

    # CORS
    ALLOW_CORS_CREDENTIALS: bool = True

    # Job Scheduling
    ENABLE_SCHEDULER: bool = True
    DATA_REFRESH_INTERVAL_HOURS: int = 24

    # Cache TTL (seconds)
    CACHE_TTL_SHORT: int = 300  # 5 minutes
    CACHE_TTL_MEDIUM: int = 1800  # 30 minutes
    CACHE_TTL_LONG: int = 3600  # 1 hour

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | List[str]) -> List[str]:
        """Allow either JSON arrays or comma-separated origins in env vars."""
        if isinstance(value, list):
            return value
        if not value:
            return []

        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            parsed = None

        if isinstance(parsed, list):
            return [str(origin).strip() for origin in parsed if str(origin).strip()]

        return [origin.strip() for origin in value.split(",") if origin.strip()]


settings = Settings()
