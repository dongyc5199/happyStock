"""
交易 API 路由
"""
from fastapi import APIRouter, Path, Query, status
from typing import Optional

from services.trade_service import TradeService
from schemas.requests import BuyTradeRequest, SellTradeRequest
from schemas.responses import SuccessResponse, TradeResponse

router = APIRouter()


@router.post(
    "/trades/buy",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="买入资产",
    description="执行买入交易，扣减账户余额，增加持仓",
)
async def buy_asset(request: BuyTradeRequest):
    """
    买入资产

    - **account_id**: 账户ID
    - **asset_symbol**: 资产代码
    - **quantity**: 买入数量
    - **price**: 买入价格
    """
    # 执行买入交易
    trade = await TradeService.buy_asset(
        account_id=request.account_id,
        asset_symbol=request.asset_symbol,
        quantity=request.quantity,
        price=request.price,
    )

    # 预加载关联数据
    await trade.fetch_related("asset", "account")

    # 计算交易后的账户余额
    account = trade.account
    total_amount = trade.quantity * trade.price

    return SuccessResponse(
        success=True,
        message="买入成功",
        data={
            "trade_id": trade.id,
            "account_id": trade.account_id,
            "asset_id": trade.asset_id,
            "asset_symbol": trade.asset.symbol,
            "asset_name": trade.asset.name,
            "trade_type": trade.trade_type,
            "quantity": trade.quantity,
            "price": trade.price,
            "total_amount": total_amount,
            "trade_time": trade.trade_time,
            "account_balance_after": account.current_balance,
        },
    )


@router.post(
    "/trades/sell",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="卖出资产",
    description="执行卖出交易，增加账户余额，减少持仓",
)
async def sell_asset(request: SellTradeRequest):
    """
    卖出资产

    - **account_id**: 账户ID
    - **asset_symbol**: 资产代码
    - **quantity**: 卖出数量
    - **price**: 卖出价格
    """
    # 执行卖出交易
    trade = await TradeService.sell_asset(
        account_id=request.account_id,
        asset_symbol=request.asset_symbol,
        quantity=request.quantity,
        price=request.price,
    )

    # 预加载关联数据
    await trade.fetch_related("asset", "account")

    # 计算交易后的账户余额
    account = trade.account
    total_amount = trade.quantity * trade.price

    return SuccessResponse(
        success=True,
        message="卖出成功",
        data={
            "trade_id": trade.id,
            "account_id": trade.account_id,
            "asset_id": trade.asset_id,
            "asset_symbol": trade.asset.symbol,
            "asset_name": trade.asset.name,
            "trade_type": trade.trade_type,
            "quantity": trade.quantity,
            "price": trade.price,
            "total_amount": total_amount,
            "trade_time": trade.trade_time,
            "account_balance_after": account.current_balance,
        },
    )


@router.get(
    "/trades/history",
    response_model=SuccessResponse,
    summary="获取交易历史",
    description="查询账户的历史交易记录，支持筛选和分页",
)
async def get_trade_history(
    account_id: int = Query(..., description="账户ID", gt=0),
    asset_symbol: Optional[str] = Query(None, description="资产代码（筛选）"),
    trade_type: Optional[str] = Query(None, description="交易类型（BUY/SELL）"),
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(20, description="每页数量", ge=1, le=100),
):
    """
    获取交易历史

    支持按资产和交易类型筛选，按时间倒序排列
    """
    # 获取交易历史
    trades, total = await TradeService.get_trade_history(
        account_id=account_id,
        asset_symbol=asset_symbol,
        trade_type=trade_type,
        page=page,
        page_size=page_size,
    )

    # 转换为响应格式
    trades_data = []
    for trade in trades:
        total_amount = trade.quantity * trade.price
        trades_data.append({
            "id": trade.id,
            "trade_type": trade.trade_type,
            "asset_symbol": trade.asset.symbol,
            "asset_name": trade.asset.name,
            "quantity": trade.quantity,
            "price": trade.price,
            "total_amount": total_amount,
            "trade_time": trade.trade_time,
        })

    return SuccessResponse(
        success=True,
        data={
            "trades": trades_data,
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    )
