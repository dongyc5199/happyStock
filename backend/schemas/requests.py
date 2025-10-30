"""
API 请求模式
定义所有 API 请求的数据结构
"""
from decimal import Decimal
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator


# ==================== 账户相关请求 ====================

class CreateAccountRequest(BaseModel):
    """创建账户请求"""

    user_id: int = Field(..., description="用户ID", gt=0)
    account_name: str = Field(..., description="账户名称", min_length=1, max_length=100)
    initial_balance: Decimal = Field(
        default=Decimal("100000.00"),
        description="初始资金",
        ge=Decimal("0.01"),
        decimal_places=2,
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "account_name": "我的第一个账户",
                "initial_balance": 100000.00,
            }
        }


class UpdateAccountRequest(BaseModel):
    """更新账户请求"""

    account_name: Optional[str] = Field(None, description="账户名称", max_length=100)

    class Config:
        json_schema_extra = {
            "example": {
                "account_name": "我的模拟账户",
            }
        }


# ==================== 交易相关请求 ====================

class BuyTradeRequest(BaseModel):
    """买入交易请求"""

    account_id: int = Field(..., description="账户ID", gt=0)
    asset_symbol: str = Field(..., description="资产代码", min_length=6, max_length=20)
    quantity: Decimal = Field(..., description="交易数量", gt=0, decimal_places=4)
    price: Decimal = Field(..., description="交易价格", gt=0, decimal_places=4)

    @validator("quantity")
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError("交易数量必须大于0")
        return v

    @validator("price")
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError("价格必须大于0")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "account_id": 1,
                "asset_symbol": "600000",
                "quantity": 100,
                "price": 12.50,
            }
        }


class SellTradeRequest(BaseModel):
    """卖出交易请求"""

    account_id: int = Field(..., description="账户ID", gt=0)
    asset_symbol: str = Field(..., description="资产代码", min_length=6, max_length=20)
    quantity: Decimal = Field(..., description="交易数量", gt=0, decimal_places=4)
    price: Decimal = Field(..., description="交易价格", gt=0, decimal_places=4)

    @validator("quantity")
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError("交易数量必须大于0")
        return v

    @validator("price")
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError("价格必须大于0")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "account_id": 1,
                "asset_symbol": "600000",
                "quantity": 50,
                "price": 13.00,
            }
        }


class TradeQueryParams(BaseModel):
    """交易历史查询参数"""

    trade_type: Optional[str] = Field(None, description="交易类型 (BUY/SELL)")
    asset_symbol: Optional[str] = Field(None, description="资产代码")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    page: int = Field(default=1, description="页码", ge=1)
    page_size: int = Field(default=20, description="每页数量", ge=1, le=100)

    class Config:
        json_schema_extra = {
            "example": {
                "trade_type": "BUY",
                "asset_symbol": "600000",
                "page": 1,
                "page_size": 20,
            }
        }


# ==================== 资产相关请求 ====================

class CreateAssetRequest(BaseModel):
    """创建资产请求"""

    symbol: str = Field(..., description="股票代码", min_length=6, max_length=20)
    name: str = Field(..., description="资产名称", min_length=1, max_length=100)
    exchange: Optional[str] = Field(None, description="交易所", max_length=50)
    asset_type: str = Field(..., description="资产类型", max_length=20)

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "600000",
                "name": "浦发银行",
                "exchange": "上海证券交易所",
                "asset_type": "股票",
            }
        }


class AssetQueryParams(BaseModel):
    """资产查询参数"""

    asset_type: Optional[str] = Field(None, description="资产类型")
    exchange: Optional[str] = Field(None, description="交易所")
    keyword: Optional[str] = Field(None, description="搜索关键词")
    page: int = Field(default=1, description="页码", ge=1)
    page_size: int = Field(default=50, description="每页数量", ge=1, le=100)

    class Config:
        json_schema_extra = {
            "example": {
                "asset_type": "股票",
                "keyword": "银行",
                "page": 1,
                "page_size": 50,
            }
        }
