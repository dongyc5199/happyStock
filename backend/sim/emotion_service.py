"""Emotion/Sentiment management for simulation sessions."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

try:
    from redis import asyncio as aioredis  # type: ignore
except ImportError:  # pragma: no cover
    aioredis = None  # type: ignore


class EmotionService:
    """Stores and retrieves session level sentiment values."""

    def __init__(self, client: Any, *, pool: Optional[Any] = None) -> None:
        if aioredis is None:  # pragma: no cover
            raise RuntimeError("redis[asyncio] not installed; cannot create EmotionService.")
        self._client = client
        self._pool = pool

    @classmethod
    async def create(cls, url: str, *, pool: Optional[Any] = None) -> "EmotionService":
        if aioredis is None:  # pragma: no cover
            raise RuntimeError("redis[asyncio] not installed; cannot create EmotionService.")
        client = aioredis.Redis.from_url(url, decode_responses=True)
        await client.ping()
        return cls(client, pool=pool)

    async def close(self) -> None:
        await self._client.close()

    def _sentiment_key(self, session: str) -> str:
        return f"sim:{session}:sentiment"

    def _stream_key(self, session: str) -> str:
        return f"sim:{session}:sentiment_stream"

    async def set_sentiment(self, session: str, value: float, *, ttl_seconds: int = 120) -> None:
        await self._client.set(self._sentiment_key(session), value, ex=ttl_seconds)
        if self._pool is not None:
            await self._persist_sentiment_metric(session, value)

    async def get_sentiment(self, session: str) -> Optional[float]:
        value = await self._client.get(self._sentiment_key(session))
        return float(value) if value is not None else None

    async def append_event(self, session: str, payload: dict[str, str], *, maxlen: int = 500) -> str:
        return await self._client.xadd(
            self._stream_key(session),
            payload,
            maxlen=maxlen,
            approximate=True,
        )

    async def read_events(
        self,
        session: str,
        *,
        last_id: str = "0-0",
        count: Optional[int] = None,
    ) -> list[tuple[str, dict[str, str]]]:
        kwargs = {}
        if count is not None:
            kwargs["count"] = count
        entries = await self._client.xread({self._stream_key(session): last_id}, **kwargs)
        if not entries:
            return []
        _, messages = entries[0]
        return messages

    async def _persist_sentiment_metric(self, session: str, value: float) -> None:
        if self._pool is None:
            return

        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            session_row = await conn.fetchrow(
                "SELECT id FROM simulation_session WHERE session_code = $1",
                session,
            )
            if session_row is None:
                return
            session_id = session_row["id"]
            tick_row = await conn.fetchrow(
                """
                SELECT tick
                  FROM market_state
                 WHERE session_id = $1
                 ORDER BY ts DESC
                 LIMIT 1
                """,
                session_id,
            )
            tick = tick_row["tick"] if tick_row else 0
            ts = datetime.now(timezone.utc)
            await conn.execute(
                """
                INSERT INTO metric_snapshot (session_id, tick, ts, metric_name, metric_value, dimension)
                VALUES ($1, $2, $3, 'sentiment', $4, '{"source": "emotion_service"}'::jsonb)
                ON CONFLICT (session_id, tick, ts, metric_name)
                DO UPDATE SET metric_value = EXCLUDED.metric_value
                """,
                session_id,
                tick,
                ts,
                value,
            )
