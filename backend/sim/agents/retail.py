"""Retail agent strategies."""

from __future__ import annotations

import random
import uuid
from collections import defaultdict
from typing import Dict, List

from .base import AgentContext, AgentStrategy, GeneratedOrder


class RetailSentimentAgent(AgentStrategy):
    """
    Sentiment-driven retail participant with random impulses.

    T062: Enhanced with configurable behavior parameters for differentiation.
    """

    behavior_category = "retail"
    participation_limit_per_tick = 40
    _tick_participation: Dict[int, Dict[str, int]] = defaultdict(
        lambda: {"tick": -1, "count": 0}
    )

    def __init__(
        self,
        code: str = "retail",
        *,
        threshold: float = 0.03,  # ADJUSTED: 0.05 -> 0.03 for higher activity
        base_quantity: float = 5.0,
        follow_chance: float = 0.45,  # ADJUSTED: 0.35 -> 0.45 for more FOMO
        weight: float = 1.0,
        # T062: Behavior parameters for differentiation
        profit_target: float | None = None,
        stop_loss: float | None = None,
        herd_behavior_strength: float | None = None,
        momentum_sensitivity: float | None = None,
        risk_tolerance: float | None = None,
        initial_cash: float = 50000.0,  # Default 50k for retail traders
        decision_latency_range: tuple[int, int] | None = (10, 20),
        mean_reversion_strength: float | None = None,
        cooldown_range: tuple[int, int] | None = None,
        reaction_delay_range: tuple[int, int] | None = None,
        max_pending_orders: int = 5,
        instant_reaction_prob: float = 0.2,
        order_ttl_range: tuple[int, int] | None = None,
        surge_heat_threshold: float = 1.6,
        surge_drift_threshold: float = 0.025,
        surge_release_batch: int = 5,
        aggressive_heat_threshold: float = 1.25,
        aggressive_drift_threshold: float = 0.015,
        aggressive_prob: float = 0.45,
        contrarian: bool = False,
    ) -> None:
        super().__init__(
            code=code,
            weight=weight,
            initial_cash=initial_cash,
            decision_latency_range=decision_latency_range,
        )
        self._threshold = threshold
        self._base_quantity = base_quantity
        self._follow_chance = follow_chance
        self._prev_price: float | None = None

        # T062: Store behavior parameters
        self.profit_target = profit_target if profit_target is not None else 0.30
        self.stop_loss = stop_loss if stop_loss is not None else 0.20  # 20% stop loss
        self.herd_behavior_strength = herd_behavior_strength if herd_behavior_strength is not None else 0.75
        self.momentum_sensitivity = momentum_sensitivity if momentum_sensitivity is not None else 0.60
        self.risk_tolerance = risk_tolerance if risk_tolerance is not None else 0.55
        self.mean_reversion_strength = (
            mean_reversion_strength if mean_reversion_strength is not None else 0.6
        )
        self._cooldown_range = cooldown_range or (8, 25)
        self._next_active_tick: Dict[int, int] = {}
        self._reaction_delay_range = reaction_delay_range or (3, 12)
        self._pending_orders: Dict[int, List[dict]] = {}
        self._pending_index: Dict[int, Dict[str, dict]] = defaultdict(dict)
        self._max_pending_orders = max(1, max_pending_orders)
        self._instant_reaction_prob = max(0.0, min(1.0, instant_reaction_prob))
        self._order_ttl_range = order_ttl_range or (8, 20)
        self._surge_heat_threshold = max(1.0, surge_heat_threshold)
        self._surge_drift_threshold = max(0.0, surge_drift_threshold)
        self._surge_release_batch = max(1, surge_release_batch)
        self._aggressive_heat_threshold = max(1.0, aggressive_heat_threshold)
        self._aggressive_drift_threshold = max(0.0, aggressive_drift_threshold)
        self._aggressive_prob = max(0.0, min(1.0, aggressive_prob))
        self._is_contrarian = contrarian
        self._reserved_cash: Dict[int, float] = defaultdict(float)
        self._reserved_position: Dict[int, float] = defaultdict(float)

    async def generate_orders(
        self,
        session_id: int,
        session_code: str,
        tick: int,
        context: AgentContext,
    ) -> List[GeneratedOrder]:
        profile = context.profile or {}
        last_price = context.last_price
        ready = self._pop_ready_orders(session_id, tick, context)
        if ready:
            if self._should_trigger_surge(profile, last_price):
                ready.extend(
                    self._release_pending_batch(
                        session_id=session_id,
                        tick=tick,
                        context=context,
                        limit=self._surge_release_batch,
                    )
                )
            return ready

        if self._should_idle(session_id, tick):
            return []

        sentiment = await context.fetch_sentiment(session_code) or 0.0
        drift = 0.0
        if self._prev_price is not None and last_price is not None and self._prev_price > 0:
            drift = (last_price - self._prev_price) / self._prev_price
        if last_price is not None:
            self._prev_price = last_price

        profile = context.profile or {}
        market_cap = profile.get("market_cap", "mid")
        threshold = self._threshold
        initial_price = None
        try:
            initial_price = float(profile.get("initial_price"))
        except (TypeError, ValueError):
            initial_price = None

        # T062: Apply herd_behavior_strength to follow chance
        # Higher herd behavior = more likely to follow without strong signal
        follow_chance = self._follow_chance * (1.0 + self.herd_behavior_strength * 0.5)  # Range: 0.35 to ~0.61

        if market_cap == "small":
            threshold *= 0.6
            follow_chance = min(0.9, follow_chance + 0.25)
        elif market_cap == "large":
            threshold *= 1.2
            follow_chance = max(0.1, follow_chance - 0.15)

        # T062: Apply momentum_sensitivity to drift weighting
        # Higher momentum sensitivity = react more to price changes
        drift_weight = 0.4 * self.momentum_sensitivity  # Range: 0.24 to 0.40

        reversion_bias = 0.0
        if (
            initial_price
            and initial_price > 0
            and last_price is not None
            and self.mean_reversion_strength > 0
        ):
            deviation = (last_price - initial_price) / initial_price
            reversion_bias = -deviation * self.mean_reversion_strength

            impulse = (
                sentiment
                + drift * drift_weight
                + reversion_bias
                + random.uniform(-0.05, 0.05)
        )

        if abs(impulse) < threshold:
            if random.random() > follow_chance:
                return []
            # T062: Herd behavior makes random impulses more extreme
            impulse_range = threshold * (0.5 + self.herd_behavior_strength * 0.5)
            impulse = random.uniform(-impulse_range, impulse_range)

        side = "BUY" if impulse >= 0 else "SELL"
        if self._is_contrarian:
            side = "SELL" if side == "BUY" else "BUY"

        # T062: Apply risk_tolerance to position sizing
        # Higher risk tolerance = willing to take larger positions
        risk_factor = 0.7 + (self.risk_tolerance * 0.8)  # Range: 0.7 to 1.5

        quantity = self._base_quantity * self.weight * risk_factor
        quantity *= (0.6 + abs(impulse) * 8.0)
        quantity *= random.uniform(0.5, 1.6)
        quantity = max(1.0, float(int(max(quantity, self._base_quantity * 0.3))))

        reference_price = self.resolve_reference_price(context, side, last_price)
        quantity = self._apply_position_limits(
            session_id, context, side, quantity, reference_price
        )
        quantity = float(round(quantity, 2))
        if quantity < 1.0:
            return []

        limit_price = self._compute_limit_price(
            side=side,
            reference_price=reference_price,
            context=context,
        )
        order_type = self._decide_order_type(
            profile=profile,
            drift=abs(drift),
        )
        scheduled = self._schedule_delayed_order(
            session_id=session_id,
            tick=tick,
            side=side,
            quantity=quantity,
            price=limit_price,
            order_type=order_type,
            context=context,
        )
        return scheduled

    def _apply_position_limits(
        self,
        session_id: int,
        context: AgentContext,
        side: str,
        quantity: float,
        reference_price: float,
    ) -> float:
        """Clamp order size by available cash or inventory."""
        state = self._account_state(session_id, context)
        state["cash"] = max(0.0, state.get("cash", 0.0) - self._reserved_cash[session_id])
        state["position"] = max(
            0.0, state.get("position", 0.0) - self._reserved_position[session_id]
        )
        qty = self._reserve_order_capacity(
            state, side=side, quantity=quantity, price=reference_price
        )
        return qty

    def _should_idle(self, session_id: int, tick: int) -> bool:
        window = self._cooldown_range
        next_tick = self._next_active_tick.get(session_id)
        if next_tick is None or tick >= next_tick:
            self._next_active_tick[session_id] = tick + random.randint(*window)
            return False
        return True

    def _schedule_delayed_order(
        self,
        *,
        session_id: int,
        tick: int,
        side: str,
        quantity: float,
        price: float,
        order_type: str,
        context: AgentContext,
    ) -> List[GeneratedOrder]:
        if order_type == "MARKET":
            return [
                self._build_order(
                    session_id=session_id,
                    tick=tick,
                    side=side,
                    quantity=quantity,
                    price=None,
                    order_type=order_type,
                )
            ]

        entry = {
            "release_tick": tick,
            "side": side,
            "quantity": quantity,
            "price": price,
            "expire_tick": None,
            "order_type": order_type,
            "order_id": None,
        }
        ttl = random.randint(*self._order_ttl_range)
        instant = random.random() < self._instant_reaction_prob
        delay = 0 if instant else random.randint(*self._reaction_delay_range)
        entry["release_tick"] = tick + delay
        entry["expire_tick"] = entry["release_tick"] + ttl
        self._reserve_entry_resources(session_id, entry)
        if instant:
            order = self._build_order(
                session_id=session_id,
                tick=tick,
                side=side,
                quantity=quantity,
                price=price,
                order_type=order_type,
            )
            entry["order_id"] = order.order_id
            self._pending_index[session_id][order.order_id] = entry
            return [order]

        queue = self._pending_orders.setdefault(session_id, [])
        by_id = self._pending_index[session_id]
        queue.append(entry)
        if len(queue) > self._max_pending_orders:
            removed = queue.pop(0)
            self._release_entry_resources(session_id, removed)
            if oid := removed.get("order_id"):
                by_id.pop(oid, None)
        return []

    def _pop_ready_orders(
        self, session_id: int, tick: int, context: AgentContext
    ) -> List[GeneratedOrder]:
        queue = self._pending_orders.setdefault(session_id, [])
        ready: List[dict] = []
        remaining: List[dict] = []
        for entry in queue:
            if tick >= entry["release_tick"] and tick <= entry.get("expire_tick", tick):
                ready.append(entry)
            elif tick > entry.get("expire_tick", tick):
                self._release_entry_resources(session_id, entry)
                continue
            else:
                remaining.append(entry)
        queue[:] = remaining

        orders: List[GeneratedOrder] = []
        for entry in ready:
            order = self._build_order(
                session_id=session_id,
                tick=tick,
                side=entry["side"],
                quantity=entry["quantity"],
                price=entry["price"] if entry.get("order_type") == "LIMIT" else None,
                order_type=entry.get("order_type", "LIMIT"),
            )
            entry["order_id"] = order.order_id
            self._pending_index[session_id][order.order_id] = entry
            orders.append(order)
        return orders

    def _compute_limit_price(
        self,
        *,
        side: str,
        reference_price: float | None,
        context: AgentContext,
    ) -> float:
        base = reference_price
        if base is None:
            if side == "BUY" and context.best_bid:
                base = context.best_bid
            elif side == "SELL" and context.best_ask:
                base = context.best_ask
        if base is None and context.last_price is not None:
            base = context.last_price
        if base is None:
            base = 1.0
        offset = random.uniform(0.0005, 0.002)
        if side == "BUY":
            price = base * (1 - offset)
        else:
            price = base * (1 + offset)
        return max(round(price, 4), 0.01)

    def _build_order(
        self,
        *,
        session_id: int,
        tick: int,
        side: str,
        quantity: float,
        price: float | None,
        order_type: str,
    ) -> GeneratedOrder:
        return GeneratedOrder(
            order_id=f"{self.code}-{session_id}-{tick}-{uuid.uuid4().hex[:8]}",
            participant_id=f"{self.code}-agent",
            participant_code=self.code,
            participant_type="agent",
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            behavior_category="retail",
            profit_target=self.profit_target,
            stop_loss=self.stop_loss,
            herd_behavior_strength=self.herd_behavior_strength,
            momentum_sensitivity=self.momentum_sensitivity,
            risk_tolerance=self.risk_tolerance,
        )

    def _should_trigger_surge(
        self, profile: dict[str, float], last_price: float | None
    ) -> bool:
        heat = float(profile.get("retail_heat", 1.0))
        drift = 0.0
        if (
            last_price is not None
            and self._prev_price is not None
            and self._prev_price > 0
        ):
            drift = abs((last_price - self._prev_price) / self._prev_price)
        return heat >= self._surge_heat_threshold or drift >= self._surge_drift_threshold

    def _release_pending_batch(
        self,
        *,
        session_id: int,
        tick: int,
        context: AgentContext,
        limit: int,
    ) -> List[GeneratedOrder]:
        queue = self._pending_orders.setdefault(session_id, [])
        if not queue or limit <= 0:
            return []
        queue.sort(key=lambda entry: entry["release_tick"])
        released: List[dict] = []
        remaining: List[dict] = []
        for entry in queue:
            if len(released) < limit and tick <= entry.get("expire_tick", tick):
                released.append(entry)
            else:
                remaining.append(entry)
        queue[:] = remaining
        if not released:
            return []
        slots = self._acquire_slots(session_id, tick, len(released))
        if slots <= 0:
            for entry in released:
                entry["release_tick"] = tick + 1
                queue.append(entry)
            return []
        usable = released[:slots]
        deferred = released[slots:]
        for entry in deferred:
            entry["release_tick"] = tick + 1
            queue.append(entry)

        orders: List[GeneratedOrder] = []
        for entry in usable:
            order = self._build_order(
                session_id=session_id,
                tick=tick,
                side=entry["side"],
                quantity=entry["quantity"],
                price=entry["price"] if entry.get("order_type") == "LIMIT" else None,
                order_type=entry.get("order_type", "LIMIT"),
            )
            entry["order_id"] = order.order_id
            self._pending_index[session_id][order.order_id] = entry
            orders.append(order)
        return orders

    def _acquire_slots(self, session_id: int, tick: int, requested: int) -> int:
        info = self._tick_participation.setdefault(
            session_id, {"tick": tick, "count": 0}
        )
        if info["tick"] != tick:
            info["tick"] = tick
            info["count"] = 0
        available = self.participation_limit_per_tick - info["count"]
        if available <= 0:
            return 0
        take = min(available, requested)
        info["count"] += take
        return take

    def _decide_order_type(self, profile: dict[str, float], drift: float) -> str:
        heat = float(profile.get("retail_heat", 1.0))
        adjusted_heat = heat * (0.7 if self._is_contrarian else 1.0)
        adjusted_drift = drift * (0.7 if self._is_contrarian else 1.0)
        aggressive = (
            adjusted_heat >= self._aggressive_heat_threshold
            or adjusted_drift >= self._aggressive_drift_threshold
        )
        probability = self._aggressive_prob * (0.5 if self._is_contrarian else 1.0)
        if aggressive and random.random() < probability:
            return "MARKET"
        return "LIMIT"

    def on_order_filled(self, session_id: int, order_id: str) -> None:
        entry = self._pending_index[session_id].pop(order_id, None)
        if entry:
            self._release_entry_resources(session_id, entry)
            queue = self._pending_orders.get(session_id)
            if queue:
                queue[:] = [item for item in queue if item is not entry]

    def _reserve_entry_resources(self, session_id: int, entry: dict) -> None:
        if entry.get("order_type") != "LIMIT":
            return
        quantity = float(entry.get("quantity") or 0.0)
        if quantity <= 0:
            return
        side = (entry.get("side") or "").upper()
        if side == "BUY":
            price = float(entry.get("price") or 0.0)
            price = max(price, 0.01)
            cash = quantity * price
            entry["reserved_cash"] = cash
            self._reserved_cash[session_id] += cash
        else:
            entry["reserved_position"] = quantity
            self._reserved_position[session_id] += quantity

    def _release_entry_resources(self, session_id: int, entry: dict) -> None:
        cash = float(entry.pop("reserved_cash", 0.0) or 0.0)
        if cash:
            self._reserved_cash[session_id] = max(
                0.0, self._reserved_cash[session_id] - cash
            )
        qty = float(entry.pop("reserved_position", 0.0) or 0.0)
        if qty:
            self._reserved_position[session_id] = max(
                0.0, self._reserved_position[session_id] - qty
            )


__all__ = ["RetailSentimentAgent"]

