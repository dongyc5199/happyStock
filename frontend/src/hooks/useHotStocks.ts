/**
 * useHotStocks Hook - Derive hot stock lists from WebSocket data
 * 
 * Returns top 5 gainers, losers, and most active stocks
 * Updates automatically when WebSocket data changes
 */

import { useMemo } from 'react';
import { useWebSocketContext, type StockData } from '@/contexts/WebSocketContext';

// HotStock 就是 StockData 的别名
export type HotStock = StockData;

export interface HotStockLists {
  gainers: HotStock[];   // Top 5 stocks by change_pct (descending)
  losers: HotStock[];    // Top 5 stocks by change_pct (ascending)
  active: HotStock[];    // Top 5 stocks by turnover (descending)
}

/**
 * Custom hook to derive hot stock lists from real-time market data
 * 
 * @returns HotStockLists | null - Returns null when no data available or not connected
 * 
 * @example
 * ```tsx
 * function HotStockSection() {
 *   const hotStocks = useHotStocks();
 *   
 *   if (!hotStocks) {
 *     return <div>加载中...</div>;
 *   }
 *   
 *   return (
 *     <div>
 *       <h2>涨幅榜</h2>
 *       {hotStocks.gainers.map(stock => (
 *         <div key={stock.symbol}>{stock.name}: {stock.change_pct}%</div>
 *       ))}
 *     </div>
 *   );
 * }
 * ```
 */
export function useHotStocks(): HotStockLists | null {
  const { marketData, isConnected } = useWebSocketContext();

  return useMemo(() => {
    // Return null if no data or not connected
    if (!marketData || !marketData.stocks || marketData.stocks.length === 0 || !isConnected) {
      return null;
    }

    // Create a copy to avoid mutating original data
    const stocks = [...marketData.stocks];

    // Calculate gainers (top 5 by change_pct, descending)
    const gainers = stocks
      .sort((a, b) => b.change_pct - a.change_pct)
      .slice(0, 5);

    // Calculate losers (top 5 by change_pct, ascending)
    const losers = stocks
      .sort((a, b) => a.change_pct - b.change_pct)
      .slice(0, 5);

    // Calculate most active (top 5 by turnover, descending)
    const active = stocks
      .sort((a, b) => b.turnover - a.turnover)
      .slice(0, 5);

    return {
      gainers,
      losers,
      active,
    };
  }, [marketData, isConnected]);
}
