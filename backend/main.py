"""
FastAPI 搴旂敤涓绘枃浠?
"""
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from contextlib import asynccontextmanager
from config import settings, TORTOISE_ORM
from exceptions import TradingException, EmailException, RateLimitExceededError
from lib.db_manager_sqlite import get_db_manager
from scheduler.jobs import start_scheduler, shutdown_scheduler
from lib.websocket_manager import get_connection_manager
from lib.redis_pubsub import get_redis_pubsub, close_redis_pubsub

try:
    from sim.unit_of_work import create_pool
except ImportError:  # pragma: no cover
    create_pool = None  # type: ignore

try:
    from sim.cache import SimulationCache
    from sim.worker import SimulationWorker
    from sim.services import SimulationService
    from sim.repositories import (
        AgentLogRepository,
        SimulationRepository,
        MarketStateRepository,
        OrderTradeRepository,
    )
    from sim.feature_service import FeatureService
    from sim.emotion_service import EmotionService
    from sim.tasks import FeatureCalibrationTask
    from sim.agents import AgentRegistry
except ImportError:  # pragma: no cover
    SimulationCache = None  # type: ignore
    SimulationWorker = None  # type: ignore
    SimulationService = None  # type: ignore
    FeatureService = None  # type: ignore
    EmotionService = None  # type: ignore
    FeatureCalibrationTask = None  # type: ignore
    AgentRegistry = None  # type: ignore


async def _feature_calibration_loop(task: FeatureCalibrationTask, interval_seconds: int) -> None:
    """Run the feature calibration task periodically."""
    try:
        while True:
            await task.run()
            await asyncio.sleep(interval_seconds)
    except asyncio.CancelledError:
        pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    搴旂敤鐢熷懡鍛ㄦ湡绠＄悊
    鍚姩鏃跺垵濮嬪寲鏁版嵁搴撳拰璋冨害鍣紝鍏抽棴鏃舵竻鐞嗚祫婧?
    """
    if not hasattr(app.state, "sim_pool"):
        app.state.sim_pool = None
    if not hasattr(app.state, "sim_cache"):
        app.state.sim_cache = None
    if not hasattr(app.state, "sim_worker"):
        app.state.sim_worker = None
    if not hasattr(app.state, "sim_agent_registry"):
        app.state.sim_agent_registry = None
    if not hasattr(app.state, "sim_feature_service"):
        app.state.sim_feature_service = None
    if not hasattr(app.state, "sim_emotion_service"):
        app.state.sim_emotion_service = None
    if not hasattr(app.state, "sim_feature_task"):
        app.state.sim_feature_task = None

    # 鍚姩鏃舵墽琛?

    print("Starting up...")
    print(f"Database URL (raw): {settings.DATABASE_URL}")
    print(f"Database URL (resolved): {settings.resolved_database_url}")

    db_manager = None
    if settings.PRICE_GENERATION_ENABLED:
        # 鍒濆鍖栬櫄鎷熷競鍦烘暟鎹簱杩炴帴姹?(PostgreSQL)
        db_manager = get_db_manager()
        db_manager.initialize()

        # 娴嬭瘯杩炴帴
        if db_manager.health_check():
            print("[+] Virtual market database connection healthy")
        else:
            print("[!] Virtual market database connection failed")

        # 鍚姩瀹氭椂浠诲姟璋冨害鍣?
        print("[*] Starting price generation scheduler...")
        start_scheduler()
        print("[+] Scheduler started successfully")
    else:
        print("[*] PRICE_GENERATION_ENABLED is False; skipping SQLite init and scheduler startup.")
    
    # 鍒濆鍖?WebSocket 绠＄悊鍣ㄥ拰 Redis Pub/Sub
    print("[*] Initializing WebSocket manager and Redis Pub/Sub...")
    try:
        # 鑾峰彇 Redis Pub/Sub 瀹炰緥 (鑷姩杩炴帴)
        pubsub = await get_redis_pubsub()
        print("[+] Redis Pub/Sub connected")
        
        # 鍚姩 WebSocket 蹇冭烦妫€娴?
        manager = get_connection_manager()
        await manager.start_heartbeat_checker()
        print("[+] WebSocket heartbeat checker started")
        
    except Exception as e:
        print(f"[!] Failed to initialize real-time push: {e}")

    # 鍒濆鍖栫幇鏈夋搷浣滀簨鍔°€佹暟鎹簱
    if create_pool is not None:
        try:
            sim_pool = await create_pool(settings.sim_database_url)
            app.state.sim_pool = sim_pool
            print("[+] Simulation database pool ready")
        except Exception as exc:
            print(f"[!] Simulation database initialization skipped: {exc}")
    else:
        print("[!] asyncpg 未安装，跳过仿真数据库初始化")

    if SimulationCache is not None and settings.SIM_REDIS_URL:
        try:
            sim_cache = await SimulationCache.create(settings.SIM_REDIS_URL)
            app.state.sim_cache = sim_cache
            print("[+] Simulation Redis cache ready")
        except Exception as exc:
            print(f"[!] Simulation cache initialization skipped: {exc}")
    elif SimulationCache is None:
        print("[!] redis[asyncio] 未安装，跳过仿真缓存初始化")

    if app.state.sim_pool and FeatureService is not None:
        app.state.sim_feature_service = FeatureService(app.state.sim_pool)
        print("[+] Simulation feature service ready")

    if (
        EmotionService is not None
        and settings.SIM_REDIS_URL
        and app.state.sim_pool
    ):
        try:
            emotion_service = await EmotionService.create(
                settings.SIM_REDIS_URL,
                pool=app.state.sim_pool,
            )
            app.state.sim_emotion_service = emotion_service
            print("[+] Simulation emotion service ready")
        except Exception as exc:
            print(f"[!] Simulation emotion service initialization skipped: {exc}")

    if settings.SIM_AGENTS_ENABLED and AgentRegistry is not None and app.state.sim_agent_registry is None:
        registry = AgentRegistry()
        app.state.sim_agent_registry = registry
        print("[+] Simulation agent registry ready")
    elif not settings.SIM_AGENTS_ENABLED:
        print("[*] Simulation agents disabled via configuration")

    if (
        SimulationWorker is not None
        and SimulationService is not None
        and app.state.sim_pool
        and app.state.sim_cache
    ):
        sim_service = SimulationService(
            session_repo=SimulationRepository(app.state.sim_pool),
            market_repo=MarketStateRepository(app.state.sim_pool),
            order_repo=OrderTradeRepository(app.state.sim_pool),
            cache=app.state.sim_cache,
            agent_log_repo=AgentLogRepository(app.state.sim_pool),
            feature_service=app.state.sim_feature_service,
            emotion_service=app.state.sim_emotion_service,
            agent_registry=app.state.sim_agent_registry if settings.SIM_AGENTS_ENABLED else None,
            agents_enabled=settings.SIM_AGENTS_ENABLED,
        )
        app.state.sim_worker = SimulationWorker(sim_service)
        print("[+] Simulation worker ready")
    else:
        app.state.sim_worker = None

    if (
        FeatureCalibrationTask is not None
        and app.state.sim_pool
        and app.state.sim_feature_task is None
    ):
        task = FeatureCalibrationTask(app.state.sim_pool)
        app.state.sim_feature_task = asyncio.create_task(
            _feature_calibration_loop(task, interval_seconds=30)
        )
        print("[+] Feature calibration task scheduled")

    yield

    # 鍏抽棴鏃舵墽琛?
    print("Shutting down...")
    
    # 鍋滄 WebSocket 蹇冭烦妫€娴?
    print("[*] Stopping WebSocket heartbeat checker...")
    manager = get_connection_manager()
    await manager.stop_heartbeat_checker()
    
    # 鍏抽棴 Redis Pub/Sub
    print("[*] Closing Redis Pub/Sub...")
    await close_redis_pubsub()
    
    if settings.PRICE_GENERATION_ENABLED:
        # 鍏抽棴璋冨害鍣?
        print("[*] Stopping scheduler...")
        shutdown_scheduler()
        
        # 鍏抽棴鏁版嵁搴?
        if db_manager is not None:
            db_manager.close()

    feature_task = getattr(app.state, "sim_feature_task", None)
    if feature_task is not None:
        feature_task.cancel()
        try:
            await feature_task
        except asyncio.CancelledError:
            pass
        app.state.sim_feature_task = None

    emotion_service = getattr(app.state, "sim_emotion_service", None)
    if emotion_service is not None:
        print("[*] Closing emotion service...")
        try:
            await emotion_service.close()
        finally:
            app.state.sim_emotion_service = None

    if getattr(app.state, "sim_agent_registry", None) is not None:
        app.state.sim_agent_registry = None

    sim_cache = getattr(app.state, "sim_cache", None)
    if sim_cache is not None:
        print("[*] Closing simulation cache...")
        try:
            await sim_cache.close()
        finally:
            app.state.sim_cache = None

    if SimulationWorker is not None and getattr(app.state, "sim_worker", None):
        worker = app.state.sim_worker
        if worker is not None:
            # stop all known workers
            queues = getattr(worker, "_queues", {})
            for session_id in list(queues.keys()):
                await worker.stop(session_id)
        app.state.sim_worker = None

    sim_pool = getattr(app.state, "sim_pool", None)
    if sim_pool is not None:
        print("[*] Closing simulation database pool...")
        try:
            await sim_pool.close()
        finally:
            app.state.sim_pool = None


# 鍒涘缓 FastAPI 搴旂敤瀹炰緥
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="妯℃嫙浜ゆ槗绯荤粺 API",
    lifespan=lifespan,
)

# 閰嶇疆 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 娉ㄥ唽 Tortoise-ORM
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,  # 鑷姩鐢熸垚鏁版嵁搴撹〃缁撴瀯
    add_exception_handlers=True,  # 娣诲姞寮傚父澶勭悊
)


# 鍏ㄥ眬寮傚父澶勭悊鍣?
@app.exception_handler(TradingException)
async def trading_exception_handler(request: Request, exc: TradingException):
    """
    澶勭悊浜ゆ槗鐩稿叧鐨勪笟鍔″紓甯?
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


@app.exception_handler(EmailException)
async def email_exception_handler(request: Request, exc: EmailException):
    """
    澶勭悊閭鐩稿叧鐨勪笟鍔″紓甯?
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


@app.exception_handler(RateLimitExceededError)
async def rate_limit_exception_handler(request: Request, exc: RateLimitExceededError):
    """
    澶勭悊棰戠巼闄愬埗寮傚父
    """
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": {
                    "retry_after": exc.retry_after
                }
            },
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    澶勭悊鍏朵粬鏈崟鑾风殑寮傚父
    """
    # 鍦ㄧ敓浜х幆澧冧腑锛屼笉搴旇鏆撮湶璇︾粏鐨勯敊璇俊鎭?
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


# Root endpoint
@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "success": True,
        "message": "Welcome to happyStock Trading API",
        "version": settings.APP_VERSION,
    }


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "success": True,
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# 瀵煎叆璺敱
from routers import accounts, assets, trades, holdings, klines, auth, password_reset, email_verification, simulate
from api import stocks as virtual_market_stocks
from api import indices as virtual_market_indices
from api import sectors as virtual_market_sectors
from api import market as virtual_market_market
from api import websocket as websocket_api

# API routers
app.include_router(auth.router, prefix="/api", tags=["Auth"])
app.include_router(password_reset.router, tags=["Password Reset"])
app.include_router(email_verification.router, tags=["Email Verification"])
app.include_router(accounts.router, prefix="/api/v1", tags=["Accounts"] )
app.include_router(assets.router, prefix="/api/v1", tags=["Assets"])
app.include_router(trades.router, prefix="/api/v1", tags=["Trades"])
app.include_router(holdings.router, prefix="/api/v1", tags=["Holdings"])
app.include_router(klines.router, prefix="/api/v1", tags=["Klines"])
app.include_router(simulate.router, prefix="/api/sim", tags=["Simulation"])

# Virtual market API routers
app.include_router(virtual_market_stocks.router, prefix="/api/v1", tags=["Virtual Stocks"])
app.include_router(virtual_market_indices.router, prefix="/api/v1", tags=["Virtual Indices"])
app.include_router(virtual_market_sectors.router, prefix="/api/v1", tags=["Virtual Sectors"])
app.include_router(virtual_market_market.router, prefix="/api/v1", tags=["Virtual Market"])

# WebSocket API routers (real-time data push)
app.include_router(websocket_api.router, prefix="/api/v1", tags=["Real-time Data"])


@app.get("/debug/routes")
async def list_all_routes():
    """璋冭瘯绔偣锛氬垪鍑烘墍鏈夋敞鍐岀殑璺敱"""
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
        timeout_keep_alive=5,  # 鍑忓皯 keep-alive 瓒呮椂
        limit_concurrency=100,  # 闄愬埗骞跺彂杩炴帴鏁?
    )







