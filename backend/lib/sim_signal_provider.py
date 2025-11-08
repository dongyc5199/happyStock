"""Reads simulation-driven signals from Redis for price generator."""

from __future__ import annotations

import json
from typing import Optional

from redis import Redis


class SimulationSignalProvider:
    def __init__(self, redis_url: str, session_code: str) -> None:
        self._redis = Redis.from_url(redis_url, decode_responses=True)
        self._session_code = session_code

    def get_market_bias(self) -> float:
        """Return normalized net flow (-1..1) aggregated across pools."""
        try:
            raw = self._redis.get(f"sim:{self._session_code}:pool_stats")
        except Exception:
            return 0.0
        if not raw:
            return 0.0
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return 0.0

        net = 0.0
        total = 0.0
        for data in payload.values():
            flow = float(data.get("net_flow", 0.0))
            net += flow
            total += abs(flow)
        if total <= 0.0:
            return 0.0
        bias = net / total
        return max(min(bias, 1.0), -1.0)

    def close(self) -> None:
        try:
            self._redis.close()
        except Exception:
            pass
