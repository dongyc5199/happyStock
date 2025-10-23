"""
模拟账户模型
对应数据库 sim_accounts 表
"""
from decimal import Decimal
from tortoise import fields
from tortoise.models import Model


class SimAccount(Model):
    """
    模拟账户表模型
    存储用户的模拟交易账户信息
    """

    id = fields.IntField(pk=True, description="账户ID")
    user_id = fields.IntField(description="用户ID")
    account_name = fields.CharField(max_length=100, description="账户名称")
    initial_balance = fields.DecimalField(
        max_digits=18, decimal_places=2, description="初始资金"
    )
    current_balance = fields.DecimalField(
        max_digits=18, decimal_places=2, description="当前可用资金"
    )
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    # 外键关系
    user: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User", related_name="accounts", on_delete=fields.CASCADE
    )

    class Meta:
        table = "sim_accounts"
        table_description = "模拟账户表"

    def __str__(self):
        return f"SimAccount(id={self.id}, name={self.account_name}, balance={self.current_balance})"

    def __repr__(self):
        return f"<SimAccount {self.account_name}>"

    async def calculate_total_assets(self) -> Decimal:
        """
        计算总资产 = 当前余额 + 持仓市值

        Returns:
            总资产金额
        """
        # 导入放在方法内避免循环导入
        from models.holding import SimHolding

        # 查询所有持仓
        holdings = await SimHolding.filter(account_id=self.id)

        # 计算持仓总市值 (这里暂时使用成本价，实际应该用当前价)
        holdings_value = sum(
            holding.quantity * holding.avg_price for holding in holdings
        )

        return self.current_balance + holdings_value

    async def calculate_profit(self) -> tuple[Decimal, Decimal]:
        """
        计算总盈亏

        Returns:
            (盈亏金额, 收益率)
        """
        total_assets = await self.calculate_total_assets()
        profit = total_assets - self.initial_balance
        profit_rate = (
            (profit / self.initial_balance) * 100 if self.initial_balance > 0 else Decimal(0)
        )
        return profit, profit_rate
