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


# User Order Schemas (Feature: 001-ai-user-order-matching)


class OrderRequest(BaseModel):
    """User order submission request"""
    side: Literal['BUY', 'SELL'] = Field(..., description='Order side: BUY or SELL')
    order_type: Literal['MARKET', 'LIMIT'] = Field(..., description='Order type: MARKET or LIMIT')
    quantity: float = Field(..., gt=0, description='Order quantity, must be > 0')
    price: Optional[float] = Field(None, gt=0, description='Limit price (required for LIMIT orders)')

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "side": "BUY",
                    "order_type": "LIMIT",
                    "quantity": 100.0,
                    "price": 50.25
                },
                {
                    "side": "SELL",
                    "order_type": "MARKET",
                    "quantity": 50.0
                }
            ]
        }


class OrderAcceptedResponse(BaseModel):
    """Response for successfully accepted user order"""
    status: Literal['accepted'] = Field(default='accepted', description='Order acceptance status')
    order_id: str = Field(..., description='Unique order identifier')
    message: str = Field(default="Order queued for next tick", description='Status message')
    estimated_execution_tick: int = Field(..., ge=0, description='Estimated tick when order will be processed')

    class Config:
        json_schema_extra = {
            "example": {
                "status": "accepted",
                "order_id": "user-12345-1699876543000-abc123",
                "message": "Order queued for next tick",
                "estimated_execution_tick": 1234
            }
        }


class TradeInfo(BaseModel):
    """Individual trade execution details"""
    trade_id: str = Field(..., description='Trade identifier')
    price: float = Field(..., description='Execution price')
    quantity: float = Field(..., description='Executed quantity')
    counterparty_type: Literal['user', 'ai_retail', 'ai_prop', 'ai_institutional', 'ai_market_maker'] = Field(
        ..., description='Type of counterparty in the trade'
    )
    executed_at: datetime = Field(..., description='Execution timestamp')


class OrderDetail(BaseModel):
    """Detailed order information including fills"""
    order_id: str = Field(..., description='Order identifier')
    session_id: int = Field(..., description='Session ID')
    user_id: int = Field(..., description='User ID')
    side: Literal['BUY', 'SELL'] = Field(..., description='Order side')
    order_type: Literal['MARKET', 'LIMIT'] = Field(..., description='Order type')
    quantity: float = Field(..., description='Order quantity')
    price: Optional[float] = Field(None, description='Limit price (for LIMIT orders)')
    status: Literal['PENDING', 'NEW', 'PARTIAL', 'FILLED', 'CANCELLED'] = Field(..., description='Order status')
    filled_quantity: float = Field(..., description='Cumulative filled quantity')
    avg_filled_price: Optional[float] = Field(None, description='Average fill price')
    timestamp: int = Field(..., description='Order timestamp (nanoseconds)')
    created_at: datetime = Field(..., description='Creation time')
    updated_at: datetime = Field(..., description='Last update time')
    trades: list[TradeInfo] = Field(default_factory=list, description='Associated trades')


class OrderListResponse(BaseModel):
    """Paginated list of orders"""
    orders: list[OrderDetail] = Field(default_factory=list, description='Order list')
    total: int = Field(..., ge=0, description='Total number of orders matching filter')
    limit: int = Field(..., description='Page size limit')
    offset: int = Field(..., description='Page offset')


class CancelOrderResponse(BaseModel):
    """Response for order cancellation"""
    status: Literal['cancelled'] = Field(default='cancelled', description='Cancellation status')
    order_id: str = Field(..., description='Cancelled order ID')
    cancelled_quantity: float = Field(..., ge=0, description='Quantity cancelled (unfilled portion)')
    message: str = Field(..., description='Cancellation message')

    class Config:
        json_schema_extra = {
            "example": {
                "status": "cancelled",
                "order_id": "user-12345-1699876543000-abc123",
                "cancelled_quantity": 40.0,
                "message": "Order cancelled, remaining 40.0 units will not be executed"
            }
        }
