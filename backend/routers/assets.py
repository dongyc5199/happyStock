"""
资产管理 API 路由
"""
from fastapi import APIRouter, Path, Query, status
from typing import Optional

from services.asset_service import AssetService
from schemas.responses import AssetResponse, SuccessResponse

router = APIRouter()


@router.get(
    "/assets",
    response_model=SuccessResponse,
    summary="获取资产列表",
    description="获取可交易资产列表，支持分页和类型筛选",
)
async def get_assets(
    asset_type: Optional[str] = Query(None, description="资产类型（股票、基金等）"),
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(50, description="每页数量", ge=1, le=100),
):
    """
    获取资产列表

    支持按类型筛选和分页查询
    """
    # 获取资产列表
    assets, total = await AssetService.get_assets(
        asset_type=asset_type,
        page=page,
        page_size=page_size,
    )

    # 转换为响应模型
    assets_data = [
        AssetResponse.model_validate(asset).model_dump()
        for asset in assets
    ]

    return SuccessResponse(
        success=True,
        data={
            "assets": assets_data,
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    )


@router.get(
    "/assets/search",
    response_model=SuccessResponse,
    summary="搜索资产",
    description="按名称或代码搜索资产",
)
async def search_assets(
    keyword: str = Query(..., description="搜索关键词", min_length=1),
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(50, description="每页数量", ge=1, le=100),
):
    """
    搜索资产

    支持模糊匹配资产名称或代码
    """
    # 搜索资产
    assets, total = await AssetService.search_assets(
        keyword=keyword,
        page=page,
        page_size=page_size,
    )

    # 转换为响应模型
    assets_data = [
        AssetResponse.model_validate(asset).model_dump()
        for asset in assets
    ]

    return SuccessResponse(
        success=True,
        data={
            "assets": assets_data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "keyword": keyword,
        },
    )


@router.get(
    "/assets/{symbol}",
    response_model=SuccessResponse,
    summary="获取资产详情",
    description="根据资产代码获取资产详细信息",
)
async def get_asset(
    symbol: str = Path(..., description="资产代码", min_length=6, max_length=20)
):
    """
    获取资产详情

    返回资产的完整信息，包括名称、类型、当前价格等
    """
    # 获取资产
    asset = await AssetService.get_asset_by_symbol(symbol)

    # 转换为响应模型
    asset_data = AssetResponse.model_validate(asset).model_dump()

    return SuccessResponse(
        success=True,
        data=asset_data,
    )


@router.get(
    "/assets/{symbol}/price",
    response_model=SuccessResponse,
    summary="获取资产价格",
    description="获取资产的当前实时价格",
)
async def get_asset_price(
    symbol: str = Path(..., description="资产代码", min_length=6, max_length=20)
):
    """
    获取资产价格

    返回资产的当前价格
    当前为 Mock 实现，未来可接入真实市场数据
    """
    # 获取价格
    price = await AssetService.get_asset_price(symbol)

    return SuccessResponse(
        success=True,
        data={
            "symbol": symbol,
            "price": price,
        },
    )
