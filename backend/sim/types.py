from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass(slots=True)
class SimulationSession:
    id: Optional[int]
    session_code: str
    status: str
    mode: str
    tick_interval_ms: int
    current_tick: int = 0
    total_ticks: int = 0
    config_version: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None


@dataclass(slots=True)
class ParticipantState:
    id: Optional[int]
    session_id: int
    participant_type: str
    influence_weight: float
    cash_balance: float
    inventory: float
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class MarketSnapshot:
    session_id: int
    tick: int
    timestamp: datetime
    best_bid: Optional[float]
    best_ask: Optional[float]
    last_price: Optional[float]
    vwap_price: Optional[float]
    total_volume: Optional[float]
    imbalance: Optional[float]
    sentiment_score: Optional[float]
    liquidity_level: Optional[float]
    features: Dict[str, float] = field(default_factory=dict)
    emotion: Optional[float] = None
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class OrderEventRecord:
    session_id: int
    tick: int
    order_code: str
    participant_id: str
    side: str
    order_type: str
    price: Optional[float]
    quantity: float
    remaining_qty: float
    status: str
    impact: Optional[float]
    created_at: datetime
    participant_code: Optional[str] = None
    participant_db_id: Optional[int] = None


@dataclass(slots=True)
class TradeEventRecord:
    session_id: int
    tick: int
    buy_order_code: str
    sell_order_code: str
    buyer_participant_id: str
    seller_participant_id: str
    price: float
    quantity: float
    created_at: datetime
    buyer_participant_code: Optional[str] = None
    seller_participant_code: Optional[str] = None
    buyer_participant_db_id: Optional[int] = None
    seller_participant_db_id: Optional[int] = None


@dataclass(slots=True)
class CoachInsight:
    session_id: int
    session_code: str
    tick: int
    participant_id: str
    participant_db_id: Optional[int]
    participant_type: str
    category: str
    severity: str
    headline: str
    summary: str
    metrics: Dict[str, Any]
    recommendations: list[str]
    created_at: datetime
