"""Service layer for the simulation subsystem."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
from statistics import pstdev
from time import perf_counter
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
)

if TYPE_CHECKING:
    from .feature_service import FeatureService
    from .emotion_service import EmotionService
    from .agents import AgentRegistry, AgentContext

from config import settings
from .cache import LeaderboardEntry, SimulationCache
from .coach import CoachInsightBuilder
from .engine import MatchingEngine, Order, OrderSide, OrderStatus, OrderType
from .repositories import (
    AgentLogRepository,
    MarketStateRepository,
    OrderTradeRepository,
    SimulationRepository,
    UserOrderRepository,
)
from .types import (
    CoachInsight,
    MarketSnapshot,
    OrderEventRecord,
    SimulationSession,
    TradeEventRecord,
)
from .agent_pools import (
    AgentPoolManager,
    DEFAULT_AGENT_POOLS,
    PoolTickStat,
)
from .agents.base import GeneratedOrder

logger = logging.getLogger(__name__)


class ImpactModel:
    """Simple price impact calculator based on power-law liquidity model."""

    def __init__(
        self, alpha: float = 0.6, beta: float = 0.5, liquidity: float = 10_000.0
    ) -> None:
        self.alpha = alpha
        self.beta = beta
        self.liquidity = liquidity

    def evaluate(self, side: OrderSide, quantity: float) -> float:
        if quantity <= 0 or self.liquidity <= 0:
            return 0.0
        signed = quantity if side == OrderSide.BUY else -quantity
        magnitude = abs(signed) / (self.liquidity**self.beta)
        return self.alpha * magnitude * (1 if signed >= 0 else -1)


class SimulationService:
    """
    Coordinate in-memory matching engine, persistence (TimescaleDB) and Redis caches.

    The service owns per-session matching engines and is responsible for driving ticks,
    recording order/trade events, and publishing derived market state snapshots.
    """

    def __init__(
        self,
        *,
        session_repo: Optional[SimulationRepository] = None,
        market_repo: MarketStateRepository,
        order_repo: OrderTradeRepository,
        cache: SimulationCache,
        agent_log_repo: Optional[AgentLogRepository] = None,
        feature_service: Optional["FeatureService"] = None,
        emotion_service: Optional["EmotionService"] = None,
        agent_registry: Optional["AgentRegistry"] = None,
        agents_enabled: bool = True,
        agent_pool_manager: Optional[AgentPoolManager] = None,
        impact_model: Optional[ImpactModel] = None,
    ) -> None:
        if session_repo is None:
            raise RuntimeError("SimulationRepository is required.")
        self._sessions = session_repo
        self._market = market_repo
        self._orders = order_repo
        self._cache = cache
        self._agent_logs = agent_log_repo
        self._features = feature_service
        self._emotion = emotion_service
        self._agents = agent_registry
        self._agents_enabled = agents_enabled
        self._use_feature_service = (
            os.getenv("SIM_USE_FEATURE_SERVICE", "0").lower() in ("1", "true", "yes")
        )
        self._impact = impact_model or ImpactModel()
        self._agent_pools = agent_pool_manager or AgentPoolManager(DEFAULT_AGENT_POOLS)
        self._engines: dict[int, MatchingEngine] = {}
        self._last_price: dict[int, float] = defaultdict(float)
        self._session_codes: dict[int, str] = {}
        self._order_participants: dict[int, dict[str, dict[str, Any]]] = defaultdict(
            dict
        )
        self._participant_db_cache: dict[int, dict[str, int]] = defaultdict(dict)
        self._session_profiles: dict[int, dict[str, Any]] = {}
        self._latest_pool_stats: dict[int, Dict[str, PoolTickStat]] = {}
        self._retail_flow_history: dict[int, list[float]] = defaultdict(list)
        self._latest_pool_stats: dict[int, Dict[str, PoolTickStat]] = {}
        self._participant_semaphore = asyncio.Semaphore(
            max(1, int(os.getenv("SIM_PARTICIPANT_CONCURRENCY", "10")))
        )
        self._orderbook_depth = max(1, int(os.getenv("SIM_WS_ORDERBOOK_DEPTH", "50")))
        self._background_tasks: set[asyncio.Task] = set()
        self._coach_builder = CoachInsightBuilder()
        self._enabled_agent_pools = self._parse_enabled_agent_pools()
        threshold_ms = float(os.getenv("SIM_SLOW_TICK_THRESHOLD_MS", "1000"))
        self._slow_tick_threshold = threshold_ms / 1000.0 if threshold_ms > 0 else None
        log_path = os.getenv("SIM_SLOW_TICK_LOG", "backend/logs/slow_ticks.log")
        self._slow_tick_log = Path(log_path)
        if self._slow_tick_log:
            self._slow_tick_log.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    # Engine helpers
    def _engine_for(self, session_id: int) -> MatchingEngine:
        engine = self._engines.get(session_id)
        if engine is None:
            engine = MatchingEngine()
            self._engines[session_id] = engine
        return engine

    # ------------------------------------------------------------------ #
    # Session metadata
    async def create_session(self, session: SimulationSession) -> SimulationSession:
        if self._sessions is None:
            raise RuntimeError("SimulationRepository is unavailable.")
        created = await self._sessions.create_session(session)
        if created.id is not None:
            self._session_codes[created.id] = created.session_code
            self._agent_pools.ensure_session(created.id)
        return created

    async def update_tick(self, session_id: int, tick: int) -> None:
        if self._sessions is None:
            raise RuntimeError("SimulationRepository is unavailable.")
        await self._sessions.update_tick(session_id, tick)

    def set_session_profile(self, session_id: int, profile: dict[str, Any]) -> None:
        self._session_profiles[session_id] = profile
        # Set initial price if provided in profile
        if "initial_price" in profile and profile["initial_price"] is not None:
            initial_price = float(profile["initial_price"])
            if initial_price > 0:
                self._last_price[session_id] = initial_price

    async def join_session(self, session_id: int, user_id: int) -> dict[str, Any]:
        """
        Add user to session and create participant record (T046).

        Returns participant info including participant_id and initial account balance.
        """
        if self._sessions is None:
            raise RuntimeError("SimulationRepository is unavailable.")

        participant_code = f"user-{user_id}"
        participant_db_id = await self._sessions.ensure_participant(
            session_id=session_id,
            participant_code=participant_code,
            participant_type="user",
            player_id=None,
            agent_profile_id=None,
        )

        # TODO: Initialize user account balance in a separate table when implemented
        initial_balance = 100_000.0  # Default virtual currency

        return {
            "participant_id": participant_code,
            "participant_db_id": participant_db_id,
            "balance": initial_balance,
            "session_id": session_id,
        }

    # ------------------------------------------------------------------ #
    # Tick processing
    async def process_tick(
        self,
        *,
        session_id: int,
        session_code: str,
        tick: int,
        orders: Sequence[dict],
        timestamp: Optional[datetime] = None,
        trace_id: Optional[str] = None,
    ) -> dict:
        """
        Execute a single simulation tick.

        Parameters
        ----------
        session_id : Timescale-backed session identifier.
        session_code : Redis cache namespace (sim:{code}).
        tick : Current tick index.
        orders : Iterable of dicts containing:
            - order_id
            - participant_id
            - side ("BUY"/"SELL")
            - type ("LIMIT"/"MARKET")
            - quantity (float)
            - price (optional float for limit orders)
        timestamp : Optional datetime override; defaults to UTC now.
        """

        engine = self._engine_for(session_id)
        self._session_codes[session_id] = session_code
        ts = timestamp or datetime.now(timezone.utc)
        self._agent_pools.ensure_session(session_id)
        self._agent_pools.begin_tick(session_id)

        timings: dict[str, float] = {}
        overall_start = perf_counter()
        last_mark = overall_start

        def mark(label: str) -> None:
            nonlocal last_mark
            now = perf_counter()
            timings[label] = now - last_mark
            last_mark = now

        # Start with provided orders (from API or other sources)
        player_orders = list(orders)

        # Fetch pending user orders from Redis (Option B: Order Matching Integration)
        user_orders = await self._cache.pop_pending_user_orders(session_code, max_count=100)
        user_order_map: dict[str, dict] = {}  # order_id -> user_order_data
        if user_orders:
            logger.info(f"Processing {len(user_orders)} user orders for session {session_code} tick {tick}")
            for user_order in user_orders:
                user_order_map[user_order["order_id"]] = user_order
            player_orders.extend(user_orders)

        agent_generated_orders: List[GeneratedOrder] = []

        if self._agents is not None and self._agents_enabled:
            await self._ensure_default_agents(session_id)
            context = await self._build_agent_context(
                session_id=session_id,
                engine=engine,
            )
            agent_orders = await self._agents.generate_orders(
                session_id, session_code, tick, context
            )
            agent_generated_orders.extend(agent_orders)

        reference_price = self._last_price.get(session_id) or 1.0
        if agent_generated_orders:
            self._agent_pools.apply_order_limits(
                session_id, agent_generated_orders, reference_price
            )

        generated_orders: List[Dict] = []
        behavior_counts: Dict[str, int] = defaultdict(int)
        for generated in agent_generated_orders:
            # T031: Add timestamp to AI-generated orders
            import time
            timestamp_ns = time.time_ns()

            payload = {
                "order_id": generated.order_id,
                "participant_id": generated.participant_id,
                "participant_code": generated.participant_code or generated.participant_id,
                "participant_type": generated.participant_type,
                "side": generated.side,
                "type": generated.order_type,
                "quantity": generated.quantity,
                "price": generated.price,
                "timestamp": timestamp_ns,  # T031: Timestamp for ordering
                # Pool and behavior parameters for persistence
                "pool_code": generated.pool_code,
                "behavior_category": generated.behavior_category,
                "profit_target": generated.profit_target,
                "stop_loss": generated.stop_loss,
                "herd_behavior_strength": generated.herd_behavior_strength,
                "momentum_sensitivity": generated.momentum_sensitivity,
                "risk_tolerance": generated.risk_tolerance,
            }
            generated_orders.append(payload)
            self._order_participants[session_id][generated.order_id] = {
                "participant_id": generated.participant_id,
                "participant_code": generated.participant_code
                or generated.participant_id,
                "participant_type": generated.participant_type,
                "db_id": None,
            }
            behavior = payload.get("behavior_category")
            if behavior:
                behavior_counts[behavior] += 1

        if settings.SIM_AUTOPLAY_VERBOSE and behavior_counts:
            behavior_lines = ", ".join(f"{k}:{v}" for k, v in behavior_counts.items())
            logger.info(
                "Agent orders session=%s tick=%s %s",
                session_code,
                tick,
                behavior_lines,
            )

        unified_orders = player_orders + generated_orders

        # T029: Sort all orders by timestamp for price-time priority
        # Ensure user orders and AI orders are processed in time order
        unified_orders.sort(key=lambda x: x.get("timestamp", 0))

        order_count = len(unified_orders)
        mark("agent_orders")

        ensure_payloads: list[dict] = []
        for payload in unified_orders:
            code = payload.get("participant_code") or payload.get("participant_id")
            if not code:
                continue
            ensure_payloads.append(payload)

        participant_db_mapping: dict[str, int] = {}
        if ensure_payloads:
            participant_db_mapping = await self._ensure_participants(
                session_id=session_id, payloads=ensure_payloads
            )
        mark("participants")

        order_events: list[OrderEventRecord] = []
        trade_events: list[TradeEventRecord] = []
        total_signed_volume = 0.0
        participants = self._order_participants[session_id]
        score_adjustments = defaultdict(float)

        for payload in unified_orders:
            order = self._to_engine_order(session_id, payload)
            trades = engine.submit_order(order)
            filled_qty = order.quantity - order.remaining
            impact = self._impact.evaluate(order.side, filled_qty)

            participant_code = payload.get("participant_code") or order.participant_id
            participant_type = payload.get("participant_type") or "user"
            db_id = participant_db_mapping.get(participant_code)
            participants[order.order_id] = {
                "participant_id": order.participant_id,
                "participant_code": participant_code,
                "participant_type": participant_type,
                "db_id": db_id,
            }

            order_events.append(
                OrderEventRecord(
                    session_id=session_id,
                    tick=tick,
                    order_code=order.order_id,
                    participant_id=order.participant_id,
                    side=order.side.value,
                    order_type=order.order_type.value,
                    price=order.price,
                    quantity=order.quantity,
                    remaining_qty=order.remaining,
                    status=(
                        order.status.value if order.status != OrderStatus.NEW else "NEW"
                    ),
                    impact=impact,
                    created_at=ts,
                    participant_code=participant_code,
                    participant_db_id=db_id,
                )
            )

            for trade in trades:
                buyer_info = participants.get(trade.buy_order_id, {})
                seller_info = participants.get(trade.sell_order_id, {})
                buyer_id = buyer_info.get("participant_id", "")
                seller_id = seller_info.get("participant_id", "")
                buyer_db = buyer_info.get("db_id")
                seller_db = seller_info.get("db_id")
                buyer_code = buyer_info.get("participant_code")
                seller_code = seller_info.get("participant_code")
                buyer_participant_type = buyer_info.get("participant_type")
                seller_participant_type = seller_info.get("participant_type")

                # Determine participant types (Step 4: buyer_type/seller_type)
                def get_participant_type(
                    order_id: str, participant_id: str, info: dict[str, Any]
                ) -> str:
                    """Determine if participant is user or AI agent type."""
                    if info.get("participant_type") == "user" or order_id in user_order_map:
                        return "user"
                    # Check if it's an AI agent based on participant_id pattern
                    if "retail" in participant_id.lower():
                        return "ai_retail"
                    elif "prop" in participant_id.lower():
                        return "ai_prop"
                    elif "inst" in participant_id.lower():
                        return "ai_institutional"
                    elif "maker" in participant_id.lower():
                        return "ai_market_maker"
                    else:
                        return "ai_retail"  # Default for unknown AI agents

                buyer_type = get_participant_type(
                    trade.buy_order_id, buyer_id, buyer_info
                )
                seller_type = get_participant_type(
                    trade.sell_order_id, seller_id, seller_info
                )

                trade_events.append(
                    TradeEventRecord(
                        session_id=session_id,
                        tick=tick,
                        buy_order_code=trade.buy_order_id,
                        sell_order_code=trade.sell_order_id,
                        buyer_participant_id=buyer_id,
                        seller_participant_id=seller_id,
                        buyer_participant_code=buyer_id or None,
                        seller_participant_code=seller_id or None,
                        buyer_participant_db_id=buyer_db,
                        seller_participant_db_id=seller_db,
                        price=trade.price,
                        quantity=trade.quantity,
                        created_at=ts,
                        buyer_type=buyer_type,  # Step 4
                        seller_type=seller_type,  # Step 4
                    )
                )

                fill_price = (
                    trade.price
                    if trade.price is not None and trade.price > 0
                    else (self._last_price.get(session_id) or reference_price)
                )
                if fill_price is None or fill_price <= 0:
                    fill_price = 1.0

                if (
                    self._agents is not None
                    and buyer_participant_type == "agent"
                    and buyer_code
                ):
                    await self._agents.record_trade(
                        session_id,
                        buyer_code,
                        "BUY",
                        trade.quantity,
                        fill_price,
                        order_id=trade.buy_order_id,
                    )
                if (
                    self._agents is not None
                    and seller_participant_type == "agent"
                    and seller_code
                ):
                    await self._agents.record_trade(
                        session_id,
                        seller_code,
                        "SELL",
                        trade.quantity,
                        fill_price,
                        order_id=trade.sell_order_id,
                    )

                signed = (
                    trade.quantity if order.side == OrderSide.BUY else -trade.quantity
                )
                total_signed_volume += signed
                if buyer_id:
                    score_adjustments[buyer_id] += trade.quantity
                if seller_id:
                    score_adjustments[seller_id] += trade.quantity

        mark("engine")

        trade_fill_stats: dict[str, dict[str, float]] = defaultdict(
            lambda: {"qty": 0.0, "value": 0.0}
        )
        for trade in trade_events:
            trade_fill_stats[trade.buy_order_code]["qty"] += trade.quantity
            trade_fill_stats[trade.buy_order_code]["value"] += (
                trade.quantity * trade.price
            )
            trade_fill_stats[trade.sell_order_code]["qty"] += trade.quantity
            trade_fill_stats[trade.sell_order_code]["value"] += (
                trade.quantity * trade.price
            )

        orders_elapsed = trades_elapsed = 0.0
        if order_events or trade_events:
            orders_elapsed, trades_elapsed = await self._orders.record_events(
                order_events, trade_events
            )
        timings["orders_persist"] = orders_elapsed
        timings["trades_persist"] = trades_elapsed
        last_mark = perf_counter()

        # Step 3: Update user order statuses after matching
        if user_order_map:
            user_order_repo = UserOrderRepository(self._sessions._pool)
            user_events: list[dict[str, Any]] = []
            for order_event in order_events:
                meta = user_order_map.get(order_event.order_code)
                if meta is None:
                    continue

                status = order_event.status
                if status not in {"FILLED", "PARTIAL", "CANCELLED"}:
                    status = "NEW"

                stats = trade_fill_stats.get(order_event.order_code)
                filled_qty = (
                    stats["qty"]
                    if stats and stats["qty"] > 0
                    else order_event.quantity - order_event.remaining_qty
                )
                avg_price = (
                    stats["value"] / stats["qty"] if stats and stats["qty"] > 0 else None
                )

                await user_order_repo.update_order_status(
                    order_id=order_event.order_code,
                    status=status,
                    filled_quantity=filled_qty,
                    avg_filled_price=avg_price,
                )

                if filled_qty <= 0 and status == "NEW":
                    continue

                user_event = {
                    "channel": "user_orders",
                    "type": "order_filled" if status == "FILLED" else "order_update",
                    "session_id": session_id,
                    "order_id": order_event.order_code,
                    "user_id": str(meta.get("user_id")) if meta.get("user_id") is not None else None,
                    "participant_id": order_event.participant_id,
                    "status": status,
                    "filled_quantity": filled_qty,
                    "remaining_quantity": order_event.remaining_qty,
                    "avg_price": avg_price,
                    "timestamp": ts.isoformat(),
                    "tick": tick,
                }
                user_events.append(user_event)

            if user_events:
                for event in user_events:
                    if event.get("user_id"):
                        self._publish_stream_event(session_code, event)
            mark("user_orders_update")

        if score_adjustments:
            await asyncio.gather(
                *(
                    self._cache.adjust_leaderboard(session_code, participant_id, delta)
                    for participant_id, delta in score_adjustments.items()
                )
            )
        mark("leaderboard")

        snapshot = self._build_market_snapshot(
            session_id, tick, ts, engine, trade_events, total_signed_volume
        )
        pool_stats = self._agent_pools.collect_tick_stats(session_id)
        if pool_stats:
            self._latest_pool_stats[session_id] = pool_stats
            retail_stat = pool_stats.get("retail")
            if retail_stat is not None:
                total_flow = retail_stat.gross_buy + retail_stat.gross_sell
                history = self._retail_flow_history[session_id]
                history.append(total_flow)
                max_window = 60
                if len(history) > max_window:
                    del history[: len(history) - max_window]
        snapshot.features = self._build_snapshot_features(
            snapshot, trade_events, total_signed_volume, pool_stats
        )
        orderbook_depth = engine.order_book.get_depth_snapshot(depth=self._orderbook_depth)
        orderbook_payload = {
            "session_id": session_id,
            "session_code": session_code,
            "tick": tick,
            "timestamp": ts.isoformat(),
            "bids": [
                {"price": price, "quantity": qty, "order_count": count}
                for price, qty, count in orderbook_depth["bids"]
            ],
            "asks": [
                {"price": price, "quantity": qty, "order_count": count}
                for price, qty, count in orderbook_depth["asks"]
            ],
        }
        if self._cache is not None:
            self._schedule_background(
                self._cache.cache_orderbook_snapshot(
                    session_code, orderbook_payload, ttl_seconds=5
                )
            )
        orderbook_event = orderbook_payload.copy()
        orderbook_event.update({"channel": "orderbook", "type": "orderbook_snapshot"})
        self._publish_stream_event(session_code, orderbook_event)

        profile = self._session_profiles.get(session_id, {})
        initial_price = None
        try:
            initial_price = float(profile.get("initial_price"))
        except (TypeError, ValueError):
            initial_price = None
        if (
            settings.SIM_AUTOPLAY_VERBOSE
            and initial_price
            and initial_price > 0
            and snapshot.last_price
        ):
            deviation_pct = (
                (snapshot.last_price - initial_price) / initial_price
            ) * 100.0
            logger.info(
                "Price gap session=%s tick=%s last=%.2f (%+.2f%% vs bootstrap) signedVol=%+.0f",
                session_code,
                tick,
                snapshot.last_price,
                deviation_pct,
                total_signed_volume,
            )
        if self._features is not None and self._use_feature_service:
            try:
                external = await self._features.get_latest_features(session_id)
                snapshot.features.update(external)
            except Exception as exc:
                logger.warning("Feature service fetch failed: %s", exc)
        if self._emotion is not None:
            snapshot.emotion = await self._emotion.get_sentiment(session_code)
        mark("snapshot_features")
        pool_payload = {
            code: {
                "gross_buy": stat.gross_buy,
                "gross_sell": stat.gross_sell,
                "net_flow": stat.net_flow,
            }
            for code, stat in pool_stats.items()
        }
        if pool_payload and settings.SIM_AUTOPLAY_VERBOSE:
            summary = ", ".join(
                f"{code}:{data['net_flow']:+.0f}" for code, data in pool_payload.items()
            )
            logger.info(
                "Pool flow session=%s tick=%s %s heat=%.2f",
                session_code,
                tick,
                summary,
                profile.get("retail_heat", 1.0),
            )
        if self._cache is not None and pool_payload:
            await self._cache.publish_pool_stats(session_code, pool_payload)
        if self._market is not None:
            self._schedule_background(self._market.bulk_insert([snapshot]))
        mark("market_persist")
        if self._cache is not None:
            self._schedule_background(self._cache.set_tick(session_code, tick))
        await self.update_tick(session_id, tick)
        mark("cache_sync")

        await self._emit_coach_logs(
            session_id=session_id,
            session_code=session_code,
            tick=tick,
            snapshot=snapshot,
            trades=trade_events,
            score_adjustments=dict(score_adjustments),
            created_at=ts,
        )
        mark("coach_logs")

        result_trace = trace_id or f"{session_code}-{tick}-{int(ts.timestamp()*1_000_000)}"

        result_payload = {
            "status": "accepted",
            "trace_id": result_trace,
            "orders": [event.order_code for event in order_events],
            "trades": [
                {
                    "buy_order": trade.buy_order_code,
                    "sell_order": trade.sell_order_code,
                    "price": trade.price,
                    "quantity": trade.quantity,
                }
                for trade in trade_events
            ],
            "snapshot": {
                "best_bid": snapshot.best_bid,
                "best_ask": snapshot.best_ask,
                "last_price": snapshot.last_price,
                "vwap_price": snapshot.vwap_price,
                "total_volume": snapshot.total_volume,
                "imbalance": snapshot.imbalance,
                "features": snapshot.features,
                "emotion": snapshot.emotion,
                "payload": snapshot.payload,
            },
            "pool_stats": pool_payload,
        }

        total_elapsed = perf_counter() - overall_start
        timings["total"] = total_elapsed
        if self._slow_tick_threshold and total_elapsed >= self._slow_tick_threshold:
            formatted = {k: f"{v * 1000:.1f}ms" for k, v in timings.items()}
            slow_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "session_id": session_id,
                "session_code": session_code,
                "tick": tick,
                "order_count": order_count,
                "total_ms": total_elapsed * 1000,
                "breakdown_ms": {k: v * 1000 for k, v in timings.items()},
            }
            logger.warning(
                "Slow sim tick session=%s tick=%s orders=%s total=%s breakdown=%s",
                session_id,
                tick,
                order_count,
                formatted.pop("total"),
                formatted,
            )
            try:
                with self._slow_tick_log.open("a", encoding="utf-8") as log_file:
                    log_file.write(json.dumps(slow_entry, ensure_ascii=False) + "\n")
            except Exception as log_exc:  # pragma: no cover - file writing errors
                logger.error("Failed to write slow tick log: %s", log_exc)
        elif logger.isEnabledFor(logging.DEBUG):
            formatted = {k: f"{v * 1000:.1f}ms" for k, v in timings.items()}
            logger.debug(
                "Tick timings session=%s tick=%s orders=%s total=%s breakdown=%s",
                session_id,
                tick,
                order_count,
                formatted.pop("total"),
                formatted,
            )

        return result_payload

    def _schedule_background(self, coro: Awaitable[Any]) -> None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return

        task = loop.create_task(coro)
        self._background_tasks.add(task)

        def _done(t: asyncio.Task) -> None:
            self._background_tasks.discard(t)
            try:
                t.result()
            except Exception as exc:
                logger.error("Background task failed: %s", exc)

        task.add_done_callback(_done)

    def _publish_stream_event(self, session_code: str, payload: dict[str, Any]) -> None:
        """Enqueue structured payload into the Redis stream for WebSocket delivery."""
        if self._cache is None:
            return

        channel = payload.get("channel", "broadcast")
        event = payload.copy()
        event.setdefault("session_code", session_code)

        def _default(obj: Any) -> str:
            if isinstance(obj, datetime):
                return obj.isoformat()
            return str(obj)

        try:
            serialized = json.dumps(event, default=_default, ensure_ascii=False)
        except TypeError:  # pragma: no cover - unexpected payloads
            serialized = json.dumps(
                {"channel": channel, "error": "serialization_failed"},
                ensure_ascii=False,
            )

        self._schedule_background(
            self._cache.append_event(
                session_code,
                {
                    "channel": channel,
                    "payload": serialized,
                },
            )
        )

    async def _emit_coach_logs(
        self,
        *,
        session_id: int,
        session_code: str,
        tick: int,
        snapshot: MarketSnapshot,
        trades: list[TradeEventRecord],
        score_adjustments: dict[str, float],
        created_at: datetime,
    ) -> None:
        if not trades:
            return
        insights = self._coach_builder.build(
            session_id=session_id,
            session_code=session_code,
            tick=tick,
            snapshot=snapshot,
            trades=trades,
            score_deltas=score_adjustments,
            created_at=created_at,
        )
        if not insights:
            return
        if self._agent_logs is not None:
            await self._agent_logs.record_logs(insights)
        await self._publish_coach_logs(insights)

    async def _publish_coach_logs(self, insights: list[CoachInsight]) -> None:
        if not insights:
            return
        if self._cache is None:
            return
        for insight in insights:
            payload = {
                "session_id": insight.session_id,
                "session_code": insight.session_code,
                "tick": insight.tick,
                "participant_id": insight.participant_id,
                "participant_type": insight.participant_type,
                "category": insight.category,
                "severity": insight.severity,
                "headline": insight.headline,
                "summary": insight.summary,
                "metrics": insight.metrics,
                "recommendations": insight.recommendations,
                "created_at": insight.created_at.isoformat(),
            }
            await self._cache.enqueue_coach_log(payload)

    async def _build_agent_context(
        self,
        *,
        session_id: int,
        engine: MatchingEngine,
    ) -> "AgentContext":
        from .agents import AgentContext  # local import to avoid circular deps

        best_bid = engine.order_book.best_bid()
        best_ask = engine.order_book.best_ask()
        profile = dict(self._session_profiles.get(session_id) or {})
        latest_pool_stats = self._latest_pool_stats.get(session_id)
        if latest_pool_stats:
            profile["pool_stats"] = {
                code: {
                    "gross_buy": stat.gross_buy,
                    "gross_sell": stat.gross_sell,
                    "net_flow": stat.net_flow,
                }
                for code, stat in latest_pool_stats.items()
            }
            retail_stat = latest_pool_stats.get("retail")
            if retail_stat is not None:
                profile["retail_net_flow"] = retail_stat.net_flow
        context = AgentContext(
            feature_provider=self._features,
            emotion_provider=self._emotion,
            last_price=self._last_price.get(session_id) or None,
            best_bid=best_bid[0] if best_bid else None,
            best_ask=best_ask[0] if best_ask else None,
            profile=self._attach_retail_heat(session_id, profile),
        )
        return context

    def _attach_retail_heat(
        self, session_id: int, profile: dict[str, Any]
    ) -> dict[str, Any]:
        history = self._retail_flow_history.get(session_id) or []
        if not history:
            profile.setdefault("retail_heat", 1.0)
            return profile
        latest = history[-1]
        average = sum(history) / len(history) if history else 0.0
        heat = 1.0
        if average > 0:
            heat = max(0.0, latest / average)
        profile["retail_heat"] = heat
        return profile

    def _build_market_snapshot(
        self,
        session_id: int,
        tick: int,
        ts: datetime,
        engine: MatchingEngine,
        trades: Sequence[TradeEventRecord],
        signed_volume: float,
    ) -> MarketSnapshot:
        best_bid = engine.order_book.best_bid()
        best_ask = engine.order_book.best_ask()

        last_price = self._last_price[session_id]
        if trades:
            last_price = trades[-1].price
            self._last_price[session_id] = last_price

        total_volume = sum(t.quantity for t in trades)
        bid_qty = best_bid[1] if best_bid else 0.0
        ask_qty = best_ask[1] if best_ask else 0.0
        imbalance = 0.0
        if bid_qty + ask_qty > 0:
            imbalance = (bid_qty - ask_qty) / (bid_qty + ask_qty)

        return MarketSnapshot(
            session_id=session_id,
            tick=tick,
            timestamp=ts,
            best_bid=best_bid[0] if best_bid else None,
            best_ask=best_ask[0] if best_ask else None,
            last_price=last_price if last_price else None,
            vwap_price=last_price if trades else None,
            total_volume=total_volume,
            imbalance=imbalance,
            sentiment_score=self._impact.evaluate(
                OrderSide.BUY if signed_volume >= 0 else OrderSide.SELL,
                abs(signed_volume),
            ),
            liquidity_level=max(bid_qty, ask_qty),
            features={},
            emotion=None,
            payload={
                "signed_volume": signed_volume,
                "order_book_depth": {
                    "bid_levels": len(engine.order_book.bid_prices),
                    "ask_levels": len(engine.order_book.ask_prices),
                },
            },
        )

    def _build_snapshot_features(
        self,
        snapshot: MarketSnapshot,
        trades: Sequence[TradeEventRecord],
        signed_volume: float,
        pool_stats: Dict[str, PoolTickStat],
    ) -> Dict[str, float]:
        spread = 0.0
        if snapshot.best_bid is not None and snapshot.best_ask is not None:
            spread = max(snapshot.best_ask - snapshot.best_bid, 0.0)
        mid_price = snapshot.last_price or snapshot.vwap_price or 0.0
        if snapshot.best_bid is not None and snapshot.best_ask is not None:
            mid_price = (snapshot.best_bid + snapshot.best_ask) / 2.0

        trade_prices = [trade.price for trade in trades if trade.price is not None]
        volatility = pstdev(trade_prices) if len(trade_prices) > 1 else 0.0
        last_trade_price = trade_prices[-1] if trade_prices else snapshot.last_price or 0.0

        depth = snapshot.payload.get("order_book_depth", {})
        depth_bid = depth.get("bid_levels", 0)
        depth_ask = depth.get("ask_levels", 0)

        features = {
            "spread": spread,
            "mid_price": mid_price,
            "trade_count": len(trades),
            "trade_volume": snapshot.total_volume or 0.0,
            "signed_volume": signed_volume,
            "volatility": volatility,
            "last_trade_price": last_trade_price,
            "depth_bid_levels": depth_bid,
            "depth_ask_levels": depth_ask,
            "imbalance": snapshot.imbalance or 0.0,
        }

        for code, stat in pool_stats.items():
            features[f"pool_{code}_net_flow"] = stat.net_flow
            features[f"pool_{code}_buy"] = stat.gross_buy
            features[f"pool_{code}_sell"] = stat.gross_sell

        return features

    def _to_engine_order(self, session_id: int, data: dict) -> Order:
        try:
            side = OrderSide(data["side"])
            order_type = OrderType(data["type"])
        except KeyError as exc:  # pragma: no cover - caller validation
            raise ValueError(f"Missing field: {exc}") from exc

        price = data.get("price")
        if order_type == OrderType.LIMIT and price is None:
            raise ValueError("Limit order must supply price.")

        # T031: Get timestamp from payload or generate if missing
        timestamp_ns = data.get("timestamp", 0)
        if timestamp_ns == 0:
            # Generate nanosecond timestamp if not provided
            import time
            timestamp_ns = time.time_ns()

        order = Order(
            order_id=data["order_id"],
            session_id=session_id,
            participant_id=data["participant_id"],
            side=side,
            order_type=order_type,
            quantity=float(data["quantity"]),
            price=float(price) if price is not None else None,
            timestamp=timestamp_ns,  # T031: Set timestamp for price-time priority
        )
        return order

    async def _ensure_participants(
        self,
        *,
        session_id: int,
        payloads: Sequence[dict],
    ) -> dict[str, int]:
        if not payloads:
            return {}
        mapping: dict[str, int] = {}
        cache = self._participant_db_cache[session_id]
        pending_meta: dict[str, dict] = {}
        session_code = self._session_codes.get(session_id)
        redis_cache = self._cache

        for payload in payloads:
            code = payload.get("participant_code") or payload.get("participant_id")
            if not code or code in mapping:
                continue

            cached = cache.get(code)
            if cached:
                mapping[code] = cached
                continue

            participant_type = payload.get("participant_type")
            if not participant_type:
                pid = payload.get("participant_id", "")
                if isinstance(pid, str) and pid.startswith(
                    ("agent", "prop", "institutional", "retail", "mm")
                ):
                    participant_type = "agent"
                else:
                    participant_type = "player"

            pending_meta[code] = {
                "participant_type": participant_type,
                "player_id": payload.get("player_id"),
                "agent_profile_id": payload.get("agent_profile_id"),
            }

        if not pending_meta:
            return mapping

        codes = list(pending_meta.keys())
        if session_code and redis_cache is not None:
            try:
                redis_hits = await redis_cache.get_participant_ids(session_code, codes)
            except Exception:
                redis_hits = {}
            if redis_hits:
                for code, db_id in redis_hits.items():
                    cache[code] = db_id
                    mapping[code] = db_id
                    pending_meta.pop(code, None)
                if not pending_meta:
                    return mapping
                codes = list(pending_meta.keys())

        existing = await self._sessions.fetch_participant_ids(session_id, codes)
        for code, db_id in existing.items():
            cache[code] = db_id
            mapping[code] = db_id
            pending_meta.pop(code, None)

        if session_code and redis_cache is not None and existing:
            try:
                await redis_cache.set_participant_ids(session_code, existing)
            except Exception:
                pass

        remaining = list(pending_meta.keys())
        new_entries: dict[str, int] = {}

        if remaining:
            bulk_payloads = [
                {
                    "participant_code": code,
                    "participant_type": pending_meta[code]["participant_type"],
                    "player_id": pending_meta[code]["player_id"],
                    "agent_profile_id": pending_meta[code]["agent_profile_id"],
                }
                for code in remaining
            ]
            bulk_result: dict[str, int] = {}
            try:
                bulk_result = await self._sessions.ensure_participants_bulk(
                    session_id=session_id,
                    payloads=bulk_payloads,
                )
            except Exception as exc:
                logger.warning("bulk participant ensure failed: %s", exc)

            for code, db_id in bulk_result.items():
                cache[code] = db_id
                mapping[code] = db_id
                new_entries[code] = db_id
                remaining.remove(code)

        if remaining:
            async def ensure_code(code: str, meta: dict) -> None:
                async with self._participant_semaphore:
                    participant_db_id = await self._sessions.ensure_participant(
                        session_id=session_id,
                        participant_code=code,
                        participant_type=meta["participant_type"],
                        player_id=meta["player_id"],
                        agent_profile_id=meta["agent_profile_id"],
                    )
                cache[code] = participant_db_id
                mapping[code] = participant_db_id
                new_entries[code] = participant_db_id

            await asyncio.gather(
                *(ensure_code(code, pending_meta[code]) for code in remaining)
            )

        if session_code and redis_cache is not None and new_entries:
            try:
                await redis_cache.set_participant_ids(session_code, new_entries)
            except Exception:
                pass

        return mapping

    async def _ensure_default_agents(self, session_id: int) -> None:
        if self._agents is None:
            return
        if await self._agents.has_agents(session_id):
            return
        from .agents import (
            RetailSentimentAgent,
            PropMomentumAgent,
            InstitutionalRebalanceAgent,
            MarketMakerAgent,
            DepthQuoterAgent,
        )

        enabled = self._enabled_agent_pools

        if "retail" in enabled:
            await self._agents.register(
                session_id, RetailSentimentAgent(), pool_code="retail"
            )
        if "prop" in enabled:
            await self._agents.register(
                session_id, self._build_prop_agent(PropMomentumAgent), pool_code="prop"
            )
        if "institutional" in enabled:
            await self._agents.register(
                session_id, InstitutionalRebalanceAgent(), pool_code="institutional"
            )
        if settings.SIM_MARKET_MAKER_ENABLED and "market_maker" in enabled:
            await self._agents.register(
                session_id, MarketMakerAgent(), pool_code="market_maker"
            )
        if "depth" in enabled and "institutional" in enabled:
            await self._agents.register(
                session_id,
                DepthQuoterAgent(
                    code="depth-A",
                    participant_prefix="depth-A",
                    base_quantity=180.0,
                    spread_bps=9.0,
                    level_spacing_bps=5.0,
                    levels=50,
                    decay=0.92,
                    refresh_interval=6,
                ),
                pool_code="institutional",
            )
        if "depth" in enabled and "prop" in enabled:
            await self._agents.register(
                session_id,
                DepthQuoterAgent(
                    code="depth-B",
                    participant_prefix="depth-B",
                    base_quantity=90.0,
                    spread_bps=11.0,
                    level_spacing_bps=6.0,
                    levels=50,
                    decay=0.9,
                    refresh_interval=4,
                ),
                pool_code="prop",
            )
        if "depth" in enabled and "retail" in enabled:
            await self._agents.register(
                session_id,
                DepthQuoterAgent(
                    code="depth-C",
                    participant_prefix="depth-C",
                    base_quantity=35.0,
                    spread_bps=13.0,
                    level_spacing_bps=7.0,
                    levels=50,
                    decay=0.88,
                    refresh_interval=3,
                ),
                pool_code="retail",
            )

    # ------------------------------------------------------------------ #
    # Market state interactions
    async def record_market_snapshots(
        self, snapshots: Iterable[MarketSnapshot]
    ) -> None:
        await self._market.bulk_insert(snapshots)

    async def fetch_recent_market_state(
        self, session_id: int, limit: int
    ) -> list[MarketSnapshot]:
        return await self._market.fetch_recent(session_id=session_id, limit=limit)

    # ------------------------------------------------------------------ #
    # Leaderboard helpers
    async def update_leaderboard(
        self, session_code: str, participant_id: str, score: float
    ) -> None:
        await self._cache.update_leaderboard(session_code, participant_id, score)

    async def top_leaderboard(
        self,
        session_code: str,
        *,
        limit: int = 10,
        reverse: bool = True,
    ) -> list[LeaderboardEntry]:
        return await self._cache.top_leaderboard(
            session_code, limit=limit, reverse=reverse
        )

    @staticmethod
    def _parse_enabled_agent_pools() -> set[str]:
        default = {"retail", "prop", "institutional", "market_maker", "depth"}
        raw = os.getenv("SIM_AGENT_POOLS")
        if not raw or raw.strip().lower() in {"", "all", "default"}:
            return default
        tokens = {
            token.strip().lower()
            for token in raw.split(",")
            if token.strip()
        }
        allowed = tokens & default
        return allowed or default

    @staticmethod
    def _env_flag(name: str, default: bool = False) -> bool:
        value = os.getenv(name)
        if value is None:
            return default
        return value.strip().lower() in {"1", "true", "yes", "on"}

    @staticmethod
    def _env_int(name: str, default: int) -> int:
        value = os.getenv(name)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default

    @staticmethod
    def _env_float(name: str, default: float) -> float:
        value = os.getenv(name)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            return default

    def _prop_override_enabled(self) -> bool:
        if self._env_flag("SIM_PROP_BURST_MODE"):
            return True
        return self._enabled_agent_pools == {"prop"}

    def _build_prop_agent(self, prop_cls):
        if not self._prop_override_enabled():
            return prop_cls()

        interval = max(1, self._env_int("SIM_PROP_BURST_INTERVAL", 30))
        duration = max(1, self._env_int("SIM_PROP_BURST_DURATION", 5))
        profit_target = self._env_float("SIM_PROP_PROFIT_TARGET", 0.05)
        stop_loss = self._env_float("SIM_PROP_STOP_LOSS", 0.2)
        volatility_trigger = self._env_float("SIM_PROP_VOLATILITY_TRIGGER", 0.0)
        noise = self._env_float("SIM_PROP_NOISE", 0.0)
        mean_reversion = self._env_float("SIM_PROP_MEAN_REVERSION", 0.0)
        burst_multiplier = self._env_float("SIM_PROP_BURST_MULTIPLIER", 4.0)
        base_quantity = self._env_float("SIM_PROP_BASE_QUANTITY", 180.0)
        momentum_sensitivity = self._env_float("SIM_PROP_MOMENTUM_SENSITIVITY", 1.0)
        herd_strength = self._env_float("SIM_PROP_HERD_STRENGTH", 0.8)

        return prop_cls(
            code=os.getenv("SIM_PROP_AGENT_CODE", "prop"),
            volatility_trigger=volatility_trigger,
            base_quantity=base_quantity,
            noise=noise,
            burst_interval_ticks=(interval, interval),
            burst_duration_range=(duration, duration),
            burst_multiplier=burst_multiplier,
            profit_target=profit_target,
            stop_loss=stop_loss,
            momentum_sensitivity=momentum_sensitivity,
            herd_behavior_strength=herd_strength,
            mean_reversion_strength=mean_reversion,
            cooldown_range=(interval, interval),
            strict_cooldown_range=(interval * 2, interval * 2),
        )


__all__ = ["SimulationService", "ImpactModel"]
