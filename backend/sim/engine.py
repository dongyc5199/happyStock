
"""
In-memory matching engine for the simulation subsystem.

提供基础订单簿与撮合逻辑，后续可扩展冲击函数、异步持久化等功能。
"""
from __future__ import annotations

import bisect
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Deque, Dict, Iterable, List, Optional, Tuple


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class OrderStatus(str, Enum):
    NEW = "NEW"
    PARTIAL = "PARTIAL"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"


@dataclass(slots=True)
class Order:
    order_id: str
    session_id: int
    participant_id: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    remaining: float = field(init=False)
    status: OrderStatus = field(default=OrderStatus.NEW)

    def __post_init__(self) -> None:
        self.remaining = self.quantity

    @property
    def is_active(self) -> bool:
        return self.status in {OrderStatus.NEW, OrderStatus.PARTIAL}


@dataclass(slots=True)
class Trade:
    buy_order_id: str
    sell_order_id: str
    price: float
    quantity: float


class OrderBook:
    """Simple price-time priority orderbook."""

    def __init__(self) -> None:
        self.bids: Dict[float, Deque[Order]] = {}
        self.asks: Dict[float, Deque[Order]] = {}
        self.bid_prices: List[float] = []
        self.ask_prices: List[float] = []

    # ------------------------------------------------------------------ #
    # Order management
    def add_limit_order(self, order: Order) -> None:
        if order.side == OrderSide.BUY:
            self._add_to_book(order, self.bids, self.bid_prices, reverse=True)
        else:
            self._add_to_book(order, self.asks, self.ask_prices, reverse=False)

    def _add_to_book(
        self,
        order: Order,
        book: Dict[float, Deque[Order]],
        price_levels: List[float],
        *,
        reverse: bool,
    ) -> None:
        assert order.price is not None
        level = book.get(order.price)
        if level is None:
            book[order.price] = deque([order])
            self._insert_price(order.price, price_levels, reverse=reverse)
        else:
            level.append(order)

    def pop_best(self, side: OrderSide) -> Optional[Order]:
        book = self.bids if side == OrderSide.BUY else self.asks
        prices = self.bid_prices if side == OrderSide.BUY else self.ask_prices
        if not prices:
            return None
        best_price = prices[0]
        queue = book.get(best_price)
        if not queue:
            self._remove_price(best_price, book, prices)
            return self.pop_best(side)

        while queue:
            order = queue.popleft()
            if not order.is_active:
                continue
            if not queue:
                self._remove_price(best_price, book, prices)
            return order

        self._remove_price(best_price, book, prices)
        return self.pop_best(side)

    def _remove_price(self, price: float, book: Dict[float, Deque[Order]], prices: List[float]) -> None:
        book.pop(price, None)
        try:
            prices.remove(price)
        except ValueError:
            pass

    def _insert_price(self, price: float, price_levels: List[float], *, reverse: bool) -> None:
        # reverse=True for bids (descending), False for asks (ascending)
        if reverse:
            idx = bisect.bisect_left([-p for p in price_levels], -price)
        else:
            idx = bisect.bisect_left(price_levels, price)
        price_levels.insert(idx, price)

    # ------------------------------------------------------------------ #
    # Market data helpers
    def best_bid(self) -> Optional[Tuple[float, float]]:
        if not self.bid_prices:
            return None
        price = self.bid_prices[0]
        qty = sum(order.remaining for order in self.bids[price] if order.is_active)
        return (price, qty)

    def best_ask(self) -> Optional[Tuple[float, float]]:
        if not self.ask_prices:
            return None
        price = self.ask_prices[0]
        qty = sum(order.remaining for order in self.asks[price] if order.is_active)
        return (price, qty)


class MatchingEngine:
    """
    Basic matching engine that supports limit and market orders.
    Market orders cross the book immediately; limit orders rest if not fully matched.
    """

    def __init__(self) -> None:
        self.order_book = OrderBook()
        self.orders: Dict[str, Order] = {}
        self.trades: List[Trade] = []

    def submit_order(self, order: Order) -> List[Trade]:
        self.orders[order.order_id] = order
        trades = self._match(order)
        if order.is_active and order.order_type == OrderType.LIMIT:
            self.order_book.add_limit_order(order)
        if not order.is_active and order.remaining == 0:
            order.status = OrderStatus.FILLED
        elif order.remaining < order.quantity:
            order.status = OrderStatus.PARTIAL
        return trades

    def _match(self, incoming: Order) -> List[Trade]:
        trades: List[Trade] = []
        opposite_side = OrderSide.SELL if incoming.side == OrderSide.BUY else OrderSide.BUY

        while incoming.remaining > 0:
            best = self.order_book.pop_best(opposite_side)
            if best is None:
                break

            if incoming.order_type == OrderType.LIMIT and best.price is not None and incoming.price is not None:
                if incoming.side == OrderSide.BUY and incoming.price < best.price:
                    # Put the best order back and stop
                    self.order_book.add_limit_order(best)
                    break
                if incoming.side == OrderSide.SELL and incoming.price > best.price:
                    self.order_book.add_limit_order(best)
                    break

            trade_qty = min(incoming.remaining, best.remaining)
            trade_price = best.price if best.price is not None else incoming.price
            if trade_price is None:
                # If both are market orders, fall back to last price or skip
                trade_price = 0.0
            incoming.remaining -= trade_qty
            best.remaining -= trade_qty
            best.status = OrderStatus.PARTIAL if best.remaining > 0 else OrderStatus.FILLED

            trades.append(
                Trade(
                    buy_order_id=incoming.order_id if incoming.side == OrderSide.BUY else best.order_id,
                    sell_order_id=best.order_id if incoming.side == OrderSide.BUY else incoming.order_id,
                    price=trade_price,
                    quantity=trade_qty,
                )
            )

            if best.remaining > 0:
                # Put partially filled order back into book
                self.order_book.add_limit_order(best)
                break

        return trades

    def cancel_order(self, order_id: str) -> bool:
        order = self.orders.get(order_id)
        if order is None or not order.is_active:
            return False
        order.status = OrderStatus.CANCELLED
        order.remaining = 0
        return True

    def order_status(self, order_id: str) -> Optional[OrderStatus]:
        order = self.orders.get(order_id)
        return order.status if order else None


__all__ = [
    "Order",
    "OrderBook",
    "OrderSide",
    "OrderStatus",
    "OrderType",
    "Trade",
    "MatchingEngine",
]
