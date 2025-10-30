/**
 * MarketOverview Component - Display real-time market statistics
 * 
 * Shows total stocks, rising/falling counts, limit up/down, and market state
 * User Story 2: 直观感受市场活跃度
 */

import React from 'react';
import { TrendingUp, TrendingDown, Minus, ArrowUpCircle, ArrowDownCircle } from 'lucide-react';
import { FlashChange } from '@/components/ui/FlashChange';
import type { MarketOverview as MarketOverviewType } from '@/types/virtual-market';

export interface MarketOverviewProps {
  /** Market overview data from API or WebSocket */
  data: MarketOverviewType;
  /** Show loading skeleton */
  loading?: boolean;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Market overview component showing real-time statistics
 * 
 * @example
 * ```tsx
 * const overview = await marketApi.getMarketOverview();
 * <MarketOverview data={overview.data} />
 * ```
 */
export function MarketOverview({ data, loading = false, className = '' }: MarketOverviewProps) {
  if (loading) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-32 mb-4"></div>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
            {[...Array(7)].map((_, i) => (
              <div key={i} className="space-y-2">
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
                <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const stats = [
    {
      label: '总股票数',
      value: data.total_stocks,
      color: 'text-gray-900 dark:text-white',
      icon: null,
    },
    {
      label: '上涨',
      value: data.rising,
      color: 'text-red-600 dark:text-red-400',
      icon: TrendingUp,
      bgColor: 'bg-red-50 dark:bg-red-900/20',
    },
    {
      label: '下跌',
      value: data.falling,
      color: 'text-green-600 dark:text-green-400',
      icon: TrendingDown,
      bgColor: 'bg-green-50 dark:bg-green-900/20',
    },
    {
      label: '平盘',
      value: data.unchanged,
      color: 'text-gray-600 dark:text-gray-400',
      icon: Minus,
      bgColor: 'bg-gray-50 dark:bg-gray-800',
    },
    {
      label: '涨停',
      value: data.limit_up,
      color: 'text-red-600 dark:text-red-400',
      icon: ArrowUpCircle,
      bgColor: 'bg-red-50 dark:bg-red-900/20',
      highlight: data.limit_up > 0,
    },
    {
      label: '跌停',
      value: data.limit_down,
      color: 'text-green-600 dark:text-green-400',
      icon: ArrowDownCircle,
      bgColor: 'bg-green-50 dark:bg-green-900/20',
      highlight: data.limit_down > 0,
    },
    {
      label: '市场状态',
      value: data.market_state,
      color: 'text-blue-600 dark:text-blue-400',
      icon: null,
      isText: true,
    },
  ];

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white">市场概况</h3>
        <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span>实时更新</span>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div
              key={index}
              className={`relative text-center p-4 rounded-lg transition-all ${
                stat.bgColor || 'bg-gray-50 dark:bg-gray-800'
              } ${stat.highlight ? 'ring-2 ring-red-500 dark:ring-red-400' : ''}`}
            >
              {/* Icon */}
              {Icon && (
                <div className="flex justify-center mb-2">
                  <Icon className={`w-5 h-5 ${stat.color}`} />
                </div>
              )}

              {/* Label */}
              <div className="text-xs text-gray-500 dark:text-gray-400 mb-1 font-medium">
                {stat.label}
              </div>

              {/* Value */}
              <FlashChange value={stat.value}>
                <div className={`text-2xl font-bold ${stat.color} transition-all`}>
                  {stat.isText ? stat.value : stat.value}
                </div>
              </FlashChange>

              {/* Highlight pulse for limit up/down */}
              {stat.highlight && (
                <div className="absolute inset-0 rounded-lg ring-2 ring-red-500 animate-ping opacity-20"></div>
              )}
            </div>
          );
        })}
      </div>

      {/* Market sentiment bar */}
      <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
          <span>市场情绪</span>
          <span>
            上涨比例: {data.total_stocks > 0 ? ((data.rising / data.total_stocks) * 100).toFixed(1) : 0}%
          </span>
        </div>
        <div className="relative h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <div
            className="absolute left-0 top-0 h-full bg-gradient-to-r from-red-500 to-red-600 transition-all duration-500"
            style={{
              width: data.total_stocks > 0 ? `${(data.rising / data.total_stocks) * 100}%` : '0%',
            }}
          />
          <div
            className="absolute right-0 top-0 h-full bg-gradient-to-r from-green-600 to-green-500 transition-all duration-500"
            style={{
              width: data.total_stocks > 0 ? `${(data.falling / data.total_stocks) * 100}%` : '0%',
            }}
          />
        </div>
      </div>
    </div>
  );
}
