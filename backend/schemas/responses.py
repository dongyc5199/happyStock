"""
API 响应模式
定义所有 API 响应的数据结构
"""
from decimal import Decimal
from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field


# ==================== 通用响应 ====================

class SuccessResponse(BaseModel):
    """成功响应基类"""

    success: bool = Field(default=True, description="是否成功")
    message: Optional[str] = Field(default=None, description="消息")
    data: Optional[Any] = Field(default=None, description="数据")


class ErrorResponse(BaseModel):
    """错误响应"""

    success: bool = Field(default=False, description="是否成功")
    error: dict = Field(..., description="错误信息")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": {
                    "code": "INSUFFICIENT_BALANCE",
                    "message": "账户余额不足",
                },
            }
        }


# ==================== 账户相关响应 ====================

class AccountResponse(BaseModel):
    """账户响应"""

    id: int = Field(..., description="账户ID")
    user_id: int = Field(..., description="用户ID")
    account_name: str = Field(..., description="账户名称")
    initial_balance: Decimal = Field(..., description="初始资金")
    current_balance: Decimal = Field(..., description="当前余额")
    total_assets: Optional[Decimal] = Field(None, description="总资产")
    total_profit: Optional[Decimal] = Field(None, description="总盈亏")
    profit_rate: Optional[Decimal] = Field(None, description="收益率")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "account_name": "我的第一个账户",
                "initial_balance": 100000.00,
                "current_balance": 85000.00,
                "total_assets": 125000.00,
                "total_profit": 25000.00,
                "profit_rate": 25.0,
                "created_at": "2025-10-23T10:00:00",
            }
        }


class AccountListResponse(BaseModel):
    """账户列表响应"""

    success: bool = Field(default=True)
    data: dict = Field(..., description="数据")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "accounts": [],
                    "total": 2,
                    "page": 1,
                    "page_size": 10,
                },
            }
        }


# ==================== 交易相关响应 ====================

class TradeResponse(BaseModel):
    """交易响应"""

    trade_id: int = Field(..., description="交易ID")
    account_id: int = Field(..., description="账户ID")
    asset_id: int = Field(..., description="资产ID")
    asset_symbol: str = Field(..., description="资产代码")
    asset_name: str = Field(..., description="资产名称")
    trade_type: str = Field(..., description="交易类型")
    quantity: Decimal = Field(..., description="交易数量")
    price: Decimal = Field(..., description="交易价格")
    total_amount: Decimal = Field(..., description="交易总金额")
    profit: Optional[Decimal] = Field(None, description="盈亏金额(卖出时)")
    profit_rate: Optional[Decimal] = Field(None, description="收益率(卖出时)")
    trade_time: datetime = Field(..., description="交易时间")
    account_balance_after: Decimal = Field(..., description="交易后余额")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "trade_id": 1001,
                "account_id": 1,
                "asset_id": 5,
                "asset_symbol": "600000",
                "asset_name": "浦发银行",
                "trade_type": "BUY",
                "quantity": 100,
                "price": 12.50,
                "total_amount": 1250.00,
                "trade_time": "2025-10-23T14:30:00",
                "account_balance_after": 98750.00,
            }
        }


class TradeListItem(BaseModel):
    """交易列表项"""

    id: int
    trade_type: str
    asset_symbol: str
    asset_name: str
    quantity: Decimal
    price: Decimal
    total_amount: Decimal
    trade_time: datetime

    class Config:
        from_attributes = True


class TradeListResponse(BaseModel):
    """交易列表响应"""

    success: bool = Field(default=True)
    data: dict = Field(..., description="数据")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "trades": [],
                    "total": 10,
                    "page": 1,
                    "page_size": 20,
                },
            }
        }


# ==================== 持仓相关响应 ====================

class HoldingItem(BaseModel):
    """持仓项"""

    id: int = Field(..., description="持仓ID")
    asset_id: int = Field(..., description="资产ID")
    asset_symbol: str = Field(..., description="资产代码")
    asset_name: str = Field(..., description="资产名称")
    quantity: Decimal = Field(..., description="持仓数量")
    avg_price: Decimal = Field(..., description="平均成本价")
    current_price: Decimal = Field(..., description="当前价格")
    cost: Decimal = Field(..., description="成本")
    market_value: Decimal = Field(..., description="市值")
    profit: Decimal = Field(..., description="盈亏金额")
    profit_rate: Decimal = Field(..., description="收益率")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "asset_id": 5,
                "asset_symbol": "600000",
                "asset_name": "浦发银行",
                "quantity": 100,
                "avg_price": 12.50,
                "current_price": 13.00,
                "cost": 1250.00,
                "market_value": 1300.00,
                "profit": 50.00,
                "profit_rate": 4.0,
            }
        }


class HoldingSummary(BaseModel):
    """持仓汇总"""

    total_cost: Decimal = Field(..., description="总成本")
    total_market_value: Decimal = Field(..., description="总市值")
    total_profit: Decimal = Field(..., description="总盈亏")
    total_profit_rate: Decimal = Field(..., description="总收益率")


class HoldingsResponse(BaseModel):
    """持仓列表响应"""

    success: bool = Field(default=True)
    data: dict = Field(..., description="数据")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "holdings": [],
                    "summary": {
                        "total_cost": 1250.00,
                        "total_market_value": 1300.00,
                        "total_profit": 50.00,
                        "total_profit_rate": 4.0,
                    },
                },
            }
        }


class HoldingSummaryResponse(BaseModel):
    """持仓汇总响应"""

    success: bool = Field(default=True)
    data: dict = Field(..., description="数据")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "account_balance": 98750.00,
                    "total_market_value": 1300.00,
                    "total_assets": 100050.00,
                    "total_cost": 1250.00,
                    "total_profit": 50.00,
                    "total_profit_rate": 4.0,
                    "holdings_count": 1,
                    "asset_allocation": [],
                },
            }
        }


# ==================== 资产相关响应 ====================

class AssetResponse(BaseModel):
    """资产响应"""

    id: int = Field(..., description="资产ID")
    symbol: str = Field(..., description="资产代码")
    name: str = Field(..., description="资产名称")
    exchange: Optional[str] = Field(None, description="交易所")
    asset_type: str = Field(..., description="资产类型")
    current_price: Optional[Decimal] = Field(None, description="当前价格")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 5,
                "symbol": "600000",
                "name": "浦发银行",
                "exchange": "上海证券交易所",
                "asset_type": "股票",
                "current_price": 13.00,
                "created_at": "2025-10-20T00:00:00",
            }
        }


class AssetListResponse(BaseModel):
    """资产列表响应"""

    success: bool = Field(default=True)
    data: dict = Field(..., description="数据")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "assets": [],
                    "total": 100,
                    "page": 1,
                    "page_size": 50,
                },
            }
        }


class AssetPriceResponse(BaseModel):
    """资产价格响应"""

    success: bool = Field(default=True)
    data: dict = Field(..., description="数据")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "symbol": "600000",
                    "price": 13.00,
                    "timestamp": "2025-10-23T15:00:00",
                },
            }
        }
