"""
持仓模型
对应数据库 sim_holdings 表
"""
from decimal import Decimal
from tortoise import fields
from tortoise.models import Model


class SimHolding(Model):
    """
    模拟持仓表模型
    记录用户在模拟账户中的持仓情况
    """

    id = fields.IntField(pk=True, description="持仓ID")
    account_id = fields.IntField(description="账户ID")
    asset_id = fields.IntField(description="资产ID")
    quantity = fields.DecimalField(max_digits=18, decimal_places=4, description="持有数量")
    avg_price = fields.DecimalField(max_digits=18, decimal_places=4, description="平均成本价")

    # 外键关系
    account: fields.ForeignKeyRelation["SimAccount"] = fields.ForeignKeyField(
        "models.SimAccount", related_name="holdings", on_delete=fields.CASCADE
    )
    asset: fields.ForeignKeyRelation["Asset"] = fields.ForeignKeyField(
        "models.Asset", related_name="holdings", on_delete=fields.CASCADE
    )

    class Meta:
        table = "sim_holdings"
        table_description = "模拟持仓表"
        unique_together = (("account_id", "asset_id"),)  # 账户和资产组合唯一
        indexes = [
            ("account_id",),  # 账户索引
        ]

    def __str__(self):
        return f"SimHolding(account_id={self.account_id}, asset_id={self.asset_id}, qty={self.quantity})"

    def __repr__(self):
        return f"<SimHolding {self.quantity}@{self.avg_price}>"

    @property
    def cost(self) -> Decimal:
        """计算持仓成本"""
        return self.quantity * self.avg_price

    def calculate_profit(self, current_price: Decimal) -> tuple[Decimal, Decimal, Decimal]:
        """
        计算持仓盈亏

        Args:
            current_price: 当前价格

        Returns:
            (市值, 盈亏金额, 盈亏率)
        """
        cost = self.cost
        market_value = self.quantity * current_price
        profit = market_value - cost
        profit_rate = (profit / cost * 100) if cost > 0 else Decimal(0)

        return market_value, profit, profit_rate
