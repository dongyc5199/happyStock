#!/usr/bin/env python3
"""
Market Data Generator Startup Script

Starts the market data generation daemon.
Use this script to run the generator as a service.
"""

import sys
import os
import logging

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.market_data_generator import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Market data generator stopped by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
