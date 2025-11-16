from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
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
    buyer_type: Optional[str] = None  # T024: user, ai_retail, ai_prop, ai_institutional, ai_market_maker
    seller_type: Optional[str] = None  # T024: user, ai_retail, ai_prop, ai_institutional, ai_market_maker


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


class OrderStatus(str, Enum):
    """Order lifecycle status"""
    PENDING = "PENDING"  # Queued in Redis, not yet in matching engine
    NEW = "NEW"  # Entered matching engine, awaiting execution
    PARTIAL = "PARTIAL"  # Partially filled
    FILLED = "FILLED"  # Completely filled
    CANCELLED = "CANCELLED"  # User cancelled


@dataclass(slots=True)
class UserOrder:
    """User-submitted trading order for simulation sessions"""
    order_id: str  # Format: user-{user_id}-{timestamp}-{random}
    session_id: int
    user_id: int
    participant_id: str  # Format: user-{user_id}
    side: str  # "BUY" or "SELL"
    order_type: str  # "MARKET" or "LIMIT"
    quantity: float
    timestamp: int  # Nanoseconds (int64)
    status: OrderStatus
    filled_quantity: float = 0.0
    price: Optional[float] = None  # Required for LIMIT orders
    avg_filled_price: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
