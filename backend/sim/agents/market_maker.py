"""Market maker agent strategies."""

from __future__ import annotations

import uuid
from typing import List

from .base import AgentContext, AgentStrategy, GeneratedOrder


class MarketMakerAgent(AgentStrategy):
    """Simple market maker quoting around the last traded price."""

    def __init__(
        self,
        code: str = "mm",
        *,
        spread_bps: float = 15.0,
        base_quantity: float = 15.0,
        weight: float = 1.0,
    ) -> None:
        super().__init__(code=code, weight=weight)
        self._spread_bps = spread_bps
        self._base_quantity = base_quantity

    async def generate_orders(
        self,
        session_id: int,
        session_code: str,
        tick: int,
        context: AgentContext,
    ) -> List[GeneratedOrder]:
        reference_price = context.last_price
        if reference_price is None:
            if context.best_bid and context.best_ask:
                reference_price = (context.best_bid + context.best_ask) / 2
            else:
                return []

        spread = max(reference_price * (self._spread_bps / 10000), 0.01)
        bid_price = max(reference_price - spread, 0.01)
        ask_price = reference_price + spread
        quantity = round(self._base_quantity * self.weight, 4)

        bid_order = GeneratedOrder(
            order_id=f"{self.code}-bid-{session_id}-{tick}-{uuid.uuid4().hex[:8]}",
            participant_id=f"{self.code}-agent",
            side="BUY",
            order_type="LIMIT",
            quantity=quantity,
            price=round(bid_price, 4),
        )
        ask_order = GeneratedOrder(
            order_id=f"{self.code}-ask-{session_id}-{tick}-{uuid.uuid4().hex[:8]}",
            participant_id=f"{self.code}-agent",
            side="SELL",
            order_type="LIMIT",
            quantity=quantity,
            price=round(ask_price, 4),
        )
        return [bid_order, ask_order]


__all__ = ["MarketMakerAgent"]
