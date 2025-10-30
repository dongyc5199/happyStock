"""
Pydantic 模式包
包含 API 请求和响应的数据模型
"""
from schemas.requests import (
    CreateAccountRequest,
    UpdateAccountRequest,
    BuyTradeRequest,
    SellTradeRequest,
    TradeQueryParams,
    CreateAssetRequest,
    AssetQueryParams,
)

from schemas.responses import (
    SuccessResponse,
    ErrorResponse,
    AccountResponse,
    AccountListResponse,
    TradeResponse,
    TradeListResponse,
    HoldingsResponse,
    HoldingSummaryResponse,
    AssetResponse,
    AssetListResponse,
    AssetPriceResponse,
)

__all__ = [
    # Requests
    "CreateAccountRequest",
    "UpdateAccountRequest",
    "BuyTradeRequest",
    "SellTradeRequest",
    "TradeQueryParams",
    "CreateAssetRequest",
    "AssetQueryParams",
    # Responses
    "SuccessResponse",
    "ErrorResponse",
    "AccountResponse",
    "AccountListResponse",
    "TradeResponse",
    "TradeListResponse",
    "HoldingsResponse",
    "HoldingSummaryResponse",
    "AssetResponse",
    "AssetListResponse",
    "AssetPriceResponse",
]
