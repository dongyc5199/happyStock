"""
K线数据Schema
"""

from pydantic import BaseModel, Field
from typing import List


class KlineData(BaseModel):
    """单个K线数据点"""
    time: int = Field(..., description="时间戳（秒）")
    open: str = Field(..., description="开盘价")
    high: str = Field(..., description="最高价")
    low: str = Field(..., description="最低价")
    close: str = Field(..., description="收盘价")
    volume: int = Field(..., description="成交量")


class KlineResponse(BaseModel):
    """K线数据响应"""
    symbol: str = Field(..., description="股票代码")
    interval: str = Field(..., description="时间间隔")
    klines: List[KlineData] = Field(..., description="K线数据列表")
