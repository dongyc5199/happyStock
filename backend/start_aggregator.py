#!/usr/bin/env python3
"""
Data Aggregator Startup Script

Starts the data aggregation daemon.
Aggregates 1m data into larger intervals (5m, 15m, 30m, etc.).
"""

import sys
import os
import logging

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.data_aggregator import run_aggregation_daemon

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Data Aggregation Daemon")
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Aggregation run interval in minutes (default: 5)",
    )

    args = parser.parse_args()

    try:
        run_aggregation_daemon(interval_minutes=args.interval)
    except KeyboardInterrupt:
        logging.info("Data aggregator stopped by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
