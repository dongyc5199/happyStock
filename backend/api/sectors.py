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

    返回10个板块的基本信息，包含实时平均涨跌幅
    """
    try:
        # 查询所有板块基础信息
        query = """
            SELECT code, name, name_en, beta, description
            FROM sectors
            ORDER BY code
        """

        sectors = db_manager.execute_query(query)

        # 为每个板块计算统计信息
        for sector in sectors:
            sector_code = sector['code']

            # 计算该板块的股票数量
            count_query = """
                SELECT COUNT(*) as stock_count
                FROM stocks
                WHERE sector_code = ? AND is_active = 1
            """
            count_result = db_manager.execute_query(
                count_query, (sector_code,), fetch_one=True
            )
            sector['stock_count'] = count_result['stock_count'] if count_result else 0

            # 计算该板块的平均涨跌幅
            avg_query = """
                SELECT AVG(change_pct) as avg_change_pct
                FROM stocks
                WHERE sector_code = ? AND is_active = 1
            """
            avg_result = db_manager.execute_query(
                avg_query, (sector_code,), fetch_one=True
            )
            avg_change = avg_result['avg_change_pct'] if avg_result and avg_result['avg_change_pct'] else 0.0
            sector['avg_change_pct'] = round(float(avg_change), 2)

            # 计算板块总市值
            cap_query = """
                SELECT SUM(sm.market_cap) as total_market_cap
                FROM stocks s
                JOIN stock_metadata sm ON s.symbol = sm.symbol
                WHERE s.sector_code = ? AND s.is_active = 1
            """
            cap_result = db_manager.execute_query(
                cap_query, (sector_code,), fetch_one=True
            )
            sector['total_market_cap'] = cap_result['total_market_cap'] if cap_result and cap_result['total_market_cap'] else 0

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
