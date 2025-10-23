"""
FastAPI 应用主文件
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from contextlib import asynccontextmanager

from config import settings, TORTOISE_ORM
from exceptions import TradingException


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时初始化数据库，关闭时清理资源
    """
    # 启动时执行
    print("🚀 Starting up...")
    print(f"📊 Database: {settings.DATABASE_URL}")
    yield
    # 关闭时执行
    print("🛑 Shutting down...")


# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="模拟交易系统 API",
    lifespan=lifespan,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 Tortoise-ORM
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,  # 自动生成数据库表结构
    add_exception_handlers=True,  # 添加异常处理
)


# 全局异常处理器
@app.exception_handler(TradingException)
async def trading_exception_handler(request: Request, exc: TradingException):
    """
    处理交易相关的业务异常
    """
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
            },
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    处理其他未捕获的异常
    """
    # 在生产环境中，不应该暴露详细的错误信息
    if settings.DEBUG:
        error_detail = str(exc)
    else:
        error_detail = "Internal server error"

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": error_detail,
            },
        },
    )


# 根路径
@app.get("/")
async def root():
    """API 根路径"""
    return {
        "success": True,
        "message": "Welcome to happyStock Trading API",
        "version": settings.APP_VERSION,
    }


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "success": True,
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# 导入路由
from routers import accounts, assets

# 注册 API 路由
app.include_router(accounts.router, prefix="/api/v1", tags=["账户管理"])
app.include_router(assets.router, prefix="/api/v1", tags=["资产管理"])
# app.include_router(trades.router, prefix="/api/v1", tags=["交易"])
# app.include_router(holdings.router, prefix="/api/v1", tags=["持仓"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
