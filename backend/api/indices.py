"""
Index API Routes
指数相关API路由
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from api.schemas import create_success_response, create_error_response
from lib.db_manager_sqlite import get_db_manager


router = APIRouter()
db_manager = get_db_manager()


@router.get("/indices", response_model=None)
async def get_indices(
    index_type: Optional[str] = None,
):
    """
    获取指数列表

    支持按类型筛选：
    - CORE: 核心指数（沪深300、上证50等）
    - SECTOR: 板块指数
    
    Args:
        index_type: 指数类型筛选 (CORE/SECTOR)
    """
    try:
        # 构建查询
        query = """
            SELECT *
            FROM indices
            WHERE 1=1
        """
        params = []

        # 添加类型筛选
        if index_type:
            query += " AND index_type = ?"
            params.append(index_type)

        query += " ORDER BY code"

        # 执行查询
        indices = db_manager.execute_query(query, tuple(params))

        return create_success_response(
            indices,
            total=len(indices)
        )

    except Exception as e:
        print(f"[-] Error in get_indices: {e}")
        return create_error_response("INTERNAL_ERROR", str(e))


@router.get("/indices/{code}", response_model=None)
async def get_index_detail(code: str):
    """
    获取指数详细信息

    包含指数基本信息和成分股列表
    """
    try:
        # 查询指数基本信息
        index_query = """
            SELECT *
            FROM indices
            WHERE code = ?
        """

        index = db_manager.execute_query(index_query, (code,), fetch_one=True)

        if not index:
            return create_error_response("NOT_FOUND", f"Index {code} not found")

        # 查询成分股
        constituents_query = """
            SELECT ic.*, s.name as stock_name, s.current_price
            FROM index_constituents ic
            LEFT JOIN stocks s ON ic.stock_symbol = s.symbol
            WHERE ic.index_code = ? AND ic.is_active = 1
            ORDER BY ic.weight DESC
        """

        constituents = db_manager.execute_query(constituents_query, (code,))

        # 组合结果
        result = dict(index)
        result['constituents'] = constituents
        result['constituent_count'] = len(constituents)

        return create_success_response(result)

    except Exception as e:
        print(f"[-] Error in get_index_detail: {e}")
        return create_error_response("INTERNAL_ERROR", str(e))


@router.get("/indices/{code}/klines", response_model=None)
async def get_index_klines(
    code: str,
    period: str = Query("1d", description="K线周期"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量")
):
    """
    获取指数K线数据

    返回指定周期的K线数据，按时间倒序
    """
    try:
        # 验证指数是否存在
        index_exists = db_manager.execute_query(
            "SELECT 1 FROM indices WHERE code = ?",
            (code,),
            fetch_one=True
        )

        if not index_exists:
            return create_error_response("NOT_FOUND", f"Index {code} not found")

        # 查询K线数据
        query = """
            SELECT *
            FROM price_data
            WHERE target_type = 'INDEX'
            AND target_code = ?
            ORDER BY datetime DESC
            LIMIT ?
        """

        klines = db_manager.execute_query(query, (code, limit))

        # 按时间正序排列
        klines.reverse()

        return create_success_response(
            klines,
            total=len(klines),
            period=period,
            index_code=code
        )

    except Exception as e:
        print(f"[-] Error in get_index_klines: {e}")
        return create_error_response("INTERNAL_ERROR", str(e))
