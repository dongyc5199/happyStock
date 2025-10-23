"""
交易记录模型
对应数据库 sim_trades 表
"""
from tortoise import fields
from tortoise.models import Model


class SimTrade(Model):
    """
    模拟交易记录表模型
    记录每一次模拟交易的详细信息
    """

    id = fields.IntField(pk=True, description="交易ID")
    account_id = fields.IntField(description="账户ID")
    asset_id = fields.IntField(description="资产ID")
    trade_type = fields.CharField(max_length=10, description="交易类型")  # BUY/SELL
    quantity = fields.DecimalField(max_digits=18, decimal_places=4, description="交易数量")
    price = fields.DecimalField(max_digits=18, decimal_places=4, description="成交价格")
    trade_time = fields.DatetimeField(auto_now_add=True, description="交易时间")

    # 外键关系
    account: fields.ForeignKeyRelation["SimAccount"] = fields.ForeignKeyField(
        "models.SimAccount", related_name="trades", on_delete=fields.CASCADE
    )
    asset: fields.ForeignKeyRelation["Asset"] = fields.ForeignKeyField(
        "models.Asset", related_name="trades", on_delete=fields.CASCADE
    )

    class Meta:
        table = "sim_trades"
        table_description = "模拟交易记录表"
        indexes = [
            ("account_id",),  # 账户索引
            ("asset_id",),  # 资产索引
            ("trade_time",),  # 交易时间索引（倒序）
        ]
        ordering = ["-trade_time"]  # 默认按时间倒序

    def __str__(self):
        return f"SimTrade(id={self.id}, type={self.trade_type}, asset_id={self.asset_id}, qty={self.quantity})"

    def __repr__(self):
        return f"<SimTrade {self.trade_type} {self.quantity}@{self.price}>"

    @property
    def total_amount(self):
        """计算交易总金额"""
        return self.quantity * self.price
