"""
账户服务
处理账户相关的业务逻辑
"""
from decimal import Decimal
from typing import List, Optional, Dict
from tortoise.exceptions import DoesNotExist

from models.account import SimAccount
from models.holding import SimHolding
from models.trade import SimTrade
from exceptions import AccountNotFoundError, AccountLimitReachedError


class AccountService:
    """账户服务类"""

    MAX_ACCOUNTS_PER_USER = 3  # 每个用户最多创建3个账户

    @staticmethod
    async def create_account(
        user_id: int,
        account_name: str,
        initial_balance: Decimal = Decimal("100000.00"),
    ) -> SimAccount:
        """
        创建模拟账户

        Args:
            user_id: 用户ID
            account_name: 账户名称
            initial_balance: 初始资金

        Returns:
            创建的账户对象

        Raises:
            AccountLimitReachedError: 账户数量达到上限
        """
        # 检查用户账户数量
        existing_count = await SimAccount.filter(user_id=user_id).count()
        if existing_count >= AccountService.MAX_ACCOUNTS_PER_USER:
            raise AccountLimitReachedError(
                f"每个用户最多创建 {AccountService.MAX_ACCOUNTS_PER_USER} 个账户"
            )

        # 创建账户
        account = await SimAccount.create(
            user_id=user_id,
            account_name=account_name,
            initial_balance=initial_balance,
            current_balance=initial_balance,
        )

        return account

    @staticmethod
    async def get_account(account_id: int) -> SimAccount:
        """
        获取账户详情

        Args:
            account_id: 账户ID

        Returns:
            账户对象

        Raises:
            AccountNotFoundError: 账户不存在
        """
        try:
            account = await SimAccount.get(id=account_id)
            return account
        except DoesNotExist:
            raise AccountNotFoundError(f"账户 {account_id} 不存在")

    @staticmethod
    async def get_user_accounts(
        user_id: int, page: int = 1, page_size: int = 10
    ) -> tuple[List[SimAccount], int]:
        """
        获取用户的所有账户

        Args:
            user_id: 用户ID
            page: 页码
            page_size: 每页数量

        Returns:
            (账户列表, 总数)
        """
        # 计算偏移量
        offset = (page - 1) * page_size

        # 查询账户
        accounts = await SimAccount.filter(user_id=user_id).offset(offset).limit(page_size)

        # 获取总数
        total = await SimAccount.filter(user_id=user_id).count()

        return accounts, total

    @staticmethod
    async def reset_account(account_id: int) -> SimAccount:
        """
        重置账户（清空持仓和交易记录，恢复初始资金）

        Args:
            account_id: 账户ID

        Returns:
            重置后的账户对象

        Raises:
            AccountNotFoundError: 账户不存在
        """
        # 获取账户
        account = await AccountService.get_account(account_id)

        # 删除所有持仓
        await SimHolding.filter(account_id=account_id).delete()

        # 删除所有交易记录
        await SimTrade.filter(account_id=account_id).delete()

        # 重置余额
        account.current_balance = account.initial_balance
        await account.save()

        return account

    @staticmethod
    async def delete_account(account_id: int) -> None:
        """
        删除账户

        Args:
            account_id: 账户ID

        Raises:
            AccountNotFoundError: 账户不存在
        """
        account = await AccountService.get_account(account_id)
        await account.delete()

    @staticmethod
    async def calculate_account_summary(account: SimAccount) -> Dict:
        """
        计算账户汇总信息

        Args:
            account: 账户对象

        Returns:
            包含总资产、总盈亏、收益率的字典
        """
        # 计算总资产和盈亏
        total_assets = await account.calculate_total_assets()
        total_profit, profit_rate = await account.calculate_profit()

        return {
            "total_assets": total_assets,
            "total_profit": total_profit,
            "profit_rate": profit_rate,
        }

    @staticmethod
    async def update_account_name(account_id: int, new_name: str) -> SimAccount:
        """
        更新账户名称

        Args:
            account_id: 账户ID
            new_name: 新名称

        Returns:
            更新后的账户对象

        Raises:
            AccountNotFoundError: 账户不存在
        """
        account = await AccountService.get_account(account_id)
        account.account_name = new_name
        await account.save()
        return account
