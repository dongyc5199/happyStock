"""Institutional agent strategies."""

from __future__ import annotations

import uuid
from typing import List

from .base import AgentContext, AgentStrategy, GeneratedOrder


class InstitutionalRebalanceAgent(AgentStrategy):
    """Rebalances when drawdown deviates from target."""

    def __init__(
        self,
        code: str = "institutional",
        *,
        drawdown_target: float = 0.04,
        base_quantity: float = 50.0,
        weight: float = 1.0,
    ) -> None:
        super().__init__(code=code, weight=weight)
        self._drawdown_target = drawdown_target
        self._base_quantity = base_quantity

    async def generate_orders(
        self,
        session_id: int,
        session_code: str,
        tick: int,
        context: AgentContext,
    ) -> List[GeneratedOrder]:
        features = await context.fetch_features(session_id, metrics=["max_drawdown"])
        drawdown = float(features.get("max_drawdown", 0.0))
        sentiment = await context.fetch_sentiment(session_code) or 0.0

        if drawdown < self._drawdown_target * 0.5:
            return []

        side = "BUY" if sentiment >= -0.1 else "SELL"
        quantity = (
            self._base_quantity
            * self.weight
            * max(drawdown / self._drawdown_target, 1.0)
        )

        order = GeneratedOrder(
            order_id=f"{self.code}-{session_id}-{tick}-{uuid.uuid4().hex[:8]}",
            participant_id=f"{self.code}-agent",
            side=side,
            order_type="MARKET",
            quantity=round(quantity, 4),
            price=None,
        )
        return [order]


__all__ = ["InstitutionalRebalanceAgent"]
