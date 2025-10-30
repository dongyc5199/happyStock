"""
Market API Routes
市场状态相关API路由
"""
from fastapi import APIRouter, Query
from typing import Optional

from api.schemas import create_success_response, create_error_response
from lib.db_manager_sqlite import get_db_manager


router = APIRouter()
db_manager = get_db_manager()


@router.get("/market/state", response_model=None)
async def get_market_state():
    """
    获取当前市场状态

    返回最新的市场状态信息（牛市/熊市/震荡）
    """
    try:
        # 查询最新的市场状态
        query = """
            SELECT *
            FROM market_states
            ORDER BY start_time DESC
            LIMIT 1
        """

        state = db_manager.execute_query(query, fetch_one=True)

        if not state:
            return create_error_response("NOT_FOUND", "Market state data not found")

        return create_success_response(state)

    except Exception as e:
        print(f"[-] Error in get_market_state: {e}")
        return create_error_response("INTERNAL_ERROR", str(e))


@router.get("/market/history", response_model=None)
async def get_market_history(
    limit: int = Query(30, ge=1, le=365, description="返回天数")
):
    """
    获取市场历史状态

    返回指定天数的市场状态历史记录
    """
    try:
        query = """
            SELECT *
            FROM market_states
            ORDER BY start_time DESC
            LIMIT ?
        """

        history = db_manager.execute_query(query, (limit,))

        # 按时间正序排列
        history.reverse()

        return create_success_response(
            history,
            total=len(history)
        )

    except Exception as e:
        print(f"[-] Error in get_market_history: {e}")
        return create_error_response("INTERNAL_ERROR", str(e))


@router.get("/market/overview", response_model=None)
async def get_market_overview():
    """
    获取市场概览

    返回市场整体统计信息：
    - 股票总数
    - 上涨/下跌/平盘数量
    - 涨停/跌停数量
    - 成交量/成交额
    """
    try:
        # 统计股票数量
        stats_query = """
            SELECT
                COUNT(*) as total_stocks,
                SUM(CASE WHEN change_pct > 0 THEN 1 ELSE 0 END) as rising,
                SUM(CASE WHEN change_pct < 0 THEN 1 ELSE 0 END) as falling,
                SUM(CASE WHEN change_pct = 0 THEN 1 ELSE 0 END) as unchanged,
                SUM(CASE WHEN change_pct >= 9.9 THEN 1 ELSE 0 END) as limit_up,
                SUM(CASE WHEN change_pct <= -9.9 THEN 1 ELSE 0 END) as limit_down,
                SUM(volume) as total_volume,
                SUM(turnover) as total_turnover
            FROM stocks
            WHERE is_active = 1
        """

        stats = db_manager.execute_query(stats_query, fetch_one=True)

        # 获取当前市场状态
        market_state_query = """
            SELECT state, daily_trend
            FROM market_states
            ORDER BY start_time DESC
            LIMIT 1
        """

        market_state = db_manager.execute_query(market_state_query, fetch_one=True)

        # 组合结果
        result = dict(stats) if stats else {}
        if market_state:
            result['market_state'] = market_state['state']
            result['market_trend'] = market_state['daily_trend']

        return create_success_response(result)

    except Exception as e:
        print(f"[-] Error in get_market_overview: {e}")
        return create_error_response("INTERNAL_ERROR", str(e))
