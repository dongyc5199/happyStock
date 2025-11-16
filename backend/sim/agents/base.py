"""Agent strategy base classes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
import random
from typing import Any, Dict, Iterable, List, Optional, Protocol

logger = logging.getLogger(__name__)


class FeatureProvider(Protocol):
    async def get_latest_features(
        self, session_id: int, *, metrics: Iterable[str] | None = None
    ) -> Dict[str, float]: ...


class EmotionProvider(Protocol):
    async def get_sentiment(self, session: str) -> float | None: ...


@dataclass(slots=True)
class GeneratedOrder:
    order_id: str
    participant_id: str
    side: str
    order_type: str
    quantity: float
    price: float | None = None
    pool_code: str | None = None
    # Behavior parameters for persistence
    participant_code: str | None = None
    participant_type: str = "agent"
    behavior_category: str | None = None
    profit_target: float | None = None
    stop_loss: float | None = None
    herd_behavior_strength: float | None = None
    momentum_sensitivity: float | None = None
    risk_tolerance: float | None = None


class AgentContext:
    """Context exposed to agent strategies."""

    def __init__(
        self,
        *,
        feature_provider: FeatureProvider | None = None,
        emotion_provider: EmotionProvider | None = None,
        last_price: Optional[float] = None,
        best_bid: Optional[float] = None,
        best_ask: Optional[float] = None,
        profile: Optional[Dict[str, Any]] = None,
        agent_cash: Optional[float] = None,
        agent_position: Optional[float] = None,
    ) -> None:
        self.feature_provider = feature_provider
        self.emotion_provider = emotion_provider
        self.last_price = last_price
        self.best_bid = best_bid
        self.best_ask = best_ask
        self.profile = profile or {}
        self.agent_cash = agent_cash  # Available cash for this agent
        self.agent_position = agent_position  # Current stock position (quantity held)

    async def fetch_features(
        self,
        session_id: int,
        *,
        metrics: Iterable[str] | None = None,
    ) -> Dict[str, float]:
        if self.feature_provider is None:
            return {}
        return await self.feature_provider.get_latest_features(
            session_id, metrics=metrics
        )

    async def fetch_sentiment(self, session_code: str) -> Optional[float]:
        if self.emotion_provider is None:
            return None
        return await self.emotion_provider.get_sentiment(session_code)


class AgentStrategy(ABC):
    """Base class for simulation strategies."""

    def __init__(
        self,
        code: str,
        *,
        weight: float = 1.0,
        initial_cash: float = 100000.0,  # Default 100k initial cash
        initial_inventory: float = 0.0,
        decision_latency_range: tuple[int, int] | None = None,
    ) -> None:
        self.code = code
        self.weight = weight
        self.initial_cash = initial_cash
        self.initial_inventory = max(0.0, initial_inventory)
        # Track cash and position per session
        self._cash: Dict[int, float] = {}  # session_id -> cash
        self._position: Dict[int, float] = {}  # session_id -> quantity
        if decision_latency_range is not None:
            low, high = decision_latency_range
            if high < low:
                low, high = high, low
            low = max(0, int(low))
            high = max(low, int(high))
            self._decision_latency_range: tuple[int, int] | None = (low, high)
        else:
            self._decision_latency_range = None
        self._next_decision_tick: Dict[int, int] = {}

    def _ensure_account(self, session_id: int) -> None:
        """Initialize cash and position for a session if not exists."""
        if session_id not in self._cash:
            self._cash[session_id] = self.initial_cash
            self._position[session_id] = self.initial_inventory

    def get_cash(self, session_id: int) -> float:
        """Get available cash for this agent in a session."""
        self._ensure_account(session_id)
        return self._cash[session_id]

    def get_position(self, session_id: int) -> float:
        """Get current position (stock quantity) for this agent in a session."""
        self._ensure_account(session_id)
        return self._position[session_id]

    def update_cash(self, session_id: int, amount: float) -> None:
        """Update cash balance (positive = add cash, negative = spend cash)."""
        self._ensure_account(session_id)
        self._cash[session_id] += amount

    def update_position(self, session_id: int, quantity: float) -> None:
        """Update position (positive = buy, negative = sell)."""
        self._ensure_account(session_id)
        self._position[session_id] += quantity

    def can_buy(self, session_id: int, quantity: float, price: float) -> bool:
        """Check if agent has enough cash to buy."""
        required_cash = quantity * price
        return self.get_cash(session_id) >= required_cash

    def can_sell(self, session_id: int, quantity: float) -> bool:
        """Check if agent has enough position to sell (no short selling)."""
        return self.get_position(session_id) >= quantity

    @staticmethod
    def resolve_reference_price(
        context: "AgentContext",
        side: str,
        fallback: Optional[float] = None,
    ) -> float:
        """
        Estimate a reasonable fill price for risk checks.

        Prefers best bid/ask, then last price, then fallback, finally 1.0.
        """
        price = context.best_ask if side.upper() == "BUY" else context.best_bid
        if price is None:
            price = context.last_price
        if price is None:
            price = fallback
        if price is None or price <= 0:
            return 1.0
        return float(price)

    def record_fill(
        self,
        session_id: int,
        side: str,
        quantity: float,
        price: float,
    ) -> None:
        """Update cash/position after a trade fill."""
        self._ensure_account(session_id)
        price = max(price, 0.0)
        if side.upper() == "BUY":
            self.update_cash(session_id, -(quantity * price))
            self.update_position(session_id, quantity)
        else:
            self.update_cash(session_id, quantity * price)
            self.update_position(session_id, -quantity)
            if self._position[session_id] < -1e-6:
                logger.warning(
                    "Agent %s session %s position dropped below zero (%.2f). Resetting to 0.",
                    self.code,
                    session_id,
                    self._position[session_id],
                )
                self._position[session_id] = 0.0

    def _account_state(self, session_id: int, context: AgentContext) -> Dict[str, float]:
        """Return mutable snapshot of cash/position used for planning a tick."""
        cash = (
            context.agent_cash
            if context.agent_cash is not None
            else self.get_cash(session_id)
        )
        position = (
            context.agent_position
            if context.agent_position is not None
            else self.get_position(session_id)
        )
        return {"cash": max(0.0, cash), "position": max(0.0, position)}

    def _reserve_order_capacity(
        self,
        state: Dict[str, float],
        *,
        side: str,
        quantity: float,
        price: float,
    ) -> float:
        """Clamp quantity so total exposure does not exceed cash/position."""
        if quantity <= 0:
            return 0.0
        side_upper = side.upper()
        if side_upper == "BUY":
            effective_price = max(price, 0.01)
            cash = state.get("cash", 0.0)
            if effective_price <= 0 or cash <= 0:
                return 0.0
            max_qty = cash / effective_price
            allowed = max(0.0, min(quantity, max_qty))
            state["cash"] = max(0.0, cash - allowed * effective_price)
            return allowed
        position = state.get("position", 0.0)
        allowed = max(0.0, min(quantity, position))
        state["position"] = max(0.0, position - allowed)
        return allowed

    def on_order_filled(self, session_id: int, order_id: str) -> None:
        """Hook for strategies that need to react when one of their orders is filled."""
        return

    def _sample_decision_latency(self) -> int:
        if self._decision_latency_range is None:
            return 0
        low, high = self._decision_latency_range
        return random.randint(low, high)

    def should_generate_orders(self, session_id: int, tick: int) -> bool:
        """
        Determine if the strategy is allowed to act on this tick based on decision latency.
        """
        if self._decision_latency_range is None:
            return True
        next_allowed = self._next_decision_tick.get(session_id)
        if next_allowed is None:
            self._next_decision_tick[session_id] = tick + self._sample_decision_latency()
            return False
        if tick < next_allowed:
            return False
        self._next_decision_tick[session_id] = tick + self._sample_decision_latency()
        return True

    @abstractmethod
    async def generate_orders(
        self,
        session_id: int,
        session_code: str,
        tick: int,
        context: AgentContext,
    ) -> List[GeneratedOrder]:
        """Produce zero or more orders for the current tick."""


class PassiveStrategy(AgentStrategy):
    """Default strategy that yields no orders."""

    async def generate_orders(
        self,
        session_id: int,
        session_code: str,
        tick: int,
        context: AgentContext,
    ) -> List[GeneratedOrder]:
        return []
