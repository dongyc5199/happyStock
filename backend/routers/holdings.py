"""
持仓管理 API 路由
"""
from fastapi import APIRouter, Path, Query, status
from decimal import Decimal

from services.trade_service import TradeService
from schemas.responses import SuccessResponse

router = APIRouter()


@router.get(
    "/holdings/{account_id}",
    response_model=SuccessResponse,
    summary="获取账户持仓",
    description="获取指定账户的所有持仓信息，包括成本、市值、盈亏等",
)
async def get_holdings(
    account_id: int = Path(..., description="账户ID", gt=0)
):
    """
    获取账户持仓

    返回账户的所有持仓，包括：
    - 持仓资产信息
    - 持有数量
    - 平均成本价
    - 当前价格
    - 成本、市值、盈亏
    """
    # 获取持仓列表
    holdings = await TradeService.get_holdings(account_id)

    # 转换为响应格式
    holdings_data = []
    for holding in holdings:
        # 获取当前价格
        current_price = holding.asset.current_price or holding.avg_price

        # 计算市值、盈亏
        market_value, profit, profit_rate = holding.calculate_profit(current_price)
        cost = holding.quantity * holding.avg_price

        holdings_data.append({
            "id": holding.id,
            "asset_id": holding.asset_id,
            "asset_symbol": holding.asset.symbol,
            "asset_name": holding.asset.name,
            "quantity": holding.quantity,
            "avg_price": holding.avg_price,
            "current_price": current_price,
            "cost": cost,
            "market_value": market_value,
            "profit": profit,
            "profit_rate": profit_rate,
        })

    # 计算汇总信息
    summary = await TradeService.calculate_holdings_summary(account_id)

    return SuccessResponse(
        success=True,
        data={
            "holdings": holdings_data,
            "summary": {
                "total_cost": summary["total_cost"],
                "total_market_value": summary["total_market_value"],
                "total_profit": summary["total_profit"],
                "total_profit_rate": summary["total_profit_rate"],
            },
        },
    )


@router.get(
    "/holdings/{account_id}/summary",
    response_model=SuccessResponse,
    summary="获取持仓汇总",
    description="获取账户持仓的汇总统计信息",
)
async def get_holdings_summary(
    account_id: int = Path(..., description="账户ID", gt=0)
):
    """
    获取持仓汇总

    返回账户的持仓汇总信息：
    - 账户余额
    - 持仓总成本
    - 持仓总市值
    - 总盈亏金额和收益率
    - 总资产（余额 + 市值）
    - 持仓数量
    """
    # 计算汇总
    summary = await TradeService.calculate_holdings_summary(account_id)

    # 计算资产配置比例
    holdings = await TradeService.get_holdings(account_id)
    total_market_value = summary["total_market_value"]

    asset_allocation = []
    for holding in holdings:
        current_price = holding.asset.current_price or holding.avg_price
        market_value = holding.quantity * current_price
        percentage = (market_value / total_market_value * 100) if total_market_value > 0 else Decimal(0)

        asset_allocation.append({
            "asset_symbol": holding.asset.symbol,
            "asset_name": holding.asset.name,
            "market_value": market_value,
            "percentage": percentage,
        })

    return SuccessResponse(
        success=True,
        data={
            "account_balance": summary["account_balance"],
            "total_market_value": summary["total_market_value"],
            "total_assets": summary["total_assets"],
            "total_cost": summary["total_cost"],
            "total_profit": summary["total_profit"],
            "total_profit_rate": summary["total_profit_rate"],
            "holdings_count": summary["holdings_count"],
            "asset_allocation": asset_allocation,
        },
    )
