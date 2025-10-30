#!/usr/bin/env python3
"""
Historical Data Initialization Script

Generates historical K-line data for all active stocks.
This populates the database with initial data for chart display.

Usage:
    python init_historical_data.py --days 30
    python init_historical_data.py --days 90 --symbol AAPL
"""

import sys
import os
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.price_generator import PriceGenerator, MarketState
from lib.db_models import get_db_manager, init_db_manager, StockMetadata
from lib.data_aggregator import DataAggregator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class HistoricalDataGenerator:
    """
    Generates historical K-line data for initialization.

    Creates realistic historical data that appears to have been
    generated over multiple trading days.
    """

    # Trading session times (Beijing time)
    MORNING_START = 9 * 60 + 30  # 9:30 in minutes from midnight
    MORNING_END = 11 * 60 + 30  # 11:30
    AFTERNOON_START = 13 * 60  # 13:00
    AFTERNOON_END = 15 * 60  # 15:00

    # Minutes per trading day
    MINUTES_PER_DAY = 240  # 120 (morning) + 120 (afternoon)

    def __init__(self, db_manager=None):
        """Initialize historical data generator"""
        self.db = db_manager or get_db_manager()
        self.generators: Dict[str, PriceGenerator] = {}

    def generate_trading_timestamps(
        self,
        start_date: datetime,
        num_days: int,
    ) -> List[int]:
        """
        Generate timestamps for trading minutes, skipping weekends.

        Args:
            start_date: Starting date
            num_days: Number of trading days

        Returns:
            List of Unix timestamps (seconds) for each trading minute
        """
        timestamps = []
        current_date = start_date
        days_generated = 0

        while days_generated < num_days:
            # Skip weekends (Saturday=5, Sunday=6)
            if current_date.weekday() < 5:
                # Generate morning session (9:30 - 11:30)
                morning_start = current_date.replace(hour=9, minute=30, second=0)
                for minute in range(120):  # 120 minutes
                    ts = morning_start + timedelta(minutes=minute)
                    timestamps.append(int(ts.timestamp()))

                # Generate afternoon session (13:00 - 15:00)
                afternoon_start = current_date.replace(hour=13, minute=0, second=0)
                for minute in range(120):  # 120 minutes
                    ts = afternoon_start + timedelta(minutes=minute)
                    timestamps.append(int(ts.timestamp()))

                days_generated += 1

            # Move to next day
            current_date += timedelta(days=1)

        return timestamps

    def generate_stock_history(
        self,
        stock: StockMetadata,
        timestamps: List[int],
    ) -> List[Dict]:
        """
        Generate historical K-line data for a stock.

        Args:
            stock: Stock metadata
            timestamps: List of timestamps to generate data for

        Returns:
            List of K-line dictionaries
        """
        symbol = stock.symbol
        base_price = float(stock.base_price)
        base_volatility = float(stock.base_volatility)

        # Initialize generator for this stock
        if symbol not in self.generators:
            self.generators[symbol] = PriceGenerator(base_volatility=base_volatility)

        generator = self.generators[symbol]

        # Generate sequence
        klines, final_state = generator.generate_kline_sequence(
            initial_price=base_price,
            num_bars=len(timestamps),
            base_volume=1000000,  # Base volume
        )

        # Attach timestamps
        historical_data = []
        for i, kline in enumerate(klines):
            historical_data.append(
                {
                    "symbol": symbol,
                    "interval": "1m",
                    "time": timestamps[i],
                    "open": kline["open"],
                    "high": kline["high"],
                    "low": kline["low"],
                    "close": kline["close"],
                    "volume": kline["volume"],
                }
            )

        logger.info(
            f"{symbol}: Generated {len(historical_data)} bars, "
            f"final price: ${klines[-1]['close']:.2f}, "
            f"final state: {final_state.value}"
        )

        return historical_data

    def initialize_all_stocks(
        self,
        num_days: int = 30,
        target_symbol: str = None,
    ):
        """
        Initialize historical data for all active stocks.

        Args:
            num_days: Number of trading days to generate
            target_symbol: If set, only generate for this symbol
        """
        logger.info(f"Initializing {num_days} days of historical data...")

        # Get active stocks
        stocks = self.db.get_active_stocks()
        if target_symbol:
            stocks = [s for s in stocks if s.symbol == target_symbol]

        if not stocks:
            logger.error("No active stocks found!")
            return

        logger.info(f"Found {len(stocks)} stocks to initialize")

        # Generate timestamps (working backwards from now)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=num_days * 2)  # Account for weekends

        timestamps = self.generate_trading_timestamps(
            start_date=start_date,
            num_days=num_days,
        )

        logger.info(
            f"Generated {len(timestamps)} timestamps "
            f"({num_days} trading days, {len(timestamps) / 240:.1f} actual days)"
        )

        # Generate data for each stock
        total_bars = 0
        for stock in stocks:
            logger.info(f"Generating history for {stock.symbol} ({stock.name})...")

            try:
                historical_data = self.generate_stock_history(
                    stock=stock,
                    timestamps=timestamps,
                )

                # Insert into database in batches
                batch_size = 1000
                for i in range(0, len(historical_data), batch_size):
                    batch = historical_data[i : i + batch_size]
                    self.db.bulk_insert_klines(batch)

                total_bars += len(historical_data)

                # Update stock state with final price
                last_kline = historical_data[-1]
                self.db.update_stock_state(
                    symbol=stock.symbol,
                    current_price=last_kline["close"],
                    volatility=stock.base_volatility,
                    trend=0.0,
                    market_state="sideways",
                    timestamp=last_kline["time"],
                )

                logger.info(f"{stock.symbol}: ✓ {len(historical_data)} bars inserted")

            except Exception as e:
                logger.error(f"Error generating {stock.symbol}: {e}", exc_info=True)

        logger.info(f"Historical data initialization complete! Total bars: {total_bars}")

        # Run aggregation
        logger.info("Running data aggregation...")
        aggregator = DataAggregator(db_manager=self.db)

        for stock in stocks:
            try:
                results = aggregator.aggregate_all_intervals(
                    symbol=stock.symbol,
                    lookback_hours=num_days * 24,
                )
                logger.info(f"{stock.symbol}: Aggregation complete - {results}")
            except Exception as e:
                logger.error(f"Error aggregating {stock.symbol}: {e}", exc_info=True)

        logger.info("All done! 🎉")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Initialize historical K-line data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 30 days of history for all stocks
  python init_historical_data.py --days 30

  # Generate 90 days for a specific stock
  python init_historical_data.py --days 90 --symbol AAPL

  # Use custom database
  python init_historical_data.py --days 30 --db-url postgresql://user:pass@host/db
        """,
    )

    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of trading days to generate (default: 30)",
    )
    parser.add_argument(
        "--symbol",
        type=str,
        help="Generate for specific symbol only",
    )
    parser.add_argument(
        "--db-url",
        type=str,
        help="Database URL (overrides environment)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing data before initialization (DANGEROUS!)",
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
    db_kwargs = {}
    if args.db_url:
        db_kwargs["db_url"] = args.db_url

    db = init_db_manager(**db_kwargs)

    # Create tables if needed
    logger.info("Verifying database tables...")
    db.create_tables()

    # Clear existing data if requested
    if args.clear:
        logger.warning("Clearing existing K-line data...")
        response = input("Are you sure? This will delete all K-line data! (yes/no): ")
        if response.lower() == "yes":
            with db.get_session() as session:
                from lib.db_models import MarketKline, StockState

                session.query(MarketKline).delete()
                session.query(StockState).delete()
                session.commit()
            logger.info("Data cleared!")
        else:
            logger.info("Clear operation cancelled")
            return

    # Run initialization
    generator = HistoricalDataGenerator(db_manager=db)

    try:
        generator.initialize_all_stocks(
            num_days=args.days,
            target_symbol=args.symbol,
        )
    except Exception as e:
        logger.error(f"Initialization failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
