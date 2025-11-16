"""Institutional agent strategies."""

from __future__ import annotations

import random
import uuid
from typing import Dict, List

from .base import AgentContext, AgentStrategy, GeneratedOrder


class InstitutionalRebalanceAgent(AgentStrategy):
    """
    Rebalances when drawdown deviates from target and fires occasional block trades.

    T060: Enhanced with configurable behavior parameters for differentiation.
    """

    behavior_category = "institutional"

    def __init__(
        self,
        code: str = "institutional",
        *,
        drawdown_target: float = 0.02,  # ADJUSTED: 0.04 -> 0.02 for earlier rebalancing
        base_quantity: float = 50.0,
        block_interval_ticks: tuple[int, int] = (1200, 2400),
        block_multiplier: float = 6.0,
        weight: float = 1.0,
        # T060: Behavior parameters for differentiation
        profit_target: float | None = None,
        stop_loss: float | None = None,
        herd_behavior_strength: float | None = None,
        momentum_sensitivity: float | None = None,
        risk_tolerance: float | None = None,
        # T068-T070: Mean reversion and order splitting parameters
        mean_reversion_window: int = 100,
        rebalance_threshold: float = 0.02,
        max_order_size: float | None = None,
        split_orders: bool = True,
        initial_cash: float = 300000.0,  # Default 300k for institutional
        decision_latency_range: tuple[int, int] | None = (10, 20),
        value_entry_threshold: float = 0.20,
        value_exit_threshold: float = 0.20,
        cooldown_ticks: tuple[int, int] | None = None,
        limit_offset_bps: tuple[float, float] = (0.15, 0.4),
    ) -> None:
        super().__init__(
            code=code,
            weight=weight,
            initial_cash=initial_cash,
            decision_latency_range=decision_latency_range,
        )
        self._drawdown_target = drawdown_target
        self._base_quantity = base_quantity
        self._block_interval = block_interval_ticks
        self._block_multiplier = block_multiplier
        self._next_block_tick: Dict[int, int] = {}

        # T060: Store behavior parameters
        self.profit_target = profit_target if profit_target is not None else 0.15
        self.stop_loss = stop_loss if stop_loss is not None else 0.08  # 8% stop loss
        self.herd_behavior_strength = herd_behavior_strength if herd_behavior_strength is not None else 0.2
        self.momentum_sensitivity = momentum_sensitivity if momentum_sensitivity is not None else 0.3
        self.risk_tolerance = risk_tolerance if risk_tolerance is not None else 0.4

        # T068-T070: Mean reversion and order splitting
        self._mean_reversion_window = mean_reversion_window
        self._rebalance_threshold = rebalance_threshold
        self._max_order_size = max_order_size if max_order_size is not None else base_quantity * 2.0
        self._split_orders = split_orders
        self._price_history: Dict[int, List[float]] = {}  # Track price history for mean reversion
        self._value_entry_threshold = max(0.0, value_entry_threshold)
        self._value_exit_threshold = max(0.0, value_exit_threshold)
        self._cooldown_ticks = cooldown_ticks or (600, 1500)
        self._next_active_tick: Dict[int, int] = {}
        self._limit_offset_bps = limit_offset_bps

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
            behavior_category="institutional",
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
        # T071: Track price history for mean reversion
        last_price = context.last_price
        if last_price is not None:
            if session_id not in self._price_history:
                self._price_history[session_id] = []
            self._price_history[session_id].append(last_price)
            # Keep only recent window
            if len(self._price_history[session_id]) > self._mean_reversion_window:
                self._price_history[session_id].pop(0)

        profile = context.profile or {}
        if self._should_idle(session_id, tick, profile):
            return []

        features = await context.fetch_features(session_id, metrics=["max_drawdown"])
        drawdown = float(features.get("max_drawdown", 0.0))
        sentiment = await context.fetch_sentiment(session_code) or 0.0
        market_cap = profile.get("market_cap", "mid")

        preference = 1.0
        if market_cap == "large":
            preference = 1.3
        elif market_cap == "small":
            preference = 0.7

        # T060: Apply risk_tolerance to quantity sizing
        # Higher risk tolerance = larger positions
        risk_factor = 0.5 + (self.risk_tolerance * 1.0)  # Range: 0.5 to 1.5

        quantity = (
            self._base_quantity
            * self.weight
            * max(drawdown / max(self._drawdown_target, 1e-6), 1.0)
            * preference
            * risk_factor  # T060: Risk tolerance affects position size
        )
        account_state = self._account_state(session_id, context)
        initial_price = None
        try:
            initial_price = float(profile.get("initial_price"))
        except (TypeError, ValueError):
            initial_price = None

        value_orders: List[GeneratedOrder] = []
        entry_deviation: float | None = None
        if initial_price and last_price:
            entry_deviation = (last_price - initial_price) / initial_price
            if entry_deviation >= self._value_exit_threshold:
                if self._can_sell(entry_deviation):
                    value_orders.extend(
                        self._schedule_value_orders(
                            session_id=session_id,
                            tick=tick,
                            side="SELL",
                            quantity=quantity,
                            account_state=account_state,
                            context=context,
                        )
                    )
            elif entry_deviation <= -self._value_entry_threshold:
                value_orders.extend(
                    self._schedule_value_orders(
                        session_id=session_id,
                        tick=tick,
                        side="BUY",
                        quantity=quantity,
                        account_state=account_state,
                        context=context,
                    )
                )

        if value_orders and entry_deviation is not None:
            if abs(entry_deviation) >= self._value_exit_threshold + 0.03:
                panic_side = (
                    "BUY" if entry_deviation <= -self._value_entry_threshold else "SELL"
                )
                panic_qty = min(sum(order.quantity for order in value_orders), quantity * 0.5)
                panic_qty = self._reserve_order_capacity(
                    account_state,
                    side=panic_side,
                    quantity=panic_qty,
                    price=self.resolve_reference_price(context, panic_side, last_price),
                )
                if panic_qty >= 1.0 and (
                    panic_side != "SELL" or self._can_sell(entry_deviation)
                ):
                    value_orders.insert(
                        0,
                        self._create_order(
                            order_id=f"{self.code}-panic-{session_id}-{tick}-{uuid.uuid4().hex[:6]}",
                            participant_id=f"{self.code}-panic",
                            side=panic_side,
                            quantity=float(round(panic_qty, 2)),
                            price=None,
                        ),
                    )
            self._next_active_tick[session_id] = tick + random.randint(
                *self._cooldown_ticks
            )
            return value_orders

        def _allow(side: str, qty: float) -> float:
            ref_price = self.resolve_reference_price(context, side, last_price)
            allowed = self._reserve_order_capacity(
                account_state, side=side, quantity=qty, price=ref_price
            )
            return float(round(allowed, 2))

        orders: List[GeneratedOrder] = []

        # T071: Mean reversion trigger check
        mean_reversion_signal = False
        if (
            last_price is not None
            and session_id in self._price_history
            and len(self._price_history[session_id]) >= 10
        ):
            history = self._price_history[session_id]
            mean_price = sum(history) / len(history)
            deviation = (last_price - mean_price) / mean_price

            # Trigger mean reversion if price deviates significantly
            if abs(deviation) >= self._rebalance_threshold:
                # Buy when price is below mean (expect reversion up)
                # Sell when price is above mean (expect reversion down)
                side = "BUY" if deviation < 0 else "SELL"
                side = self._enforce_swing_bias(side, entry_deviation)
                mean_reversion_signal = True

                # T072: TWAP - Split large orders
                if self._split_orders and quantity > self._max_order_size:
                    # Split into multiple chunks
                    num_chunks = int(quantity / self._max_order_size) + 1
                    chunk_size = quantity / num_chunks

                    for i in range(num_chunks):
                        chunk_qty = max(1.0, float(int(chunk_size)))
                        chunk_qty = _allow(side, chunk_qty)
                        if chunk_qty < 1.0:
                            continue
                        orders.append(
                            self._create_order(
                                order_id=f"{self.code}-twap-{i}-{session_id}-{tick}-{uuid.uuid4().hex[:6]}",
                                participant_id=f"{self.code}-agent",
                                side=side,
                                quantity=chunk_qty,
                                price=None,
                            )
                        )
                else:
                    # Single order within size limit
                    single_qty = max(1.0, float(int(quantity)))
                    single_qty = _allow(side, single_qty)
                    if single_qty >= 1.0:
                        orders.append(
                            self._create_order(
                                order_id=f"{self.code}-reversion-{session_id}-{tick}-{uuid.uuid4().hex[:8]}",
                                participant_id=f"{self.code}-agent",
                                side=side,
                                quantity=single_qty,
                                price=None,
                            )
                        )

        # Use drawdown_target as the trigger threshold (if not triggered by mean reversion)
        # This is the primary threshold for when to start rebalancing
        if not mean_reversion_signal and drawdown >= self._drawdown_target:
            # T060: Apply herd_behavior_strength to sentiment weighting
            # Low herd = more contrarian, high herd = follow sentiment
            sentiment_weight = self.herd_behavior_strength
            contrarian_weight = 1.0 - self.herd_behavior_strength

            # Contrarians buy when sentiment is negative
            decision_score = (sentiment * sentiment_weight) - (sentiment * contrarian_weight * 0.5)

            side = "BUY" if decision_score >= -0.1 else "SELL"
            side = self._enforce_swing_bias(side, entry_deviation)
            draw_qty = max(1.0, float(int(quantity)))
            draw_qty = _allow(side, draw_qty)
            if draw_qty >= 1.0:
                orders.append(
                    self._create_order(
                        order_id=f"{self.code}-{session_id}-{tick}-{uuid.uuid4().hex[:8]}",
                        participant_id=f"{self.code}-agent",
                        side=side,
                        quantity=draw_qty,
                        price=None,
                    )
                )

        if self._should_fire_block(session_id, tick):
            # T060: Block trade direction influenced by herd behavior
            sentiment_noise = random.uniform(-0.2, 0.2) * (1.0 - self.herd_behavior_strength)
            block_side = "BUY" if sentiment + sentiment_noise >= 0 else "SELL"
            block_side = self._enforce_swing_bias(block_side, entry_deviation)

            block_qty = quantity * self._block_multiplier * random.uniform(0.7, 1.4)
            block_qty = max(1.0, float(int(max(block_qty, self._base_quantity * 2))))
            block_qty = _allow(block_side, block_qty)
            if block_qty >= 1.0:
                orders.append(
                    self._create_order(
                        order_id=f"{self.code}-block-{session_id}-{tick}-{uuid.uuid4().hex[:6]}",
                        participant_id=f"{self.code}-block",
                        side=block_side,
                        quantity=block_qty,
                        price=None,
                    )
                )

        return orders

    def _should_fire_block(self, session_id: int, tick: int) -> bool:
        target = self._next_block_tick.get(session_id)
        if target is None:
            self._next_block_tick[session_id] = tick + random.randint(
                *self._block_interval
            )
            return False
        if tick >= target:
            self._next_block_tick[session_id] = tick + random.randint(
                *self._block_interval
            )
            return True
        return False

    def _should_idle(
        self, session_id: int, tick: int, profile: dict[str, float]
    ) -> bool:
        next_tick = self._next_active_tick.get(session_id)
        if next_tick is None or tick >= next_tick:
            return False
        return True

    def _can_sell(self, entry_deviation: float | None) -> bool:
        if entry_deviation is None:
            return True
        return entry_deviation >= self._value_exit_threshold

    def _enforce_swing_bias(
        self, side: str, entry_deviation: float | None
    ) -> str:
        side_upper = side.upper()
        if side_upper == "SELL" and not self._can_sell(entry_deviation):
            return "BUY"
        return side_upper

    def _schedule_value_orders(
        self,
        *,
        session_id: int,
        tick: int,
        side: str,
        quantity: float,
        account_state: dict[str, float],
        context: AgentContext,
    ) -> List[GeneratedOrder]:
        reference_price = context.last_price or self.resolve_reference_price(
            context, side, context.last_price
        )
        batches = max(3, int(quantity / max(self._base_quantity, 1.0)))
        batch_size = max(1.0, quantity / batches)
        orders: List[GeneratedOrder] = []
        min_offset, max_offset = self._limit_offset_bps
        for _ in range(batches):
            offset_bps = random.uniform(min_offset, max_offset) / 100.0
            limit_price = reference_price
            if limit_price is None or limit_price <= 0:
                limit_price = 1.0
            if side == "BUY":
                limit_price = max(0.01, limit_price * (1 - offset_bps))
            else:
                limit_price = limit_price * (1 + offset_bps)
            allowed_qty = self._reserve_order_capacity(
                account_state, side=side, quantity=batch_size, price=limit_price
            )
            allowed_qty = float(round(allowed_qty, 2))
            if allowed_qty < 1.0:
                break
            orders.append(
                self._create_order(
                    order_id=f"{self.code}-value-{session_id}-{tick}-{uuid.uuid4().hex[:6]}",
                    participant_id=f"{self.code}-value",
                    side=side,
                    quantity=allowed_qty,
                    price=limit_price,
                )
            )
        return orders


__all__ = ["InstitutionalRebalanceAgent"]
