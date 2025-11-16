"""Depth quoting agent that maintains multi-level limit orders."""

from __future__ import annotations

import random
import uuid
from typing import Dict, List

from .base import AgentContext, AgentStrategy, GeneratedOrder


class DepthQuoterAgent(AgentStrategy):
    """Provides limit order depth (similar to a pool-specific market maker)."""

    def __init__(
        self,
        code: str,
        *,
        participant_prefix: str,
        spread_bps: float = 10.0,
        base_quantity: float = 20.0,
        levels: int = 50,
        level_spacing_bps: float = 5.0,
        decay: float = 0.9,
        refresh_interval: int = 4,
        initial_cash: float = 5000000.0,
        initial_inventory: float = 200000.0,
    ) -> None:
        super().__init__(
            code=code,
            weight=1.0,
            initial_cash=initial_cash,
            initial_inventory=initial_inventory,
        )
        self._spread_bps = spread_bps
        self._base_quantity = base_quantity
        self._levels = max(1, levels)
        self._level_spacing_bps = max(level_spacing_bps, 1.0)
        self._decay = min(max(decay, 0.4), 0.99)
        self._refresh_interval = max(1, refresh_interval)
        self._participant_prefix = participant_prefix
        self._next_refresh_tick: Dict[int, int] = {}

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

        if not self._should_refresh(session_id, tick):
            return []

        base_spread = max(reference_price * (self._spread_bps / 10000), 0.01)
        spacing = reference_price * (self._level_spacing_bps / 10000)
        quantity = self._base_quantity

        orders: List[GeneratedOrder] = []
        account_state = self._account_state(session_id, context)
        for level in range(1, self._levels + 1):
            offset = base_spread + spacing * (level - 1)
            noise = reference_price * random.uniform(-0.0008, 0.0008)
            bid_price = max(reference_price - offset + noise, 0.01)
            ask_price = reference_price + offset + noise
            level_qty = max(quantity * (self._decay ** (level - 1)), quantity * 0.2)
            level_qty = max(1.0, float(int(level_qty)))

            bid_qty = self._reserve_order_capacity(
                account_state, side="BUY", quantity=level_qty, price=bid_price
            )
            bid_qty = float(round(bid_qty, 2))
            if bid_qty >= 1.0:
                orders.append(
                    GeneratedOrder(
                        order_id=f"{self._participant_prefix}-bid-{level}-{session_id}-{tick}-{uuid.uuid4().hex[:5]}",
                        participant_id=f"{self._participant_prefix}-b{level}",
                        side="BUY",
                        order_type="LIMIT",
                        quantity=bid_qty,
                        price=round(bid_price, 4),
                    )
                )
            ask_qty = self._reserve_order_capacity(
                account_state, side="SELL", quantity=level_qty, price=ask_price
            )
            ask_qty = float(round(ask_qty, 2))
            if ask_qty >= 1.0:
                orders.append(
                    GeneratedOrder(
                        order_id=f"{self._participant_prefix}-ask-{level}-{session_id}-{tick}-{uuid.uuid4().hex[:5]}",
                        participant_id=f"{self._participant_prefix}-a{level}",
                        side="SELL",
                        order_type="LIMIT",
                        quantity=ask_qty,
                        price=round(ask_price, 4),
                    )
                )

        return orders

    def _should_refresh(self, session_id: int, tick: int) -> bool:
        target = self._next_refresh_tick.get(session_id)
        if target is None or tick >= target:
            self._next_refresh_tick[session_id] = tick + self._refresh_interval
            return True
        return False


__all__ = ["DepthQuoterAgent"]
