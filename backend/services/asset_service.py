"""
资产服务
处理资产相关的业务逻辑
"""
from decimal import Decimal
from typing import List, Optional
from tortoise.exceptions import DoesNotExist

from models.asset import Asset
from exceptions import AssetNotFoundError


class AssetService:
    """资产服务类"""

    @staticmethod
    async def get_assets(
        asset_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[List[Asset], int]:
        """
        获取资产列表

        Args:
            asset_type: 资产类型（股票、基金等），为空则返回所有
            page: 页码
            page_size: 每页数量

        Returns:
            (资产列表, 总数)
        """
        # 计算偏移量
        offset = (page - 1) * page_size

        # 构建查询
        query = Asset.all()
        if asset_type:
            query = query.filter(asset_type=asset_type)

        # 查询资产
        assets = await query.offset(offset).limit(page_size)

        # 获取总数
        if asset_type:
            total = await Asset.filter(asset_type=asset_type).count()
        else:
            total = await Asset.all().count()

        return assets, total

    @staticmethod
    async def get_asset_by_symbol(symbol: str) -> Asset:
        """
        根据资产代码获取资产

        Args:
            symbol: 资产代码

        Returns:
            资产对象

        Raises:
            AssetNotFoundError: 资产不存在
        """
        try:
            asset = await Asset.get(symbol=symbol)
            return asset
        except DoesNotExist:
            raise AssetNotFoundError(f"资产 {symbol} 不存在")

    @staticmethod
    async def search_assets(
        keyword: str,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[List[Asset], int]:
        """
        搜索资产（按名称或代码）

        Args:
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量

        Returns:
            (资产列表, 总数)
        """
        # 计算偏移量
        offset = (page - 1) * page_size

        # 搜索资产（模糊匹配名称或代码）
        assets = (
            await Asset.filter(name__icontains=keyword)
            .union(Asset.filter(symbol__icontains=keyword))
            .offset(offset)
            .limit(page_size)
        )

        # 获取总数
        total = await (
            Asset.filter(name__icontains=keyword)
            .union(Asset.filter(symbol__icontains=keyword))
            .count()
        )

        return assets, total

    @staticmethod
    async def get_asset_price(symbol: str) -> Decimal:
        """
        获取资产当前价格

        当前为 Mock 实现，返回资产的 current_price 字段
        未来可接入真实的市场数据 API

        Args:
            symbol: 资产代码

        Returns:
            当前价格

        Raises:
            AssetNotFoundError: 资产不存在
        """
        asset = await AssetService.get_asset_by_symbol(symbol)

        # Mock 实现：返回数据库中的价格
        # TODO: 未来接入真实市场数据 API（如新浪财经、东方财富等）
        if asset.current_price is None:
            # 如果没有价格数据，返回默认值 0
            return Decimal("0.00")

        return asset.current_price

    @staticmethod
    async def update_asset_price(symbol: str, price: Decimal) -> Asset:
        """
        更新资产价格

        Args:
            symbol: 资产代码
            price: 新价格

        Returns:
            更新后的资产对象

        Raises:
            AssetNotFoundError: 资产不存在
        """
        asset = await AssetService.get_asset_by_symbol(symbol)
        asset.current_price = price
        await asset.save()
        return asset
