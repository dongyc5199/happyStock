"""Market maker agent strategies."""

from __future__ import annotations

import random
import uuid
from typing import List, Tuple

from .base import AgentContext, AgentStrategy, GeneratedOrder


class MarketMakerAgent(AgentStrategy):
    """Market maker that maintains multiple depth levels on both sides."""

    behavior_category = "market_maker"

    def __init__(
        self,
        code: str = "mm",
        *,
        spread_bps: float = 10.0,
        base_quantity: float = 100.0,
        base_quantity_range: tuple[float, float] | None = None,
        levels: int = 50,
        level_spacing_bps: float = 10.0,
        decay: float = 0.88,
        refresh_interval: int = 3,
        weight: float = 1.0,
        initial_cash: float = 500000000.0,
        initial_inventory: float = 2000000.0,
        # Behavior parameters for differentiation
        profit_target: float | None = None,
        stop_loss: float | None = None,
        herd_behavior_strength: float | None = None,
        momentum_sensitivity: float | None = None,
        risk_tolerance: float | None = None,
    ) -> None:
        super().__init__(
            code=code,
            weight=weight,
            initial_cash=initial_cash,
            initial_inventory=initial_inventory,
        )
        self._spread_bps = spread_bps
        self._base_quantity = base_quantity
        self._base_quantity_range: Tuple[float, float] = (
            base_quantity_range if base_quantity_range is not None else (50.0, 500.0)
        )
        self._levels = max(1, levels)
        self._level_spacing_bps = max(level_spacing_bps, 1.0)
        self._decay = min(max(decay, 0.5), 0.99)
        self._refresh_interval = max(1, refresh_interval)
        self._next_refresh_tick: dict[int, int] = {}

        # Store behavior parameters (market makers are neutral with minimal profit targets)
        self.profit_target = profit_target if profit_target is not None else 0.02  # 2% profit target
        self.stop_loss = stop_loss if stop_loss is not None else 0.01  # 1% stop loss
        self.herd_behavior_strength = herd_behavior_strength if herd_behavior_strength is not None else 0.0  # No herd behavior
        self.momentum_sensitivity = momentum_sensitivity if momentum_sensitivity is not None else 0.1  # Low momentum sensitivity
        self.risk_tolerance = risk_tolerance if risk_tolerance is not None else 0.3  # Moderate risk tolerance

    def _create_order(
        self,
        order_id: str,
        participant_id: str,
        side: str,
        quantity: float,
        price: float | None = None,
    ) -> GeneratedOrder:
        """Helper to create order with behavior parameters."""
        return GeneratedOrder(
            order_id=order_id,
            participant_id=participant_id,
            participant_code=self.code,
            participant_type="agent",
            side=side,
            order_type="MARKET" if price is None else "LIMIT",
            quantity=quantity,
            price=price,
            behavior_category="market_maker",
            profit_target=self.profit_target,
            stop_loss=self.stop_loss,
            herd_behavior_strength=self.herd_behavior_strength,
            momentum_sensitivity=self.momentum_sensitivity,
            risk_tolerance=self.risk_tolerance,
        )

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
        orders: List[GeneratedOrder] = []
        account_state = self._account_state(session_id, context)
        for level in range(1, self._levels + 1):
            offset = base_spread + spacing * (level - 1)
            noise = reference_price * random.uniform(-0.0005, 0.0005)
            bid_price = max(reference_price - offset + noise, 0.01)
            ask_price = reference_price + offset + noise
            raw_qty = random.uniform(
                self._base_quantity_range[0], self._base_quantity_range[1]
            )
            level_qty = raw_qty * (self._decay ** (level - 1)) * self.weight
            level_qty = max(50.0, float(int(level_qty)))

            bid_qty = self._reserve_order_capacity(
                account_state, side="BUY", quantity=level_qty, price=bid_price
            )
            bid_qty = float(round(bid_qty, 2))
            if bid_qty >= 1.0:
                orders.append(
                    self._create_order(
                        order_id=f"{self.code}-bid-{level}-{session_id}-{tick}-{uuid.uuid4().hex[:6]}",
                        participant_id=f"{self.code}-agent",
                        side="BUY",
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
                    self._create_order(
                        order_id=f"{self.code}-ask-{level}-{session_id}-{tick}-{uuid.uuid4().hex[:6]}",
                        participant_id=f"{self.code}-agent",
                        side="SELL",
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


__all__ = ["MarketMakerAgent"]



