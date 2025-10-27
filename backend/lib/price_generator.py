"""
Price Generation Algorithm using Geometric Brownian Motion

This module implements realistic stock price generation for simulated trading.
Prices follow Geometric Brownian Motion with dynamic volatility and trend adjustments.
"""

import numpy as np
from typing import Dict, Tuple
from enum import Enum


class MarketState(Enum):
    """Market state enumeration"""
    BULL = "bull"           # Upward trend (positive drift)
    BEAR = "bear"           # Downward trend (negative drift)
    SIDEWAYS = "sideways"   # Range-bound (near-zero drift)


class PriceGenerator:
    """
    Generates realistic stock prices using Geometric Brownian Motion (GBM).

    The model: dS = μS dt + σS dW
    Where:
        S = stock price
        μ = drift (trend)
        σ = volatility
        dW = Wiener process (random walk)
    """

    # Market state transition probabilities (Markov chain)
    STATE_TRANSITION = {
        MarketState.BULL: {
            MarketState.BULL: 0.90,
            MarketState.SIDEWAYS: 0.08,
            MarketState.BEAR: 0.02,
        },
        MarketState.SIDEWAYS: {
            MarketState.BULL: 0.15,
            MarketState.SIDEWAYS: 0.70,
            MarketState.BEAR: 0.15,
        },
        MarketState.BEAR: {
            MarketState.BULL: 0.02,
            MarketState.SIDEWAYS: 0.08,
            MarketState.BEAR: 0.90,
        },
    }

    # Market state parameters
    STATE_PARAMS = {
        MarketState.BULL: {
            "trend": 0.15,          # 15% annual upward drift
            "volatility_mult": 1.0,
        },
        MarketState.BEAR: {
            "trend": -0.15,         # -15% annual downward drift
            "volatility_mult": 1.5, # Higher volatility in bear market
        },
        MarketState.SIDEWAYS: {
            "trend": 0.0,           # No drift
            "volatility_mult": 0.8, # Lower volatility
        },
    }

    def __init__(self, base_volatility: float = 0.02):
        """
        Initialize price generator.

        Args:
            base_volatility: Base annual volatility (default 0.02 = 2%)
        """
        self.base_volatility = base_volatility
        self.state_transition_timer = 0
        self.state_duration = 0

    def transition_market_state(
        self,
        current_state: MarketState,
        minutes_elapsed: int = 1
    ) -> MarketState:
        """
        Determine if market state should transition using Markov chain.

        Args:
            current_state: Current market state
            minutes_elapsed: Minutes since last transition check

        Returns:
            New market state (may be same as current)
        """
        self.state_transition_timer += minutes_elapsed

        # Check for state transition every 30-120 minutes (random)
        if self.state_duration == 0:
            self.state_duration = np.random.randint(30, 121)

        if self.state_transition_timer < self.state_duration:
            return current_state

        # Time to potentially transition
        self.state_transition_timer = 0
        self.state_duration = 0

        # Sample next state based on transition probabilities
        probabilities = self.STATE_TRANSITION[current_state]
        states = list(probabilities.keys())
        probs = list(probabilities.values())

        next_state = np.random.choice(states, p=probs)
        return next_state

    def generate_next_kline(
        self,
        current_price: float,
        market_state: MarketState = MarketState.SIDEWAYS,
        base_volume: int = 1000000,
        dt: float = 1 / 240  # 1 minute in trading day (240 minutes total)
    ) -> Dict[str, float]:
        """
        Generate next 1-minute K-line using Geometric Brownian Motion.

        Args:
            current_price: Current stock price (close of previous bar)
            market_state: Current market state (bull/bear/sideways)
            base_volume: Base trading volume
            dt: Time step (1/240 for 1 minute in 4-hour trading day)

        Returns:
            Dictionary with OHLCV data:
                - open: Opening price
                - high: Highest price
                - low: Lowest price
                - close: Closing price
                - volume: Trading volume
        """
        # Get state parameters
        params = self.STATE_PARAMS[market_state]
        trend = params["trend"]
        volatility = self.base_volatility * params["volatility_mult"]

        # Open price is previous close
        open_price = current_price

        # Generate close price using GBM
        drift = trend * dt
        shock = volatility * np.sqrt(dt) * np.random.normal(0, 1)
        close_price = current_price * (1 + drift + shock)

        # Ensure price doesn't go negative
        close_price = max(close_price, current_price * 0.5)

        # Generate intraday volatility for high/low
        intraday_volatility = volatility * np.sqrt(dt)

        # High and low prices (realistic spread)
        # Use half-normal distribution for spread from open/close
        high_spread = abs(np.random.normal(0, intraday_volatility * current_price * 0.5))
        low_spread = abs(np.random.normal(0, intraday_volatility * current_price * 0.5))

        high_price = max(open_price, close_price) + high_spread
        low_price = min(open_price, close_price) - low_spread

        # Ensure OHLC constraints
        high_price = max(high_price, open_price, close_price)
        low_price = min(low_price, open_price, close_price)
        low_price = max(low_price, 0.01)  # Prevent negative prices

        # Generate volume correlated with price movement
        price_change_pct = abs((close_price - open_price) / open_price)

        # Volume increases with larger price movements
        # Base volume + volume spike based on price change
        volume_multiplier = 1.0 + (price_change_pct * 10)  # 1% move = 10% more volume

        # Add random noise to volume
        volume_noise = np.random.uniform(0.7, 1.3)

        volume = int(base_volume * volume_multiplier * volume_noise)
        volume = max(volume, int(base_volume * 0.3))  # Minimum 30% of base volume

        return {
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(close_price, 2),
            "volume": volume,
        }

    def generate_kline_sequence(
        self,
        initial_price: float,
        num_bars: int,
        initial_state: MarketState = MarketState.SIDEWAYS,
        base_volume: int = 1000000,
    ) -> Tuple[list, MarketState]:
        """
        Generate a sequence of K-lines with state transitions.

        Args:
            initial_price: Starting price
            num_bars: Number of bars to generate
            initial_state: Starting market state
            base_volume: Base trading volume

        Returns:
            Tuple of (list of OHLCV dicts, final market state)
        """
        klines = []
        current_price = initial_price
        current_state = initial_state

        for i in range(num_bars):
            # Check for state transition
            current_state = self.transition_market_state(current_state, minutes_elapsed=1)

            # Generate next bar
            kline = self.generate_next_kline(
                current_price=current_price,
                market_state=current_state,
                base_volume=base_volume,
            )

            klines.append(kline)
            current_price = kline["close"]

        return klines, current_state


def generate_historical_data(
    symbol: str,
    start_price: float,
    num_days: int = 30,
    base_volatility: float = 0.02,
    base_volume: int = 1000000,
) -> list:
    """
    Generate historical K-line data for initialization.

    Args:
        symbol: Stock symbol
        start_price: Starting price
        num_days: Number of trading days to generate
        base_volatility: Base volatility
        base_volume: Base volume

    Returns:
        List of K-line data dictionaries with timestamps
    """
    generator = PriceGenerator(base_volatility=base_volatility)

    # Each trading day has 240 minutes (4 hours: 9:30-11:30, 13:00-15:00)
    bars_per_day = 240
    total_bars = num_days * bars_per_day

    # Generate sequence
    klines, _ = generator.generate_kline_sequence(
        initial_price=start_price,
        num_bars=total_bars,
        base_volume=base_volume,
    )

    # Add timestamps (working backwards from current time)
    # This is a simplified version - actual implementation should skip weekends
    import time
    current_time = int(time.time())
    minute_seconds = 60

    result = []
    for i, kline in enumerate(reversed(klines)):
        timestamp = current_time - (i * minute_seconds)
        result.append({
            "symbol": symbol,
            "interval": "1m",
            "time": timestamp,
            **kline,
        })

    # Return in chronological order
    return list(reversed(result))


if __name__ == "__main__":
    # Test the price generator
    generator = PriceGenerator(base_volatility=0.025)

    print("Testing Price Generator")
    print("=" * 60)

    # Generate 10 bars in different market states
    states = [MarketState.BULL, MarketState.SIDEWAYS, MarketState.BEAR]

    for state in states:
        print(f"\n{state.value.upper()} Market:")
        print("-" * 60)

        current_price = 100.0
        for i in range(10):
            kline = generator.generate_next_kline(
                current_price=current_price,
                market_state=state,
                base_volume=1000000,
            )

            change = ((kline["close"] - kline["open"]) / kline["open"]) * 100
            print(
                f"Bar {i+1}: O={kline['open']:7.2f} H={kline['high']:7.2f} "
                f"L={kline['low']:7.2f} C={kline['close']:7.2f} "
                f"V={kline['volume']:>10,} Change={change:+.2f}%"
            )

            current_price = kline["close"]

    print("\n" + "=" * 60)
    print("Testing state transitions...")

    # Test state transitions
    klines, final_state = generator.generate_kline_sequence(
        initial_price=150.0,
        num_bars=100,
        initial_state=MarketState.SIDEWAYS,
    )

    print(f"Generated {len(klines)} bars")
    print(f"Final state: {final_state.value}")
    print(f"Price range: ${klines[0]['open']:.2f} -> ${klines[-1]['close']:.2f}")

    price_change = ((klines[-1]['close'] - klines[0]['open']) / klines[0]['open']) * 100
    print(f"Total change: {price_change:+.2f}%")
