"""Application configuration."""
from __future__ import annotations

from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    environment: Literal["development", "production", "test"] = "development"
    debug: bool = False

    # Build settings
    build_timeout: int = 120
    max_html_size: int = 512_000  # 512 KB
    build_workers: int = 2

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl: int = 3600  # 1 hour

    # Rate limiting
    rate_limit_builds: str = "5/minute"
    rate_limit_downloads: str = "60/minute"

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # PlatformIO
    platformio_home: str = "/root/.platformio"

    # Firmware output
    firmware_dir: str = "/tmp/firmware"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


settings = Settings()
