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
from lib.db_manager_sqlite import get_db_manager
from scheduler.jobs import start_scheduler, shutdown_scheduler
from lib.websocket_manager import get_connection_manager
from lib.redis_pubsub import get_redis_pubsub, close_redis_pubsub


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时初始化数据库和调度器，关闭时清理资源
    """
    # 启动时执行
    print("Starting up...")
    print(f"Database URL (raw): {settings.DATABASE_URL}")
    print(f"Database URL (resolved): {settings.resolved_database_url}")

    # 初始化虚拟市场数据库连接池 (PostgreSQL)
    db_manager = get_db_manager()
    db_manager.initialize()

    # 测试连接
    if db_manager.health_check():
        print("[+] Virtual market database connection healthy")
    else:
        print("[!] Virtual market database connection failed")

    # 启动定时任务调度器
    print("[*] Starting price generation scheduler...")
    start_scheduler()
    print("[+] Scheduler started successfully")
    
    # 初始化 WebSocket 管理器和 Redis Pub/Sub
    print("[*] Initializing WebSocket manager and Redis Pub/Sub...")
    try:
        # 获取 Redis Pub/Sub 实例 (自动连接)
        pubsub = await get_redis_pubsub()
        print("[+] Redis Pub/Sub connected")
        
        # 启动 WebSocket 心跳检测
        manager = get_connection_manager()
        await manager.start_heartbeat_checker()
        print("[+] WebSocket heartbeat checker started")
        
    except Exception as e:
        print(f"[!] Failed to initialize real-time push: {e}")

    yield

    # 关闭时执行
    print("Shutting down...")
    
    # 停止 WebSocket 心跳检测
    print("[*] Stopping WebSocket heartbeat checker...")
    manager = get_connection_manager()
    await manager.stop_heartbeat_checker()
    
    # 关闭 Redis Pub/Sub
    print("[*] Closing Redis Pub/Sub...")
    await close_redis_pubsub()
    
    # 关闭调度器
    print("[*] Stopping scheduler...")
    shutdown_scheduler()
    
    # 关闭数据库
    db_manager.close()


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
from routers import accounts, assets, trades, holdings, klines, auth
from api import stocks as virtual_market_stocks
from api import indices as virtual_market_indices
from api import sectors as virtual_market_sectors
from api import market as virtual_market_market
from api import websocket as websocket_api

# 注册 API 路由
app.include_router(auth.router, prefix="/api", tags=["认证"])
app.include_router(accounts.router, prefix="/api/v1", tags=["账户管理"])
app.include_router(assets.router, prefix="/api/v1", tags=["资产管理"])
app.include_router(trades.router, prefix="/api/v1", tags=["交易管理"])
app.include_router(holdings.router, prefix="/api/v1", tags=["持仓管理"])
app.include_router(klines.router, prefix="/api/v1", tags=["K线数据"])

# 虚拟市场API路由
app.include_router(virtual_market_stocks.router, prefix="/api/v1", tags=["虚拟市场-股票"])
app.include_router(virtual_market_indices.router, prefix="/api/v1", tags=["虚拟市场-指数"])
app.include_router(virtual_market_sectors.router, prefix="/api/v1", tags=["虚拟市场-板块"])
app.include_router(virtual_market_market.router, prefix="/api/v1", tags=["虚拟市场-市场"])

# WebSocket API路由 (实时数据推送)
app.include_router(websocket_api.router, prefix="/api/v1", tags=["实时数据推送"])


@app.get("/debug/routes")
async def list_all_routes():
    """调试端点：列出所有注册的路由"""
    routes = []
    for route in app.routes:
        route_info = {
            "path": route.path,
            "name": getattr(route, "name", "unknown"),
            "methods": list(getattr(route, "methods", [])) if hasattr(route, "methods") else ["WEBSOCKET"] if "websocket" in route.path.lower() else []
        }
        routes.append(route_info)
    return {"total": len(routes), "routes": routes}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        timeout_keep_alive=5,  # 减少 keep-alive 超时
        limit_concurrency=100,  # 限制并发连接数
    )
