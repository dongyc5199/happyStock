"""Agent pool configuration and runtime state."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

from .agents.base import GeneratedOrder


@dataclass(slots=True)
class AgentPoolConfig:
    code: str
    name: str
    weight: float
    initial_capital: float
    turnover_limit: float  # as fraction of capital per tick
    strategies: List[str]
    description: str = ""


@dataclass(slots=True)
class AgentPoolState:
    capital: float
    turnover_used: float = 0.0


@dataclass(slots=True)
class PoolTickStat:
    gross_buy: float = 0.0
    gross_sell: float = 0.0

    @property
    def net_flow(self) -> float:
        return self.gross_buy - self.gross_sell


class AgentPoolManager:
    """Tracks pool level capital/turnover and per-tick stats."""

    def __init__(self, configs: Iterable[AgentPoolConfig]) -> None:
        self._configs: Dict[str, AgentPoolConfig] = {cfg.code: cfg for cfg in configs}
        self._states: Dict[int, Dict[str, AgentPoolState]] = {}
        self._tick_stats: Dict[int, Dict[str, PoolTickStat]] = {}

    def ensure_session(self, session_id: int) -> None:
        states = self._states.setdefault(session_id, {})
        for cfg in self._configs.values():
            states.setdefault(cfg.code, AgentPoolState(cfg.initial_capital))

    def begin_tick(self, session_id: int) -> None:
        states = self._states.get(session_id)
        if states:
            for state in states.values():
                state.turnover_used = 0.0
        self._tick_stats[session_id] = {
            code: PoolTickStat() for code in self._configs.keys()
        }

    def apply_order_limits(
        self,
        session_id: int,
        orders: List[GeneratedOrder],
        reference_price: float,
    ) -> None:
        states = self._states.get(session_id)
        if not states:
            return
        stats = self._tick_stats.setdefault(
            session_id, {code: PoolTickStat() for code in self._configs.keys()}
        )

        for order in orders:
            pool_code = order.pool_code
            if not pool_code or pool_code not in states:
                continue
            cfg = self._configs.get(pool_code)
            if cfg is None:
                continue
            state = states[pool_code]
            price = order.price or reference_price or 1.0
            price = max(price, 0.01)
            order_value = abs(order.quantity) * price
            limit_value = cfg.initial_capital * max(cfg.turnover_limit, 0.0)
            available = max(limit_value - state.turnover_used, 0.0)
            if available <= 0.0:
                order.quantity = 0.0
                continue
            if order_value > available:
                allowed_qty = available / price
                if allowed_qty <= 0.0:
                    order.quantity = 0.0
                    continue
                order.quantity = allowed_qty * (1 if order.quantity >= 0 else -1)
                order_value = available
            state.turnover_used += order_value
            stat = stats.setdefault(pool_code, PoolTickStat())
            if order.quantity >= 0:
                stat.gross_buy += order_value
            else:
                stat.gross_sell += order_value

    def collect_tick_stats(self, session_id: int) -> Dict[str, PoolTickStat]:
        return self._tick_stats.get(session_id, {})


DEFAULT_AGENT_POOLS: List[AgentPoolConfig] = [
    AgentPoolConfig(
        code="A",
        name="Institutions",
        weight=0.6,
        initial_capital=1_000_000_000.0,
        turnover_limit=0.02,
        strategies=["institutional", "market_maker"],
        description="Long-term funds, slow rotation.",
    ),
    AgentPoolConfig(
        code="B",
        name="Momentum Funds",
        weight=0.25,
        initial_capital=400_000_000.0,
        turnover_limit=0.05,
        strategies=["prop"],
        description="Short-term opportunistic capital.",
    ),
    AgentPoolConfig(
        code="C",
        name="Retail",
        weight=0.15,
        initial_capital=120_000_000.0,
        turnover_limit=0.10,
        strategies=["retail"],
        description="High-frequency small orders following sentiment.",
    ),
]
