"""
配置文件
包含数据库连接、Redis连接等配置信息
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""

    # 应用基础配置
    APP_NAME: str = "happyStock Trading API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库配置
    DATABASE_URL: str = "postgres://postgres:postgres@localhost:5432/fin_tech_mvp"

    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # JWT配置 (未来用于认证)
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS配置
    CORS_ORIGINS: list = [
        "http://localhost:3000",  # Next.js 开发服务器
        "http://localhost:8000",  # FastAPI 开发服务器
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建配置实例
settings = Settings()


# Tortoise-ORM 配置
TORTOISE_ORM = {
    "connections": {
        "default": settings.DATABASE_URL
    },
    "apps": {
        "models": {
            "models": [
                "models.user",
                "models.account",
                "models.asset",
                "models.trade",
                "models.holding",
                "aerich.models",  # 数据库迁移工具
            ],
            "default_connection": "default",
        },
    },
    "use_tz": False,
    "timezone": "Asia/Shanghai",
}
