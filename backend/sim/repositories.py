"""Repositories for simulation subsystem entities."""

from __future__ import annotations

import json
from time import perf_counter
from typing import Any, Iterable, Optional, Sequence

from .types import (
    CoachInsight,
    MarketSnapshot,
    OrderEventRecord,
    SimulationSession,
    TradeEventRecord,
)

try:
    import asyncpg  # type: ignore
except ImportError:  # pragma: no cover
    asyncpg = None  # type: ignore[misc]


def _ensure_asyncpg() -> None:
    if asyncpg is None:  # pragma: no cover
        raise RuntimeError("asyncpg 未安装，无法访问仿真数据库。")


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

    async def update_tick(self, session_id: int, tick: int) -> None:
        _ensure_asyncpg()
        query = """
            UPDATE simulation_session
               SET current_tick = $2,
                   total_ticks = GREATEST(total_ticks, $2),
                   updated_at = NOW()
             WHERE id = $1
        """
        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            await conn.execute(query, session_id, tick)

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
                player_id,
                agent_profile_id,
                participant_code,
            )
        return int(participant_id)

    async def ensure_participants_bulk(
        self,
        session_id: int,
        payloads: Sequence[dict[str, Any]],
    ) -> dict[str, int]:
        if not payloads:
            return {}
        _ensure_asyncpg()

        codes = [payload["participant_code"] for payload in payloads]
        participant_types = [
            payload.get("participant_type") or "player" for payload in payloads
        ]
        player_ids = [payload.get("player_id") for payload in payloads]
        agent_profile_ids = [payload.get("agent_profile_id") for payload in payloads]

        query = """
            WITH input_data AS (
                SELECT
                    unnest($1::text[]) AS participant_code,
                    unnest($2::text[]) AS participant_type,
                    unnest($3::text[]) AS player_id,
                    unnest($4::int[]) AS agent_profile_id
            )
            INSERT INTO session_participant (
                session_id,
                participant_type,
                player_id,
                agent_profile_id,
                participant_code
            )
            SELECT
                $5,
                input_data.participant_type,
                input_data.player_id,
                NULLIF(input_data.agent_profile_id, 0),
                input_data.participant_code
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
            buyer_participant_code, seller_participant_code
        )
        VALUES (
            $1, $2, NULL, NULL,
            $3, $4, NULL,
            $5, $6,
            $7,
            $8, $9,
            $10, $11
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
                            )
                            for trade in trade_records
                        ],
                    )
                    trade_elapsed = perf_counter() - start

        return order_elapsed, trade_elapsed


class AgentLogRepository:
    """Timescale repository for AI 教练日志 (agent_log hypertable)."""

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
        """
        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            await conn.executemany(query, rows)
