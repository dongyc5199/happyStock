"""Agent registry managing multiple strategies per session."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Dict, Iterable, List

from .base import AgentContext, AgentStrategy, GeneratedOrder


@dataclass
class RegisteredAgent:
    strategy: AgentStrategy
    weight: float
    pool_code: str | None = None


class AgentRegistry:
    """Registry holding agent strategies keyed by session."""

    def __init__(self) -> None:
        self._agents: Dict[int, List[RegisteredAgent]] = {}
        self._lock = asyncio.Lock()

    async def register(
        self,
        session_id: int,
        agent: AgentStrategy,
        *,
        weight: float = 1.0,
        pool_code: str | None = None,
    ) -> None:
        async with self._lock:
            bucket = self._agents.setdefault(session_id, [])
            bucket.append(RegisteredAgent(agent, weight, pool_code))

    async def unregister(self, session_id: int, agent_code: str) -> None:
        async with self._lock:
            bucket = self._agents.get(session_id, [])
            self._agents[session_id] = [
                entry for entry in bucket if entry.strategy.code != agent_code
            ]

    async def generate_orders(
        self,
        session_id: int,
        session_code: str,
        tick: int,
        context: AgentContext,
    ) -> List[GeneratedOrder]:
        async with self._lock:
            agents = list(self._agents.get(session_id, []))

        if not agents:
            return []

        orders: List[GeneratedOrder] = []
        for entry in agents:
            generated = await entry.strategy.generate_orders(
                session_id, session_code, tick, context
            )
            for order in generated:
                if order.pool_code is None:
                    order.pool_code = entry.pool_code
            orders.extend(generated)
        return orders

    async def has_agents(self, session_id: int) -> bool:
        async with self._lock:
            return bool(self._agents.get(session_id))
