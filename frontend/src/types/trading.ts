/**
 * 交易系统 TypeScript 类型定义
 */

// ============ 账户相关类型 ============

export interface Account {
  id: number;
  user_id: number;
  account_name: string;
  initial_balance: string;
  current_balance: string;
  created_at: string;
}

export interface AccountSummary {
  account_balance: string;
  total_market_value: string;
  total_assets: string;
  total_cost: string;
  total_profit: string;
  total_profit_rate: string;
  holdings_count: number;
}

// ============ 资产相关类型 ============

export interface Asset {
  id: number;
  symbol: string;
  name: string;
  exchange: string;
  asset_type: string;
  current_price?: string;
  created_at: string;
}

export interface AssetPrice {
  symbol: string;
  price: string;
  change?: string;
  change_percent?: string;
  timestamp?: string;
}

// ============ 交易相关类型 ============

export type TradeType = 'BUY' | 'SELL';

export interface Trade {
  id: number;
  account_id: number;
  asset_id: number;
  asset_symbol: string;
  asset_name: string;
  trade_type: TradeType;
  quantity: string;
  price: string;
  total_amount: string;
  trade_time: string;
}

export interface BuyTradeRequest {
  account_id: number;
  asset_symbol: string;
  quantity: string;
  price: string;
}

export interface SellTradeRequest {
  account_id: number;
  asset_symbol: string;
  quantity: string;
  price: string;
}

export interface TradeHistoryParams {
  account_id: number;
  asset_symbol?: string;
  trade_type?: TradeType;
  page?: number;
  page_size?: number;
}

// ============ 持仓相关类型 ============

export interface Holding {
  id: number;
  asset_id: number;
  asset_symbol: string;
  asset_name: string;
  quantity: string;
  avg_price: string;
  current_price: string;
  cost: string;
  market_value: string;
  profit: string;
  profit_rate: string;
}

export interface HoldingsSummary {
  total_cost: string;
  total_market_value: string;
  total_profit: string;
  total_profit_rate: string;
}

export interface AssetAllocation {
  asset_symbol: string;
  asset_name: string;
  market_value: string;
  percentage: string;
}

// ============ API 响应类型 ============

export interface ApiResponse<T = any> {
  success: boolean;
  message?: string;
  data?: T;
  error?: {
    code: string;
    message: string;
  };
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

// ============ K线数据类型 ============

/**
 * 后端API返回的K线数据格式（原始数据）
 * - 价格字段为字符串类型（Decimal精度）
 */
export interface KlineData {
  time: number;       // Unix时间戳（秒）
  open: string;       // 开盘价（字符串，来自Decimal）
  high: string;       // 最高价（字符串，来自Decimal）
  low: string;        // 最低价（字符串，来自Decimal）
  close: string;      // 收盘价（字符串，来自Decimal）
  volume: number;     // 成交量
}

/**
 * 前端图表使用的K线数据格式（已转换）
 * - 价格字段为数字类型
 */
export interface CandlestickData {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

/**
 * K线数据API响应
 */
export interface KlineResponse {
  symbol: string;
  interval: string;
  klines: KlineData[];  // 使用KlineData（原始格式）
}

// ============ 界面状态类型 ============

export type OrderSide = 'buy' | 'sell';

export interface TradeFormData {
  asset?: Asset;
  side: OrderSide;
  quantity: string;
  price: string;
}
