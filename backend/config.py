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
    # 生产环境使用 PostgreSQL: postgres://postgres:postgres@localhost:5432/fin_tech_mvp
    # 开发环境可使用 SQLite: sqlite://db.sqlite3
    DATABASE_URL: str = "sqlite://db.sqlite3"

    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_URL: Optional[str] = None  # 完整的Redis连接URL (可选)

    # JWT配置 (未来用于认证)
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS配置
    CORS_ORIGINS: list = [
        "http://localhost:3000",  # Next.js 开发服务器
        "http://localhost:8000",  # FastAPI 开发服务器
    ]

    # 虚拟市场配置
    PRICE_GENERATION_ENABLED: bool = True  # 是否启用价格生成

    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建配置实例
settings = Settings()


# Tortoise-ORM 配置
TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.sqlite",
            "credentials": {
                "file_path": "db.sqlite3"
            }
        }
    },
    "apps": {
        "models": {
            "models": [
                "models.user",
                "models.account",
                "models.asset",
                "models.trade",
                "models.holding",
            ],
            "default_connection": "default",
        },
    },
    "use_tz": False,
    "timezone": "Asia/Shanghai",
}
