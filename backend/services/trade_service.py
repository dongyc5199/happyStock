"""
交易服务
处理买入、卖出等交易业务逻辑
"""
from decimal import Decimal
from typing import List, Optional
from datetime import datetime
from tortoise.transactions import in_transaction

from models.account import SimAccount
from models.asset import Asset
from models.trade import SimTrade
from models.holding import SimHolding
from exceptions import (
    AccountNotFoundError,
    AssetNotFoundError,
    InsufficientBalanceError,
    InsufficientHoldingsError,
    InvalidQuantityError,
)


class TradeService:
    """交易服务类"""

    @staticmethod
    async def buy_asset(
        account_id: int,
        asset_symbol: str,
        quantity: Decimal,
        price: Decimal,
    ) -> SimTrade:
        """
        买入资产

        Args:
            account_id: 账户ID
            asset_symbol: 资产代码
            quantity: 买入数量
            price: 买入价格

        Returns:
            交易记录对象

        Raises:
            AccountNotFoundError: 账户不存在
            AssetNotFoundError: 资产不存在
            InsufficientBalanceError: 余额不足
            InvalidQuantityError: 交易数量无效
        """
        # 验证交易数量
        if quantity <= 0:
            raise InvalidQuantityError("交易数量必须大于0")

        # 计算交易总金额
        total_amount = quantity * price

        # 使用数据库事务确保原子性
        async with in_transaction() as conn:
            # 1. 获取账户（加锁防止并发）
            try:
                account = await SimAccount.get(id=account_id).using_db(conn)
            except Exception:
                raise AccountNotFoundError(f"账户 {account_id} 不存在")

            # 2. 获取资产
            try:
                asset = await Asset.get(symbol=asset_symbol).using_db(conn)
            except Exception:
                raise AssetNotFoundError(f"资产 {asset_symbol} 不存在")

            # 3. 检查账户余额
            if account.current_balance < total_amount:
                raise InsufficientBalanceError(
                    f"余额不足。当前余额: {account.current_balance}, 需要: {total_amount}"
                )

            # 4. 扣减账户余额
            account.current_balance -= total_amount
            await account.save(using_db=conn)

            # 5. 更新或创建持仓
            holding = await SimHolding.filter(
                account_id=account_id,
                asset_id=asset.id
            ).using_db(conn).first()

            if holding:
                # 更新现有持仓（计算新的平均成本价）
                old_cost = holding.quantity * holding.avg_price
                new_cost = old_cost + total_amount
                new_quantity = holding.quantity + quantity
                holding.avg_price = new_cost / new_quantity
                holding.quantity = new_quantity
                await holding.save(using_db=conn)
            else:
                # 创建新持仓
                holding = await SimHolding.create(
                    account_id=account_id,
                    asset_id=asset.id,
                    quantity=quantity,
                    avg_price=price,
                    using_db=conn
                )

            # 6. 创建交易记录
            trade = await SimTrade.create(
                account_id=account_id,
                asset_id=asset.id,
                trade_type="BUY",
                quantity=quantity,
                price=price,
                using_db=conn
            )

        return trade

    @staticmethod
    async def sell_asset(
        account_id: int,
        asset_symbol: str,
        quantity: Decimal,
        price: Decimal,
    ) -> SimTrade:
        """
        卖出资产

        Args:
            account_id: 账户ID
            asset_symbol: 资产代码
            quantity: 卖出数量
            price: 卖出价格

        Returns:
            交易记录对象

        Raises:
            AccountNotFoundError: 账户不存在
            AssetNotFoundError: 资产不存在
            InsufficientHoldingsError: 持仓不足
            InvalidQuantityError: 交易数量无效
        """
        # 验证交易数量
        if quantity <= 0:
            raise InvalidQuantityError("交易数量必须大于0")

        # 计算交易总金额
        total_amount = quantity * price

        # 使用数据库事务确保原子性
        async with in_transaction() as conn:
            # 1. 获取账户
            try:
                account = await SimAccount.get(id=account_id).using_db(conn)
            except Exception:
                raise AccountNotFoundError(f"账户 {account_id} 不存在")

            # 2. 获取资产
            try:
                asset = await Asset.get(symbol=asset_symbol).using_db(conn)
            except Exception:
                raise AssetNotFoundError(f"资产 {asset_symbol} 不存在")

            # 3. 获取持仓
            holding = await SimHolding.filter(
                account_id=account_id,
                asset_id=asset.id
            ).using_db(conn).first()

            if not holding:
                raise InsufficientHoldingsError(f"没有持有资产 {asset_symbol}")

            # 4. 检查持仓数量
            if holding.quantity < quantity:
                raise InsufficientHoldingsError(
                    f"持仓不足。当前持仓: {holding.quantity}, 需要卖出: {quantity}"
                )

            # 5. 增加账户余额
            account.current_balance += total_amount
            await account.save(using_db=conn)

            # 6. 更新持仓
            holding.quantity -= quantity
            if holding.quantity == 0:
                # 如果持仓清零，删除持仓记录
                await holding.delete(using_db=conn)
            else:
                await holding.save(using_db=conn)

            # 7. 创建交易记录
            trade = await SimTrade.create(
                account_id=account_id,
                asset_id=asset.id,
                trade_type="SELL",
                quantity=quantity,
                price=price,
                using_db=conn
            )

        return trade

    @staticmethod
    async def get_trade_history(
        account_id: int,
        asset_symbol: Optional[str] = None,
        trade_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[SimTrade], int]:
        """
        获取交易历史记录

        Args:
            account_id: 账户ID
            asset_symbol: 资产代码（可选）
            trade_type: 交易类型（BUY/SELL，可选）
            page: 页码
            page_size: 每页数量

        Returns:
            (交易记录列表, 总数)
        """
        # 计算偏移量
        offset = (page - 1) * page_size

        # 构建查询
        query = SimTrade.filter(account_id=account_id)

        if asset_symbol:
            asset = await Asset.get(symbol=asset_symbol)
            query = query.filter(asset_id=asset.id)

        if trade_type:
            query = query.filter(trade_type=trade_type.upper())

        # 查询交易记录（按时间倒序）
        trades = await query.order_by("-trade_time").offset(offset).limit(page_size).prefetch_related("asset")

        # 获取总数
        total = await query.count()

        return trades, total

    @staticmethod
    async def get_holdings(account_id: int) -> List[SimHolding]:
        """
        获取账户持仓

        Args:
            account_id: 账户ID

        Returns:
            持仓列表
        """
        holdings = await SimHolding.filter(account_id=account_id).prefetch_related("asset")
        return holdings

    @staticmethod
    async def calculate_holdings_summary(account_id: int) -> dict:
        """
        计算持仓汇总信息

        Args:
            account_id: 账户ID

        Returns:
            持仓汇总字典
        """
        # 获取持仓
        holdings = await TradeService.get_holdings(account_id)

        # 获取账户
        account = await SimAccount.get(id=account_id)

        # 初始化汇总数据
        total_cost = Decimal(0)
        total_market_value = Decimal(0)

        # 计算每个持仓的市值和成本
        for holding in holdings:
            cost = holding.quantity * holding.avg_price
            # 使用资产当前价格计算市值
            current_price = holding.asset.current_price or holding.avg_price
            market_value = holding.quantity * current_price

            total_cost += cost
            total_market_value += market_value

        # 计算总盈亏
        total_profit = total_market_value - total_cost
        total_profit_rate = (total_profit / total_cost * 100) if total_cost > 0 else Decimal(0)

        # 计算总资产
        total_assets = account.current_balance + total_market_value

        return {
            "account_balance": account.current_balance,
            "total_cost": total_cost,
            "total_market_value": total_market_value,
            "total_profit": total_profit,
            "total_profit_rate": total_profit_rate,
            "total_assets": total_assets,
            "holdings_count": len(holdings),
        }
