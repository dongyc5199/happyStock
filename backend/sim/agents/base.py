"""Agent strategy base classes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Protocol


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
    ) -> None:
        self.feature_provider = feature_provider
        self.emotion_provider = emotion_provider
        self.last_price = last_price
        self.best_bid = best_bid
        self.best_ask = best_ask

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

    def __init__(self, code: str, *, weight: float = 1.0) -> None:
        self.code = code
        self.weight = weight

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
