/**
 * HotStockList Component - Display lists of hot stocks (gainers/losers/active)
 * 
 * Container for top 5 gainers, losers, and most active stocks
 * User Story 2: 直观感受市场活跃度
 */

import React, { useState } from 'react';
import { TrendingUp, TrendingDown, Activity } from 'lucide-react';
import { HotStockRow } from './HotStockRow';
import { useHotStocks } from '@/hooks/useHotStocks';

export interface HotStockListProps {
  /** Additional CSS classes */
  className?: string;
}

type TabType = 'gainers' | 'losers' | 'active';

/**
 * Hot stock list component with tabs
 * 
 * @example
 * ```tsx
 * <HotStockList />
 * ```
 */
export function HotStockList({ className = '' }: HotStockListProps) {
  const [activeTab, setActiveTab] = useState<TabType>('gainers');
  const hotStocks = useHotStocks();

  const tabs = [
    { id: 'gainers' as TabType, label: '涨幅榜', icon: TrendingUp, color: 'text-red-600' },
    { id: 'losers' as TabType, label: '跌幅榜', icon: TrendingDown, color: 'text-green-600' },
    { id: 'active' as TabType, label: '成交活跃', icon: Activity, color: 'text-blue-600' },
  ];

  if (!hotStocks) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700 ${className}`}>
        <div className="animate-pulse">
          <div className="flex gap-2 mb-6">
            {tabs.map((tab) => (
              <div key={tab.id} className="h-10 bg-gray-200 dark:bg-gray-700 rounded-lg flex-1"></div>
            ))}
          </div>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const currentStocks = hotStocks[activeTab];
  const showVolume = activeTab === 'active';

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 ${className}`}>
      {/* Header with tabs */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white">热门股票</h3>
          <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span>实时排名</span>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg 
                  font-medium text-sm transition-all
                  ${isActive 
                    ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 shadow-sm' 
                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700/50'
                  }
                `}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Stock list */}
      <div className="p-4">
        {currentStocks.length === 0 ? (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            暂无数据
          </div>
        ) : (
          <div className="space-y-2">
            {currentStocks.map((stock, index) => (
              <HotStockRow
                key={stock.symbol}
                stock={stock}
                rank={index + 1}
                showVolume={showVolume}
                highlightChange={false}
              />
            ))}
          </div>
        )}
      </div>

      {/* Footer tip */}
      <div className="px-4 pb-4">
        <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
          {activeTab === 'gainers' && '按涨幅排序，前5名'}
          {activeTab === 'losers' && '按跌幅排序，前5名'}
          {activeTab === 'active' && '按成交额排序，前5名'}
        </div>
      </div>
    </div>
  );
}
