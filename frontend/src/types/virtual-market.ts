/**
 * Virtual Market Type Definitions
 * 虚拟市场类型定义
 */

export interface Stock {
  symbol: string;
  name: string;
  sector_code: string;
  current_price: number;
  previous_close: number;
  change_value: number;
  change_pct: number;
  volume: number;
  turnover: number;
  is_active: number;
  created_at: string;
  updated_at: string;
  // Metadata
  market_cap?: number;
  market_cap_tier?: string;
  beta?: number;
}

export interface StockDetail extends Stock {
  volatility: number;
  outstanding_shares: number;
  listing_date: string;
  is_happy300: number;
  weight_in_happy300: number | null;
}

export interface KlineData {
  id: number;
  target_type: string;
  target_code: string;
  timestamp: number;
  datetime: string;
  open: number;
  close: number;
  high: number;
  low: number;
  volume: number;
  turnover: number;
  change_pct: number;
  created_at: string;
}

export interface Index {
  code: string;
  name: string;
  index_type: string;
  base_point: number;
  base_date: string;
  current_value: number;
  previous_close: number;
  change_value: number | null;
  change_pct: number | null;
  volume: number | null;
  turnover: number | null;
  constituent_count: number;
  calculation_method: string;
  created_at: string;
  updated_at: string;
}

export interface Sector {
  code: string;
  name: string;
  name_en: string;
  beta: number;
  total_market_cap: number | null;
  stock_count: number;
  avg_change_pct: number | null;
  description: string;
  created_at: string;
}

export interface MarketState {
  id: number;
  state: string;
  start_time: string;
  end_time: string | null;
  daily_trend: number;
  volatility_multiplier: number;
  description: string;
  is_current: number;
  created_at: string;
}

export interface MarketOverview {
  total_stocks: number;
  rising: number;
  falling: number;
  unchanged: number;
  limit_up: number;
  limit_down: number;
  total_volume: number;
  total_turnover: number;
  market_state: string;
  market_trend: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  total?: number;
  page?: number;
  page_size?: number;
  error?: {
    code: string;
    message: string;
  };
}
