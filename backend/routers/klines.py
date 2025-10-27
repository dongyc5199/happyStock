"""
K线数据路由

提供股票K线历史数据查询接口。
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Literal
from datetime import datetime, timedelta
import random
from decimal import Decimal

from schemas.responses import SuccessResponse
from schemas.kline import KlineData, KlineResponse

router = APIRouter(prefix="/klines", tags=["K线数据"])


def generate_mock_klines(
    symbol: str,
    interval: str,
    start_time: datetime,
    end_time: datetime
) -> List[KlineData]:
    """
    生成模拟K线数据

    在真实项目中，这里应该：
    1. 从数据库查询历史K线数据
    2. 或调用第三方API（如聚宽、Tushare、东方财富等）

    Args:
        symbol: 股票代码
        interval: 时间间隔 (1d, 1w, 1M)
        start_time: 开始时间
        end_time: 结束时间

    Returns:
        K线数据列表
    """
    klines = []

    # 根据时间间隔计算数据点数量和时间增量
    if interval == "5m":
        delta = timedelta(minutes=5)
        count = min(int((end_time - start_time).total_seconds() / 300), 500)  # 最多500个数据点
    elif interval == "15m":
        delta = timedelta(minutes=15)
        count = min(int((end_time - start_time).total_seconds() / 900), 500)
    elif interval == "30m":
        delta = timedelta(minutes=30)
        count = min(int((end_time - start_time).total_seconds() / 1800), 500)
    elif interval == "60m":
        delta = timedelta(hours=1)
        count = min(int((end_time - start_time).total_seconds() / 3600), 500)
    elif interval == "120m":
        delta = timedelta(hours=2)
        count = min(int((end_time - start_time).total_seconds() / 7200), 500)
    elif interval == "1d":
        delta = timedelta(days=1)
        count = min((end_time - start_time).days, 90)  # 最多90天
    elif interval == "1w":
        delta = timedelta(weeks=1)
        count = min((end_time - start_time).days // 7, 52)  # 最多52周
    elif interval == "1M":
        delta = timedelta(days=30)
        count = min((end_time - start_time).days // 30, 24)  # 最多24个月
    else:
        delta = timedelta(days=1)
        count = 60

    # 生成模拟数据
    base_price = Decimal("100.00")
    current_time = start_time

    for i in range(count):
        if current_time > end_time:
            break

        # 模拟价格波动
        price_change = Decimal(str(random.uniform(-5, 5)))
        open_price = base_price + price_change

        close_change = Decimal(str(random.uniform(-3, 3)))
        close_price = open_price + close_change

        high_price = max(open_price, close_price) + Decimal(str(random.uniform(0, 2)))
        low_price = min(open_price, close_price) - Decimal(str(random.uniform(0, 2)))

        # 模拟成交量
        volume = int(random.uniform(500000, 2000000))

        klines.append(KlineData(
            time=int(current_time.timestamp()),
            open=str(open_price),
            high=str(high_price),
            low=str(low_price),
            close=str(close_price),
            volume=volume
        ))

        base_price = close_price
        current_time += delta

    return klines


@router.get("/{symbol}", response_model=SuccessResponse)
async def get_klines(
    symbol: str,
    interval: Literal["5m", "15m", "30m", "60m", "120m", "1d", "1w", "1M"] = Query(
        "1d",
        description="时间间隔：5m=5分钟, 15m=15分钟, 30m=30分钟, 60m=60分钟, 120m=120分钟, 1d=日K, 1w=周K, 1M=月K"
    ),
    limit: int = Query(90, ge=1, le=500, description="返回数据条数")
):
    """
    获取股票K线数据

    Args:
        symbol: 股票代码（如 600000.SH）
        interval: 时间间隔
        limit: 返回数据条数

    Returns:
        K线数据

    Example:
        GET /api/v1/klines/600000.SH?interval=1d&limit=60
    """
    try:
        # 计算时间范围
        end_time = datetime.now()

        # 根据不同的时间间隔计算起始时间
        if interval == "5m":
            start_time = end_time - timedelta(minutes=limit * 5)
        elif interval == "15m":
            start_time = end_time - timedelta(minutes=limit * 15)
        elif interval == "30m":
            start_time = end_time - timedelta(minutes=limit * 30)
        elif interval == "60m":
            start_time = end_time - timedelta(hours=limit)
        elif interval == "120m":
            start_time = end_time - timedelta(hours=limit * 2)
        elif interval == "1d":
            start_time = end_time - timedelta(days=limit)
        elif interval == "1w":
            start_time = end_time - timedelta(weeks=limit)
        elif interval == "1M":
            start_time = end_time - timedelta(days=limit * 30)
        else:
            start_time = end_time - timedelta(days=90)

        # 生成K线数据
        klines = generate_mock_klines(symbol, interval, start_time, end_time)

        return SuccessResponse(
            success=True,
            data=KlineResponse(
                symbol=symbol,
                interval=interval,
                klines=klines
            )
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取K线数据失败: {str(e)}")
