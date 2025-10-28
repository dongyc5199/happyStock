"""
Index and IndexConstituent Models
市场指数和成分股模型
"""
from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List


@dataclass
class Index:
    """
    市场指数
    Table: indices
    """
    code: str  # 指数代码 (e.g., "HAPPY300")
    name: str  # 指数名称 (e.g., "快乐综合指数")
    index_type: str  # 指数类型: CORE核心指数 / SECTOR行业指数
    base_point: Decimal  # 基点 (e.g., 3000)
    base_date: date  # 基期日期
    current_value: Decimal  # 当前点位
    previous_close: Decimal  # 昨收点位
    change_value: Optional[Decimal] = None  # 涨跌点数
    change_pct: Optional[Decimal] = None  # 涨跌幅 (%)
    volume: Optional[int] = None  # 成交量
    turnover: Optional[int] = None  # 成交额
    constituent_count: int = 0  # 成分股数量
    calculation_method: str = 'FREE_FLOAT_MKT_CAP'  # 计算方法
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """计算涨跌点数和涨跌幅"""
        if self.change_value is None and self.previous_close > 0:
            self.change_value = self.current_value - self.previous_close

        if self.change_pct is None and self.previous_close > 0:
            self.change_pct = ((self.current_value - self.previous_close) / self.previous_close) * 100

    @property
    def is_core_index(self) -> bool:
        """是否核心指数"""
        return self.index_type == 'CORE'

    @property
    def is_sector_index(self) -> bool:
        """是否行业指数"""
        return self.index_type == 'SECTOR'

    @property
    def cumulative_return(self) -> Decimal:
        """累计收益率 (相对基点)"""
        if self.base_point > 0:
            return ((self.current_value - self.base_point) / self.base_point) * 100
        return Decimal('0')

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'code': self.code,
            'name': self.name,
            'index_type': self.index_type,
            'base_point': float(self.base_point),
            'base_date': self.base_date.isoformat() if self.base_date else None,
            'current_value': float(self.current_value),
            'previous_close': float(self.previous_close),
            'change_value': float(self.change_value) if self.change_value else None,
            'change_pct': float(self.change_pct) if self.change_pct else None,
            'volume': self.volume,
            'turnover': self.turnover,
            'constituent_count': self.constituent_count,
            'calculation_method': self.calculation_method,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class IndexConstituent:
    """
    指数成分股
    Table: index_constituents
    """
    index_code: str  # 指数代码
    stock_symbol: str  # 股票代码
    weight: Decimal  # 权重 (0.0001 - 0.1000, 即0.01% - 10%)
    rank: Optional[int] = None  # 排名
    join_date: Optional[date] = None  # 加入日期
    is_active: bool = True  # 是否活跃
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def weight_percent(self) -> Decimal:
        """权重百分比 (%)"""
        return self.weight * 100

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'index_code': self.index_code,
            'stock_symbol': self.stock_symbol,
            'weight': float(self.weight),
            'weight_percent': float(self.weight_percent),
            'rank': self.rank,
            'join_date': self.join_date.isoformat() if self.join_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


# 指数类型常量
INDEX_TYPE_CORE = 'CORE'
INDEX_TYPE_SECTOR = 'SECTOR'

# 核心指数代码
CORE_INDICES = ['HAPPY300', 'HAPPY50', 'GROW100']

# 行业指数映射 (指数代码 -> 板块代码)
SECTOR_INDEX_MAPPING = {
    'TECH_IDX': 'TECH',
    'FIN_IDX': 'FIN',
    'CONS_IDX': 'CONS',
    'NEV_IDX': 'NEV',
    'HEALTH_IDX': 'HEALTH',
    'IND_IDX': 'IND',
    'REAL_IDX': 'REAL',
    'ENERGY_IDX': 'ENERGY',
    'MATER_IDX': 'MATER',
    'UTIL_IDX': 'UTIL',
}

# 指数权重上限
MAX_WEIGHT_PER_STOCK = Decimal('0.1000')  # 单只股票最高权重10%


def validate_index_weights(constituents: List[IndexConstituent], tolerance: Decimal = Decimal('0.0001')) -> bool:
    """
    验证成分股权重总和是否为1.0

    Args:
        constituents: 成分股列表
        tolerance: 容差 (默认0.01%)

    Returns:
        bool: 权重总和是否接近1.0
    """
    total_weight = sum(c.weight for c in constituents if c.is_active)
    deviation = abs(total_weight - Decimal('1.0'))
    return deviation <= tolerance


def normalize_weights(constituents: List[IndexConstituent]) -> List[IndexConstituent]:
    """
    归一化权重，确保总和为1.0

    Args:
        constituents: 成分股列表

    Returns:
        归一化后的成分股列表
    """
    active_constituents = [c for c in constituents if c.is_active]
    total_weight = sum(c.weight for c in active_constituents)

    if total_weight == 0:
        return constituents

    for constituent in active_constituents:
        constituent.weight = constituent.weight / total_weight

    return constituents
