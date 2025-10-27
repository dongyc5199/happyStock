"""
Data Aggregation Module

Aggregates 1-minute K-line data into larger timeframes:
- 5m, 15m, 30m, 60m (1h), 120m (2h)
- 1d (daily), 1w (weekly), 1M (monthly)

Runs periodically to update aggregated data.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy import and_, func

from .db_models import get_db_manager, DatabaseManager, MarketKline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataAggregator:
    """
    Aggregates 1-minute K-line data into larger intervals.

    Uses database queries to efficiently aggregate OHLCV data.
    """

    # Interval definitions (in minutes)
    INTERVALS = {
        "5m": 5,
        "15m": 15,
        "30m": 30,
        "60m": 60,
        "120m": 120,
        "1d": 1440,  # 240 minutes/day * 6 trading days (approximate)
        "1w": 7200,  # Approximate
        "1M": 30000,  # Approximate
    }

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        Initialize data aggregator.

        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager or get_db_manager()
        logger.info("DataAggregator initialized")

    def aggregate_klines(
        self,
        symbol: str,
        source_interval: str = "1m",
        target_interval: str = "5m",
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> List[Dict]:
        """
        Aggregate K-line data from source interval to target interval.

        Args:
            symbol: Stock symbol
            source_interval: Source interval (e.g., "1m")
            target_interval: Target interval (e.g., "5m", "15m", etc.)
            start_time: Start timestamp (seconds), None = all available
            end_time: End timestamp (seconds), None = now

        Returns:
            List of aggregated K-line dictionaries
        """
        if target_interval not in self.INTERVALS:
            raise ValueError(f"Invalid target interval: {target_interval}")

        interval_minutes = self.INTERVALS[target_interval]

        # Query source data
        with self.db.get_session() as session:
            query = session.query(MarketKline).filter(
                and_(
                    MarketKline.symbol == symbol,
                    MarketKline.interval == source_interval,
                )
            )

            # Apply time filters
            if start_time:
                query = query.filter(MarketKline.time >= start_time)
            if end_time:
                query = query.filter(MarketKline.time <= end_time)

            # Order by time
            query = query.order_by(MarketKline.time)

            source_klines = query.all()

        if not source_klines:
            logger.warning(
                f"No source data found for {symbol} {source_interval} "
                f"(start={start_time}, end={end_time})"
            )
            return []

        # Group and aggregate
        aggregated = self._aggregate_klines_list(
            klines=[k.to_dict() for k in source_klines],
            interval_minutes=interval_minutes,
        )

        logger.info(
            f"Aggregated {len(source_klines)} {source_interval} bars "
            f"into {len(aggregated)} {target_interval} bars for {symbol}"
        )

        return aggregated

    def _aggregate_klines_list(
        self,
        klines: List[Dict],
        interval_minutes: int,
    ) -> List[Dict]:
        """
        Aggregate a list of K-lines into larger intervals.

        Args:
            klines: List of K-line dictionaries (sorted by time)
            interval_minutes: Target interval in minutes

        Returns:
            List of aggregated K-line dictionaries
        """
        if not klines:
            return []

        aggregated = []
        current_group = []
        group_start_time = None

        interval_seconds = interval_minutes * 60

        for kline in klines:
            timestamp = kline["time"]

            # Determine group start time (floor to interval boundary)
            # For simplicity, use simple division
            period_start = (timestamp // interval_seconds) * interval_seconds

            if group_start_time is None:
                group_start_time = period_start

            # Check if this kline belongs to current group
            if period_start == group_start_time:
                current_group.append(kline)
            else:
                # Finalize current group
                if current_group:
                    agg_kline = self._aggregate_group(
                        group=current_group,
                        timestamp=group_start_time,
                    )
                    aggregated.append(agg_kline)

                # Start new group
                current_group = [kline]
                group_start_time = period_start

        # Finalize last group
        if current_group:
            agg_kline = self._aggregate_group(
                group=current_group,
                timestamp=group_start_time,
            )
            aggregated.append(agg_kline)

        return aggregated

    def _aggregate_group(self, group: List[Dict], timestamp: int) -> Dict:
        """
        Aggregate a group of K-lines into a single K-line.

        Args:
            group: List of K-line dictionaries
            timestamp: Timestamp for aggregated bar

        Returns:
            Aggregated K-line dictionary
        """
        if not group:
            raise ValueError("Cannot aggregate empty group")

        # OHLC aggregation rules:
        # - Open: first bar's open
        # - High: max of all highs
        # - Low: min of all lows
        # - Close: last bar's close
        # - Volume: sum of all volumes

        return {
            "symbol": group[0]["symbol"],
            "interval": group[0]["interval"],  # Will be updated by caller
            "time": timestamp,
            "open": group[0]["open"],
            "high": max(k["high"] for k in group),
            "low": min(k["low"] for k in group),
            "close": group[-1]["close"],
            "volume": sum(k["volume"] for k in group),
        }

    def aggregate_all_intervals(
        self,
        symbol: str,
        lookback_hours: int = 24,
    ):
        """
        Aggregate all target intervals for a symbol.

        Args:
            symbol: Stock symbol
            lookback_hours: How many hours to look back for aggregation
        """
        end_time = int(datetime.now().timestamp())
        start_time = end_time - (lookback_hours * 3600)

        results = {}

        for target_interval in ["5m", "15m", "30m", "60m", "120m"]:
            try:
                aggregated = self.aggregate_klines(
                    symbol=symbol,
                    source_interval="1m",
                    target_interval=target_interval,
                    start_time=start_time,
                    end_time=end_time,
                )

                # Update interval field
                for kline in aggregated:
                    kline["interval"] = target_interval

                # Save to database
                if aggregated:
                    self.db.bulk_insert_klines(aggregated)
                    results[target_interval] = len(aggregated)
                else:
                    results[target_interval] = 0

            except Exception as e:
                logger.error(
                    f"Error aggregating {symbol} to {target_interval}: {e}",
                    exc_info=True,
                )
                results[target_interval] = 0

        logger.info(f"Aggregation results for {symbol}: {results}")
        return results

    def aggregate_all_stocks(
        self,
        lookback_hours: int = 24,
    ):
        """
        Aggregate all intervals for all active stocks.

        Args:
            lookback_hours: How many hours to look back
        """
        stocks = self.db.get_active_stocks()
        logger.info(f"Starting aggregation for {len(stocks)} stocks...")

        for stock in stocks:
            logger.info(f"Aggregating {stock.symbol}...")
            try:
                self.aggregate_all_intervals(
                    symbol=stock.symbol,
                    lookback_hours=lookback_hours,
                )
            except Exception as e:
                logger.error(
                    f"Error aggregating {stock.symbol}: {e}",
                    exc_info=True,
                )

        logger.info("Aggregation completed for all stocks")


def run_aggregation_daemon(interval_minutes: int = 5):
    """
    Run data aggregation as a daemon process.

    Args:
        interval_minutes: How often to run aggregation (in minutes)
    """
    import time

    logger.info(f"Starting aggregation daemon (interval={interval_minutes}m)")

    aggregator = DataAggregator()

    while True:
        try:
            logger.info("Running aggregation...")
            aggregator.aggregate_all_stocks(lookback_hours=24)
            logger.info(f"Aggregation complete, sleeping {interval_minutes}m...")

            time.sleep(interval_minutes * 60)

        except KeyboardInterrupt:
            logger.info("Aggregation daemon stopped by user")
            break

        except Exception as e:
            logger.error(f"Error in aggregation daemon: {e}", exc_info=True)
            time.sleep(60)  # Sleep 1 minute on error


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Data Aggregation Daemon")
    parser.add_argument(
        "--symbol",
        type=str,
        help="Aggregate single symbol only",
    )
    parser.add_argument(
        "--interval",
        type=str,
        default="5m",
        help="Target interval (5m, 15m, 30m, 60m, 120m)",
    )
    parser.add_argument(
        "--lookback",
        type=int,
        default=24,
        help="Lookback hours",
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon (continuous aggregation)",
    )
    parser.add_argument(
        "--daemon-interval",
        type=int,
        default=5,
        help="Daemon run interval in minutes",
    )

    args = parser.parse_args()

    aggregator = DataAggregator()

    if args.daemon:
        # Run as daemon
        run_aggregation_daemon(interval_minutes=args.daemon_interval)
    elif args.symbol:
        # Aggregate single symbol
        if args.interval == "all":
            aggregator.aggregate_all_intervals(
                symbol=args.symbol,
                lookback_hours=args.lookback,
            )
        else:
            result = aggregator.aggregate_klines(
                symbol=args.symbol,
                source_interval="1m",
                target_interval=args.interval,
                start_time=None,
                end_time=None,
            )
            print(f"Aggregated {len(result)} bars")
    else:
        # Aggregate all stocks
        aggregator.aggregate_all_stocks(lookback_hours=args.lookback)
