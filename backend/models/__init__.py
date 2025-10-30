"""
ORM 模型包
包含所有数据库表的 Tortoise-ORM 模型和虚拟市场数据模型
"""
from models.user import User
from models.account import SimAccount
from models.asset import Asset
from models.trade import SimTrade
from models.holding import SimHolding

# 虚拟市场数据模型 (dataclass models)
from .stock import Stock, StockMetadata, get_market_cap_tier, MARKET_CAP_TIERS
from .index import (
    Index,
    IndexConstituent,
    INDEX_TYPE_CORE,
    INDEX_TYPE_SECTOR,
    CORE_INDICES,
    SECTOR_INDEX_MAPPING,
    validate_index_weights,
    normalize_weights,
)
from .market import (
    Sector,
    MarketState,
    MARKET_STATE_BULL,
    MARKET_STATE_BEAR,
    MARKET_STATE_SIDEWAYS,
    ALL_SECTORS,
    SECTOR_BETA_MAP,
    get_sector_beta,
    validate_daily_trend,
)
from .price import (
    PriceData,
    TARGET_TYPE_STOCK,
    TARGET_TYPE_INDEX,
    SUPPORTED_PERIODS,
    PERIOD_1MIN,
    PERIOD_1DAY,
    validate_ohlc,
    get_period_seconds,
)

__all__ = [
    # Original Tortoise-ORM models
    "User",
    "SimAccount",
    "Asset",
    "SimTrade",
    "SimHolding",
    # Virtual market stock models
    'Stock',
    'StockMetadata',
    'get_market_cap_tier',
    'MARKET_CAP_TIERS',
    # Virtual market index models
    'Index',
    'IndexConstituent',
    'INDEX_TYPE_CORE',
    'INDEX_TYPE_SECTOR',
    'CORE_INDICES',
    'SECTOR_INDEX_MAPPING',
    'validate_index_weights',
    'normalize_weights',
    # Virtual market market models
    'Sector',
    'MarketState',
    'MARKET_STATE_BULL',
    'MARKET_STATE_BEAR',
    'MARKET_STATE_SIDEWAYS',
    'ALL_SECTORS',
    'SECTOR_BETA_MAP',
    'get_sector_beta',
    'validate_daily_trend',
    # Virtual market price models
    'PriceData',
    'TARGET_TYPE_STOCK',
    'TARGET_TYPE_INDEX',
    'SUPPORTED_PERIODS',
    'PERIOD_1MIN',
    'PERIOD_1DAY',
    'validate_ohlc',
    'get_period_seconds',
]
