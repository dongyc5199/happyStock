"""
资产模型
对应数据库 assets 表
"""
from tortoise import fields
from tortoise.models import Model


class Asset(Model):
    """
    金融资产表模型
    存储模拟交易中可用的金融产品，如股票、基金
    """

    id = fields.IntField(pk=True, description="资产ID")
    symbol = fields.CharField(max_length=20, unique=True, description="股票代码/唯一标识符")
    name = fields.CharField(max_length=100, description="资产名称")
    exchange = fields.CharField(max_length=50, null=True, description="所属交易所")
    asset_type = fields.CharField(max_length=20, description="资产类型")  # 股票/基金/虚拟货币
    current_price = fields.DecimalField(
        max_digits=18, decimal_places=4, null=True, description="当前价格"
    )
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "assets"
        table_description = "金融资产表"
        indexes = [
            ("symbol",),  # 股票代码索引
            ("asset_type",),  # 资产类型索引
        ]

    def __str__(self):
        return f"Asset(symbol={self.symbol}, name={self.name})"

    def __repr__(self):
        return f"<Asset {self.symbol} - {self.name}>"
