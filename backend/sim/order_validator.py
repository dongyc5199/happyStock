"""
Order validation and error handling for user orders (T053-T056).

Feature: 001-ai-user-order-matching, Phase 4, US1
"""
from typing import Optional
from fastapi import HTTPException, status


class OrderValidationError(Exception):
    """Base exception for order validation errors."""
    pass


class InsufficientFundsError(OrderValidationError):
    """Raised when user has insufficient balance for order (T053)."""
    pass


class PriceOutOfRangeError(OrderValidationError):
    """Raised when order price is outside acceptable range (T054)."""
    pass


class OrderValidator:
    """Validates user orders before submission."""

    def __init__(
        self,
        *,
        min_price: float = 0.01,
        max_price: float = 10_000.0,
        price_deviation_pct: float = 10.0,  # Max % deviation from current price
    ):
        self.min_price = min_price
        self.max_price = max_price
        self.price_deviation_pct = price_deviation_pct

    def validate_price_range(
        self,
        price: Optional[float],
        current_price: Optional[float] = None,
    ) -> None:
        """
        Validate order price is within acceptable range (T054).

        Args:
            price: Order price to validate
            current_price: Current market price for deviation check

        Raises:
            HTTPException: 400 if price is out of range
        """
        if price is None:
            return  # Market orders have no price

        # Absolute bounds check
        if price < self.min_price or price > self.max_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Price must be between {self.min_price} and {self.max_price}",
            )

        # Deviation check if current price is available
        if current_price and current_price > 0:
            deviation_pct = abs(price - current_price) / current_price * 100
            if deviation_pct > self.price_deviation_pct:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Price deviates {deviation_pct:.1f}% from current price "
                        f"({current_price:.2f}). Maximum allowed deviation is "
                        f"{self.price_deviation_pct}%"
                    ),
                )

    def validate_balance(
        self,
        user_balance: float,
        order_cost: float,
    ) -> None:
        """
        Validate user has sufficient balance for order (T053).

        Args:
            user_balance: User's available balance
            order_cost: Total cost of order (price * quantity)

        Raises:
            HTTPException: 400 if insufficient funds
        """
        if user_balance < order_cost:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Insufficient funds. Required: {order_cost:.2f}, "
                    f"Available: {user_balance:.2f}"
                ),
            )

    def calculate_order_cost(
        self,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float],
        current_price: Optional[float] = None,
    ) -> float:
        """
        Calculate estimated cost of an order.

        For BUY orders: cost = price * quantity
        For SELL orders: cost = 0 (selling existing holdings)

        Args:
            side: "BUY" or "SELL"
            order_type: "LIMIT" or "MARKET"
            quantity: Order quantity
            price: Limit price (for LIMIT orders)
            current_price: Current market price (for MARKET orders)

        Returns:
            Estimated cost in currency units
        """
        if side == "SELL":
            return 0.0  # Selling doesn't require balance

        # For BUY orders
        if order_type == "LIMIT":
            return price * quantity if price else 0.0
        else:
            # MARKET orders: estimate using current price with buffer
            if current_price and current_price > 0:
                # Add 5% buffer for slippage
                return current_price * quantity * 1.05
            else:
                # No current price available, use a conservative estimate
                return quantity * 100.0  # Assume price of 100


class RateLimiter:
    """Simple in-memory rate limiter for order submissions (T056)."""

    def __init__(
        self,
        max_orders_per_minute: int = 10,
        max_orders_per_hour: int = 100,
    ):
        self.max_orders_per_minute = max_orders_per_minute
        self.max_orders_per_hour = max_orders_per_hour
        self._user_submissions: dict[int, list[float]] = {}  # user_id -> [timestamps]

    def check_rate_limit(self, user_id: int) -> None:
        """
        Check if user has exceeded rate limits (T056).

        Args:
            user_id: User identifier

        Raises:
            HTTPException: 429 if rate limit exceeded
        """
        import time

        now = time.time()
        one_minute_ago = now - 60
        one_hour_ago = now - 3600

        # Get user's submission history
        if user_id not in self._user_submissions:
            self._user_submissions[user_id] = []

        submissions = self._user_submissions[user_id]

        # Clean old entries
        submissions = [ts for ts in submissions if ts > one_hour_ago]
        self._user_submissions[user_id] = submissions

        # Check minute limit
        recent_minute = [ts for ts in submissions if ts > one_minute_ago]
        if len(recent_minute) >= self.max_orders_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Rate limit exceeded: {self.max_orders_per_minute} orders "
                    f"per minute. Try again in {60 - (now - recent_minute[0]):.0f} seconds."
                ),
            )

        # Check hour limit
        if len(submissions) >= self.max_orders_per_hour:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Rate limit exceeded: {self.max_orders_per_hour} orders "
                    f"per hour. Try again later."
                ),
            )

        # Record this submission
        submissions.append(now)

    def reset_user(self, user_id: int) -> None:
        """Reset rate limit counter for a user."""
        self._user_submissions.pop(user_id, None)


# Global instances (in production, use Redis-based rate limiting)
order_validator = OrderValidator()
rate_limiter = RateLimiter()
