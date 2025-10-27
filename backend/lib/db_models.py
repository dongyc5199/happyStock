"""
Database models and connection management for market data generation.

Uses SQLAlchemy ORM with connection pooling for high performance.
Supports both PostgreSQL (recommended) and SQLite (fallback).
"""

from sqlalchemy import (
    create_engine,
    Column,
    String,
    BigInteger,
    Numeric,
    Boolean,
    Integer,
    TIMESTAMP,
    text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, NullPool
from contextlib import contextmanager
from typing import Optional, List, Dict
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base class for all models
Base = declarative_base()


# ==================== Models ====================

class MarketKline(Base):
    """Market K-line data (partitioned by time)"""

    __tablename__ = "market_klines"

    symbol = Column(String(20), primary_key=True, nullable=False)
    interval = Column(String(10), primary_key=True, nullable=False)
    time = Column(BigInteger, primary_key=True, nullable=False)
    open = Column(Numeric(10, 2), nullable=False)
    high = Column(Numeric(10, 2), nullable=False)
    low = Column(Numeric(10, 2), nullable=False)
    close = Column(Numeric(10, 2), nullable=False)
    volume = Column(BigInteger, nullable=False, default=0)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "symbol": self.symbol,
            "interval": self.interval,
            "time": self.time,
            "open": float(self.open),
            "high": float(self.high),
            "low": float(self.low),
            "close": float(self.close),
            "volume": int(self.volume),
        }


class StockState(Base):
    """Current state tracking for each stock"""

    __tablename__ = "stock_state"

    symbol = Column(String(20), primary_key=True)
    current_price = Column(Numeric(10, 2), nullable=False)
    volatility = Column(Numeric(6, 4), nullable=False, default=0.02)
    trend = Column(Numeric(6, 4), nullable=False, default=0.0)
    market_state = Column(String(20), nullable=False, default="sideways")
    last_update = Column(BigInteger, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
    )

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "symbol": self.symbol,
            "current_price": float(self.current_price),
            "volatility": float(self.volatility),
            "trend": float(self.trend),
            "market_state": self.market_state,
            "last_update": self.last_update,
        }


class MarketStatus(Base):
    """Global market trading status"""

    __tablename__ = "market_status"

    id = Column(Integer, primary_key=True, autoincrement=True)
    is_trading = Column(Boolean, nullable=False, default=False)
    current_session = Column(String(20))  # morning, afternoon, closed
    session_start = Column(BigInteger)
    session_end = Column(BigInteger)
    last_update = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))


class StockRealtimePrice(Base):
    """Realtime price cache (UNLOGGED table for performance)"""

    __tablename__ = "stock_realtime_price"

    symbol = Column(String(20), primary_key=True)
    current_price = Column(Numeric(10, 2), nullable=False)
    change_percent = Column(Numeric(6, 3))
    volume = Column(BigInteger)
    last_update = Column(BigInteger, nullable=False)
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))


class StockMetadata(Base):
    """Static stock metadata"""

    __tablename__ = "stock_metadata"

    symbol = Column(String(20), primary_key=True)
    name = Column(String(100), nullable=False)
    sector = Column(String(50))
    base_price = Column(Numeric(10, 2), nullable=False)
    base_volatility = Column(Numeric(6, 4), default=0.02)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "symbol": self.symbol,
            "name": self.name,
            "sector": self.sector,
            "base_price": float(self.base_price),
            "base_volatility": float(self.base_volatility),
            "is_active": self.is_active,
        }


# ==================== Database Manager ====================

class DatabaseManager:
    """
    Database connection and session management.

    Supports PostgreSQL (recommended) and SQLite (fallback).
    Uses connection pooling for high concurrency.
    """

    def __init__(
        self,
        db_url: Optional[str] = None,
        pool_size: int = 20,
        max_overflow: int = 30,
        pool_timeout: int = 30,
        echo: bool = False,
    ):
        """
        Initialize database manager.

        Args:
            db_url: Database URL (if None, reads from environment)
            pool_size: Base connection pool size
            max_overflow: Max overflow connections
            pool_timeout: Pool timeout in seconds
            echo: Echo SQL statements (debug mode)
        """
        if db_url is None:
            db_url = self._get_db_url_from_env()

        self.db_url = db_url
        self.is_sqlite = db_url.startswith("sqlite")

        # Create engine with appropriate pooling
        if self.is_sqlite:
            # SQLite doesn't support connection pooling well
            self.engine = create_engine(
                db_url,
                poolclass=NullPool,
                echo=echo,
                connect_args={"check_same_thread": False},
            )
            logger.warning("Using SQLite - not recommended for production!")
        else:
            # PostgreSQL with connection pooling
            self.engine = create_engine(
                db_url,
                poolclass=QueuePool,
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_timeout=pool_timeout,
                pool_pre_ping=True,  # Verify connections before use
                echo=echo,
            )
            logger.info(
                f"PostgreSQL connection pool initialized: "
                f"size={pool_size}, max_overflow={max_overflow}"
            )

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )

    def _get_db_url_from_env(self) -> str:
        """
        Get database URL from environment variables.

        Supported formats:
            - DATABASE_URL (direct URL)
            - DB_TYPE, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
        """
        # Try direct URL first
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            return db_url

        # Build URL from components
        db_type = os.getenv("DB_TYPE", "postgresql")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_user = os.getenv("DB_USER", "postgres")
        db_password = os.getenv("DB_PASSWORD", "postgres")
        db_name = os.getenv("DB_NAME", "happystock")

        if db_type == "postgresql":
            return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        elif db_type == "sqlite":
            return f"sqlite:///{db_name}.db"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    def create_tables(self):
        """Create all tables (if not exist)"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created/verified")

    def drop_tables(self):
        """Drop all tables (use with caution!)"""
        Base.metadata.drop_all(bind=self.engine)
        logger.warning("All database tables dropped!")

    @contextmanager
    def get_session(self) -> Session:
        """
        Get a database session (context manager).

        Usage:
            with db_manager.get_session() as session:
                session.query(...)
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def execute_raw_sql(self, sql: str, params: Optional[dict] = None):
        """
        Execute raw SQL statement.

        Args:
            sql: SQL statement
            params: Parameters for parameterized query
        """
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), params or {})
            conn.commit()
            return result

    def bulk_insert_klines(self, klines: List[Dict]) -> int:
        """
        Bulk insert K-line data for performance.

        Args:
            klines: List of K-line dictionaries

        Returns:
            Number of rows inserted
        """
        if not klines:
            return 0

        with self.get_session() as session:
            # Use bulk insert for performance
            session.bulk_insert_mappings(MarketKline, klines)
            session.commit()

        logger.info(f"Bulk inserted {len(klines)} K-lines")
        return len(klines)

    def get_stock_state(self, symbol: str) -> Optional[StockState]:
        """Get current state for a stock"""
        with self.get_session() as session:
            return session.query(StockState).filter_by(symbol=symbol).first()

    def update_stock_state(
        self,
        symbol: str,
        current_price: float,
        volatility: float,
        trend: float,
        market_state: str,
        timestamp: int,
    ):
        """Update stock state"""
        with self.get_session() as session:
            state = session.query(StockState).filter_by(symbol=symbol).first()

            if state:
                # Update existing
                state.current_price = current_price
                state.volatility = volatility
                state.trend = trend
                state.market_state = market_state
                state.last_update = timestamp
            else:
                # Create new
                state = StockState(
                    symbol=symbol,
                    current_price=current_price,
                    volatility=volatility,
                    trend=trend,
                    market_state=market_state,
                    last_update=timestamp,
                )
                session.add(state)

            session.commit()

    def get_active_stocks(self) -> List[StockMetadata]:
        """Get all active stocks"""
        with self.get_session() as session:
            return session.query(StockMetadata).filter_by(is_active=True).all()

    def close(self):
        """Close database engine and connections"""
        self.engine.dispose()
        logger.info("Database connections closed")


# ==================== Singleton instance ====================

# Global database manager instance (initialized on import)
_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """Get global database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def init_db_manager(**kwargs) -> DatabaseManager:
    """
    Initialize global database manager with custom config.

    Args:
        **kwargs: Arguments to pass to DatabaseManager constructor

    Returns:
        Initialized DatabaseManager instance
    """
    global _db_manager
    _db_manager = DatabaseManager(**kwargs)
    return _db_manager


if __name__ == "__main__":
    # Test database connection
    print("Testing database connection...")

    try:
        db = get_db_manager()
        print(f"Database URL: {db.db_url}")
        print(f"Database type: {'SQLite' if db.is_sqlite else 'PostgreSQL'}")

        # Create tables
        db.create_tables()
        print("✓ Tables created successfully")

        # Test session
        with db.get_session() as session:
            count = session.query(StockMetadata).count()
            print(f"✓ Stock metadata count: {count}")

        print("\nDatabase test successful!")

    except Exception as e:
        print(f"✗ Database test failed: {e}")
        raise
