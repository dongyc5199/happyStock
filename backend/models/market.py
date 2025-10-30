"""
Market Models: Sector and MarketState
板块和市场状态模型
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class Sector:
    """
    行业板块
    Table: sectors
    """
    code: str  # 板块代码 (e.g., "TECH")
    name: str  # 板块名称 (e.g., "科技板块")
    name_en: Optional[str] = None  # 英文名称 (e.g., "Technology")
    beta: Decimal = Decimal('1.0')  # Beta系数 (板块整体波动性)
    total_market_cap: Optional[int] = None  # 总市值 (元)
    stock_count: int = 0  # 股票数量
    avg_change_pct: Optional[Decimal] = None  # 平均涨跌幅 (%)
    description: Optional[str] = None  # 板块描述
    created_at: Optional[datetime] = None

    @property
    def market_cap_billion(self) -> Optional[Decimal]:
        """总市值(亿元)"""
        if self.total_market_cap:
            return Decimal(self.total_market_cap) / Decimal('100000000')
        return None

    @property
    def is_tech_sector(self) -> bool:
        """是否科技板块"""
        return self.code == 'TECH'

    @property
    def is_high_beta_sector(self) -> bool:
        """是否高Beta板块 (>1.2)"""
        return self.beta > Decimal('1.2')

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'code': self.code,
            'name': self.name,
            'name_en': self.name_en,
            'beta': float(self.beta),
            'total_market_cap': self.total_market_cap,
            'stock_count': self.stock_count,
            'avg_change_pct': float(self.avg_change_pct) if self.avg_change_pct else None,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


@dataclass
class MarketState:
    """
    市场状态 (牛市/熊市/横盘)
    Table: market_states
    """
    state: str  # 市场状态: BULL牛市 / BEAR熊市 / SIDEWAYS横盘
    start_time: datetime  # 状态开始时间
    daily_trend: Decimal  # 日均趋势 (-0.05 到 0.05, 即-5%到5%)
    volatility_multiplier: Decimal = Decimal('1.0')  # 波动率倍数
    end_time: Optional[datetime] = None  # 状态结束时间
    description: Optional[str] = None  # 状态描述
    is_current: bool = False  # 是否当前状态
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    @property
    def is_bull_market(self) -> bool:
        """是否牛市"""
        return self.state == 'BULL'

    @property
    def is_bear_market(self) -> bool:
        """是否熊市"""
        return self.state == 'BEAR'

    @property
    def is_sideways_market(self) -> bool:
        """是否横盘"""
        return self.state == 'SIDEWAYS'

    @property
    def duration_days(self) -> Optional[int]:
        """状态持续天数"""
        if self.end_time:
            return (self.end_time - self.start_time).days
        elif self.is_current:
            return (datetime.now() - self.start_time).days
        return None

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'state': self.state,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'daily_trend': float(self.daily_trend),
            'volatility_multiplier': float(self.volatility_multiplier),
            'description': self.description,
            'is_current': self.is_current,
            'duration_days': self.duration_days,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# 市场状态常量
MARKET_STATE_BULL = 'BULL'  # 牛市
MARKET_STATE_BEAR = 'BEAR'  # 熊市
MARKET_STATE_SIDEWAYS = 'SIDEWAYS'  # 横盘

# 板块代码常量
SECTOR_TECH = 'TECH'  # 科技
SECTOR_FIN = 'FIN'  # 金融
SECTOR_CONS = 'CONS'  # 消费
SECTOR_NEV = 'NEV'  # 新能源
SECTOR_HEALTH = 'HEALTH'  # 医药
SECTOR_IND = 'IND'  # 工业
SECTOR_REAL = 'REAL'  # 地产
SECTOR_ENERGY = 'ENERGY'  # 能源
SECTOR_MATER = 'MATER'  # 材料
SECTOR_UTIL = 'UTIL'  # 公用事业

# 10大板块列表
ALL_SECTORS = [
    SECTOR_TECH, SECTOR_FIN, SECTOR_CONS, SECTOR_NEV, SECTOR_HEALTH,
    SECTOR_IND, SECTOR_REAL, SECTOR_ENERGY, SECTOR_MATER, SECTOR_UTIL
]

# 板块Beta系数映射 (从SQL初始化脚本)
SECTOR_BETA_MAP = {
    SECTOR_TECH: Decimal('1.25'),
    SECTOR_FIN: Decimal('0.75'),
    SECTOR_CONS: Decimal('0.85'),
    SECTOR_NEV: Decimal('1.40'),
    SECTOR_HEALTH: Decimal('0.90'),
    SECTOR_IND: Decimal('1.05'),
    SECTOR_REAL: Decimal('1.15'),
    SECTOR_ENERGY: Decimal('0.95'),
    SECTOR_MATER: Decimal('1.10'),
    SECTOR_UTIL: Decimal('0.65'),
}

# 日均趋势范围
DAILY_TREND_MIN = Decimal('-0.05')  # -5%
DAILY_TREND_MAX = Decimal('0.05')  # +5%


def get_sector_beta(sector_code: str) -> Decimal:
    """
    获取板块Beta系数

    Args:
        sector_code: 板块代码

    Returns:
        Beta系数，默认1.0
    """
    return SECTOR_BETA_MAP.get(sector_code, Decimal('1.0'))


def validate_daily_trend(daily_trend: Decimal) -> bool:
    """
    验证日均趋势是否在合法范围内

    Args:
        daily_trend: 日均趋势

    Returns:
        bool: 是否合法
    """
    return DAILY_TREND_MIN <= daily_trend <= DAILY_TREND_MAX
