/**
 * CoreIndexCards Component - Display core market indices
 * 
 * Shows Happy300, HappyLarge, HappySmall indices with real-time data
 * User Story 2: 直观感受市场活跃度
 */

import React from 'react';
import Link from 'next/link';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { FlashChange } from '@/components/ui/FlashChange';
import type { Index } from '@/types/virtual-market';

export interface CoreIndexCardsProps {
  /** Core indices data from API */
  indices: Index[];
  /** Show loading skeleton */
  loading?: boolean;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Core index cards component
 * 
 * @example
 * ```tsx
 * const indices = await indicesApi.getIndices('CORE');
 * <CoreIndexCards indices={indices.data} />
 * ```
 */
export function CoreIndexCards({ indices, loading = false, className = '' }: CoreIndexCardsProps) {
  if (loading) {
    return (
      <div className={`grid grid-cols-1 md:grid-cols-3 gap-6 ${className}`}>
        {[...Array(3)].map((_, i) => (
          <div key={i} className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
            <div className="animate-pulse">
              <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-24 mb-2"></div>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-16 mb-4"></div>
              <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded w-32 mb-2"></div>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-20"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (indices.length === 0) {
    return (
      <div className={`text-center py-8 ${className}`}>
        <p className="text-gray-500 dark:text-gray-400">暂无指数数据</p>
      </div>
    );
  }

  return (
    <div className={`grid grid-cols-1 md:grid-cols-3 gap-6 ${className}`}>
      {indices.map((index) => {
        const changePct = index.change_pct ?? 0;
        const isPositive = changePct > 0;
        const isNegative = changePct < 0;
        const changeAmount = (index.current_value * changePct) / 100;

        // Icon based on change direction
        const TrendIcon = isPositive ? TrendingUp : isNegative ? TrendingDown : Minus;
        const iconColor = isPositive 
          ? 'text-red-500 dark:text-red-400' 
          : isNegative 
          ? 'text-green-500 dark:text-green-400' 
          : 'text-gray-400';

        return (
          <Link
            key={index.code}
            href={`/virtual-market/indices`}
            className="group relative bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700 hover:shadow-xl hover:border-blue-500 dark:hover:border-blue-400 transition-all"
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h4 className="text-lg font-bold text-gray-900 dark:text-white mb-1 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                  {index.name}
                </h4>
                <p className="text-sm text-gray-500 dark:text-gray-400">{index.code}</p>
              </div>
              <Badge value={changePct} variant="auto" size="md" />
            </div>

            {/* Current value */}
            <div className="mb-2">
              <FlashChange value={index.current_value}>
                <div className="text-3xl font-bold text-gray-900 dark:text-white">
                  {index.current_value.toFixed(2)}
                </div>
              </FlashChange>
            </div>

            {/* Change amount and trend */}
            <div className="flex items-center justify-between">
              <FlashChange value={changeAmount}>
                <div className={`
                  text-sm font-medium
                  ${isPositive ? 'text-red-600 dark:text-red-400' : ''}
                  ${isNegative ? 'text-green-600 dark:text-green-400' : ''}
                  ${!isPositive && !isNegative ? 'text-gray-600 dark:text-gray-400' : ''}
                `}>
                  {isPositive ? '+' : ''}{changeAmount.toFixed(2)}
                </div>
              </FlashChange>
              <TrendIcon className={`w-5 h-5 ${iconColor} group-hover:scale-110 transition-transform`} />
            </div>

            {/* Hover indicator */}
            <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
              <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>

            {/* Real-time indicator */}
            <div className="absolute bottom-4 right-4 flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-xs text-gray-400 dark:text-gray-500">实时</span>
            </div>
          </Link>
        );
      })}
    </div>
  );
}
