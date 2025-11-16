"""Redis cache helpers for the simulation backend."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional, Sequence

try:
    from redis import asyncio as aioredis  # type: ignore
except ImportError:  # pragma: no cover
    aioredis = None  # type: ignore


@dataclass(slots=True)
class LeaderboardEntry:
    participant_id: str
    score: float


class SimulationCache:
    """High-level cache for simulation sessions."""

    def __init__(self, client: Any):
        if aioredis is None:  # pragma: no cover
            raise RuntimeError("redis[asyncio] 未安装，无法初始化仿真缓存。")
        self._client = client

    @classmethod
    async def create(cls, url: str) -> "SimulationCache":
        if aioredis is None:  # pragma: no cover
            raise RuntimeError("redis[asyncio] 未安装，无法初始化仿真缓存。")
        client = aioredis.Redis.from_url(url, decode_responses=True)
        await client.ping()
        return cls(client)

    async def close(self) -> None:
        await self._client.close()

    # ------------------------------------------------------------------
    # Key helpers
    def _key(self, session: str, suffix: str) -> str:
        return f"sim:{session}:{suffix}"

    def _leaderboard_key(self, session: str) -> str:
        return self._key(session, "leaderboard")

    def _player_key(self, session: str, participant: str) -> str:
        return self._key(session, f"player:{participant}")

    def _stream_key(self, session: str) -> str:
        return self._key(session, "stream")

    def _participant_key(self, session: str) -> str:
        return self._key(session, "participants")

    def _coach_queue_key(self) -> str:
        return "sim:coach:queue"

    async def set_status(self, session: str, status: str) -> None:
        await self._client.set(self._key(session, "status"), status)

    async def set_tick(self, session: str, tick: int) -> None:
        await self._client.set(self._key(session, "tick"), tick)

    # ------------------------------------------------------------------
    # Leaderboard
    async def update_leaderboard(self, session: str, participant_id: str, score: float) -> None:
        await self._client.zadd(self._leaderboard_key(session), {participant_id: score})

    async def adjust_leaderboard(self, session: str, participant_id: str, delta: float) -> None:
        await self._client.zincrby(self._leaderboard_key(session), delta, participant_id)

    async def top_leaderboard(self, session: str, limit: int = 10, reverse: bool = True) -> list[LeaderboardEntry]:
        key = self._leaderboard_key(session)
        if reverse:
            raw = await self._client.zrevrange(key, 0, limit - 1, withscores=True)
        else:
            raw = await self._client.zrange(key, 0, limit - 1, withscores=True)
        return [LeaderboardEntry(participant_id=pid, score=score) for pid, score in raw]

    # ------------------------------------------------------------------
    # Player snapshot
    async def set_player_snapshot(
        self,
        session: str,
        participant_id: str,
        *,
        cash: float,
        inventory: float,
        score: float,
        ttl_seconds: int = 30,
        extra: Optional[dict[str, Any]] = None,
    ) -> None:
        key = self._player_key(session, participant_id)
        payload: dict[str, Any] = {
            "cash": cash,
            "inventory": inventory,
            "score": score,
        }
        if extra:
            payload.update(extra)
        await self._client.hset(key, mapping={k: str(v) for k, v in payload.items()})
        await self._client.expire(key, ttl_seconds)

    async def get_player_snapshot(self, session: str, participant_id: str) -> Optional[dict[str, str]]:
        key = self._player_key(session, participant_id)
        data = await self._client.hgetall(key)
        return data or None

    async def publish_pool_stats(
        self,
        session: str,
        stats: dict[str, dict[str, float]],
        ttl_seconds: int = 5,
    ) -> None:
        key = self._key(session, "pool_stats")
        await self._client.set(
            key, json.dumps(stats, ensure_ascii=False), ex=ttl_seconds
        )

    # ------------------------------------------------------------------
    # Participant cache
    async def get_participant_ids(
        self,
        session: str,
        participant_codes: Sequence[str],
    ) -> dict[str, int]:
        if not participant_codes:
            return {}
        key = self._participant_key(session)
        values = await self._client.hmget(key, participant_codes)
        mapping: dict[str, int] = {}
        for code, raw in zip(participant_codes, values):
            if raw is None:
                continue
            try:
                mapping[code] = int(raw)
            except ValueError:
                continue
        return mapping

    async def set_participant_ids(
        self,
        session: str,
        mapping: dict[str, int],
        *,
        ttl_seconds: int = 3600,
    ) -> None:
        if not mapping:
            return
        key = self._participant_key(session)
        await self._client.hset(key, mapping={code: db_id for code, db_id in mapping.items()})
        await self._client.expire(key, ttl_seconds)

    # ------------------------------------------------------------------
    # Event stream
    async def append_event(self, session: str, event: dict[str, Any], *, maxlen: int = 1000) -> str:
        key = self._stream_key(session)
        return await self._client.xadd(key, event, maxlen=maxlen, approximate=True)

    async def read_events(
        self,
        session: str,
        *,
        last_id: str = "0-0",
        count: Optional[int] = None,
        block_ms: Optional[int] = None,
    ) -> list[tuple[str, dict[str, str]]]:
        key = self._stream_key(session)
        kwargs = {}
        if count is not None:
            kwargs["count"] = count
        if block_ms is not None:
            kwargs["block"] = block_ms
        entries = await self._client.xread({key: last_id}, **kwargs)
        if not entries:
            return []
        # XREAD returns [(key, [(id, {field: value})...])]
        _, messages = entries[0]
        return messages

    # ------------------------------------------------------------------
    async def trim_stream(self, session: str, maxlen: int = 1000) -> None:
        await self._client.xtrim(self._stream_key(session), maxlen=maxlen, approximate=True)

    # ------------------------------------------------------------------
    # Coach queue
    async def enqueue_coach_log(self, payload: dict[str, Any], *, maxlen: int = 1000) -> None:
        message = json.dumps(payload, ensure_ascii=False)
        await self._client.lpush(self._coach_queue_key(), message)
        await self._client.ltrim(self._coach_queue_key(), 0, maxlen - 1)

    # ------------------------------------------------------------------
    # User order queue (T025-T026)
    def _user_orders_key(self, session: str) -> str:
        return f"sim:{session}:pending_orders"

    async def push_pending_user_order(self, session: str, order_data: dict[str, Any]) -> None:
        """Queue a user order for processing in the next tick (T025)."""
        message = json.dumps(order_data, ensure_ascii=False)
        await self._client.rpush(self._user_orders_key(session), message)

    async def pop_pending_user_orders(self, session: str, max_count: int = 100) -> list[dict[str, Any]]:
        """Retrieve and remove all pending user orders for a session (T026)."""
        key = self._user_orders_key(session)
        orders = []
        for _ in range(max_count):
            message = await self._client.lpop(key)
            if message is None:
                break
            try:
                order_data = json.loads(message)
                orders.append(order_data)
            except json.JSONDecodeError:
                continue
        return orders

    # ------------------------------------------------------------------
    # Orderbook snapshot cache (T027)
    def _orderbook_snapshot_key(self, session: str) -> str:
        return f"sim:{session}:orderbook"

    async def cache_orderbook_snapshot(
        self, session: str, snapshot: dict[str, Any], ttl_seconds: int = 5
    ) -> None:
        """Cache orderbook depth snapshot with TTL (T027)."""
        key = self._orderbook_snapshot_key(session)
        data = json.dumps(snapshot, ensure_ascii=False)
        await self._client.setex(key, ttl_seconds, data)

    async def get_cached_orderbook(self, session: str) -> dict[str, Any] | None:
        """Retrieve cached orderbook snapshot (T027)."""
        key = self._orderbook_snapshot_key(session)
        data = await self._client.get(key)
        if data is None:
            return None
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return None

