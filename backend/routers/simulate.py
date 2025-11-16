"""Simulation API endpoints."""

from __future__ import annotations

import asyncio
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
    WebSocket,
    WebSocketDisconnect,
    status,
)
from config import settings
from sim.cache import SimulationCache
from sim.repositories import (
    AgentLogRepository,
    MarketStateRepository,
    OrderTradeRepository,
    SimulationRepository,
    UserOrderRepository,
)
from sim.schemas import (
    LeaderboardEntryOut,
    MarketSnapshotOut,
    OrderRequest,
    OrderAcceptedResponse,
    OrderDetail,
    OrderListResponse,
    CancelOrderResponse,
    TickRequest,
    TickResponse,
)
from sim.agent_schemas import (
    UpdateAgentBehaviorRequest,
    AgentBehaviorResponse,
    BehaviorConfig,
    AgentListResponse,
    AgentPerformanceResponse,
    AgentPoolListResponse,
    AgentPoolDetailResponse,
    UpdateAgentConfigRequest,
    UpdateAgentConfigResponse,
    AgentDetail,
    AgentPerformance,
    AgentPoolStats,
)
from sim.services import SimulationService
from sim.start_models import SimulationStartRequest, SimulationStartResponse
from sim.types import MarketSnapshot, OrderStatus, SimulationSession, UserOrder
from sim.order_validator import order_validator, rate_limiter

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
    existing = getattr(request.app.state, "sim_service", None)
    if existing is not None:
        return existing

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
    service = SimulationService(
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
    return service


def get_worker(request: Request):
    worker = getattr(request.app.state, "sim_worker", None)
    if worker is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulation worker unavailable",
        )
    return worker


def get_user_order_repo(request: Request) -> UserOrderRepository:
    """Get UserOrderRepository dependency."""
    pool = _get_sim_pool(request)
    return UserOrderRepository(pool)


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
        "timestamp": snapshot.timestamp.isoformat(),
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


@router.websocket("/ws/ticks")
async def websocket_sim_ticks(
    websocket: WebSocket,
    session_id: int = Query(..., ge=1),
    limit: int = Query(30, ge=1, le=500),
    interval_ms: int = Query(1000, ge=200, le=10_000),
):
    await websocket.accept()
    service: SimulationService | None = getattr(
        websocket.app.state, "sim_service", None
    )
    if service is None:
        await websocket.close(code=1011, reason="Simulation service unavailable")
        return

    try:
        while True:
            snapshots = await service.fetch_recent_market_state(
                session_id=session_id, limit=limit
            )
            await websocket.send_json(
                {
                    "type": "tick_update",
                    "session_id": session_id,
                    "snapshots": [_snapshot_to_dict(snapshot) for snapshot in snapshots],
                }
            )
            await asyncio.sleep(max(interval_ms / 1000, 0.2))
    except WebSocketDisconnect:
        return
    except Exception as exc:  # pragma: no cover
        await websocket.close(code=1011, reason=str(exc))


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

# ============================================================================
# User Order Endpoints (Feature: 001-ai-user-order-matching, Phase 4, US1)
# ============================================================================


@router.post(
    "/sessions/{session_id}/orders",
    response_model=OrderAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit user order",
    tags=["User Orders"],
)
async def submit_user_order(
    session_id: int,
    order_request: OrderRequest,
    request: Request,
    cache: SimulationCache = Depends(get_sim_cache),
    user_order_repo: UserOrderRepository = Depends(get_user_order_repo),
    service: SimulationService = Depends(get_simulation_service),
) -> OrderAcceptedResponse:
    """
    Submit a user order for the next tick (T038-T040, T053-T056).

    Orders are queued in Redis and will be processed in the next simulation tick.
    """
    # TODO: Get actual user_id from auth system
    user_id = 1  # Placeholder

    # T056: Check rate limits
    rate_limiter.check_rate_limit(user_id)

    # T039: Validate order basics
    if order_request.order_type == "LIMIT" and order_request.price is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="LIMIT orders must specify price",
        )

    if order_request.price is not None and order_request.price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price must be positive",
        )

    # T055: Get session info and verify it exists
    session_repo = SimulationRepository(_get_sim_pool(request))
    session = await session_repo.fetch_session_by_id(session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    # Get current market price for validation
    engine = service._engine_for(session_id)
    current_price = service._last_price.get(session_id)

    # T054: Validate price range
    order_validator.validate_price_range(
        price=order_request.price,
        current_price=current_price,
    )

    # T053: Calculate order cost and validate balance
    order_cost = order_validator.calculate_order_cost(
        side=order_request.side,
        order_type=order_request.order_type,
        quantity=order_request.quantity,
        price=order_request.price,
        current_price=current_price,
    )

    # TODO: Get actual user balance from account table
    user_balance = 100_000.0  # Placeholder

    if order_cost > 0:
        order_validator.validate_balance(
            user_balance=user_balance,
            order_cost=order_cost,
        )

    # T040: Generate nanosecond timestamp and order ID
    timestamp_ns = int(datetime.now(timezone.utc).timestamp() * 1_000_000_000)
    order_id = f"user-{user_id}-{timestamp_ns}-{uuid.uuid4().hex[:6]}"
    participant_id = f"user-{user_id}"

    # Create UserOrder record
    user_order = UserOrder(
        order_id=order_id,
        session_id=session_id,
        user_id=user_id,
        participant_id=participant_id,
        side=order_request.side,
        order_type=order_request.order_type,
        quantity=order_request.quantity,
        price=order_request.price,
        timestamp=timestamp_ns,
        status=OrderStatus.PENDING,
        filled_quantity=0.0,
    )

    # Save to database
    await user_order_repo.create_order(user_order)

    # T040: Push to Redis queue for next tick processing
    order_data = {
        "order_id": order_id,
        "participant_id": participant_id,
        "side": order_request.side,
        "type": order_request.order_type,
        "quantity": order_request.quantity,
        "price": order_request.price,
        "timestamp": timestamp_ns,
        "user_id": user_id,
    }
    await cache.push_pending_user_order(session.session_code, order_data)

    # Estimate next tick (current tick + 1)
    current_tick = session.current_tick or 0
    estimated_tick = current_tick + 1

    return OrderAcceptedResponse(
        status="accepted",
        order_id=order_id,
        message="Order queued for next tick",
        estimated_execution_tick=estimated_tick,
    )


@router.get(
    "/sessions/{session_id}/orders/{order_id}",
    response_model=OrderDetail,
    summary="Get order by ID",
    tags=["User Orders"],
)
async def get_order(
    session_id: int,
    order_id: str,
    user_order_repo: UserOrderRepository = Depends(get_user_order_repo),
) -> OrderDetail:
    """
    Retrieve a single order by ID (T041).
    """
    order = await user_order_repo.get_order(order_id)
    if order is None or order.session_id != session_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found in session {session_id}",
        )

    # TODO: Fetch associated trades from trade_event table
    return OrderDetail(
        order_id=order.order_id,
        session_id=order.session_id,
        user_id=order.user_id,
        side=order.side,
        order_type=order.order_type,
        quantity=order.quantity,
        price=order.price,
        status=order.status.value if isinstance(order.status, OrderStatus) else order.status,
        filled_quantity=order.filled_quantity,
        avg_filled_price=order.avg_filled_price,
        timestamp=order.timestamp,
        created_at=order.created_at,
        updated_at=order.updated_at,
        trades=[],  # TODO: populate from trade_event
    )


@router.get(
    "/sessions/{session_id}/orders",
    response_model=OrderListResponse,
    summary="List user orders",
    tags=["User Orders"],
)
async def list_orders(
    session_id: int,
    status_filter: str = Query(None, alias="status", description="Filter by order status"),
    limit: int = Query(100, ge=1, le=500, description="Page size"),
    offset: int = Query(0, ge=0, description="Page offset"),
    user_order_repo: UserOrderRepository = Depends(get_user_order_repo),
) -> OrderListResponse:
    """
    List orders with pagination and filtering (T042).
    """
    # TODO: Get actual user_id from auth system
    user_id = 1  # Placeholder

    orders, total = await user_order_repo.list_orders(
        session_id=session_id,
        user_id=user_id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )

    order_details = [
        OrderDetail(
            order_id=o.order_id,
            session_id=o.session_id,
            user_id=o.user_id,
            side=o.side,
            order_type=o.order_type,
            quantity=o.quantity,
            price=o.price,
            status=o.status.value if isinstance(o.status, OrderStatus) else o.status,
            filled_quantity=o.filled_quantity,
            avg_filled_price=o.avg_filled_price,
            timestamp=o.timestamp,
            created_at=o.created_at,
            updated_at=o.updated_at,
            trades=[],
        )
        for o in orders
    ]

    return OrderListResponse(
        orders=order_details,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.delete(
    "/sessions/{session_id}/orders/{order_id}",
    response_model=CancelOrderResponse,
    summary="Cancel order",
    tags=["User Orders"],
)
async def cancel_order(
    session_id: int,
    order_id: str,
    user_order_repo: UserOrderRepository = Depends(get_user_order_repo),
) -> CancelOrderResponse:
    """
    Cancel a pending/partial order (T043).
    """
    # Verify order exists and belongs to session
    order = await user_order_repo.get_order(order_id)
    if order is None or order.session_id != session_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found in session {session_id}",
        )

    # Check if order is cancellable
    if order.status not in [OrderStatus.PENDING, OrderStatus.NEW, OrderStatus.PARTIAL]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order {order_id} cannot be cancelled (status: {order.status.value})",
        )

    # Cancel the order
    success = await user_order_repo.cancel_order(order_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel order",
        )

    cancelled_quantity = order.quantity - order.filled_quantity

    return CancelOrderResponse(
        status="cancelled",
        order_id=order_id,
        cancelled_quantity=cancelled_quantity,
        message=f"Order cancelled, remaining {cancelled_quantity} units will not be executed",
    )


@router.get(
    "/sessions/{session_id}/orderbook",
    summary="Get orderbook snapshot",
    tags=["Market Data"],
)
async def get_orderbook(
    session_id: int,
    request: Request,
    depth: int = Query(50, ge=1, le=50, description="Number of price levels to return"),
    service: SimulationService = Depends(get_simulation_service),
    cache: SimulationCache = Depends(get_sim_cache),
) -> dict:
    """
    Get current orderbook depth snapshot (T044).

    Returns aggregated bids and asks with price, quantity, and order count per level.
    """
    # Get session
    session_repo = SimulationRepository(_get_sim_pool(request))
    session = await session_repo.fetch_session_by_id(session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    # Try to get cached orderbook first (T027)
    cached = await cache.get_cached_orderbook(session.session_code)
    if cached:
        return cached

    # Get live orderbook from matching engine
    engine = service._engine_for(session_id)
    snapshot = engine.order_book.get_depth_snapshot(depth=depth)

    # Transform to API response format
    response = {
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "bids": [
            {"price": price, "quantity": qty, "order_count": count}
            for price, qty, count in snapshot["bids"]
        ],
        "asks": [
            {"price": price, "quantity": qty, "order_count": count}
            for price, qty, count in snapshot["asks"]
        ],
    }

    # Cache for 5 seconds
    await cache.cache_orderbook_snapshot(session.session_code, response, ttl_seconds=5)

    return response


@router.post(
    "/sessions/{session_id}/join",
    summary="Join simulation session",
    tags=["User Management"],
)
async def join_session(
    session_id: int,
    request: Request,
    service: SimulationService = Depends(get_simulation_service),
) -> dict:
    """
    Join a simulation session as a user (T045-T046).

    Creates a participant record and initializes user account.
    """
    # Get session to verify it exists
    session_repo = SimulationRepository(_get_sim_pool(request))
    session = await session_repo.fetch_session_by_id(session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    # TODO: Get actual user_id from auth system
    user_id = 1  # Placeholder

    # Join session and create participant
    participant_info = await service.join_session(session_id, user_id)

    return {
        "message": "Successfully joined session",
        "session_id": session_id,
        "session_code": session.session_code,
        **participant_info,
    }


@router.get(
    "/sessions/{session_id}/agents/{participant_code}/behavior",
    summary="Get agent behavior configuration",
    tags=["Agent Configuration"],
)
async def get_agent_behavior(
    session_id: int,
    participant_code: str,
    request: Request,
) -> AgentBehaviorResponse:
    """
    T064: Get current behavior configuration for an agent.

    Returns the agent's behavior parameters including:
    - behavior_category (institutional, prop, retail, market_maker)
    - profit_target
    - stop_loss
    - herd_behavior_strength
    - momentum_sensitivity
    - risk_tolerance
    """
    session_repo = SimulationRepository(_get_sim_pool(request))
    behavior = await session_repo.fetch_participant_behavior(session_id, participant_code)

    if behavior is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {participant_code} not found in session {session_id}",
        )

    return AgentBehaviorResponse(
        participant_code=participant_code,
        behavior_config=BehaviorConfig(**behavior),
        updated=False,
    )


@router.put(
    "/sessions/{session_id}/agents/{participant_code}/behavior",
    summary="Update agent behavior configuration",
    tags=["Agent Configuration"],
)
async def update_agent_behavior(
    session_id: int,
    participant_code: str,
    request: Request,
    config: BehaviorConfig,
) -> AgentBehaviorResponse:
    """
    T064: Update behavior parameters for an agent.

    This allows fine-tuning agent behavior for different simulation scenarios.
    Parameters will be persisted and used in future ticks.
    """
    session_repo = SimulationRepository(_get_sim_pool(request))

    # Verify participant exists
    behavior = await session_repo.fetch_participant_behavior(session_id, participant_code)
    if behavior is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {participant_code} not found in session {session_id}",
        )

    # Update behavior parameters
    payload = {
        "participant_code": participant_code,
        "behavior_category": config.behavior_category,
        "profit_target": config.profit_target,
        "stop_loss": config.stop_loss,
        "herd_behavior_strength": config.herd_behavior_strength,
        "momentum_sensitivity": config.momentum_sensitivity,
        "risk_tolerance": config.risk_tolerance,
    }

    await session_repo.ensure_participants_bulk(session_id, [payload])

    return AgentBehaviorResponse(
        participant_code=participant_code,
        behavior_config=config,
        updated=True,
    )


# ========== T075-T080: Agent Management API Endpoints ==========


@router.get(
    "/sessions/{session_id}/agents",
    response_model=AgentListResponse,
    summary="List all agents in a session",
    tags=["Agent Management"],
)
async def list_session_agents(
    session_id: int,
    request: Request,
    participant_type: str | None = Query(None, description="Filter by participant type"),
) -> AgentListResponse:
    """
    T075: List all agents (AI participants) in a simulation session.

    Returns agent details including behavior parameters, position cost, and scores.
    """
    session_repo = SimulationRepository(_get_sim_pool(request))

    # Verify session exists
    session = await session_repo.fetch_session_by_id(session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    agents_data = await session_repo.list_agents(
        session_id, participant_type=participant_type
    )

    agents = [
        AgentDetail(
            participant_code=agent["participant_code"],
            participant_type=agent["participant_type"],
            behavior_category=agent.get("behavior_category"),
            profit_target=float(agent["profit_target"]) if agent.get("profit_target") is not None else None,
            stop_loss=float(agent["stop_loss"]) if agent.get("stop_loss") is not None else None,
            herd_behavior_strength=float(agent["herd_behavior_strength"]) if agent.get("herd_behavior_strength") is not None else None,
            momentum_sensitivity=float(agent["momentum_sensitivity"]) if agent.get("momentum_sensitivity") is not None else None,
            risk_tolerance=float(agent["risk_tolerance"]) if agent.get("risk_tolerance") is not None else None,
            avg_position_cost=float(agent["avg_position_cost"]) if agent.get("avg_position_cost") is not None else None,
            score=float(agent.get("score", 0.0)),
            created_at=agent["created_at"].isoformat(),
            updated_at=agent["updated_at"].isoformat(),
        )
        for agent in agents_data
    ]

    return AgentListResponse(
        session_id=session_id,
        total=len(agents),
        agents=agents,
    )


@router.get(
    "/sessions/{session_id}/agents/{participant_code}",
    response_model=AgentDetail,
    summary="Get detailed agent information",
    tags=["Agent Management"],
)
async def get_agent_detail(
    session_id: int,
    participant_code: str,
    request: Request,
) -> AgentDetail:
    """
    T076: Get detailed information for a single agent.

    Returns full agent configuration including behavior parameters and current state.
    """
    session_repo = SimulationRepository(_get_sim_pool(request))

    agent_data = await session_repo.get_agent(session_id, participant_code)
    if agent_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {participant_code} not found in session {session_id}",
        )

    return AgentDetail(
        participant_code=agent_data["participant_code"],
        participant_type=agent_data["participant_type"],
        behavior_category=agent_data.get("behavior_category"),
        profit_target=float(agent_data["profit_target"]) if agent_data.get("profit_target") is not None else None,
        stop_loss=float(agent_data["stop_loss"]) if agent_data.get("stop_loss") is not None else None,
        herd_behavior_strength=float(agent_data["herd_behavior_strength"]) if agent_data.get("herd_behavior_strength") is not None else None,
        momentum_sensitivity=float(agent_data["momentum_sensitivity"]) if agent_data.get("momentum_sensitivity") is not None else None,
        risk_tolerance=float(agent_data["risk_tolerance"]) if agent_data.get("risk_tolerance") is not None else None,
        avg_position_cost=float(agent_data["avg_position_cost"]) if agent_data.get("avg_position_cost") is not None else None,
        score=float(agent_data.get("score", 0.0)),
        created_at=agent_data["created_at"].isoformat(),
        updated_at=agent_data["updated_at"].isoformat(),
    )


@router.put(
    "/sessions/{session_id}/agents/{participant_code}/config",
    response_model=UpdateAgentConfigResponse,
    summary="Update agent configuration",
    tags=["Agent Management"],
)
async def update_agent_config(
    session_id: int,
    participant_code: str,
    config: UpdateAgentConfigRequest,
    request: Request,
) -> UpdateAgentConfigResponse:
    """
    T077: Update behavior configuration for an agent.

    Only provided parameters will be updated. Useful for fine-tuning agent behavior
    during simulation development.
    """
    session_repo = SimulationRepository(_get_sim_pool(request))

    # Verify agent exists
    agent_data = await session_repo.get_agent(session_id, participant_code)
    if agent_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {participant_code} not found in session {session_id}",
        )

    # Update parameters
    updated = await session_repo.update_participant(
        session_id,
        participant_code,
        behavior_category=config.behavior_category,
        profit_target=config.profit_target,
        stop_loss=config.stop_loss,
        herd_behavior_strength=config.herd_behavior_strength,
        momentum_sensitivity=config.momentum_sensitivity,
        risk_tolerance=config.risk_tolerance,
    )

    # Fetch updated agent data
    updated_agent = await session_repo.get_agent(session_id, participant_code)

    return UpdateAgentConfigResponse(
        session_id=session_id,
        participant_code=participant_code,
        updated=updated,
        config=AgentDetail(
            participant_code=updated_agent["participant_code"],
            participant_type=updated_agent["participant_type"],
            behavior_category=updated_agent.get("behavior_category"),
            profit_target=float(updated_agent["profit_target"]) if updated_agent.get("profit_target") is not None else None,
            stop_loss=float(updated_agent["stop_loss"]) if updated_agent.get("stop_loss") is not None else None,
            herd_behavior_strength=float(updated_agent["herd_behavior_strength"]) if updated_agent.get("herd_behavior_strength") is not None else None,
            momentum_sensitivity=float(updated_agent["momentum_sensitivity"]) if updated_agent.get("momentum_sensitivity") is not None else None,
            risk_tolerance=float(updated_agent["risk_tolerance"]) if updated_agent.get("risk_tolerance") is not None else None,
            avg_position_cost=float(updated_agent["avg_position_cost"]) if updated_agent.get("avg_position_cost") is not None else None,
            score=float(updated_agent.get("score", 0.0)),
            created_at=updated_agent["created_at"].isoformat(),
            updated_at=updated_agent["updated_at"].isoformat(),
        ),
    )


@router.get(
    "/sessions/{session_id}/agents/{participant_code}/performance",
    response_model=AgentPerformanceResponse,
    summary="Get agent performance metrics",
    tags=["Agent Management"],
)
async def get_agent_performance(
    session_id: int,
    participant_code: str,
    request: Request,
) -> AgentPerformanceResponse:
    """
    T078: Get performance statistics for a single agent.

    Returns metrics like order count, trade count, volume, and win rate.
    """
    session_repo = SimulationRepository(_get_sim_pool(request))
    order_repo = OrderTradeRepository(_get_sim_pool(request))

    # Verify agent exists
    agent_data = await session_repo.get_agent(session_id, participant_code)
    if agent_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {participant_code} not found in session {session_id}",
        )

    # Get performance data
    perf_data = await order_repo.get_agent_performance(session_id, participant_code)

    return AgentPerformanceResponse(
        session_id=session_id,
        participant_code=participant_code,
        performance=AgentPerformance(**perf_data),
    )


@router.get(
    "/sessions/{session_id}/pools",
    response_model=AgentPoolListResponse,
    summary="List agent pools",
    tags=["Agent Management"],
)
async def list_agent_pools(
    session_id: int,
    request: Request,
) -> AgentPoolListResponse:
    """
    T079: List all agent pools (behavior categories) in a session.

    Each pool represents a group of agents with the same behavior category
    (e.g., retail, institutional, prop, market_maker).
    """
    session_repo = SimulationRepository(_get_sim_pool(request))
    order_repo = OrderTradeRepository(_get_sim_pool(request))

    # Verify session exists
    session = await session_repo.fetch_session_by_id(session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    # Get pool codes
    pool_codes = await order_repo.list_pool_codes(session_id)

    pools = []
    for pool_code in pool_codes:
        stats_data = await order_repo.get_pool_statistics(session_id, pool_code)
        pools.append(
            AgentPoolStats(
                pool_code=pool_code,
                agent_count=stats_data["agent_count"],
                total_orders=stats_data["total_orders"],
                total_trades=stats_data["total_trades"],
                total_volume=stats_data["total_volume"],
                avg_behavior_params={},  # TODO: Calculate average parameters
            )
        )

    return AgentPoolListResponse(
        session_id=session_id,
        pools=pools,
    )


@router.get(
    "/sessions/{session_id}/pools/{pool_code}/stats",
    response_model=AgentPoolDetailResponse,
    summary="Get detailed pool statistics",
    tags=["Agent Management"],
)
async def get_pool_stats(
    session_id: int,
    pool_code: str,
    request: Request,
) -> AgentPoolDetailResponse:
    """
    T080: Get detailed statistics for a specific agent pool.

    Returns aggregated statistics and list of all agents in the pool.
    """
    session_repo = SimulationRepository(_get_sim_pool(request))
    order_repo = OrderTradeRepository(_get_sim_pool(request))

    # Verify session exists
    session = await session_repo.fetch_session_by_id(session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    # Get pool statistics
    stats_data = await order_repo.get_pool_statistics(session_id, pool_code)

    # Get all agents in this pool
    agents_data = await session_repo.list_agents(session_id)
    pool_agents = [
        agent for agent in agents_data
        if agent.get("behavior_category") == pool_code
    ]

    agents = [
        AgentDetail(
            participant_code=agent["participant_code"],
            participant_type=agent["participant_type"],
            behavior_category=agent.get("behavior_category"),
            profit_target=float(agent["profit_target"]) if agent.get("profit_target") is not None else None,
            stop_loss=float(agent["stop_loss"]) if agent.get("stop_loss") is not None else None,
            herd_behavior_strength=float(agent["herd_behavior_strength"]) if agent.get("herd_behavior_strength") is not None else None,
            momentum_sensitivity=float(agent["momentum_sensitivity"]) if agent.get("momentum_sensitivity") is not None else None,
            risk_tolerance=float(agent["risk_tolerance"]) if agent.get("risk_tolerance") is not None else None,
            avg_position_cost=float(agent["avg_position_cost"]) if agent.get("avg_position_cost") is not None else None,
            score=float(agent.get("score", 0.0)),
            created_at=agent["created_at"].isoformat(),
            updated_at=agent["updated_at"].isoformat(),
        )
        for agent in pool_agents
    ]

    return AgentPoolDetailResponse(
        session_id=session_id,
        pool_code=pool_code,
        stats=AgentPoolStats(
            pool_code=pool_code,
            agent_count=stats_data["agent_count"],
            total_orders=stats_data["total_orders"],
            total_trades=stats_data["total_trades"],
            total_volume=stats_data["total_volume"],
            avg_behavior_params={},  # TODO: Calculate average parameters
        ),
        agents=agents,
    )
