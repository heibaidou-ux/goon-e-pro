from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "高岸ERP API Server"
    version: str = "V1.1"
    debug: bool = False

    # Database
    database_url: str = "sqlite+aiosqlite:///./gaoan_erp.db"

    # JWT — 生产环境必须通过环境变量覆盖
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30  # 30分钟
    refresh_token_expire_days: int = 7

    # Security
    cors_origins: list[str] = []  # 生产必须填写具体域名
    csrf_enabled: bool = True
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60
    login_rate_limit_per_minute: int = 5  # 登录接口更严格

    # File uploads
    upload_dir: str = str(Path(__file__).parent / "uploads")
    max_upload_size_mb: int = 10
    thumbnail_sizes: list[int] = [240, 480, 800]

    # WeChat Mini Program
    wechat_appid: str = "wx181568857908b5ae"
    wechat_secret: str = ""

    # Home Assistant
    ha_url: str = "http://localhost:8123"
    ha_token: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# 运行时校验
if not settings.debug:
    if not settings.secret_key or len(settings.secret_key) < 32:
        raise ValueError("❌ 生产环境必须设置 SECRET_KEY 且长度≥32字符")
    if not settings.cors_origins:
        raise ValueError("❌ 生产环境必须设置 CORS_ORIGINS（允许的域名列表）")
