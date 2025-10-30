/**
 * WebSocket Context - 全局 WebSocket 连接管理
 * 
 * 功能:
 * - 全局单例连接,多个组件共享
 * - 自动管理订阅/取消订阅
 * - 根据页面场景自动调整推送频率
 * - 页面失焦自动降频
 * 
 * @example
 * ```tsx
 * // 在 _app.tsx 中包裹
 * <WebSocketProvider>
 *   <Component {...pageProps} />
 * </WebSocketProvider>
 * 
 * // 在组件中使用
 * const { marketData, isConnected } = useWebSocketContext();
 * ```
 */

'use client';

import React, { createContext, useContext, useEffect, useMemo } from 'react';
import { useWebSocket, PUSH_INTERVALS, type PushInterval } from '@/hooks/useWebSocket';
import { usePathname } from 'next/navigation';

// 市场数据类型
export interface StockData {
  symbol: string;
  name: string;
  sector: string;
  current_price: number;
  previous_close: number;
  change_value: number;
  change_pct: number;
  volume: number;
  turnover: number;
  timestamp: number;
}

export interface MarketData {
  stocks: StockData[];
  timestamp: number;
}

// Context 类型
interface WebSocketContextValue {
  /** 市场数据 */
  marketData: MarketData | null;
  
  /** 连接状态 */
  isConnected: boolean;
  
  /** 错误信息 */
  error: string | null;
  
  /** 当前节流间隔 */
  currentThrottle: number;
  
  /** 设置节流间隔 */
  setThrottle: (interval: number) => void;
  
  /** 订阅单只股票 */
  subscribeStock: (symbol: string) => void;
  
  /** 取消订阅单只股票 */
  unsubscribeStock: (symbol: string) => void;
}

const WebSocketContext = createContext<WebSocketContextValue | undefined>(undefined);

// 根据路径确定推送频率
function getThrottleByPath(pathname: string): PushInterval {
  // 交易页面 - 1秒实时
  if (pathname.includes('/trade') || pathname.includes('/order')) {
    return PUSH_INTERVALS.REALTIME;
  }
  
  // 市场/行情页面 - 1秒实时 (包含 /virtual-market 路径)
  if (pathname.includes('/market') || pathname.includes('/stocks') || pathname.includes('/virtual-market')) {
    return PUSH_INTERVALS.REALTIME;
  }
  
  // K线图/详情页 - 10秒慢速
  if (pathname.includes('/chart') || pathname.includes('/detail')) {
    return PUSH_INTERVALS.SLOW;
  }
  
  // 其他页面 - 60秒懒加载
  return PUSH_INTERVALS.LAZY;
}

interface WebSocketProviderProps {
  children: React.ReactNode;
  /** 是否启用自动连接 */
  autoConnect?: boolean;
  /** 是否根据路径自动调整频率 */
  autoAdjustThrottle?: boolean;
}

export function WebSocketProvider({ 
  children,
  autoConnect = true,
  autoAdjustThrottle = true,
}: WebSocketProviderProps) {
  const pathname = usePathname();
  
  // 根据当前路径确定初始节流间隔
  const initialThrottle = useMemo(() => {
    return autoAdjustThrottle ? getThrottleByPath(pathname) : PUSH_INTERVALS.NORMAL;
  }, [pathname, autoAdjustThrottle]);

  // 使用 WebSocket Hook 连接市场数据
  const {
    data: marketData,
    isConnected,
    error,
    currentThrottle,
    setThrottle,
    subscribe,
    unsubscribe,
  } = useWebSocket<MarketData>('/ws/market', {
    autoConnect,
    throttle: initialThrottle,
    autoSlowDownOnBlur: false,  // 禁用自动降频,避免页面切换时降到60秒
    debug: process.env.NODE_ENV === 'development',
  });

  // 路径变化时自动调整节流间隔
  useEffect(() => {
    if (autoAdjustThrottle) {
      const newThrottle = getThrottleByPath(pathname);
      if (newThrottle !== currentThrottle) {
        console.log(`[WebSocket] Route changed to ${pathname}, adjusting throttle to ${newThrottle}ms`);
        setThrottle(newThrottle);
      }
    }
  }, [pathname, autoAdjustThrottle, currentThrottle, setThrottle]);

  // 订阅单只股票
  const subscribeStock = (symbol: string) => {
    subscribe(`stock:${symbol}`);
  };

  // 取消订阅单只股票
  const unsubscribeStock = (symbol: string) => {
    unsubscribe(`stock:${symbol}`);
  };

  const value: WebSocketContextValue = {
    marketData,
    isConnected,
    error,
    currentThrottle,
    setThrottle,
    subscribeStock,
    unsubscribeStock,
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
}

/**
 * 使用 WebSocket Context
 */
export function useWebSocketContext(): WebSocketContextValue {
  const context = useContext(WebSocketContext);
  
  if (context === undefined) {
    throw new Error('useWebSocketContext must be used within a WebSocketProvider');
  }
  
  return context;
}

/**
 * 获取特定股票的实时数据
 */
export function useStockData(symbol: string): StockData | null {
  const { marketData } = useWebSocketContext();
  
  return useMemo(() => {
    if (!marketData?.stocks) return null;
    return marketData.stocks.find(stock => stock.symbol === symbol) || null;
  }, [marketData, symbol]);
}

/**
 * 获取多只股票的实时数据
 */
export function useStocksData(symbols: string[]): StockData[] {
  const { marketData } = useWebSocketContext();
  
  return useMemo(() => {
    if (!marketData?.stocks) return [];
    return marketData.stocks.filter(stock => symbols.includes(stock.symbol));
  }, [marketData, symbols]);
}
