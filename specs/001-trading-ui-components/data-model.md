# Data Model: TradingView 风格交易界面核心组件

**Feature**: 001-trading-ui-components
**Date**: 2025-10-24
**Status**: Phase 1 Design

## Overview

本功能为纯前端 UI 层，数据模型已在 `frontend/src/types/trading.ts` 中定义。本文档描述前端组件使用的数据结构和状态管理模型。

## Frontend Data Models

### 1. 组件本地状态

#### CandlestickChart Component State

```typescript
interface ChartState {
  chart: IChartApi | null;           // Lightweight Charts 实例
  candlestickSeries: ISeriesApi<"Candlestick"> | null;  // K线系列
  volumeSeries: ISeriesApi<"Histogram"> | null;  // 成交量系列
  timeframe: 'D' | 'W' | 'M';        // 时间周期 (日/周/月)
  loading: boolean;                   // 加载状态
  error: string | null;               // 错误信息
}
```

**Validation Rules**:
- `timeframe` 必须是 'D', 'W', 'M' 之一
- `chart` 必须在组件挂载后初始化
- `loading` 在数据请求期间为 true

**State Transitions**:
```
IDLE → LOADING → LOADED / ERROR
     ↓
   UPDATING (切换时间周期)
```

---

#### TradePanel Component State

```typescript
interface TradePanelState {
  side: 'buy' | 'sell';              // 交易方向
  assetSymbol: string;               // 股票代码
  price: string;                     // 价格输入
  quantity: string;                  // 数量输入
  showConfirmDialog: boolean;        // 显示确认对话框
  submitting: boolean;               // 提交中状态
  errors: {                          // 表单验证错误
    assetSymbol?: string;
    price?: string;
    quantity?: string;
  };
}
```

**Validation Rules**:
- `assetSymbol` 不能为空
- `price` 必须 > 0 的数字
- `quantity` 必须 > 0 的数字
- 买入时：`price * quantity <= 账户余额`
- 卖出时：`quantity <= 持仓数量`

**State Transitions**:
```
IDLE → FILLING → VALIDATING → CONFIRMING → SUBMITTING → SUCCESS / ERROR
                                  ↓
                                CANCELLED (用户取消)
```

---

#### HoldingsList Component State

```typescript
interface HoldingsListState {
  holdings: Holding[];               // 持仓列表
  selectedHolding: Holding | null;   // 选中的持仓
  sortBy: 'profit' | 'value' | 'quantity';  // 排序字段
  sortOrder: 'asc' | 'desc';        // 排序方向
  loading: boolean;
}
```

**Validation Rules**:
- `holdings` 数组中每个元素必须符合 `Holding` 类型
- `sortBy` 必须是有效的排序字段

**Derived Data** (通过 `useMemo` 计算):
- 总成本 = Σ(holding.cost)
- 总市值 = Σ(holding.market_value)
- 总盈亏 = 总市值 - 总成本
- 盈亏率 = (总盈亏 / 总成本) * 100%

---

#### TradeHistory Component State

```typescript
interface TradeHistoryState {
  trades: Trade[];                   // 交易记录列表
  filter: {
    assetSymbol?: string;            // 股票代码筛选
    tradeType?: 'BUY' | 'SELL';     // 交易类型筛选
  };
  page: number;                      // 当前页码
  pageSize: number;                  // 每页大小
  total: number;                     // 总记录数
  loading: boolean;
  hasMore: boolean;                  // 是否有更多数据
}
```

**Validation Rules**:
- `page` 必须 >= 1
- `pageSize` 默认 20，范围 [10, 100]
- `total` 必须 >= 0

---

#### StockSearch Component State

```typescript
interface StockSearchState {
  query: string;                     // 搜索关键词
  results: Asset[];                  // 搜索结果
  loading: boolean;
  debouncedQuery: string;            // 防抖后的查询词
}
```

**Validation Rules**:
- 防抖延迟 300ms
- `query` 长度 < 50 字符
- 空查询时清空结果

---

### 2. 全局状态 (Zustand Store)

已在 `frontend/src/stores/tradingStore.ts` 中实现：

```typescript
interface TradingState {
  // 状态
  currentAccount: Account | null;
  accounts: Account[];
  holdings: Holding[];
  selectedAsset: Asset | null;
  recentTrades: Trade[];
  assets: Asset[];
  loading: boolean;
  error: string | null;

  // Actions
  setCurrentAccount: (account: Account | null) => void;
  setSelectedAsset: (asset: Asset | null) => void;
  setError: (error: string | null) => void;
  fetchAccount: (accountId: number) => Promise<void>;
  fetchHoldings: (accountId: number) => Promise<void>;
  fetchTradeHistory: (accountId: number, page?: number, pageSize?: number) => Promise<void>;
  fetchAssets: (page?: number, pageSize?: number) => Promise<void>;
  searchAssets: (keyword: string) => Promise<Asset[]>;
  executeBuy: (accountId: number, assetSymbol: string, quantity: string, price: string) => Promise<Trade>;
  executeSell: (accountId: number, assetSymbol: string, quantity: string, price: string) => Promise<Trade>;
  refreshData: (accountId: number) => Promise<void>;
}
```

**State Update Triggers**:
- 用户登录 → `fetchAccount`, `fetchHoldings`
- 选择股票 → `setSelectedAsset`, 更新图表
- 执行交易 → `executeBuy` / `executeSell`, 然后 `refreshData`
- 搜索股票 → `searchAssets`

---

## Data Flow

### 交易流程数据流

```
用户输入 (TradePanel)
  ↓
表单验证 (本地 state)
  ↓
显示确认对话框 (TradeConfirmDialog)
  ↓
用户确认
  ↓
调用 Zustand Store.executeBuy/executeSell
  ↓
API 请求 (tradingApi.buyAsset/sellAsset)
  ↓
后端处理 (TradeService)
  ↓
返回交易结果
  ↓
Zustand Store.refreshData
  ↓
更新 holdings, recentTrades, currentAccount
  ↓
组件重新渲染 (HoldingsList, TradeHistory, AccountHeader)
```

### K线图表数据流

```
用户选择股票 (StockListItem onClick)
  ↓
Zustand Store.setSelectedAsset
  ↓
CandlestickChart useEffect 监听 selectedAsset 变化
  ↓
调用 API 获取 K线数据 (假设后端提供)
  ↓
Lightweight Charts API 更新数据
  ↓
图表重新渲染
```

### 持仓盈亏实时更新数据流

```
定时器 (每 5秒) 或 WebSocket (未来)
  ↓
获取最新价格 (assetApi.getAssetPrice)
  ↓
更新 Asset.current_price
  ↓
HoldingsList useMemo 重新计算
  ↓
盈亏数值和颜色实时更新
```

---

## Relationships

### 组件与状态关系

```
TradingPage (主页面)
├── AccountHeader (读: currentAccount from Store)
├── StockSearch (读写: searchAssets from Store, 写: setSelectedAsset)
├── StockListItem[] (读: selectedAsset from Store, 写: setSelectedAsset)
├── CandlestickChart (读: selectedAsset from Store)
├── TradePanel (读: selectedAsset, currentAccount from Store, 写: executeBuy/Sell)
├── HoldingsList (读: holdings from Store, 写: setSelectedAsset)
└── TradeHistory (读: recentTrades from Store)
```

### 数据依赖关系

```
Account (账户)
  ↓ (has many)
Holding (持仓)
  ↓ (belongs to)
Asset (资产)

Account (账户)
  ↓ (has many)
Trade (交易记录)
  ↓ (belongs to)
Asset (资产)
```

---

## Performance Considerations

### 数据缓存策略

1. **Zustand Store**: 缓存最近获取的数据
2. **React.memo**: 缓存组件渲染结果
3. **useMemo**: 缓存计算结果（盈亏计算）
4. **useCallback**: 缓存回调函数

### 数据更新优化

1. **选择性订阅**: 组件只订阅需要的 Store 片段
2. **批量更新**: 使用 `refreshData` 批量更新多个状态
3. **防抖**: 搜索输入防抖 300ms
4. **虚拟化**: 大列表使用虚拟滚动

---

## Data Validation Summary

| Field | Type | Constraints | Validation Location |
|-------|------|-------------|---------------------|
| assetSymbol | string | 非空, < 20 chars | TradePanel, StockSearch |
| price | string | > 0, 数字格式 | TradePanel |
| quantity | string | > 0, 数字格式 | TradePanel |
| timeframe | 'D'\|'W'\|'M' | 枚举值 | CandlestickChart |
| page | number | >= 1 | TradeHistory |
| pageSize | number | [10, 100] | TradeHistory |

---

## Notes

- **已实现**: `frontend/src/types/trading.ts` 中的所有类型定义
- **已实现**: `frontend/src/stores/tradingStore.ts` 中的全局状态管理
- **待实现**: 各组件的本地状态管理和数据验证逻辑
- **后端数据模型**: 已在 `backend/models/` 中完整实现，无需修改
