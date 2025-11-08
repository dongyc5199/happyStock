"""Access layer for simulation feature snapshots."""
from __future__ import annotations

import asyncio
import os
import time
from typing import Any, Dict, Iterable, List, Optional, Tuple


class FeatureService:
    """Provides read access to aggregated feature snapshots with light caching."""

    def __init__(self, pool: Any, cache_ttl: Optional[float] = None) -> None:
        self._pool = pool
        ttl = cache_ttl
        if ttl is None:
            ttl = float(os.getenv("SIM_FEATURE_CACHE_TTL", "2.0"))
        self._cache_ttl = max(ttl, 0.0)
        self._cache: dict[int, Tuple[float, Dict[str, float]]] = {}
        self._refresh_tasks: dict[int, asyncio.Task] = {}

    async def get_latest_features(
        self,
        session_id: int,
        *,
        metrics: Optional[Iterable[str]] = None,
    ) -> Dict[str, float]:
        use_cache = metrics is None and self._cache_ttl > 0
        cached = self._cache.get(session_id)
        now = time.monotonic()
        if use_cache and cached:
            age = now - cached[0]
            if age <= self._cache_ttl:
                return dict(cached[1])
            self._maybe_schedule_refresh(session_id)
            return dict(cached[1])

        data = await self._query_features(session_id, metrics)
        if data:
            if use_cache and metrics is None:
                self._cache[session_id] = (time.monotonic(), data)
            return data

        if cached:
            return dict(cached[1])

        candidates = metrics or ("volatility", "max_drawdown", "avg_volume")
        return {metric: 0.0 for metric in candidates}

    async def get_metric_history(
        self,
        session_id: int,
        metric_name: str,
        *,
        limit: int = 50,
    ) -> List[Dict[str, float]]:
        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            rows = await conn.fetch(
                """
                SELECT tick, metric_value
                  FROM metric_snapshot
                 WHERE session_id = 
                   AND metric_name = 
                 ORDER BY ts DESC
                 LIMIT 
                """,
                session_id,
                metric_name,
                limit,
            )

        return [
            {"tick": int(row["tick"]), "value": float(row["metric_value"])}
            for row in rows
        ]

    def _maybe_schedule_refresh(self, session_id: int) -> None:
        if session_id in self._refresh_tasks:
            return
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return

        async def _refresh() -> None:
            try:
                data = await self._query_features(session_id, None)
                if data:
                    self._cache[session_id] = (time.monotonic(), data)
            finally:
                self._refresh_tasks.pop(session_id, None)

        task = loop.create_task(_refresh())
        self._refresh_tasks[session_id] = task

    async def _query_features(
        self, session_id: int, metrics: Optional[Iterable[str]]
    ) -> Dict[str, float]:
        query = """
            SELECT metric_name, metric_value
              FROM metric_snapshot
             WHERE session_id = 
               AND ts = (
                   SELECT MAX(ts)
                     FROM metric_snapshot
                    WHERE session_id = 
               )
        """
        args: List[Any] = [session_id]

        if metrics:
            metric_list = list(metrics)
            query += " AND metric_name = ANY()"
            args.append(metric_list)

        rows = []
        try:
            async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
                rows = await conn.fetch(query, *args)
        except Exception:
            return {}

        return {row["metric_name"]: float(row["metric_value"]) for row in rows}
