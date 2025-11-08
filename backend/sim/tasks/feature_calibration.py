"""Periodic feature calibration task for simulation sessions."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence


def _compute_max_drawdown(prices: Sequence[float]) -> float:
    """Compute max drawdown in percentage terms."""
    if not prices:
        return 0.0
    peak = prices[0]
    max_dd = 0.0
    for price in prices[1:]:
        if price > peak:
            peak = price
        elif peak > 0:
            drawdown = (price - peak) / peak
            if drawdown < max_dd:
                max_dd = drawdown
    return abs(max_dd)


def _compute_volatility(returns: Sequence[float]) -> float:
    """Compute simple volatility (standard deviation of returns)."""
    if not returns:
        return 0.0
    mean = sum(returns) / len(returns)
    variance = sum((r - mean) ** 2 for r in returns) / len(returns)
    return variance ** 0.5


@dataclass(slots=True)
class FeatureRecord:
    metric_name: str
    metric_value: float
    dimension: Dict[str, Any]


class FeatureCalibrationTask:
    """Responsible for refreshing session level features inside TimescaleDB."""

    def __init__(
        self,
        pool: Any,
        *,
        lookback_ticks: int = 120,
        min_points: int = 10,
    ) -> None:
        self._pool = pool
        self._lookback = lookback_ticks
        self._min_points = min_points

    async def run(self) -> None:
        """Entry point for scheduled execution."""
        session_ids = await self._list_active_sessions()
        if not session_ids:
            return

        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            for session_id in session_ids:
                rows = await conn.fetch(
                    """
                    SELECT tick, last_price, total_volume, ts
                      FROM market_state
                     WHERE session_id = $1
                       AND last_price IS NOT NULL
                     ORDER BY ts DESC
                     LIMIT $2
                    """,
                    session_id,
                    self._lookback,
                )

                features = self._build_feature_records(rows)
                if not features:
                    continue

                latest_tick = rows[0]["tick"] if rows else 0
                await self._persist_features(conn, session_id, latest_tick, features)

    async def _list_active_sessions(self) -> List[int]:
        async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
            rows = await conn.fetch(
                """
                SELECT id
                  FROM simulation_session
                 WHERE status NOT IN ('closed', 'archived')
                """
            )
        return [row["id"] for row in rows]

    def _build_feature_records(self, rows: Sequence[Any]) -> List[FeatureRecord]:
        if len(rows) < self._min_points:
            return []

        prices = [float(row["last_price"]) for row in reversed(rows)]
        volumes = [float(row["total_volume"] or 0.0) for row in reversed(rows)]

        returns: List[float] = []
        for prev, curr in zip(prices, prices[1:]):
            if prev > 0:
                returns.append((curr - prev) / prev)

        volatility = _compute_volatility(returns)
        drawdown = _compute_max_drawdown(prices)
        avg_volume = sum(volumes) / len(volumes) if volumes else 0.0

        window_info = {"window": len(prices)}

        return [
            FeatureRecord("volatility", volatility, window_info),
            FeatureRecord("max_drawdown", drawdown, window_info),
            FeatureRecord("avg_volume", avg_volume, window_info),
        ]

    async def _persist_features(
        self,
        conn: Any,
        session_id: int,
        tick: int,
        features: Iterable[FeatureRecord],
    ) -> None:
        ts = datetime.now(timezone.utc)
        values = [
            (
                session_id,
                tick,
                ts,
                record.metric_name,
                float(record.metric_value),
                json.dumps(record.dimension),
            )
            for record in features
        ]

        await conn.executemany(
            """
            INSERT INTO metric_snapshot (session_id, tick, ts, metric_name, metric_value, dimension)
            VALUES ($1, $2, $3, $4, $5, $6::jsonb)
            ON CONFLICT (session_id, tick, ts, metric_name)
            DO UPDATE SET metric_value = EXCLUDED.metric_value,
                          dimension = EXCLUDED.dimension
            """,
            values,
        )
