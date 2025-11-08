"""Retail agent strategies."""

from __future__ import annotations

import uuid
from typing import List

from .base import AgentContext, AgentStrategy, GeneratedOrder


class RetailSentimentAgent(AgentStrategy):
    """Sentiment-driven retail participant."""

    def __init__(
        self,
        code: str = "retail",
        *,
        threshold: float = 0.05,
        base_quantity: float = 5.0,
        weight: float = 1.0,
    ) -> None:
        super().__init__(code=code, weight=weight)
        self._threshold = threshold
        self._base_quantity = base_quantity

    async def generate_orders(
        self,
        session_id: int,
        session_code: str,
        tick: int,
        context: AgentContext,
    ) -> List[GeneratedOrder]:
        sentiment = await context.fetch_sentiment(session_code)
        if sentiment is None:
            return []

        if sentiment > self._threshold:
            side = "BUY"
        elif sentiment < -self._threshold:
            side = "SELL"
        else:
            return []

        quantity = max(
            self._base_quantity * self.weight * abs(sentiment) * 10,
            self._base_quantity * 0.5,
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


__all__ = ["RetailSentimentAgent"]
