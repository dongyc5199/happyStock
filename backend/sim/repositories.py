"""Repositories for simulation subsystem entities."""

from __future__ import annotations

import json
import logging
import os
import uuid
from time import perf_counter
from typing import Any, Iterable, Optional, Sequence

from .types import (
    CoachInsight,
    MarketSnapshot,
    OrderEventRecord,
    OrderStatus,
    SimulationSession,
    TradeEventRecord,
    UserOrder,
)

try:
    import asyncpg  # type: ignore
except ImportError:  # pragma: no cover
    asyncpg = None  # type: ignore[misc]


def _ensure_asyncpg() -> None:
    if asyncpg is None:  # pragma: no cover
        raise RuntimeError("asyncpg not installed; simulation DB unavailable.")


def _normalize_uuid(value: Optional[str]) -> Optional[uuid.UUID]:
    if not value:
        return None
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError):
        return None



def _normalize_uuid(value: Optional[str]) -> Optional[uuid.UUID]:
    if not value:
        return None
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError):
        return None


logger = logging.getLogger(__name__)


class SimulationRepository:
    """TimescaleDB repository for simulation session metadata and participants."""

    def __init__(self, pool: Any) -> None:
        self._pool = pool

    async def create_session(self, session: SimulationSession) -> SimulationSession:
        _ensure_asyncpg()
        query = """
            INSERT INTO simulation_session
                (session_code, status, mode, tick_interval_ms, total_ticks, config_version)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id, created_at, updated_at
        """
        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            row = await conn.fetchrow(
                query,
                session.session_code,
                session.status,
                session.mode,
                session.tick_interval_ms,
                session.total_ticks,
                session.config_version,
            )
        session.id = row["id"]
        session.created_at = row["created_at"]
        session.updated_at = row["updated_at"]
        return session

    async def fetch_session_by_code(
        self, session_code: str
    ) -> Optional[SimulationSession]:
        _ensure_asyncpg()
        query = """
            SELECT
                id,
                session_code,
                status,
                mode,
                tick_interval_ms,
                COALESCE(current_tick, 0) AS current_tick,
                COALESCE(total_ticks, 0) AS total_ticks,
                config_version,
                created_at,
                updated_at,
                closed_at
            FROM simulation_session
            WHERE session_code = $1
            LIMIT 1
        """
        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            row = await conn.fetchrow(query, session_code)
        if row is None:
            return None
        return SimulationSession(
            id=row["id"],
            session_code=row["session_code"],
            status=row["status"],
            mode=row["mode"],
            tick_interval_ms=row["tick_interval_ms"],
            current_tick=row["current_tick"],
            total_ticks=row["total_ticks"],
            config_version=row["config_version"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            closed_at=row["closed_at"],
        )

    async def fetch_session_by_id(self, session_id: int) -> Optional[SimulationSession]:
        """Fetch session by numeric ID."""
        _ensure_asyncpg()
        query = """
            SELECT
                id,
                session_code,
                status,
                mode,
                tick_interval_ms,
                COALESCE(current_tick, 0) AS current_tick,
                COALESCE(total_ticks, 0) AS total_ticks,
                config_version,
                created_at,
                updated_at,
                closed_at
            FROM simulation_session
            WHERE id = $1
            LIMIT 1
        """
        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            row = await conn.fetchrow(query, session_id)
        if row is None:
            return None
        return SimulationSession(
            id=row["id"],
            session_code=row["session_code"],
            status=row["status"],
            mode=row["mode"],
            tick_interval_ms=row["tick_interval_ms"],
            current_tick=row["current_tick"],
            total_ticks=row["total_ticks"],
            config_version=row["config_version"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            closed_at=row["closed_at"],
        )

    async def update_tick(self, session_id: int, tick: int) -> None:
        _ensure_asyncpg()
        query = """
            UPDATE simulation_session
               SET current_tick = $2,
                   total_ticks = GREATEST(total_ticks, $2),
                   updated_at = NOW()
             WHERE id = $1
        """
        threshold_ms = float(
            os.getenv("SIM_SLOW_UPDATE_TICK_THRESHOLD_MS", "50.0")
        )
        explain_enabled = os.getenv("SIM_EXPLAIN_TICK", "0").lower() in (
            "1",
            "true",
            "yes",
        )

        start = perf_counter()
        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            await conn.execute(query, session_id, tick)
        elapsed_ms = (perf_counter() - start) * 1000.0

        if elapsed_ms > threshold_ms:
            logger.warning(
                "simulation.update_tick slow query: session_id=%s tick=%s elapsed_ms=%.2f",
                session_id,
                tick,
                elapsed_ms,
            )
            if explain_enabled:
                explain_sql = (
                    "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) " + query
                )
                try:
                    async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
                        plan = await conn.fetchval(explain_sql, session_id, tick)
                    logger.warning(
                        "simulation.update_tick explain: session_id=%s tick=%s plan=%s",
                        session_id,
                        tick,
                        plan,
                    )
                except Exception as exc:  # pragma: no cover - diagnostics only
                    logger.warning(
                        "simulation.update_tick EXPLAIN failed: %s", exc
                    )

    async def adjust_participant_score(self, participant_id: int, delta: float) -> None:
        _ensure_asyncpg()
        query = """
            UPDATE session_participant
               SET score = score + $2,
                   updated_at = NOW()
             WHERE id = $1
        """
        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            await conn.execute(query, participant_id, delta)

    async def ensure_participant(
        self,
        *,
        session_id: int,
        participant_code: str,
        participant_type: str,
        player_id: Optional[str] = None,
        agent_profile_id: Optional[int] = None,
    ) -> int:
        """
        Ensure a session_participant row exists for the given code.

        Returns the database primary key.
        """
        _ensure_asyncpg()
        player_uuid = _normalize_uuid(player_id)
        query = """
            INSERT INTO session_participant (
                session_id,
                participant_type,
                player_id,
                agent_profile_id,
                participant_code
            )
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (session_id, participant_code)
            DO UPDATE SET
                participant_type = COALESCE(EXCLUDED.participant_type, session_participant.participant_type),
                player_id = COALESCE(EXCLUDED.player_id, session_participant.player_id),
                agent_profile_id = COALESCE(
                    EXCLUDED.agent_profile_id, session_participant.agent_profile_id
                ),
                updated_at = NOW()
            RETURNING id
        """
        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            participant_id = await conn.fetchval(
                query,
                session_id,
                participant_type,
                player_uuid,
                agent_profile_id,
                participant_code,
            )
        return int(participant_id)

    async def ensure_participants_bulk(
        self,
        session_id: int,
        payloads: Sequence[dict[str, Any]],
    ) -> dict[str, int]:
        """
        T063: Enhanced to support behavior parameter persistence.
        """
        if not payloads:
            return {}
        _ensure_asyncpg()

        codes = [payload["participant_code"] for payload in payloads]
        participant_types = [
            payload.get("participant_type") or "player" for payload in payloads
        ]
        player_ids = [
            _normalize_uuid(payload.get("player_id")) for payload in payloads
        ]
        agent_profile_ids = [
            payload.get("agent_profile_id") or 0 for payload in payloads
        ]

        # T063: Extract behavior parameters from payloads
        behavior_categories = [payload.get("behavior_category") for payload in payloads]
        profit_targets = [payload.get("profit_target") for payload in payloads]
        stop_losses = [payload.get("stop_loss") for payload in payloads]
        herd_behaviors = [payload.get("herd_behavior_strength") for payload in payloads]
        momentum_sensitivities = [payload.get("momentum_sensitivity") for payload in payloads]
        risk_tolerances = [payload.get("risk_tolerance") for payload in payloads]

        query = """
            WITH input_data AS (
                SELECT
                    unnest($1::text[]) AS participant_code,
                    unnest($2::text[]) AS participant_type,
                    unnest($3::uuid[]) AS player_id,
                    unnest($4::int[]) AS agent_profile_id,
                    unnest($6::text[]) AS behavior_category,
                    unnest($7::decimal[]) AS profit_target,
                    unnest($8::decimal[]) AS stop_loss,
                    unnest($9::decimal[]) AS herd_behavior_strength,
                    unnest($10::decimal[]) AS momentum_sensitivity,
                    unnest($11::decimal[]) AS risk_tolerance
            )
            INSERT INTO session_participant (
                session_id,
                participant_type,
                player_id,
                agent_profile_id,
                participant_code,
                behavior_category,
                profit_target,
                stop_loss,
                herd_behavior_strength,
                momentum_sensitivity,
                risk_tolerance
            )
            SELECT
                $5,
                input_data.participant_type,
                input_data.player_id,
                NULLIF(input_data.agent_profile_id, 0),
                input_data.participant_code,
                input_data.behavior_category,
                input_data.profit_target,
                input_data.stop_loss,
                input_data.herd_behavior_strength,
                input_data.momentum_sensitivity,
                input_data.risk_tolerance
            FROM input_data
            ON CONFLICT (session_id, participant_code)
            DO UPDATE SET
                participant_type = COALESCE(
                    EXCLUDED.participant_type,
                    session_participant.participant_type
                ),
                player_id = COALESCE(
                    EXCLUDED.player_id,
                    session_participant.player_id
                ),
                agent_profile_id = COALESCE(
                    EXCLUDED.agent_profile_id,
                    session_participant.agent_profile_id
                ),
                behavior_category = COALESCE(
                    EXCLUDED.behavior_category,
                    session_participant.behavior_category
                ),
                profit_target = COALESCE(
                    EXCLUDED.profit_target,
                    session_participant.profit_target
                ),
                stop_loss = COALESCE(
                    EXCLUDED.stop_loss,
                    session_participant.stop_loss
                ),
                herd_behavior_strength = COALESCE(
                    EXCLUDED.herd_behavior_strength,
                    session_participant.herd_behavior_strength
                ),
                momentum_sensitivity = COALESCE(
                    EXCLUDED.momentum_sensitivity,
                    session_participant.momentum_sensitivity
                ),
                risk_tolerance = COALESCE(
                    EXCLUDED.risk_tolerance,
                    session_participant.risk_tolerance
                ),
                updated_at = NOW()
            RETURNING participant_code, id
        """

        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            rows = await conn.fetch(
                query,
                codes,
                participant_types,
                player_ids,
                [ap_id or 0 for ap_id in agent_profile_ids],
                session_id,
                behavior_categories,
                profit_targets,
                stop_losses,
                herd_behaviors,
                momentum_sensitivities,
                risk_tolerances,
            )
        return {row["participant_code"]: row["id"] for row in rows}

    async def fetch_participant_ids(
        self, session_id: int, participant_codes: Sequence[str]
    ) -> dict[str, int]:
        """Return mapping from participant_code to numeric id for the provided codes."""
        if not participant_codes:
            return {}
        _ensure_asyncpg()
        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            rows = await conn.fetch(
                """
                SELECT participant_code, id
                  FROM session_participant
                 WHERE session_id = $1
                   AND participant_code = ANY($2::text[])
                """,
                session_id,
                list(participant_codes),
            )
        return {row["participant_code"]: row["id"] for row in rows}

    async def batch_create_participants(
        self,
        session_id: int,
        participants: Sequence[dict[str, Any]],
    ) -> dict[str, int]:
        """
        Batch create participants for performance optimization (T023).
        This is an alias for ensure_participants_bulk for clarity.
        """
        return await self.ensure_participants_bulk(session_id, participants)

    async def fetch_participant_behavior(
        self,
        session_id: int,
        participant_code: str,
    ) -> dict[str, Any] | None:
        """
        T063: Fetch behavior parameters for a participant.

        Returns:
            Dictionary with behavior parameters or None if not found
        """
        _ensure_asyncpg()
        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            row = await conn.fetchrow(
                """
                SELECT
                    behavior_category,
                    profit_target,
                    stop_loss,
                    herd_behavior_strength,
                    momentum_sensitivity,
                    risk_tolerance
                FROM session_participant
                WHERE session_id = $1 AND participant_code = $2
                """,
                session_id,
                participant_code,
            )
        if row is None:
            return None
        return dict(row)

    async def update_participant(
        self,
        session_id: int,
        participant_code: str,
        *,
        behavior_category: Optional[str] = None,
        profit_target: Optional[float] = None,
        stop_loss: Optional[float] = None,
        herd_behavior_strength: Optional[float] = None,
        momentum_sensitivity: Optional[float] = None,
        risk_tolerance: Optional[float] = None,
    ) -> bool:
        """
        T073: Update behavior parameters for an existing participant.

        Only non-None parameters are updated. Returns True if the update succeeded.
        """
        _ensure_asyncpg()

        # Build dynamic SET clause for non-None parameters
        updates: list[str] = []
        params: list[Any] = [session_id, participant_code]
        param_idx = 3

        if behavior_category is not None:
            updates.append(f"behavior_category = ${param_idx}")
            params.append(behavior_category)
            param_idx += 1
        if profit_target is not None:
            updates.append(f"profit_target = ${param_idx}")
            params.append(profit_target)
            param_idx += 1
        if stop_loss is not None:
            updates.append(f"stop_loss = ${param_idx}")
            params.append(stop_loss)
            param_idx += 1
        if herd_behavior_strength is not None:
            updates.append(f"herd_behavior_strength = ${param_idx}")
            params.append(herd_behavior_strength)
            param_idx += 1
        if momentum_sensitivity is not None:
            updates.append(f"momentum_sensitivity = ${param_idx}")
            params.append(momentum_sensitivity)
            param_idx += 1
        if risk_tolerance is not None:
            updates.append(f"risk_tolerance = ${param_idx}")
            params.append(risk_tolerance)
            param_idx += 1

        if not updates:
            # No parameters to update
            return False

        # Add updated_at
        updates.append("updated_at = NOW()")

        query = f"""
            UPDATE session_participant
            SET {', '.join(updates)}
            WHERE session_id = $1 AND participant_code = $2
        """

        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            result = await conn.execute(query, *params)

        # PostgreSQL returns "UPDATE n" where n is the number of rows affected
        return result.endswith(" 1")

    async def update_avg_position_cost(
        self,
        session_id: int,
        participant_code: str,
        avg_position_cost: Optional[float],
    ) -> bool:
        """
        T074: Update average position cost for position tracking.

        This is used by prop traders to track their entry prices for P&L calculation.
        Setting to None clears the position (after closing).
        """
        _ensure_asyncpg()
        query = """
            UPDATE session_participant
            SET avg_position_cost = $3,
                updated_at = NOW()
            WHERE session_id = $1 AND participant_code = $2
        """
        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            result = await conn.execute(query, session_id, participant_code, avg_position_cost)

        # PostgreSQL returns "UPDATE n" where n is the number of rows affected
        return result.endswith(" 1")

    async def list_agents(
        self,
        session_id: int,
        *,
        participant_type: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        T075: List all agents in a session with their behavior parameters.

        Parameters
        ----------
        session_id : Session ID
        participant_type : Optional filter by participant type (e.g., 'ai_agent')

        Returns
        -------
        List of agent details including behavior parameters
        """
        _ensure_asyncpg()
        query = """
            SELECT
                participant_code,
                participant_type,
                behavior_category,
                profit_target,
                stop_loss,
                herd_behavior_strength,
                momentum_sensitivity,
                risk_tolerance,
                avg_position_cost,
                score,
                created_at,
                updated_at
            FROM session_participant
            WHERE session_id = $1
        """
        params: list[Any] = [session_id]

        if participant_type:
            query += " AND participant_type = $2"
            params.append(participant_type)

        query += " ORDER BY participant_code"

        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            rows = await conn.fetch(query, *params)

        return [dict(row) for row in rows]

    async def get_agent(
        self,
        session_id: int,
        participant_code: str,
    ) -> Optional[dict[str, Any]]:
        """
        T076: Get detailed information for a single agent.

        Returns
        -------
        Agent details or None if not found
        """
        _ensure_asyncpg()
        query = """
            SELECT
                participant_code,
                participant_type,
                behavior_category,
                profit_target,
                stop_loss,
                herd_behavior_strength,
                momentum_sensitivity,
                risk_tolerance,
                avg_position_cost,
                score,
                created_at,
                updated_at
            FROM session_participant
            WHERE session_id = $1 AND participant_code = $2
        """
        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            row = await conn.fetchrow(query, session_id, participant_code)

        if row is None:
            return None
        return dict(row)


class MarketStateRepository:
    """Persistence helpers for the market_state hypertable."""

    def __init__(self, pool: Any) -> None:
        self._pool = pool

    async def bulk_insert(self, snapshots: Iterable[MarketSnapshot]) -> None:
        _ensure_asyncpg()
        records = list(snapshots)
        if not records:
            return

        query = """
            INSERT INTO market_state (
                session_id, tick, ts, best_bid, best_ask, last_price,
                vwap_price, total_volume, imbalance, sentiment_score,
                liquidity_level, payload
            )
            VALUES (
                $1, $2, $3, $4, $5, $6,
                $7, $8, $9, $10,
                $11, $12::jsonb
            )
            ON CONFLICT (session_id, tick, ts) DO UPDATE
            SET ts = EXCLUDED.ts,
                best_bid = EXCLUDED.best_bid,
                best_ask = EXCLUDED.best_ask,
                last_price = EXCLUDED.last_price,
                vwap_price = EXCLUDED.vwap_price,
                total_volume = EXCLUDED.total_volume,
                imbalance = EXCLUDED.imbalance,
                sentiment_score = EXCLUDED.sentiment_score,
                liquidity_level = EXCLUDED.liquidity_level,
                payload = EXCLUDED.payload
        """

        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            async with conn.transaction():
                await conn.executemany(
                    query,
                    [
                        (
                            snapshot.session_id,
                            snapshot.tick,
                            snapshot.timestamp,
                            snapshot.best_bid,
                            snapshot.best_ask,
                            snapshot.last_price,
                            snapshot.vwap_price,
                            snapshot.total_volume,
                            snapshot.imbalance,
                            snapshot.sentiment_score,
                            snapshot.liquidity_level,
                            json.dumps(snapshot.payload)
                            if snapshot.payload is not None
                            else "{}",
                        )
                        for snapshot in records
                    ],
                )

    async def fetch_recent(
        self,
        session_id: int,
        limit: int = 100,
    ) -> list[MarketSnapshot]:
        _ensure_asyncpg()
        query = """
            SELECT session_id, tick, ts, best_bid, best_ask, last_price,
                   vwap_price, total_volume, imbalance, sentiment_score,
                   liquidity_level, payload
              FROM market_state
             WHERE session_id = $1
             ORDER BY tick DESC
             LIMIT $2
        """
        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            rows = await conn.fetch(query, session_id, limit)
        snapshots: list[MarketSnapshot] = []
        for row in rows:
            payload = row["payload"]
            if isinstance(payload, str):
                payload = json.loads(payload)
            snapshots.append(
                MarketSnapshot(
                    session_id=row["session_id"],
                    tick=row["tick"],
                    timestamp=row["ts"],
                    best_bid=row["best_bid"],
                    best_ask=row["best_ask"],
                    last_price=row["last_price"],
                    vwap_price=row["vwap_price"],
                    total_volume=row["total_volume"],
                    imbalance=row["imbalance"],
                    sentiment_score=row["sentiment_score"],
                    liquidity_level=row["liquidity_level"],
                    payload=payload or {},
                )
            )
        return snapshots


class OrderTradeRepository:
    """Persistence for order_event and trade_event hypertables."""

    ORDER_INSERT = """
        INSERT INTO order_event (
            session_id, tick, participant_id, side, order_type,
            price, quantity, remaining_qty, status, impact, metadata, created_at,
            order_code, participant_code
        )
        VALUES (
            $1, $2, $3, $4, $5,
            $6, $7, $8, $9, $10, $11::jsonb, $12,
            $13, $14
        )
    """

    TRADE_INSERT = """
        INSERT INTO trade_event (
            session_id, tick, buy_order_id, sell_order_id,
            price, quantity, impact,
            buyer_participant_id, seller_participant_id,
            created_at,
            buy_order_code, sell_order_code,
            buyer_participant_code, seller_participant_code,
            buyer_type, seller_type
        )
        VALUES (
            $1, $2, NULL, NULL,
            $3, $4, NULL,
            $5, $6,
            $7,
            $8, $9,
            $10, $11,
            $12, $13
        )
    """

    def __init__(self, pool: Any) -> None:
        self._pool = pool

    async def record_orders(self, events: Iterable[OrderEventRecord]) -> None:
        await self.record_events(events, [])

    async def record_trades(self, trades: Iterable[TradeEventRecord]) -> None:
        await self.record_events([], trades)

    async def record_events(
        self,
        orders: Iterable[OrderEventRecord],
        trades: Iterable[TradeEventRecord],
    ) -> tuple[float, float]:
        _ensure_asyncpg()
        order_records = list(orders)
        trade_records = list(trades)
        if not order_records and not trade_records:
            return 0.0, 0.0

        order_elapsed = 0.0
        trade_elapsed = 0.0

        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            async with conn.transaction():
                if order_records:
                    start = perf_counter()
                    await conn.executemany(
                        self.ORDER_INSERT,
                        [
                            (
                                event.session_id,
                                event.tick,
                                event.participant_db_id,
                                event.side,
                                event.order_type,
                                event.price,
                                event.quantity,
                                event.remaining_qty,
                                event.status,
                                event.impact,
                                json.dumps({"order_code": event.order_code}),
                                event.created_at,
                                event.order_code,
                                event.participant_code,
                            )
                            for event in order_records
                        ],
                    )
                    order_elapsed = perf_counter() - start

                if trade_records:
                    start = perf_counter()
                    await conn.executemany(
                        self.TRADE_INSERT,
                        [
                            (
                                trade.session_id,
                                trade.tick,
                                trade.price,
                                trade.quantity,
                                trade.buyer_participant_db_id,
                                trade.seller_participant_db_id,
                                trade.created_at,
                                trade.buy_order_code,
                                trade.sell_order_code,
                                trade.buyer_participant_code,
                                trade.seller_participant_code,
                                trade.buyer_type,  # T024
                                trade.seller_type,  # T024
                            )
                            for trade in trade_records
                        ],
                    )
                    trade_elapsed = perf_counter() - start

        return order_elapsed, trade_elapsed

    async def get_agent_performance(
        self,
        session_id: int,
        participant_code: str,
    ) -> dict[str, Any]:
        """
        T078: Get performance statistics for a single agent.

        Returns order count, trade count, volume, etc.
        """
        _ensure_asyncpg()

        # Get order statistics
        order_query = """
            SELECT
                COUNT(*) as total_orders,
                COALESCE(SUM(quantity), 0) as total_order_volume
            FROM order_event
            WHERE session_id = $1 AND participant_code = $2
        """

        # Get trade statistics
        trade_query = """
            SELECT
                COUNT(*) as total_trades,
                COALESCE(SUM(quantity), 0) as total_trade_volume,
                COALESCE(AVG(quantity), 0) as avg_trade_size
            FROM trade_event
            WHERE session_id = $1
              AND (buyer_participant_code = $2 OR seller_participant_code = $2)
        """

        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            order_row = await conn.fetchrow(order_query, session_id, participant_code)
            trade_row = await conn.fetchrow(trade_query, session_id, participant_code)

        return {
            "participant_code": participant_code,
            "total_orders": int(order_row["total_orders"]) if order_row else 0,
            "total_trades": int(trade_row["total_trades"]) if trade_row else 0,
            "total_volume": float(trade_row["total_trade_volume"]) if trade_row else 0.0,
            "avg_trade_size": float(trade_row["avg_trade_size"]) if trade_row else 0.0,
            "win_rate": None,  # TODO: Calculate from P&L data
            "profit_loss_pct": None,  # TODO: Calculate from position data
            "sharpe_ratio": None,  # TODO: Calculate from returns series
        }

    async def get_pool_statistics(
        self,
        session_id: int,
        pool_code: str,
    ) -> dict[str, Any]:
        """
        T079-T080: Get aggregated statistics for all agents in a pool.

        Pool code is typically the behavior_category (e.g., 'retail', 'institutional').
        """
        _ensure_asyncpg()

        # Get pool aggregate statistics from trades
        stats_query = """
            SELECT
                COUNT(DISTINCT sp.participant_code) as agent_count,
                COUNT(DISTINCT oe.order_code) as total_orders,
                COUNT(DISTINCT te.buy_order_code) + COUNT(DISTINCT te.sell_order_code) as total_trades,
                COALESCE(SUM(te.quantity), 0) as total_volume
            FROM session_participant sp
            LEFT JOIN order_event oe
                ON oe.session_id = sp.session_id
                AND oe.participant_code = sp.participant_code
            LEFT JOIN trade_event te
                ON te.session_id = sp.session_id
                AND (te.buyer_participant_code = sp.participant_code
                     OR te.seller_participant_code = sp.participant_code)
            WHERE sp.session_id = $1
              AND sp.behavior_category = $2
        """

        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            row = await conn.fetchrow(stats_query, session_id, pool_code)

        return {
            "pool_code": pool_code,
            "agent_count": int(row["agent_count"]) if row else 0,
            "total_orders": int(row["total_orders"]) if row else 0,
            "total_trades": int(row["total_trades"]) if row else 0,
            "total_volume": float(row["total_volume"]) if row else 0.0,
        }

    async def list_pool_codes(self, session_id: int) -> list[str]:
        """
        T079: List all unique pool codes (behavior categories) in a session.
        """
        _ensure_asyncpg()
        query = """
            SELECT DISTINCT behavior_category
            FROM session_participant
            WHERE session_id = $1
              AND behavior_category IS NOT NULL
            ORDER BY behavior_category
        """
        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            rows = await conn.fetch(query, session_id)

        return [row["behavior_category"] for row in rows]


class AgentLogRepository:
    """Timescale repository for AI 鏁欑粌鏃ュ織 (agent_log hypertable)."""

    def __init__(self, pool: Any) -> None:
        self._pool = pool

    async def record_logs(self, logs: Iterable[CoachInsight]) -> None:
        _ensure_asyncpg()
        rows = [
            (
                log.session_id,
                log.tick,
                log.participant_db_id,
                log.category,
                json.dumps(
                    {
                        "session_code": log.session_code,
                        "participant_id": log.participant_id,
                        "participant_type": log.participant_type,
                        "severity": log.severity,
                        "headline": log.headline,
                        "summary": log.summary,
                        "metrics": log.metrics,
                        "recommendations": log.recommendations,
                        "created_at": log.created_at.isoformat(),
                    },
                    ensure_ascii=False,
                ),
                log.created_at,
            )
            for log in logs
            if log.participant_db_id is not None
        ]
        if not rows:
            return

        query = """
            INSERT INTO agent_log (
                session_id,
                tick,
                participant_id,
                event_type,
                detail,
                created_at
            )
            VALUES ($1, $2, $3, $4, $5::jsonb, $6)
            ON CONFLICT (session_id, tick, created_at, participant_id, event_type) DO NOTHING
        """
        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            await conn.executemany(query, rows)


class UserOrderRepository:
    """Repository for user-submitted orders (Feature: 001-ai-user-order-matching)."""

    def __init__(self, pool: Any) -> None:
        self._pool = pool

    async def create_order(self, order: UserOrder) -> UserOrder:
        """Create a new user order record (T018)."""
        _ensure_asyncpg()
        query = """
            INSERT INTO user_orders (
                order_id, session_id, user_id, participant_id,
                side, order_type, quantity, price, timestamp,
                status, filled_quantity, avg_filled_price
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            RETURNING created_at, updated_at
        """
        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            row = await conn.fetchrow(
                query,
                order.order_id,
                order.session_id,
                order.user_id,
                order.participant_id,
                order.side,
                order.order_type,
                order.quantity,
                order.price,
                order.timestamp,
                order.status.value if isinstance(order.status, OrderStatus) else order.status,
                order.filled_quantity,
                order.avg_filled_price,
            )
        order.created_at = row["created_at"]
        order.updated_at = row["updated_at"]
        return order

    async def get_order(self, order_id: str) -> Optional[UserOrder]:
        """Fetch a single order by order_id (T019)."""
        _ensure_asyncpg()
        query = """
            SELECT
                order_id, session_id, user_id, participant_id,
                side, order_type, quantity, price, timestamp,
                status, filled_quantity, avg_filled_price,
                created_at, updated_at
            FROM user_orders
            WHERE order_id = $1
        """
        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            row = await conn.fetchrow(query, order_id)
        if row is None:
            return None
        return UserOrder(
            order_id=row["order_id"],
            session_id=row["session_id"],
            user_id=row["user_id"],
            participant_id=row["participant_id"],
            side=row["side"],
            order_type=row["order_type"],
            quantity=float(row["quantity"]),
            timestamp=row["timestamp"],
            status=OrderStatus(row["status"]),
            filled_quantity=float(row["filled_quantity"]),
            price=float(row["price"]) if row["price"] is not None else None,
            avg_filled_price=float(row["avg_filled_price"]) if row["avg_filled_price"] is not None else None,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def list_orders(
        self,
        session_id: int,
        user_id: int,
        *,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[UserOrder], int]:
        """List orders for a session/user with optional status filter (T020)."""
        _ensure_asyncpg()
        where_clause = "WHERE session_id = $1 AND user_id = $2"
        params: list[Any] = [session_id, user_id]
        if status:
            where_clause += " AND status = $3"
            params.append(status)

        count_query = f"SELECT COUNT(*) as total FROM user_orders {where_clause}"

        list_query = f"""
            SELECT
                order_id, session_id, user_id, participant_id,
                side, order_type, quantity, price, timestamp,
                status, filled_quantity, avg_filled_price,
                created_at, updated_at
            FROM user_orders
            {where_clause}
            ORDER BY created_at DESC
            LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
        """
        params.extend([limit, offset])

        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            count_row = await conn.fetchrow(count_query, *params[:-2])
            total = count_row["total"] if count_row else 0
            rows = await conn.fetch(list_query, *params)

        orders = [
            UserOrder(
                order_id=row["order_id"],
                session_id=row["session_id"],
                user_id=row["user_id"],
                participant_id=row["participant_id"],
                side=row["side"],
                order_type=row["order_type"],
                quantity=float(row["quantity"]),
                timestamp=row["timestamp"],
                status=OrderStatus(row["status"]),
                filled_quantity=float(row["filled_quantity"]),
                price=float(row["price"]) if row["price"] is not None else None,
                avg_filled_price=float(row["avg_filled_price"]) if row["avg_filled_price"] is not None else None,
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]
        return orders, total

    async def update_order_status(
        self,
        order_id: str,
        status: str,
        filled_quantity: float,
        avg_filled_price: Optional[float] = None,
    ) -> bool:
        """Update order status and fill information (T021)."""
        _ensure_asyncpg()
        query = """
            UPDATE user_orders
            SET status = $2,
                filled_quantity = $3,
                avg_filled_price = $4,
                updated_at = NOW()
            WHERE order_id = $1
        """
        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            result = await conn.execute(query, order_id, status, filled_quantity, avg_filled_price)
        # PostgreSQL returns "UPDATE n" where n is the number of rows affected
        return result.endswith(" 1")

    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order if it's in a cancellable state (T022)."""
        _ensure_asyncpg()
        query = """
            UPDATE user_orders
            SET status = 'CANCELLED',
                updated_at = NOW()
            WHERE order_id = $1
              AND status IN ('PENDING', 'NEW', 'PARTIAL')
        """
        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            result = await conn.execute(query, order_id)
        return result.endswith(" 1")

