"""
Stock API Routes
股票相关API路由
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
import sqlite3

from api.schemas import (
    StockSummary,
    StockDetail,
    KlineData,
    StockListResponse,
    KlineListResponse,
    create_success_response,
    create_error_response
)
from lib.db_manager_sqlite import get_db_manager


router = APIRouter()
db_manager = get_db_manager()


@router.get("/stocks", response_model=None)
async def get_stocks(
    sector: Optional[str] = Query(None, description="板块代码筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(100, ge=1, le=500, description="每页数量")
):
    """
    获取股票列表

    支持分页和板块筛选
    """
    try:
        # 构建查询
        offset = (page - 1) * page_size

        # 基础查询
        base_query = """
            SELECT s.*, sm.market_cap, sm.market_cap_tier, sm.beta
            FROM stocks s
            LEFT JOIN stock_metadata sm ON s.symbol = sm.symbol
            WHERE s.is_active = 1
        """

        count_query = """
            SELECT COUNT(*) as total
            FROM stocks s
            WHERE s.is_active = 1
        """

        params = []

        # 添加板块筛选
        if sector:
            base_query += " AND s.sector_code = ?"
            count_query += " AND s.sector_code = ?"
            params.append(sector)

        # 添加排序和分页
        base_query += " ORDER BY sm.market_cap DESC LIMIT ? OFFSET ?"
        params_with_pagination = params + [page_size, offset]

        # 执行查询
        stocks = db_manager.execute_query(base_query, tuple(params_with_pagination))
        total = db_manager.execute_query(count_query, tuple(params), fetch_one=True)

        return create_success_response(
            stocks,
            total=total['total'] if total else 0,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        print(f"[-] Error in get_stocks: {e}")
        return create_error_response("INTERNAL_ERROR", str(e))


@router.get("/stocks/{symbol}", response_model=None)
async def get_stock_detail(symbol: str):
    """
    获取股票详细信息

    包含基本信息、完整元数据、HAPPY300成分信息和所属指数列表
    """
    try:
        # 查询股票详细信息（包含完整元数据）
        query = """
            SELECT 
                s.symbol,
                s.name,
                s.sector_code,
                sec.name as sector_name,
                s.current_price,
                s.previous_close,
                s.change_value,
                s.change_pct,
                s.is_active,
                sm.market_cap,
                sm.market_cap_tier,
                sm.beta,
                sm.volatility,
                sm.outstanding_shares,
                sm.listing_date
            FROM stocks s
            LEFT JOIN stock_metadata sm ON s.symbol = sm.symbol
            LEFT JOIN sectors sec ON s.sector_code = sec.code
            WHERE s.symbol = ? AND s.is_active = 1
        """

        stock = db_manager.execute_query(query, (symbol,), fetch_one=True)

        if not stock:
            return create_error_response("NOT_FOUND", f"Stock {symbol} not found")

        # 查询该股票所属的所有指数（包括权重）
        indices_query = """
            SELECT 
                ic.index_code,
                i.name as index_name,
                ic.weight
            FROM index_constituents ic
            LEFT JOIN indices i ON ic.index_code = i.code
            WHERE ic.stock_symbol = ?
            ORDER BY ic.weight DESC
        """
        
        indices = db_manager.execute_query(indices_query, (symbol,))
        
        # 检查是否为 HAPPY300 成分股
        is_happy300 = False
        weight_in_happy300 = None
        
        for index in indices:
            if index['index_code'] == 'HAPPY300':
                is_happy300 = True
                weight_in_happy300 = index['weight']
                break
        
        # 构建返回数据
        result = dict(stock)
        result['is_happy300'] = is_happy300
        result['weight_in_happy300'] = weight_in_happy300
        result['indices'] = indices

        return create_success_response(result)

    except Exception as e:
        print(f"[-] Error in get_stock_detail: {e}")
        return create_error_response("INTERNAL_ERROR", str(e))


@router.get("/stocks/{symbol}/klines", response_model=None)
async def get_stock_klines(
    symbol: str,
    period: str = Query("1d", description="K线周期 (1m/5m/15m/30m/1h/4h/1d/1w/1M)"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量")
):
    """
    获取股票K线数据

    返回指定周期的K线数据，按时间倒序
    """
    try:
        # 验证股票是否存在
        stock_exists = db_manager.execute_query(
            "SELECT 1 FROM stocks WHERE symbol = ? AND is_active = 1",
            (symbol,),
            fetch_one=True
        )

        if not stock_exists:
            return create_error_response("NOT_FOUND", f"Stock {symbol} not found")

        # 查询K线数据
        query = """
            SELECT *
            FROM price_data
            WHERE target_type = 'STOCK'
            AND target_code = ?
            ORDER BY datetime DESC
            LIMIT ?
        """

        klines = db_manager.execute_query(query, (symbol, limit))

        # 按时间正序排列（前端需要从旧到新）
        klines.reverse()

        return create_success_response(
            klines,
            total=len(klines),
            period=period,
            symbol=symbol
        )

    except Exception as e:
        print(f"[-] Error in get_stock_klines: {e}")
        return create_error_response("INTERNAL_ERROR", str(e))


@router.get("/stocks/{symbol}/metadata", response_model=None)
async def get_stock_metadata(symbol: str):
    """
    获取股票元数据

    包含Beta系数、波动率、市值等静态属性
    """
    try:
        query = """
            SELECT *
            FROM stock_metadata
            WHERE symbol = ?
        """

        metadata = db_manager.execute_query(query, (symbol,), fetch_one=True)

        if not metadata:
            return create_error_response("NOT_FOUND", f"Stock metadata for {symbol} not found")

        return create_success_response(metadata)

    except Exception as e:
        print(f"[-] Error in get_stock_metadata: {e}")
        return create_error_response("INTERNAL_ERROR", str(e))
