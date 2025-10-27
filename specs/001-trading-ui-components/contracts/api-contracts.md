# API Contracts: TradingView 风格交易界面核心组件

**Feature**: 001-trading-ui-components
**Date**: 2025-10-24

## Overview

本功能为纯前端 UI 组件，使用后端已实现的 API。所有 API 端点已在后端完成，本文档仅作为前端组件与后端 API 的集成契约参考。

## Backend API Endpoints (已实现)

### 1. 账户管理

#### GET `/api/v1/accounts/{account_id}`
获取账户信息

**Response**: `{ success: true, data: Account }`

---

### 2. 资产管理

#### GET `/api/v1/assets`
获取资产列表

**Query Parameters**:
- `page`: int (default: 1)
- `page_size`: int (default: 50)

**Response**: `{ success: true, data: { assets: Asset[], total: number } }`

---

#### GET `/api/v1/assets/search`
搜索资产

**Query Parameters**:
- `keyword`: string
- `page_size`: int (default: 20)

**Response**: `{ success: true, data: { assets: Asset[], total: number } }`

---

#### GET `/api/v1/assets/{symbol}`
获取资产详情

**Response**: `{ success: true, data: Asset }`

---

#### GET `/api/v1/assets/{symbol}/price`
获取资产当前价格

**Response**: `{ success: true, data: { price: string } }`

---

### 3. 交易管理

#### POST `/api/v1/trades/buy`
执行买入交易

**Request Body**:
```json
{
  "account_id": number,
  "asset_symbol": string,
  "quantity": string,
  "price": string
}
```

**Response**: `{ success: true, message: "买入成功", data: Trade }`

**Error Response**:
```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_BALANCE",
    "message": "余额不足"
  }
}
```

---

#### POST `/api/v1/trades/sell`
执行卖出交易

**Request Body**:
```json
{
  "account_id": number,
  "asset_symbol": string,
  "quantity": string,
  "price": string
}
```

**Response**: `{ success: true, message: "卖出成功", data: Trade }`

**Error Response**:
```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_HOLDINGS",
    "message": "持仓不足"
  }
}
```

---

#### GET `/api/v1/trades/history`
获取交易历史

**Query Parameters**:
- `account_id`: number (required)
- `asset_symbol`: string (optional)
- `trade_type`: "BUY" | "SELL" (optional)
- `page`: number (default: 1)
- `page_size`: number (default: 20)

**Response**:
```json
{
  "success": true,
  "data": {
    "trades": Trade[],
    "total": number,
    "page": number,
    "page_size": number
  }
}
```

---

### 4. 持仓管理

#### GET `/api/v1/holdings/{account_id}`
获取持仓列表

**Response**:
```json
{
  "success": true,
  "data": {
    "holdings": Holding[],
    "summary": HoldingsSummary
  }
}
```

---

#### GET `/api/v1/holdings/{account_id}/summary`
获取持仓汇总

**Response**:
```json
{
  "success": true,
  "data": {
    "account_balance": string,
    "total_market_value": string,
    "total_assets": string,
    "total_cost": string,
    "total_profit": string,
    "total_profit_rate": string,
    "holdings_count": number,
    "asset_allocation": AssetAllocation[]
  }
}
```

---

## Frontend Integration

所有 API 调用已封装在 `frontend/src/lib/api/trading.ts`：

```typescript
import * as api from '@/lib/api/trading';

// 示例调用
const account = await api.getAccount(1);
const assets = await api.searchAssets('银行');
const trade = await api.buyAsset({ account_id: 1, asset_symbol: '600000.SH', quantity: '100', price: '12.5' });
const holdings = await api.getHoldings(1);
```

---

## Error Handling

所有错误通过 Axios 拦截器统一处理（`frontend/src/lib/api/client.ts`）：

1. 400 Bad Request → "请求参数错误"
2. 401 Unauthorized → "未授权，请登录"
3. 404 Not Found → "请求的资源不存在"
4. 500 Server Error → "服务器内部错误"
5. Network Error → "网络错误，请检查网络连接"

业务错误通过 `error.code` 和 `error.message` 传递。

---

## Notes

- 所有 API 端点已在后端完整实现并测试通过
- 前端组件只需调用已封装的 API 函数
- 无需修改后端代码
