"""Prop (momentum) agent strategies."""

from __future__ import annotations

import logging
import random
import uuid
from typing import Any, Dict, List

from .base import AgentContext, AgentStrategy, GeneratedOrder

# Use uvicorn logger so INFO-level simulation traces surface in console output
logger = logging.getLogger("uvicorn.error")


class PropMomentumAgent(AgentStrategy):
    """
    Momentum-driven prop trader reacting to volatility surges.

    T061: Enhanced with configurable behavior parameters for differentiation.
    """

    behavior_category = "prop"

    def __init__(
        self,
        code: str = "prop",
        *,
        volatility_trigger: float = 0.02,
        base_quantity: float = 120.0,
        trend_sensitivity: float = 0.6,
        noise: float = 0.15,
        burst_interval_ticks: tuple[int, int] = (60, 160),
        burst_multiplier: float = 3.5,
        weight: float = 1.0,
        # T061: Behavior parameters for differentiation
        profit_target: float | None = None,
        stop_loss: float | None = None,
        herd_behavior_strength: float | None = None,
        momentum_sensitivity: float | None = None,
        risk_tolerance: float | None = None,
        initial_cash: float = 100000.0,  # Default 100k for prop traders
        # Prop traders now react within ~1s (assuming 500ms ticks -> 2 ticks)
        decision_latency_range: tuple[int, int] | None = (2, 2),
        mean_reversion_strength: float | None = None,
        cooldown_range: tuple[int, int] | None = None,
        burst_duration_range: tuple[int, int] | None = None,
        observe_window_range: tuple[int, int] | None = None,
        strict_cooldown_range: tuple[int, int] | None = None,
        heat_threshold: float = 1.2,
    ) -> None:
        super().__init__(
            code=code,
            weight=weight,
            initial_cash=initial_cash,
            decision_latency_range=decision_latency_range,
        )
        self._volatility_trigger = volatility_trigger
        self._base_quantity = base_quantity
        self._trend_sensitivity = trend_sensitivity
        self._noise = noise
        self._prev_price: float | None = None
        self._burst_interval = burst_interval_ticks
        self._burst_multiplier = burst_multiplier
        self._next_burst_tick: Dict[int, int] = {}

        # T061: Store behavior parameters
        self.profit_target = profit_target if profit_target is not None else 0.03  # T063: 3% profit target
        self.stop_loss = stop_loss if stop_loss is not None else 0.015  # T064: 1.5% stop loss
        self.herd_behavior_strength = herd_behavior_strength if herd_behavior_strength is not None else 0.4
        self.momentum_sensitivity = momentum_sensitivity if momentum_sensitivity is not None else 0.85
        self.risk_tolerance = risk_tolerance if risk_tolerance is not None else 0.75
        self.mean_reversion_strength = (
            mean_reversion_strength if mean_reversion_strength is not None else 0.5
        )
        self._cooldown_range = cooldown_range or (360, 600)
        self._next_active_tick: Dict[int, int] = {}
        self._burst_duration_range = burst_duration_range or (10, 20)
        self._observe_window_range = observe_window_range or (120, 300)
        self._strict_cooldown_range = strict_cooldown_range or (600, 1800)
        self._strict_block_until: Dict[int, int] = {}
        self._heat_threshold = heat_threshold
        self._phase_state: Dict[int, Dict[str, Any]] = {}
        self._jolt_heat_threshold = 1.8
        self._build_duration_ticks = (60, 90)
        self._build_move_range = (0.005, 0.01)
        self._heat_deferrals: Dict[int, int] = {}
        self._low_heat_patience = 3
        self._low_heat_forced_ratio = 0.85
        self._last_active_tick: Dict[int, int] = {}
        self._max_idle_without_heat = 180

        # T065: Position tracking - tracks entry price by session
        # Format: {session_id: {"entry_price": float, "quantity": float, "side": str}}
        self._positions: Dict[int, Dict[str, float | str]] = {}

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
            behavior_category="prop",
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
        profile = context.profile or {}
        if self._should_idle(session_id, tick, profile):
            if context.last_price is not None:
                self._prev_price = context.last_price
            return []

        # T066-T067: Check for profit target or stop loss trigger first
        position = self._positions.get(session_id)
        last_price = context.last_price
        if self._in_observation_window(session_id, tick):
            if last_price is not None:
                self._prev_price = last_price
            return []

        if position and last_price is not None:
            entry_price = float(position["entry_price"])
            position_side = str(position["side"])
            planned_qty = float(position["quantity"])
            actual_qty = self.get_position(session_id)
            position_qty = min(planned_qty, actual_qty)
            if position_qty <= 0:
                del self._positions[session_id]
            else:
                # Calculate P&L percentage
                if position_side == "BUY":
                    pnl_pct = (last_price - entry_price) / entry_price
                else:  # SELL position
                    pnl_pct = (entry_price - last_price) / entry_price

                # T066: Profit target trigger - close position if profit target reached
                if pnl_pct >= self.profit_target:
                    close_side = "SELL" if position_side == "BUY" else "BUY"
                    qty = self._reserve_order_capacity(
                        self._account_state(session_id, context),
                        side=close_side,
                        quantity=position_qty,
                        price=self.resolve_reference_price(
                            context, close_side, last_price
                        ),
                    )
                    qty = float(round(qty, 2))
                    if qty >= 1.0:
                        profit_order = self._create_order(
                            order_id=f"{self.code}-profit-{session_id}-{tick}-{uuid.uuid4().hex[:8]}",
                            participant_id=f"{self.code}-agent",
                            side=close_side,
                            quantity=qty,
                        )
                        del self._positions[session_id]
                        return [profit_order]

                # T067: Stop loss trigger - close position if stop loss hit
                if pnl_pct <= -self.stop_loss:
                    close_side = "SELL" if position_side == "BUY" else "BUY"
                    qty = self._reserve_order_capacity(
                        self._account_state(session_id, context),
                        side=close_side,
                        quantity=position_qty,
                        price=self.resolve_reference_price(
                            context, close_side, last_price
                        ),
                    )
                    qty = float(round(qty, 2))
                    if qty >= 1.0:
                        stoploss_order = self._create_order(
                            order_id=f"{self.code}-stoploss-{session_id}-{tick}-{uuid.uuid4().hex[:8]}",
                            participant_id=f"{self.code}-agent",
                            side=close_side,
                            quantity=qty,
                        )
                        del self._positions[session_id]
                        return [stoploss_order]

        features = await context.fetch_features(
            session_id, metrics=["volatility", "avg_volume"]
        )
        volatility = float(features.get("volatility", 0.0))
        avg_volume = float(features.get("avg_volume", 0.0))

        trend = 0.0
        if (
            self._prev_price is not None
            and last_price is not None
            and self._prev_price > 0
        ):
            trend = (last_price - self._prev_price) / self._prev_price
        if last_price is not None:
            self._prev_price = last_price

        sentiment = await context.fetch_sentiment(session_code) or 0.0
        profile = context.profile or {}
        market_cap = profile.get("market_cap", "mid")
        initial_price = None
        try:
            initial_price = float(profile.get("initial_price"))
        except (TypeError, ValueError):
            initial_price = None
        trigger = self._volatility_trigger
        preference = 1.0
        if market_cap == "small":
            trigger *= 0.6
            preference = 2.0
        elif market_cap == "large":
            trigger *= 1.35
            preference = 0.6

        # T061: Apply momentum_sensitivity to trend weighting
        # Higher momentum sensitivity = follow trends more aggressively
        trend_weight = self._trend_sensitivity * self.momentum_sensitivity
        sentiment_weight = 0.35 * (1.0 + self.herd_behavior_strength * 0.5)  # Herd increases sentiment weight

        reversion_bias = 0.0
        if (
            initial_price
            and initial_price > 0
            and last_price is not None
            and self.mean_reversion_strength > 0
        ):
            deviation = (last_price - initial_price) / initial_price
            reversion_bias = -deviation * self.mean_reversion_strength

        direction_score = (
            sentiment * sentiment_weight + trend * trend_weight + reversion_bias
        )
        direction_score += random.uniform(-self._noise, self._noise)

        phase = self._phase_state.get(session_id)
        burst_active = (
            phase is not None
            and phase.get("state") == "burst"
            and tick < phase.get("until", tick)
        )
        if not burst_active:
            if abs(direction_score) < 0.08:
                self._phase_state[session_id] = {
                    "state": "observe",
                    "until": tick + random.randint(*self._observe_window_range),
                }
                if last_price is not None:
                    self._prev_price = last_price
                return []
            self._phase_state[session_id] = {
                "state": "burst",
                "until": tick + random.randint(*self._burst_duration_range),
            }

        if volatility < trigger and abs(direction_score) < 0.05:
            return []

        side = "BUY" if direction_score >= 0 else "SELL"

        inventory_state = self._account_state(session_id, context)
        reference_price = self.resolve_reference_price(context, side, last_price)

        # T061: Apply risk_tolerance to position sizing
        # Higher risk tolerance = larger positions
        risk_factor = 0.7 + (self.risk_tolerance * 0.8)  # Range: 0.7 to 1.5

        return self._build_orders_for_phase(
            session_id=session_id,
            session_code=session_code,
            tick=tick,
            context=context,
            side=side,
            direction_score=direction_score,
            volatility=volatility,
            volatility_trigger=trigger,
            avg_volume=avg_volume,
            reference_price=reference_price,
            inventory_state=inventory_state,
            burst_active=burst_active,
        )

    def _should_burst(
        self, session_id: int, tick: int, market_cap: str = "mid"
    ) -> bool:
        target = self._next_burst_tick.get(session_id)
        interval = self._burst_interval
        if market_cap == "small":
            interval = (max(20, interval[0] // 3), max(30, interval[1] // 3))
        elif market_cap == "large":
            interval = (interval[0] * 2, interval[1] * 2)

        if target is None:
            self._next_burst_tick[session_id] = tick + random.randint(*interval)
            return False
        if tick >= target:
            self._next_burst_tick[session_id] = tick + random.randint(*interval)
            return True
        return False

    def _in_observation_window(self, session_id: int, tick: int) -> bool:
        phase = self._phase_state.get(session_id)
        if not phase:
            return False
        state = phase.get("state")
        until = phase.get("until", tick)
        if state == "burst":
            if tick >= until:
                self._phase_state[session_id] = {
                    "state": "observe",
                    "until": tick + random.randint(*self._observe_window_range),
                }
                self._strict_block_until[
                    session_id
                ] = tick + random.randint(*self._strict_cooldown_range)
                return True
            return False
        if state == "observe":
            if tick >= until:
                self._phase_state.pop(session_id, None)
                return False
            return True
        return False

    def _build_orders_for_phase(
        self,
        *,
        session_id: int,
        session_code: str,
        tick: int,
        context: AgentContext,
        side: str,
        direction_score: float,
        volatility: float,
        volatility_trigger: float,
        avg_volume: float,
        reference_price: float | None,
        inventory_state: dict[str, float],
        burst_active: bool,
    ) -> List[GeneratedOrder]:
        profile = context.profile or {}
        heat = float(profile.get("retail_heat", 1.0))
        heat_multiplier = min(3.0, max(1.0, heat))
        quantity = self._base_quantity * self.weight * heat_multiplier
        volatility_factor = max((volatility / max(volatility_trigger, 1e-6)) ** 0.8, 0.4)
        direction_factor = 1 + min(abs(direction_score) * 5.0, 3.0)
        random_factor = random.uniform(0.8, 1.35)
        quantity *= volatility_factor * direction_factor * random_factor

        if avg_volume > 0:
            quantity = min(quantity, max(avg_volume * 0.15, self._base_quantity))

        if not burst_active and not self._in_observation_window(session_id, tick):
            self._ensure_build_phase(session_id, tick)
        if self._is_build_phase(session_id, tick):
            build_phase = self._get_build_phase(session_id)
            min_move_pct = None
            if build_phase is not None:
                prev_direction = build_phase.get("direction")
                if prev_direction not in {"BUY", "SELL"}:
                    build_phase["direction"] = side
                elif prev_direction != side:
                    build_phase["direction"] = side
                    # reset progress if direction flips mid build
                    build_phase["progress_move_pct"] = 0.0

                target_pct = float(build_phase.get("target_move_pct") or 0.0)
                progress_pct = float(build_phase.get("progress_move_pct") or 0.0)
                remaining_pct = max(target_pct - progress_pct, 0.0)
                if remaining_pct > 0:
                    min_deadline = build_phase.get("min_until", build_phase.get("until", tick))
                    max_deadline = build_phase.get("until", min_deadline)
                    ticks_remaining = max(
                        min_deadline - tick,
                        5,
                    )
                    per_tick_base = remaining_pct / ticks_remaining
                    urgency = 1.0
                    if tick >= max(min_deadline - 5, build_phase.get("start_tick", tick)):
                        urgency = 1.5
                    if tick >= max_deadline - 10:
                        urgency = max(urgency, 2.0)
                    floor = 0.0015 if tick < min_deadline else 0.0025
                    if tick >= max_deadline - 10:
                        floor = max(floor, 0.0035)
                    min_move_pct = min(
                        remaining_pct,
                        max(per_tick_base * urgency, floor),
                    )
            return self._probe_orders(
                session_id=session_id,
                tick=tick,
                context=context,
                side=side,
                quantity=quantity,
                reference_price=reference_price,
                inventory_state=inventory_state,
                enforce_min_move=True,
                min_move_pct=min_move_pct,
                build_state=build_phase,
            )

        if burst_active:
            return self._burst_orders(
                session_id=session_id,
                session_code=session_code,
                tick=tick,
                context=context,
                side=side,
                quantity=quantity,
                inventory_state=inventory_state,
            )
        orders = self._probe_orders(
            session_id=session_id,
            tick=tick,
            context=context,
            side=side,
            quantity=quantity,
            reference_price=reference_price,
            inventory_state=inventory_state,
            enforce_min_move=False,
        )
        key_move = heat >= self._jolt_heat_threshold and abs(direction_score) >= 0.1
        if key_move:
            jolt_order = self._jolt_order(
                session_id=session_id,
                tick=tick,
                context=context,
                side=side,
                quantity=quantity,
                inventory_state=inventory_state,
            )
            if jolt_order is not None:
                orders.append(jolt_order)
        return orders

    def _burst_orders(
        self,
        *,
        session_id: int,
        session_code: str,
        tick: int,
        context: AgentContext,
        side: str,
        quantity: float,
        inventory_state: dict[str, float],
    ) -> List[GeneratedOrder]:
        orders: List[GeneratedOrder] = []
        parts = max(3, random.randint(4, 8))
        drift_side = side
        hedge_parts = max(1, parts // 4)
        directional_parts = parts - hedge_parts
        impact_pct = 0.0
        for idx in range(parts):
            is_hedge = idx >= directional_parts
            order_side = (
                drift_side
                if not is_hedge
                else ("SELL" if drift_side == "BUY" else "BUY")
            )
            chunk_qty = quantity / parts
            chunk_qty *= (
                random.uniform(1.0, 1.6) if not is_hedge else random.uniform(0.4, 0.9)
            )
            chunk_qty = self._apply_inventory_controls(
                session_id,
                order_side,
                self.resolve_reference_price(context, order_side, context.last_price),
                chunk_qty,
                inventory_state,
            )
            chunk_qty = float(round(chunk_qty, 2))
            if chunk_qty < 1.0:
                continue
            use_market = not is_hedge or random.random() < 0.35
            ref_price = self.resolve_reference_price(
                context, order_side, context.last_price
            )
            target_price = None
            if ref_price:
                move = ref_price * random.uniform(0.002, 0.005)
                if not use_market:
                    if order_side == "BUY":
                        target_price = ref_price + move
                    else:
                        target_price = max(0.01, ref_price - move)
                if not is_hedge:
                    impact_pct += move / max(ref_price, 0.01)
            orders.append(
                self._create_order(
                    order_id=f"{self.code}-burst-{idx}-{session_id}-{tick}-{uuid.uuid4().hex[:5]}",
                    participant_id=f"{self.code}-burst",
                    side=order_side,
                    quantity=chunk_qty,
                    price=None if use_market else target_price,
                )
            )
        if orders:
            logger.info(
                "Prop burst code=%s session=%s tick=%s parts=%s impact=%.2f%%",
                self.code,
                session_id,
                tick,
                parts,
                impact_pct * 100,
            )
        return orders

    def _probe_orders(
        self,
        *,
        session_id: int,
        tick: int,
        context: AgentContext,
        side: str,
        quantity: float,
        reference_price: float | None,
        inventory_state: dict[str, float],
        enforce_min_move: bool,
        min_move_pct: float | None = None,
        build_state: Dict[str, Any] | None = None,
    ) -> List[GeneratedOrder]:
        parts = max(2, random.randint(3, 5))
        orders: List[GeneratedOrder] = []
        impact_pct = 0.0
        for idx in range(parts):
            chunk_qty = (quantity / parts) * random.uniform(0.6, 1.1)
            chunk_qty = self._apply_inventory_controls(
                session_id,
                side,
                self.resolve_reference_price(context, side, reference_price),
                chunk_qty,
                inventory_state,
            )
            chunk_qty = float(round(chunk_qty, 2))
            if chunk_qty < 1.0:
                continue
            base_price = (
                context.last_price
                if context.last_price is not None
                else self.resolve_reference_price(context, side, reference_price)
            )
            if base_price is None:
                base_price = 1.0
            drift = base_price * random.uniform(0.001, 0.003)
            impact_pct += drift / max(base_price, 0.01)
            limit_price = (
                base_price + drift if side == "BUY" else max(0.01, base_price - drift)
            )
            orders.append(
                self._create_order(
                    order_id=f"{self.code}-probe-{idx}-{session_id}-{tick}-{uuid.uuid4().hex[:6]}",
                    participant_id=f"{self.code}-probe",
                    side=side,
                    quantity=chunk_qty,
                    price=limit_price,
                )
            )
        target_pct = None
        if enforce_min_move:
            if min_move_pct is not None and min_move_pct > 0:
                target_pct = min_move_pct
            else:
                target_pct = 0.005
        if target_pct is not None and impact_pct < target_pct:
            missing_pct = max(target_pct - impact_pct, 0.0)
            boost_ratio = min(1.0, max(missing_pct / max(target_pct, 1e-6), 0.35))
            boost_qty = self._apply_inventory_controls(
                session_id,
                side,
                self.resolve_reference_price(context, side, reference_price),
                quantity * boost_ratio,
                inventory_state,
            )
            boost_qty = float(round(boost_qty, 2))
            if boost_qty >= 1.0:
                orders.append(
                    self._create_order(
                        order_id=f"{self.code}-probe-boost-{session_id}-{tick}",
                        participant_id=f"{self.code}-boost",
                        side=side,
                        quantity=boost_qty,
                        price=None,
                    )
                )
                impact_pct += missing_pct
        if build_state is not None and impact_pct > 0:
            self._record_build_progress(session_id, tick, impact_pct)
        if orders:
            logger.info(
                "Prop build orders code=%s session=%s tick=%s count=%s move=%.2f%% target=%.2f%%",
                self.code,
                session_id,
                tick,
                len(orders),
                impact_pct * 100,
                (target_pct or 0.0) * 100,
            )
        return orders

    def _jolt_order(
        self,
        *,
        session_id: int,
        tick: int,
        context: AgentContext,
        side: str,
        quantity: float,
        inventory_state: dict[str, float],
    ) -> GeneratedOrder | None:
        jolt_qty = quantity * random.uniform(1.5, 3.0)
        jolt_qty = self._apply_inventory_controls(
            session_id,
            side,
            self.resolve_reference_price(context, side, context.last_price),
            jolt_qty,
            inventory_state,
        )
        jolt_qty = float(round(jolt_qty, 2))
        if jolt_qty < 1.0:
            return None
        target_price = None
        if context.last_price:
            movement = context.last_price * random.uniform(0.02, 0.05)
            if side == "BUY":
                target_price = context.last_price + movement
            else:
                target_price = max(0.01, context.last_price - movement)
        order = self._create_order(
            order_id=f"{self.code}-jolt-{session_id}-{tick}-{uuid.uuid4().hex[:6]}",
            participant_id=f"{self.code}-jolt",
            side=side,
            quantity=jolt_qty,
            price=target_price,
        )
        logger.info(
            "Prop jolt code=%s session=%s tick=%s side=%s qty=%.2f",
            self.code,
            session_id,
            tick,
            side,
            jolt_qty,
        )
        return order

    def _apply_inventory_controls(
        self,
        session_id: int,
        side: str,
        reference_price: float,
        quantity: float,
        state: dict[str, float],
    ) -> float:
        """Consume available cash or position to avoid shorting/overspending."""
        qty = self._reserve_order_capacity(
            state, side=side, quantity=quantity, price=reference_price
        )
        return qty

    def _should_idle(
        self, session_id: int, tick: int, profile: dict[str, float]
    ) -> bool:
        strict_until = self._strict_block_until.get(session_id)
        if strict_until is not None and tick < strict_until:
            return True

        phase = self._phase_state.get(session_id)
        if phase and phase.get("state") in {"build", "burst"}:
            return False

        window = self._cooldown_range
        next_tick = self._next_active_tick.get(session_id)
        if next_tick is None:
            self._next_active_tick[session_id] = tick + random.randint(*window)
            next_tick = self._next_active_tick[session_id]
        if tick < next_tick:
            last_active = self._last_active_tick.get(session_id, 0)
            if tick - last_active >= self._max_idle_without_heat:
                self._next_active_tick[session_id] = tick  # force check now
                next_tick = tick
            else:
                return True

        heat = float(profile.get("retail_heat", 1.0))
        if heat >= self._heat_threshold:
            self._heat_deferrals[session_id] = 0
            self._ensure_build_phase(session_id, tick)
            self._last_active_tick[session_id] = tick
            logger.info(
                "Prop idle exit heat %.2f code=%s session=%s tick=%s",
                heat,
                self.code,
                session_id,
                tick,
            )
            return False

        deferrals = self._heat_deferrals.get(session_id, 0) + 1
        self._heat_deferrals[session_id] = deferrals
        patience = self._low_heat_patience
        forced_level = max(1.0, self._heat_threshold * self._low_heat_forced_ratio)
        should_force = False
        reason = "moderate"
        if deferrals >= patience and heat >= forced_level:
            should_force = True
        elif deferrals >= patience * 2 and random.random() < 0.4:
            should_force = True
            reason = "timeout"
        else:
            last_active = self._last_active_tick.get(session_id, 0)
            if tick - last_active >= self._max_idle_without_heat:
                should_force = True
                reason = "max_idle"
        if should_force:
            self._heat_deferrals[session_id] = 0
            self._ensure_build_phase(session_id, tick)
            self._last_active_tick[session_id] = tick
            logger.info(
                "Prop idle exit (%s) heat %.2f code=%s session=%s tick=%s",
                reason,
                heat,
                self.code,
                session_id,
                tick,
            )
            return False

        self._next_active_tick[session_id] = tick + random.randint(*window)
        return True


    def _ensure_build_phase(self, session_id: int, tick: int) -> None:
        phase = self._phase_state.get(session_id)
        if phase is None or phase.get("state") not in {"build", "burst", "observe"}:
            min_duration = random.randint(*self._build_duration_ticks)
            max_duration = min_duration + random.randint(30, 60)
            target_move = random.uniform(*self._build_move_range)
            self._phase_state[session_id] = {
                "state": "build",
                "start_tick": tick,
                "min_until": tick + min_duration,
                "until": tick + max_duration,
                "target_move_pct": target_move,
                "progress_move_pct": 0.0,
                "ticks_worked": 0,
                "direction": None,
            }
            self._last_active_tick[session_id] = tick
            logger.info(
                "Prop build start code=%s session=%s tick=%s duration=%s target=%.2f%%",
                self.code,
                session_id,
                tick,
                min_duration,
                target_move * 100,
            )

    def _is_build_phase(self, session_id: int, tick: int) -> bool:
        phase = self._phase_state.get(session_id)
        if phase and phase.get("state") == "build":
            max_until = phase.get("until", tick)
            min_until = phase.get("min_until", max_until)
            progress = float(phase.get("progress_move_pct", 0.0))
            target = float(phase.get("target_move_pct", 0.0))
            completed = target > 0 and progress >= target
            if tick >= max_until or (tick >= min_until and completed):
                self._phase_state.pop(session_id, None)
                self._next_active_tick[session_id] = tick + random.randint(
                    *self._observe_window_range
                )
                self._last_active_tick[session_id] = tick
                logger.info(
                    "Prop build finish code=%s session=%s tick=%s progress=%.2f%% target=%.2f%%",
                    self.code,
                    session_id,
                    tick,
                    progress * 100,
                    target * 100,
                )
                return False
            return True
        return False

    def _get_build_phase(self, session_id: int) -> Dict[str, Any] | None:
        phase = self._phase_state.get(session_id)
        if phase and phase.get("state") == "build":
            return phase
        return None

    def _record_build_progress(
        self, session_id: int, tick: int, move_pct: float
    ) -> None:
        phase = self._get_build_phase(session_id)
        if not phase:
            return
        progress = float(phase.get("progress_move_pct", 0.0)) + max(0.0, move_pct)
        phase["progress_move_pct"] = progress
        phase["ticks_worked"] = phase.get("ticks_worked", 0) + 1
        target = float(phase.get("target_move_pct", 0.0))
        if target > 0 and progress >= target and not phase.get("target_completed"):
            phase["target_completed"] = True
            logger.info(
                "Prop build target met code=%s session=%s tick=%s progress=%.2f%%",
                self.code,
                session_id,
                tick,
                progress * 100,
            )


__all__ = ["PropMomentumAgent"]
