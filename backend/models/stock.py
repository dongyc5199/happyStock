"""
Stock and StockMetadata Models
股票基础信息和元数据模型
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class Stock:
    """
    股票基本信息
    Table: stocks
    """
    symbol: str  # 股票代码 (e.g., "600519")
    name: str  # 股票名称 (e.g., "贵州茅台")
    sector_code: str  # 所属板块代码 (e.g., "CONS")
    current_price: Decimal  # 当前价格
    previous_close: Decimal  # 昨收价
    change_value: Optional[Decimal] = None  # 涨跌额
    change_pct: Optional[Decimal] = None  # 涨跌幅 (%)
    volume: int = 0  # 成交量
    turnover: Decimal = Decimal('0')  # 成交额
    is_active: bool = True  # 是否活跃
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """计算涨跌额和涨跌幅"""
        if self.change_value is None and self.previous_close > 0:
            self.change_value = self.current_price - self.previous_close

        if self.change_pct is None and self.previous_close > 0:
            self.change_pct = ((self.current_price - self.previous_close) / self.previous_close) * 100

    @property
    def is_limit_up(self) -> bool:
        """是否涨停 (10%)"""
        return self.change_pct is not None and self.change_pct >= Decimal('9.9')

    @property
    def is_limit_down(self) -> bool:
        """是否跌停 (-10%)"""
        return self.change_pct is not None and self.change_pct <= Decimal('-9.9')

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'symbol': self.symbol,
            'name': self.name,
            'sector_code': self.sector_code,
            'current_price': float(self.current_price),
            'previous_close': float(self.previous_close),
            'change_value': float(self.change_value) if self.change_value else None,
            'change_pct': float(self.change_pct) if self.change_pct else None,
            'volume': self.volume,
            'turnover': float(self.turnover),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class StockMetadata:
    """
    股票元数据 (静态属性)
    Table: stock_metadata
    """
    symbol: str  # 股票代码
    market_cap: int  # 市值 (单位: 元)
    market_cap_tier: str  # 市值分档 (超大盘/大盘/中盘/小盘/微盘)
    beta: Decimal  # Beta系数 (0.5-2.0)
    volatility: Decimal  # 波动率 (0.01-1.0)
    outstanding_shares: int  # 流通股本
    listing_date: Optional[datetime] = None  # 上市日期
    is_happy300: bool = False  # 是否HAPPY300成分股
    weight_in_happy300: Optional[Decimal] = None  # HAPPY300权重
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def market_cap_billion(self) -> Decimal:
        """市值(亿元)"""
        return Decimal(self.market_cap) / Decimal('100000000')

    @property
    def is_high_beta(self) -> bool:
        """是否高Beta股票 (>1.2)"""
        return self.beta > Decimal('1.2')

    @property
    def is_low_beta(self) -> bool:
        """是否低Beta股票 (<0.8)"""
        return self.beta < Decimal('0.8')

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'symbol': self.symbol,
            'market_cap': self.market_cap,
            'market_cap_tier': self.market_cap_tier,
            'beta': float(self.beta),
            'volatility': float(self.volatility),
            'outstanding_shares': self.outstanding_shares,
            'listing_date': self.listing_date.isoformat() if self.listing_date else None,
            'is_happy300': self.is_happy300,
            'weight_in_happy300': float(self.weight_in_happy300) if self.weight_in_happy300 else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


# 市值分档标准 (单位: 亿元)
MARKET_CAP_TIERS = {
    '超大盘': 1000,  # >= 1000亿
    '大盘': 300,     # 300-1000亿
    '中盘': 100,     # 100-300亿
    '小盘': 50,      # 50-100亿
    '微盘': 0,       # < 50亿
}


def get_market_cap_tier(market_cap: int) -> str:
    """
    根据市值确定市值分档

    Args:
        market_cap: 市值(元)

    Returns:
        市值分档: 超大盘/大盘/中盘/小盘/微盘
    """
    market_cap_billion = market_cap / 100000000  # 转换为亿元

    if market_cap_billion >= MARKET_CAP_TIERS['超大盘']:
        return '超大盘'
    elif market_cap_billion >= MARKET_CAP_TIERS['大盘']:
        return '大盘'
    elif market_cap_billion >= MARKET_CAP_TIERS['中盘']:
        return '中盘'
    elif market_cap_billion >= MARKET_CAP_TIERS['小盘']:
        return '小盘'
    else:
        return '微盘'
