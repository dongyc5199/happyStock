"""
Sector API Routes
板块相关API路由
"""
from fastapi import APIRouter

from api.schemas import create_success_response, create_error_response
from lib.db_manager_sqlite import get_db_manager


router = APIRouter()
db_manager = get_db_manager()


@router.get("/sectors", response_model=None)
async def get_sectors():
    """
    获取所有板块列表

    返回10个板块的基本信息
    """
    try:
        # 查询所有板块
        query = """
            SELECT *
            FROM sectors
            ORDER BY code
        """

        sectors = db_manager.execute_query(query)

        return create_success_response(
            sectors,
            total=len(sectors)
        )

    except Exception as e:
        print(f"[-] Error in get_sectors: {e}")
        return create_error_response("INTERNAL_ERROR", str(e))


@router.get("/sectors/{code}", response_model=None)
async def get_sector_detail(code: str):
    """
    获取板块详细信息

    包含板块信息和该板块下的股票列表
    """
    try:
        # 查询板块信息
        sector_query = """
            SELECT *
            FROM sectors
            WHERE code = ?
        """

        sector = db_manager.execute_query(sector_query, (code,), fetch_one=True)

        if not sector:
            return create_error_response("NOT_FOUND", f"Sector {code} not found")

        # 查询板块下的股票
        stocks_query = """
            SELECT s.*, sm.market_cap, sm.market_cap_tier, sm.beta
            FROM stocks s
            LEFT JOIN stock_metadata sm ON s.symbol = sm.symbol
            WHERE s.sector_code = ? AND s.is_active = 1
            ORDER BY sm.market_cap DESC
        """

        stocks = db_manager.execute_query(stocks_query, (code,))

        # 组合结果
        result = dict(sector)
        result['stocks'] = stocks
        result['stock_count'] = len(stocks)

        return create_success_response(result)

    except Exception as e:
        print(f"[-] Error in get_sector_detail: {e}")
        return create_error_response("INTERNAL_ERROR", str(e))
