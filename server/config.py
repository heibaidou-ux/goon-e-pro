from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    app_name: str = "高岸ERP API Server"
    version: str = "V1.0"
    debug: bool = True

    # Database
    database_url: str = "sqlite+aiosqlite:///./gaoan_erp.db"

    # JWT
    secret_key: str = "gaoan-erp-secret-key-change-in-production-2026"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480  # 8 hours
    refresh_token_expire_days: int = 7
    # Security (relaxed in dev, tighten for production)
    cors_allow_credentials: bool = False
    csrf_enabled: bool = False
    rate_limit_enabled: bool = False
    rate_limit_per_minute: int = 60

    # File uploads
    upload_dir: str = str(Path(__file__).parent / "uploads")
    max_upload_size_mb: int = 10
    thumbnail_sizes: list[int] = [240, 480, 800]

    # CORS
    cors_origins: list[str] = ["*"]

    # Home Assistant
    ha_url: str = "http://localhost:8123"
    ha_token: str = ""  # Set to empty for mock mode

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
