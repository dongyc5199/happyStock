"""
Market Data Generator Daemon

Continuously generates realistic stock market data during trading hours.
Runs as a background service and updates data every minute.

Trading Hours (Beijing Time):
- Morning: 9:30 - 11:30
- Afternoon: 13:00 - 15:00
- Closed: Weekends and outside trading hours
"""

import time
import logging
from datetime import datetime, time as dt_time
from typing import List, Dict, Optional
from enum import Enum
import signal
import sys

from .price_generator import PriceGenerator, MarketState
from .db_models import (
    get_db_manager,
    DatabaseManager,
    StockState,
    StockMetadata,
    MarketStatus,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class TradingSession(Enum):
    """Trading session types"""

    MORNING = "morning"  # 9:30 - 11:30
    AFTERNOON = "afternoon"  # 13:00 - 15:00
    CLOSED = "closed"


class MarketDataGenerator:
    """
    Main daemon class for generating market data.

    Responsibilities:
    - Monitor trading hours (Beijing time)
    - Generate 1-minute K-line data for all active stocks
    - Update stock states (price, volatility, market state)
    - Trigger data aggregation for other intervals
    """

    # Trading hours definition (Beijing time)
    MORNING_START = dt_time(9, 30)
    MORNING_END = dt_time(11, 30)
    AFTERNOON_START = dt_time(13, 0)
    AFTERNOON_END = dt_time(15, 0)

    # Update interval (60 seconds = 1 minute)
    UPDATE_INTERVAL = 60

    def __init__(
        self,
        db_manager: Optional[DatabaseManager] = None,
        test_mode: bool = False,
    ):
        """
        Initialize market data generator.

        Args:
            db_manager: Database manager instance (uses default if None)
            test_mode: If True, runs continuously without time checks
        """
        self.db = db_manager or get_db_manager()
        self.test_mode = test_mode
        self.running = False
        self.stocks: List[StockMetadata] = []
        self.stock_states: Dict[str, dict] = {}
        self.generators: Dict[str, PriceGenerator] = {}

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info("MarketDataGenerator initialized")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)

    def is_trading_time(self) -> tuple[bool, TradingSession]:
        """
        Check if current time is within trading hours.

        Returns:
            Tuple of (is_trading, current_session)
        """
        if self.test_mode:
            return True, TradingSession.MORNING

        now = datetime.now()

        # Check if weekend
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False, TradingSession.CLOSED

        current_time = now.time()

        # Check morning session
        if self.MORNING_START <= current_time <= self.MORNING_END:
            return True, TradingSession.MORNING

        # Check afternoon session
        if self.AFTERNOON_START <= current_time <= self.AFTERNOON_END:
            return True, TradingSession.AFTERNOON

        return False, TradingSession.CLOSED

    def load_stocks(self):
        """Load active stocks from database"""
        self.stocks = self.db.get_active_stocks()
        logger.info(f"Loaded {len(self.stocks)} active stocks")

        # Initialize price generators
        for stock in self.stocks:
            self.generators[stock.symbol] = PriceGenerator(
                base_volatility=float(stock.base_volatility)
            )
            logger.debug(f"Initialized generator for {stock.symbol}")

    def load_stock_states(self):
        """Load current states for all stocks"""
        for stock in self.stocks:
            state = self.db.get_stock_state(stock.symbol)

            if state:
                # Load existing state
                self.stock_states[stock.symbol] = {
                    "current_price": float(state.current_price),
                    "volatility": float(state.volatility),
                    "trend": float(state.trend),
                    "market_state": MarketState(state.market_state),
                    "last_update": state.last_update,
                }
                logger.debug(f"Loaded state for {stock.symbol}: ${state.current_price:.2f}")
            else:
                # Initialize new state with base price
                market_state = MarketState.SIDEWAYS
                self.stock_states[stock.symbol] = {
                    "current_price": float(stock.base_price),
                    "volatility": float(stock.base_volatility),
                    "trend": 0.0,
                    "market_state": market_state,
                    "last_update": int(time.time()),
                }

                # Save to database
                self.db.update_stock_state(
                    symbol=stock.symbol,
                    current_price=float(stock.base_price),
                    volatility=float(stock.base_volatility),
                    trend=0.0,
                    market_state=market_state.value,
                    timestamp=int(time.time()),
                )
                logger.info(f"Initialized new state for {stock.symbol}: ${stock.base_price:.2f}")

    def generate_minute_data(self):
        """
        Generate 1-minute K-line data for all stocks.

        This is called every minute during trading hours.
        """
        timestamp = int(time.time())
        klines_to_insert = []

        for stock in self.stocks:
            symbol = stock.symbol
            state = self.stock_states[symbol]
            generator = self.generators[symbol]

            # Check for market state transition
            new_state = generator.transition_market_state(
                current_state=state["market_state"],
                minutes_elapsed=1,
            )

            if new_state != state["market_state"]:
                logger.info(
                    f"{symbol}: Market state changed from "
                    f"{state['market_state'].value} to {new_state.value}"
                )
                state["market_state"] = new_state

            # Generate next K-line
            kline = generator.generate_next_kline(
                current_price=state["current_price"],
                market_state=state["market_state"],
                base_volume=1000000,  # Base volume, can be customized per stock
            )

            # Update current price
            state["current_price"] = kline["close"]
            state["last_update"] = timestamp

            # Prepare for batch insert
            klines_to_insert.append(
                {
                    "symbol": symbol,
                    "interval": "1m",
                    "time": timestamp,
                    "open": kline["open"],
                    "high": kline["high"],
                    "low": kline["low"],
                    "close": kline["close"],
                    "volume": kline["volume"],
                }
            )

            # Log price update
            change = ((kline["close"] - kline["open"]) / kline["open"]) * 100
            logger.debug(
                f"{symbol}: O={kline['open']:.2f} H={kline['high']:.2f} "
                f"L={kline['low']:.2f} C={kline['close']:.2f} "
                f"V={kline['volume']:,} ({change:+.2f}%)"
            )

        # Batch insert all K-lines
        if klines_to_insert:
            self.db.bulk_insert_klines(klines_to_insert)
            logger.info(f"Generated and saved {len(klines_to_insert)} K-lines at {timestamp}")

        # Update stock states in database
        for stock in self.stocks:
            symbol = stock.symbol
            state = self.stock_states[symbol]

            self.db.update_stock_state(
                symbol=symbol,
                current_price=state["current_price"],
                volatility=state["volatility"],
                trend=state["trend"],
                market_state=state["market_state"].value,
                timestamp=timestamp,
            )

    def update_market_status(self, is_trading: bool, session: TradingSession):
        """Update global market status"""
        with self.db.get_session() as db_session:
            status = db_session.query(MarketStatus).first()

            if status:
                status.is_trading = is_trading
                status.current_session = session.value
                status.last_update = datetime.now()
            else:
                status = MarketStatus(
                    is_trading=is_trading,
                    current_session=session.value,
                )
                db_session.add(status)

            db_session.commit()

    def run(self):
        """
        Main daemon loop.

        Checks trading hours every minute and generates data when market is open.
        """
        self.running = True
        logger.info("MarketDataGenerator started")

        # Load stocks and states
        self.load_stocks()
        self.load_stock_states()

        if not self.stocks:
            logger.error("No active stocks found! Exiting...")
            return

        last_trading_state = False

        while self.running:
            try:
                # Check if we're in trading hours
                is_trading, session = self.is_trading_time()

                # Log trading status changes
                if is_trading != last_trading_state:
                    if is_trading:
                        logger.info(
                            f"Market OPENED - {session.value} session "
                            f"({datetime.now().strftime('%H:%M:%S')})"
                        )
                    else:
                        logger.info(
                            f"Market CLOSED ({datetime.now().strftime('%H:%M:%S')})"
                        )

                    last_trading_state = is_trading

                # Update market status
                self.update_market_status(is_trading, session)

                # Generate data if market is open
                if is_trading:
                    self.generate_minute_data()
                else:
                    logger.debug("Market closed, skipping data generation")

                # Sleep until next minute
                # Calculate seconds until next minute boundary
                now = datetime.now()
                seconds_until_next_minute = 60 - now.second

                if not self.test_mode:
                    time.sleep(seconds_until_next_minute)
                else:
                    # In test mode, sleep shorter interval
                    time.sleep(5)

            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt, shutting down...")
                self.stop()
                break

            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                # Sleep and continue
                time.sleep(10)

        logger.info("MarketDataGenerator stopped")

    def stop(self):
        """Stop the daemon gracefully"""
        self.running = False
        logger.info("Stopping MarketDataGenerator...")


def main():
    """Main entry point for daemon"""
    import argparse

    parser = argparse.ArgumentParser(description="Market Data Generator Daemon")
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run in test mode (continuous generation, no time checks)",
    )
    parser.add_argument(
        "--db-url",
        type=str,
        help="Database URL (overrides environment)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize database
    from .db_models import init_db_manager

    db_kwargs = {}
    if args.db_url:
        db_kwargs["db_url"] = args.db_url

    db = init_db_manager(**db_kwargs)

    # Create tables if needed
    db.create_tables()

    # Create and run generator
    generator = MarketDataGenerator(db_manager=db, test_mode=args.test)

    try:
        generator.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
