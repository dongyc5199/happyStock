"""
Price Data Model
K线价格数据模型
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class PriceData:
    """
    K线价格数据 (OHLCV)
    Table: price_data

    Supports both stocks and indices
    """
    target_type: str  # 目标类型: STOCK股票 / INDEX指数
    target_code: str  # 目标代码 (股票symbol或指数code)
    timestamp: int  # Unix时间戳 (毫秒)
    datetime: datetime  # 时间
    open: Decimal  # 开盘价
    close: Decimal  # 收盘价
    high: Decimal  # 最高价
    low: Decimal  # 最低价
    volume: int = 0  # 成交量
    turnover: Decimal = Decimal('0')  # 成交额
    change_pct: Optional[Decimal] = None  # 涨跌幅 (%)
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """数据验证"""
        # 验证高低价格合法性
        if self.low > min(self.open, self.close):
            raise ValueError(f"Low price {self.low} cannot be higher than min(open={self.open}, close={self.close})")

        if self.high < max(self.open, self.close):
            raise ValueError(f"High price {self.high} cannot be lower than max(open={self.open}, close={self.close})")

    @property
    def is_stock(self) -> bool:
        """是否股票数据"""
        return self.target_type == 'STOCK'

    @property
    def is_index(self) -> bool:
        """是否指数数据"""
        return self.target_type == 'INDEX'

    @property
    def is_up(self) -> bool:
        """是否上涨"""
        return self.close > self.open

    @property
    def is_down(self) -> bool:
        """是否下跌"""
        return self.close < self.open

    @property
    def is_flat(self) -> bool:
        """是否平盘"""
        return self.close == self.open

    @property
    def price_change(self) -> Decimal:
        """价格变动额"""
        return self.close - self.open

    @property
    def amplitude(self) -> Decimal:
        """振幅 (%)"""
        if self.open == 0:
            return Decimal('0')
        return ((self.high - self.low) / self.open) * 100

    @property
    def upper_shadow_ratio(self) -> Decimal:
        """上影线比例"""
        body_high = max(self.open, self.close)
        if self.high == self.low:
            return Decimal('0')
        return ((self.high - body_high) / (self.high - self.low)) * 100

    @property
    def lower_shadow_ratio(self) -> Decimal:
        """下影线比例"""
        body_low = min(self.open, self.close)
        if self.high == self.low:
            return Decimal('0')
        return ((body_low - self.low) / (self.high - self.low)) * 100

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'target_type': self.target_type,
            'target_code': self.target_code,
            'timestamp': self.timestamp,
            'datetime': self.datetime.isoformat() if self.datetime else None,
            'open': float(self.open),
            'close': float(self.close),
            'high': float(self.high),
            'low': float(self.low),
            'volume': self.volume,
            'turnover': float(self.turnover),
            'change_pct': float(self.change_pct) if self.change_pct else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def to_lightweight_charts_format(self) -> dict:
        """
        转换为 Lightweight Charts 库所需的格式

        Returns:
            dict: {time: timestamp, open, high, low, close, volume}
        """
        return {
            'time': self.timestamp // 1000,  # Lightweight Charts uses seconds
            'open': float(self.open),
            'high': float(self.high),
            'low': float(self.low),
            'close': float(self.close),
            'volume': self.volume,
        }


# 目标类型常量
TARGET_TYPE_STOCK = 'STOCK'
TARGET_TYPE_INDEX = 'INDEX'

# K线周期常量 (用于查询)
PERIOD_1MIN = '1m'
PERIOD_5MIN = '5m'
PERIOD_15MIN = '15m'
PERIOD_30MIN = '30m'
PERIOD_1HOUR = '1h'
PERIOD_4HOUR = '4h'
PERIOD_1DAY = '1d'
PERIOD_1WEEK = '1w'
PERIOD_1MONTH = '1M'

# 支持的周期列表
SUPPORTED_PERIODS = [
    PERIOD_1MIN, PERIOD_5MIN, PERIOD_15MIN, PERIOD_30MIN,
    PERIOD_1HOUR, PERIOD_4HOUR, PERIOD_1DAY, PERIOD_1WEEK, PERIOD_1MONTH
]

# 周期转秒数
PERIOD_TO_SECONDS = {
    PERIOD_1MIN: 60,
    PERIOD_5MIN: 300,
    PERIOD_15MIN: 900,
    PERIOD_30MIN: 1800,
    PERIOD_1HOUR: 3600,
    PERIOD_4HOUR: 14400,
    PERIOD_1DAY: 86400,
    PERIOD_1WEEK: 604800,
    PERIOD_1MONTH: 2592000,  # Approximate 30 days
}


def validate_ohlc(open_price: Decimal, high: Decimal, low: Decimal, close: Decimal) -> bool:
    """
    验证OHLC数据的一致性

    Args:
        open_price: 开盘价
        high: 最高价
        low: 最低价
        close: 收盘价

    Returns:
        bool: 数据是否一致
    """
    # 最低价不能高于开盘/收盘的较小值
    if low > min(open_price, close):
        return False

    # 最高价不能低于开盘/收盘的较大值
    if high < max(open_price, close):
        return False

    # 最低价不能高于最高价
    if low > high:
        return False

    return True


def get_period_seconds(period: str) -> int:
    """
    获取周期对应的秒数

    Args:
        period: 周期代码 (e.g., '1m', '1d')

    Returns:
        秒数

    Raises:
        ValueError: 不支持的周期
    """
    if period not in PERIOD_TO_SECONDS:
        raise ValueError(f"Unsupported period: {period}. Supported: {SUPPORTED_PERIODS}")

    return PERIOD_TO_SECONDS[period]
