"""Prop (momentum) agent strategies."""

from __future__ import annotations

import uuid
from typing import List

from .base import AgentContext, AgentStrategy, GeneratedOrder


class PropMomentumAgent(AgentStrategy):
    """Momentum-driven prop trader reacting to volatility surges."""

    def __init__(
        self,
        code: str = "prop",
        *,
        volatility_trigger: float = 0.02,
        base_quantity: float = 20.0,
        weight: float = 1.0,
    ) -> None:
        super().__init__(code=code, weight=weight)
        self._volatility_trigger = volatility_trigger
        self._base_quantity = base_quantity

    async def generate_orders(
        self,
        session_id: int,
        session_code: str,
        tick: int,
        context: AgentContext,
    ) -> List[GeneratedOrder]:
        features = await context.fetch_features(
            session_id, metrics=["volatility", "avg_volume"]
        )
        volatility = float(features.get("volatility", 0.0))
        avg_volume = float(features.get("avg_volume", 0.0))

        if volatility < self._volatility_trigger:
            return []

        sentiment = await context.fetch_sentiment(session_code)
        side = "BUY" if (sentiment or 0.0) >= 0 else "SELL"

        quantity = (
            self._base_quantity
            * self.weight
            * max(volatility / self._volatility_trigger, 1.0)
        )
        if avg_volume > 0:
            quantity = min(quantity, max(avg_volume * 0.05, self._base_quantity))

        order = GeneratedOrder(
            order_id=f"{self.code}-{session_id}-{tick}-{uuid.uuid4().hex[:8]}",
            participant_id=f"{self.code}-agent",
            side=side,
            order_type="MARKET",
            quantity=round(max(quantity, self._base_quantity * 0.5), 4),
            price=None,
        )
        return [order]


__all__ = ["PropMomentumAgent"]
