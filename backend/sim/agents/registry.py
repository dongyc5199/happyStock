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
        self._agent_map: Dict[int, Dict[str, AgentStrategy]] = {}
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
            lookup = self._agent_map.setdefault(session_id, {})
            lookup[agent.code] = agent

    async def unregister(self, session_id: int, agent_code: str) -> None:
        async with self._lock:
            bucket = self._agents.get(session_id, [])
            self._agents[session_id] = [
                entry for entry in bucket if entry.strategy.code != agent_code
            ]
            lookup = self._agent_map.get(session_id)
            if lookup and agent_code in lookup:
                lookup.pop(agent_code, None)

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
            # Create agent-specific context with cash and position
            agent_context = AgentContext(
                feature_provider=context.feature_provider,
                emotion_provider=context.emotion_provider,
                last_price=context.last_price,
                best_bid=context.best_bid,
                best_ask=context.best_ask,
                profile=context.profile,
                agent_cash=entry.strategy.get_cash(session_id),
                agent_position=entry.strategy.get_position(session_id),
            )

            if not entry.strategy.should_generate_orders(session_id, tick):
                continue

            generated = await entry.strategy.generate_orders(
                session_id, session_code, tick, agent_context
            )
            for order in generated:
                if order.pool_code is None:
                    order.pool_code = entry.pool_code
            orders.extend(generated)
        return orders

    async def has_agents(self, session_id: int) -> bool:
        async with self._lock:
            return bool(self._agents.get(session_id))

    async def record_trade(
        self,
        session_id: int,
        agent_code: str,
        side: str,
        quantity: float,
        price: float,
        order_id: str | None = None,
    ) -> None:
        async with self._lock:
            strategy = self._agent_map.get(session_id, {}).get(agent_code)
            if strategy is None:
                return
            strategy.record_fill(session_id, side, quantity, price)
            if order_id:
                try:
                    strategy.on_order_filled(session_id, order_id)
                except AttributeError:
                    pass
            try:
                strategy.on_order_filled(session_id, order_id)
            except AttributeError:
                pass
