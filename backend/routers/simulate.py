"""Simulation API endpoints."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List
import uuid

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    Request,
    status,
)
from config import settings
from sim.cache import SimulationCache
from sim.repositories import (
    AgentLogRepository,
    MarketStateRepository,
    OrderTradeRepository,
    SimulationRepository,
)
from sim.schemas import (
    LeaderboardEntryOut,
    MarketSnapshotOut,
    TickRequest,
    TickResponse,
)
from sim.services import SimulationService
from sim.start_models import SimulationStartRequest, SimulationStartResponse
from sim.types import MarketSnapshot, SimulationSession

router = APIRouter()


def _get_sim_pool(request: Request):
    pool = getattr(request.app.state, "sim_pool", None)
    if pool is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulation database unavailable",
        )
    return pool


def get_sim_cache(request: Request) -> SimulationCache:
    cache = getattr(request.app.state, "sim_cache", None)
    if cache is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulation cache unavailable",
        )
    return cache


def get_simulation_service(request: Request) -> SimulationService:
    pool = _get_sim_pool(request)
    cache = get_sim_cache(request)
    session_repo = SimulationRepository(pool)
    market_repo = MarketStateRepository(pool)
    order_repo = OrderTradeRepository(pool)
    agent_log_repo = AgentLogRepository(pool)
    feature_service = getattr(request.app.state, "sim_feature_service", None)
    emotion_service = getattr(request.app.state, "sim_emotion_service", None)
    agent_registry = getattr(request.app.state, "sim_agent_registry", None)
    if not settings.SIM_AGENTS_ENABLED:
        agent_registry = None
    return SimulationService(
        session_repo=session_repo,
        market_repo=market_repo,
        order_repo=order_repo,
        cache=cache,
        agent_log_repo=agent_log_repo,
        feature_service=feature_service,
        emotion_service=emotion_service,
        agent_registry=agent_registry,
        agents_enabled=settings.SIM_AGENTS_ENABLED,
    )


def get_worker(request: Request):
    worker = getattr(request.app.state, "sim_worker", None)
    if worker is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulation worker unavailable",
        )
    return worker


@router.post("/start", response_model=SimulationStartResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_simulation(
    payload: SimulationStartRequest,
    request: Request,
    service: SimulationService = Depends(get_simulation_service),
) -> SimulationStartResponse:
    trace_id = request.headers.get("X-Trace-Id") or str(uuid.uuid4())
    session = SimulationSession(
        id=None,
        session_code=payload.session_code,
        status="pending",
        mode=payload.mode,
        tick_interval_ms=payload.tick_interval_ms,
        total_ticks=payload.total_ticks,
        config_version=payload.config_version,
    )

    try:
        created = await service.create_session(session)
    except Exception as exc:  # pragma: no cover - rely on DB constraints
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to persist simulation session: {exc}",
        ) from exc
    if created.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create simulation session",
        )

    await service.update_tick(created.id, 0)

    cache = get_sim_cache(request)
    await cache.set_status(payload.session_code, "pending")
    await cache.set_tick(payload.session_code, 0)

    worker = getattr(request.app.state, "sim_worker", None)
    if worker is not None:
        try:
            await worker.start(created.id)
        except Exception as exc:  # pragma: no cover - defensive guard
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to start simulation worker: {exc}",
            ) from exc

    return SimulationStartResponse(
        session_id=created.id,
        session_code=created.session_code,
        tick_interval_ms=created.tick_interval_ms,
        total_ticks=created.total_ticks,
        status="accepted",
        trace_id=trace_id,
        created_at=created.created_at or datetime.now(timezone.utc),
    )


@router.get("/state", response_model=List[MarketSnapshotOut])
async def read_market_state(
    *,
    session_id: int = Query(..., ge=1, description="????? ID"),
    limit: int = Query(50, ge=1, le=500, description="????????"),
    service: SimulationService = Depends(get_simulation_service),
) -> List[MarketSnapshotOut]:
    snapshots = await service.fetch_recent_market_state(
        session_id=session_id, limit=limit
    )
    return [MarketSnapshotOut(**_snapshot_to_dict(snapshot)) for snapshot in snapshots]


@router.get("/leaderboard", response_model=List[LeaderboardEntryOut])
async def read_leaderboard(
    *,
    session: str = Query(..., min_length=1, description="????? code"),
    limit: int = Query(10, ge=1, le=100, description="????????????"),
    service: SimulationService = Depends(get_simulation_service),
) -> List[LeaderboardEntryOut]:
    entries = await service.top_leaderboard(session, limit=limit)
    return [
        LeaderboardEntryOut(participant_id=entry.participant_id, score=entry.score)
        for entry in entries
    ]


@router.post("/tick", response_model=TickResponse, status_code=status.HTTP_202_ACCEPTED)
async def process_tick(
    payload: TickRequest,
    request: Request,
    service: SimulationService = Depends(get_simulation_service),
) -> TickResponse:
    trace_id = request.headers.get("X-Trace-Id") or str(uuid.uuid4())
    result = await service.process_tick(
        session_id=payload.session_id,
        session_code=payload.session_code,
        tick=payload.tick,
        orders=[order.model_dump() for order in payload.orders],
        timestamp=payload.timestamp,
        trace_id=trace_id,
    )
    return TickResponse(**result)


def _snapshot_to_dict(snapshot: MarketSnapshot) -> dict:
    return {
        "session_id": snapshot.session_id,
        "tick": snapshot.tick,
        "timestamp": snapshot.timestamp,
        "best_bid": snapshot.best_bid,
        "best_ask": snapshot.best_ask,
        "last_price": snapshot.last_price,
        "vwap_price": snapshot.vwap_price,
        "total_volume": snapshot.total_volume,
        "imbalance": snapshot.imbalance,
        "sentiment_score": snapshot.sentiment_score,
        "liquidity_level": snapshot.liquidity_level,
        "features": snapshot.features,
        "emotion": snapshot.emotion,
        "payload": snapshot.payload,
    }


@router.post("/step", response_model=TickResponse, status_code=status.HTTP_202_ACCEPTED)
async def step_simulation(
    payload: TickRequest,
    request: Request,
    worker=Depends(get_worker),
) -> TickResponse:
    if not payload.orders:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="orders must not be empty"
        )

    tick_timestamp = payload.timestamp or datetime.now(timezone.utc)
    trace_id = request.headers.get("X-Trace-Id") or str(uuid.uuid4())

    try:
        await worker.submit(
            TickRequest(
                session_id=payload.session_id,
                session_code=payload.session_code,
                tick=payload.tick,
                orders=payload.orders,
                timestamp=tick_timestamp,
            )
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
        ) from exc
    return TickResponse(
        trace_id=trace_id,
        status="accepted",
        orders=[],
        trades=[],
        snapshot={},
    )


@router.post("/player/order", response_model=TickResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_player_order(
    payload: TickRequest,
    request: Request,
    worker=Depends(get_worker),
) -> TickResponse:
    if not payload.orders:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="orders must not be empty"
        )

    tick_timestamp = payload.timestamp or datetime.now(timezone.utc)
    trace_id = request.headers.get("X-Trace-Id") or str(uuid.uuid4())

    try:
        await worker.submit(
            TickRequest(
                session_id=payload.session_id,
                session_code=payload.session_code,
                tick=payload.tick,
                orders=payload.orders,
                timestamp=tick_timestamp,
            )
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
        ) from exc
    return TickResponse(
        trace_id=trace_id,
        status="accepted",
        orders=[],
        trades=[],
        snapshot={},
    )
