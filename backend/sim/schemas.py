"""Pydantic schemas for simulation endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class MarketSnapshotOut(BaseModel):
    session_id: int = Field(..., description='Simulation session ID')
    tick: int = Field(..., description='Tick index')
    timestamp: datetime = Field(..., description='Snapshot timestamp')
    best_bid: Optional[float] = Field(None, description='Best bid price')
    best_ask: Optional[float] = Field(None, description='Best ask price')
    last_price: Optional[float] = Field(None, description='Last traded price')
    vwap_price: Optional[float] = Field(None, description='Volume weighted price')
    total_volume: Optional[float] = Field(None, description='Total traded volume')
    imbalance: Optional[float] = Field(None, description='Order book imbalance')
    sentiment_score: Optional[float] = Field(None, description='Sentiment indicator')
    liquidity_level: Optional[float] = Field(None, description='Liquidity indicator')
    features: dict[str, float] = Field(default_factory=dict, description='Latest feature metrics')
    emotion: Optional[float] = Field(None, description='Cached sentiment value')
    payload: dict[str, Any] = Field(default_factory=dict, description='Extra data payload')


class LeaderboardEntryOut(BaseModel):
    participant_id: str = Field(..., description='Participant identifier')
    score: float = Field(..., description='Score or influence metric')


class OrderInput(BaseModel):
    order_id: str = Field(..., description='Order identifier')
    participant_id: str = Field(..., description='Participant identifier')
    side: Literal['BUY', 'SELL'] = Field(..., description='Order side')
    type: Literal['LIMIT', 'MARKET'] = Field(..., description='Order type')
    quantity: float = Field(..., gt=0, description='Order quantity')
    price: Optional[float] = Field(None, description='Limit price when applicable')


class TickRequest(BaseModel):
    session_id: int = Field(..., ge=1, description='Simulation session ID')
    session_code: str = Field(..., min_length=1, description='Session code for Redis namespace')
    tick: int = Field(..., ge=0, description='Tick index to process')
    orders: list[OrderInput] = Field(default_factory=list, description='Orders to process during the tick')
    timestamp: Optional[datetime] = Field(None, description='Optional override timestamp')


class TickResponse(BaseModel):
    trace_id: str = Field(..., description='Trace identifier for idempotent handling')
    status: str = Field("accepted", description='Processing status (accepted/duplicate/error)')
    orders: list[str] = Field(default_factory=list, description='Accepted order identifiers')
    trades: list[dict[str, Any]] = Field(default_factory=list, description='Executed trades summary')
    snapshot: dict[str, Any] = Field(default_factory=dict, description='Resulting market snapshot data')
