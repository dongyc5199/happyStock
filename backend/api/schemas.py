"""
API Response Schemas
FastAPI Pydantic模型用于API响应
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, date
from decimal import Decimal


# ============================================================================
# Base Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = False
    error: dict = Field(..., description="错误信息")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Stock not found"
                }
            }
        }


class SuccessResponse(BaseModel):
    """成功响应"""
    success: bool = True
    data: dict = Field(..., description="响应数据")


# ============================================================================
# Stock Schemas
# ============================================================================

class StockSummary(BaseModel):
    """股票摘要信息"""
    symbol: str = Field(..., description="股票代码", examples=["600519"])
    name: str = Field(..., description="股票名称", examples=["贵州茅台"])
    sector_code: str = Field(..., description="板块代码", examples=["CONS"])
    current_price: float = Field(..., description="当前价格", examples=[1685.50])
    previous_close: float = Field(..., description="昨收价", examples=[1672.00])
    change_value: Optional[float] = Field(None, description="涨跌额", examples=[13.50])
    change_pct: Optional[float] = Field(None, description="涨跌幅(%)", examples=[0.81])
    volume: int = Field(0, description="成交量")
    turnover: float = Field(0, description="成交额")

    class Config:
        from_attributes = True


class StockDetail(StockSummary):
    """股票详细信息（包含元数据）"""
    market_cap: int = Field(..., description="市值(元)")
    market_cap_tier: str = Field(..., description="市值分档", examples=["超大盘"])
    beta: float = Field(..., description="Beta系数", examples=[0.85])
    volatility: float = Field(..., description="波动率", examples=[0.025])
    outstanding_shares: int = Field(..., description="流通股本")
    listing_date: Optional[str] = Field(None, description="上市日期")
    is_happy300: bool = Field(False, description="是否HAPPY300成分股")
    weight_in_happy300: Optional[float] = Field(None, description="HAPPY300权重")

    class Config:
        from_attributes = True


# ============================================================================
# Index Schemas
# ============================================================================

class IndexSummary(BaseModel):
    """指数摘要信息"""
    code: str = Field(..., description="指数代码", examples=["HAPPY300"])
    name: str = Field(..., description="指数名称", examples=["快乐综合指数"])
    index_type: str = Field(..., description="指数类型", examples=["CORE"])
    current_value: float = Field(..., description="当前点位", examples=[3125.50])
    previous_close: float = Field(..., description="昨收点位", examples=[3100.00])
    change_value: Optional[float] = Field(None, description="涨跌点数", examples=[25.50])
    change_pct: Optional[float] = Field(None, description="涨跌幅(%)", examples=[0.82])

    class Config:
        from_attributes = True


class IndexDetail(IndexSummary):
    """指数详细信息"""
    base_point: float = Field(..., description="基点", examples=[3000.0])
    base_date: str = Field(..., description="基期日期", examples=["2024-01-01"])
    constituent_count: int = Field(..., description="成分股数量", examples=[100])
    calculation_method: str = Field("FREE_FLOAT_MKT_CAP", description="计算方法")

    class Config:
        from_attributes = True


class IndexConstituent(BaseModel):
    """指数成分股"""
    symbol: str = Field(..., description="股票代码", examples=["601318"])
    name: str = Field(..., description="股票名称", examples=["平安保险"])
    weight: float = Field(..., description="权重", examples=[0.085], ge=0.0001, le=0.1)
    rank: Optional[int] = Field(None, description="排名", examples=[2])

    class Config:
        from_attributes = True


# ============================================================================
# Sector Schemas
# ============================================================================

class SectorSummary(BaseModel):
    """板块摘要信息"""
    code: str = Field(..., description="板块代码", examples=["TECH"])
    name: str = Field(..., description="板块名称", examples=["科技板块"])
    beta: float = Field(..., description="Beta系数", examples=[1.25])
    stock_count: int = Field(0, description="股票数量")
    avg_change_pct: Optional[float] = Field(None, description="平均涨跌幅(%)", examples=[1.35])

    class Config:
        from_attributes = True


# ============================================================================
# Market State Schemas
# ============================================================================

class MarketState(BaseModel):
    """市场状态"""
    state: str = Field(..., description="市场状态", examples=["BULL"])
    start_time: str = Field(..., description="开始时间")
    daily_trend: float = Field(..., description="日均趋势", examples=[0.005])
    volatility_multiplier: float = Field(1.0, description="波动率倍数")
    description: Optional[str] = Field(None, description="状态描述")
    duration_days: Optional[int] = Field(None, description="持续天数")

    class Config:
        from_attributes = True


# ============================================================================
# K-line (Price Data) Schemas
# ============================================================================

class KlineData(BaseModel):
    """K线数据"""
    timestamp: int = Field(..., description="时间戳(毫秒)")
    datetime: str = Field(..., description="时间")
    open: float = Field(..., description="开盘价")
    high: float = Field(..., description="最高价")
    low: float = Field(..., description="最低价")
    close: float = Field(..., description="收盘价")
    volume: int = Field(0, description="成交量")
    turnover: float = Field(0, description="成交额")
    change_pct: Optional[float] = Field(None, description="涨跌幅(%)")

    class Config:
        from_attributes = True


class LightweightChartsKline(BaseModel):
    """Lightweight Charts格式的K线数据"""
    time: int = Field(..., description="时间戳(秒)")
    open: float = Field(..., description="开盘价")
    high: float = Field(..., description="最高价")
    low: float = Field(..., description="最低价")
    close: float = Field(..., description="收盘价")
    volume: int = Field(0, description="成交量")

    class Config:
        from_attributes = True


# ============================================================================
# List Response Wrappers
# ============================================================================

class StockListResponse(BaseModel):
    """股票列表响应"""
    success: bool = True
    data: List[StockSummary]
    total: int = Field(..., description="总数")
    page: int = Field(1, description="当前页码")
    page_size: int = Field(100, description="每页数量")


class IndexListResponse(BaseModel):
    """指数列表响应"""
    success: bool = True
    data: List[IndexSummary]
    total: int = Field(..., description="总数")


class SectorListResponse(BaseModel):
    """板块列表响应"""
    success: bool = True
    data: List[SectorSummary]
    total: int = Field(..., description="总数")


class KlineListResponse(BaseModel):
    """K线数据列表响应"""
    success: bool = True
    data: List[KlineData]
    total: int = Field(..., description="总数")
    period: str = Field(..., description="周期", examples=["1d"])
    symbol: str = Field(..., description="股票/指数代码")


# ============================================================================
# Utility Functions
# ============================================================================

def create_success_response(data, **kwargs):
    """创建成功响应"""
    return {
        "success": True,
        "data": data,
        **kwargs
    }


def create_error_response(code: str, message: str):
    """创建错误响应"""
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message
        }
    }
