/**
 * HotStockRow Component - Display a single stock in hot stock list
 * 
 * Shows stock symbol, name, price, change with visual indicators
 * User Story 2: 直观感受市场活跃度
 */

import React from 'react';
import Link from 'next/link';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { FlashChange } from '@/components/ui/FlashChange';
import { formatPrice, formatVolumeZh } from '@/lib/formatters';
import { useStockSparkline, sparklineToPath } from '@/hooks/useStockSparkline';
import type { HotStock } from '@/hooks/useHotStocks';

export interface HotStockRowProps {
  /** Stock data */
  stock: HotStock;
  /** Rank number (1-5) */
  rank: number;
  /** Show volume/turnover */
  showVolume?: boolean;
  /** Show sparkline chart */
  showSparkline?: boolean;
  /** Highlight on change (flash animation) */
  highlightChange?: boolean;
}

/**
 * Single row component for hot stock lists
 * 
 * @example
 * ```tsx
 * <HotStockRow stock={stock} rank={1} showVolume={true} />
 * ```
 */
export function HotStockRow({ 
  stock, 
  rank, 
  showVolume = false,
  showSparkline = true,
  highlightChange = false 
}: HotStockRowProps) {
  const isPositive = stock.change_pct > 0;
  const isNegative = stock.change_pct < 0;
  const isLimitUp = stock.change_pct >= 9.9;
  const isLimitDown = stock.change_pct <= -9.9;
  
  // Generate sparkline data
  const sparkline = useStockSparkline(stock, 20);

  return (
    <Link
      href={`/virtual-market/stocks/${stock.symbol}`}
      className={`
        flex items-center gap-3 p-3 rounded-lg 
        hover:bg-gray-50 dark:hover:bg-gray-700/50 
        transition-all group
        ${highlightChange ? 'animate-flash' : ''}
        ${isLimitUp ? 'bg-red-50 dark:bg-red-900/20' : ''}
        ${isLimitDown ? 'bg-green-50 dark:bg-green-900/20' : ''}
      `}
    >
      {/* Rank */}
      <div className="flex-shrink-0 w-6 text-center">
        <span
          className={`
            text-sm font-bold
            ${rank === 1 ? 'text-yellow-600 dark:text-yellow-400' : ''}
            ${rank === 2 ? 'text-gray-500 dark:text-gray-400' : ''}
            ${rank === 3 ? 'text-orange-600 dark:text-orange-400' : ''}
            ${rank > 3 ? 'text-gray-400 dark:text-gray-500' : ''}
          `}
        >
          {rank}
        </span>
      </div>

      {/* Stock info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-baseline gap-2">
          <span className="font-semibold text-gray-900 dark:text-white truncate">
            {stock.name}
          </span>
          <span className="text-xs text-gray-500 dark:text-gray-400 flex-shrink-0">
            {stock.symbol}
          </span>
        </div>
        
        {/* Volume info (optional) */}
        {showVolume && (
          <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
            成交: {formatVolumeZh(stock.turnover)}
          </div>
        )}
      </div>

      {/* Sparkline chart (optional) */}
      {showSparkline && sparkline && (
        <div className="flex-shrink-0 w-16 h-8">
          <svg
            width="60"
            height="30"
            viewBox="0 0 60 30"
            className="w-full h-full"
            preserveAspectRatio="none"
          >
            <path
              d={sparklineToPath(sparkline, 60, 30, 2)}
              fill="none"
              stroke={isPositive ? 'rgb(220, 38, 38)' : isNegative ? 'rgb(22, 163, 74)' : 'rgb(156, 163, 175)'}
              strokeWidth="1.5"
              className="transition-colors duration-300"
            />
          </svg>
        </div>
      )}

      {/* Price and change */}
      <div className="flex-shrink-0 text-right">
        <FlashChange value={stock.current_price} format={formatPrice}>
          <div className={`
            font-semibold
            ${isPositive ? 'text-red-600 dark:text-red-400' : ''}
            ${isNegative ? 'text-green-600 dark:text-green-400' : ''}
            ${!isPositive && !isNegative ? 'text-gray-600 dark:text-gray-400' : ''}
          `}>
            {formatPrice(stock.current_price)}
          </div>
        </FlashChange>
        <div className="mt-1">
          <FlashChange value={stock.change_pct}>
            <Badge value={stock.change_pct} variant="auto" size="sm" />
          </FlashChange>
        </div>
      </div>

      {/* Trend indicator */}
      <div className="flex-shrink-0 w-6 flex justify-center">
        {isPositive && (
          <TrendingUp className="w-5 h-5 text-red-500 dark:text-red-400 group-hover:scale-110 transition-transform" />
        )}
        {isNegative && (
          <TrendingDown className="w-5 h-5 text-green-500 dark:text-green-400 group-hover:scale-110 transition-transform" />
        )}
      </div>

      {/* Limit up/down badge */}
      {(isLimitUp || isLimitDown) && (
        <div className="absolute -right-1 -top-1 px-2 py-0.5 rounded-full text-xs font-bold bg-red-600 text-white animate-pulse">
          {isLimitUp ? '涨停' : '跌停'}
        </div>
      )}
    </Link>
  );
}
