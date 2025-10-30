/**
 * 图表相关类型定义
 *
 * 用于 P0 功能：倒计时、动态加载、线形图切换
 */

import { CandlestickData, Time } from 'lightweight-charts';

/**
 * 图表类型
 */
export type ChartType = 'candlestick' | 'line';

/**
 * 图表用户偏好设置
 */
export interface ChartPreferences {
  /** 图表类型 */
  chartType: ChartType;
  /** 启用的 EMA 周期 */
  enabledEMAs: number[];
  /** 是否显示 MACD */
  showMACD: boolean;
  /** 默认时间周期 */
  defaultTimeframe?: string;
}

/**
 * 已加载的数据范围
 */
export interface LoadedRange {
  /** 最早加载的时间戳（秒） */
  from: number;
  /** 最晚加载的时间戳（秒） */
  to: number;
  /** 是否已到达历史最早数据 */
  reachedStart: boolean;
  /** 是否已到达最新数据 */
  reachedEnd: boolean;
}

/**
 * K线数据响应（带元数据）
 */
export interface KlineDataResponse {
  /** 股票代码 */
  symbol: string;
  /** 时间周期 */
  interval: string;
  /** K线数据 */
  klines: CandlestickData[];
  /** 元数据 */
  meta?: {
    /** 是否还有更多数据 */
    hasMore: boolean;
    /** 最早可用时间 */
    earliestTime?: number;
    /** 最新可用时间 */
    latestTime?: number;
  };
}

/**
 * 数据加载状态
 */
export interface LoadingState {
  /** 是否正在加载 */
  loading: boolean;
  /** 加载方向 */
  direction?: 'historical' | 'latest';
  /** 错误信息 */
  error?: string | null;
}

/**
 * 倒计时状态
 */
export interface CountdownState {
  /** 剩余秒数 */
  remaining: number;
  /** 格式化的倒计时字符串 */
  formatted: string;
  /** 是否归零 */
  isZero: boolean;
}

/**
 * 图表配置选项
 */
export interface ChartOptions {
  /** 图表类型 */
  chartType: ChartType;
  /** 是否显示倒计时 */
  showCountdown: boolean;
  /** 是否启用动态加载 */
  enableDynamicLoading: boolean;
  /** 数据缓存最大数量 */
  maxCacheSize?: number;
  /** 提前加载的缓冲区大小（根K线数量） */
  loadBuffer?: number;
}

/**
 * 缓存项
 */
export interface CacheItem<T> {
  /** 缓存键 */
  key: string;
  /** 缓存数据 */
  data: T;
  /** 创建时间戳 */
  timestamp: number;
  /** 过期时间（秒），undefined 表示不过期 */
  ttl?: number;
}

/**
 * 数据加载请求参数
 */
export interface LoadDataParams {
  /** 股票代码 */
  symbol: string;
  /** 时间周期 */
  interval: string;
  /** 开始时间（秒） */
  startTime: number;
  /** 结束时间（秒） */
  endTime: number;
  /** 数据条数限制 */
  limit?: number;
}

/**
 * 可见范围变化事件
 */
export interface VisibleRangeChangeEvent {
  /** 逻辑范围 from */
  from: number;
  /** 逻辑范围 to */
  to: number;
  /** 时间范围 from */
  timeFrom?: Time;
  /** 时间范围 to */
  timeTo?: Time;
}
