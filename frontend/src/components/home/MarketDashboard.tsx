/**
 * MarketDashboard - 整合的市场看板
 * 
 * 整合了热门股票和核心指数,提供一站式市场视图
 */

import Link from 'next/link';
import { TrendingUp, TrendingDown, Minus, ArrowRight, Activity } from 'lucide-react';
import { HotStockList } from './HotStockList';
import { FlashChange } from '@/components/ui/FlashChange';
import type { Index } from '@/types/virtual-market';

interface MarketDashboardProps {
  coreIndices: Index[];
  loading?: boolean;
}

export function MarketDashboard({ coreIndices, loading = false }: MarketDashboardProps) {
  return (
    <div className="space-y-8">
      {/* 标题 */}
      <div className="text-center space-y-3">
        <h2 className="text-3xl lg:text-4xl font-bold text-gray-900">
          市场实时动态
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          把握市场脉搏,捕捉投资机会
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左侧: 核心指数 (1/3 宽度) */}
        <div className="lg:col-span-1 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold text-gray-900">核心指数</h3>
            <Link
              href="/virtual-market/indices"
              className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1"
            >
              查看全部
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="bg-white rounded-lg p-4 shadow-sm animate-pulse">
                  <div className="h-5 bg-gray-200 rounded w-1/2 mb-2"></div>
                  <div className="h-7 bg-gray-200 rounded w-3/4"></div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              {coreIndices.slice(0, 3).map((index) => {
                const changeValue = index.change_value ?? 0;
                const changePct = index.change_pct ?? 0;
                const isPositive = changeValue > 0;
                const isNegative = changeValue < 0;

                return (
                  <Link
                    key={index.code}
                    href={`/virtual-market/indices/${index.code}`}
                    className="block bg-white rounded-lg p-4 shadow-sm hover:shadow-md transition-all border border-gray-100 hover:border-blue-200"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900 mb-1">{index.name}</h4>
                        <div className="flex items-baseline gap-2">
                          <FlashChange value={index.current_value ?? 0}>
                            <span className="text-2xl font-bold text-gray-900">
                              {index.current_value?.toFixed(2) ?? '-'}
                            </span>
                          </FlashChange>
                        </div>
                      </div>

                      <div className="text-right">
                        <div className={`flex items-center gap-1 text-sm font-medium ${
                          isPositive ? 'text-red-600' : isNegative ? 'text-green-600' : 'text-gray-500'
                        }`}>
                          {isPositive ? (
                            <TrendingUp className="w-4 h-4" />
                          ) : isNegative ? (
                            <TrendingDown className="w-4 h-4" />
                          ) : (
                            <Minus className="w-4 h-4" />
                          )}
                          <FlashChange value={changeValue}>
                            <span>{isPositive ? '+' : ''}{changeValue.toFixed(2)}</span>
                          </FlashChange>
                        </div>
                        <FlashChange value={changePct}>
                          <div className={`text-sm font-medium ${
                            isPositive ? 'text-red-600' : isNegative ? 'text-green-600' : 'text-gray-500'
                          }`}>
                            {isPositive ? '+' : ''}{changePct.toFixed(2)}%
                          </div>
                        </FlashChange>
                      </div>
                    </div>

                    {/* 简单的走势图示意 */}
                    <div className="mt-3 h-1 bg-gray-100 rounded-full overflow-hidden">
                      <div 
                        className={`h-full transition-all duration-500 ${
                          isPositive ? 'bg-red-500' : isNegative ? 'bg-green-500' : 'bg-gray-300'
                        }`}
                        style={{ width: `${Math.min(Math.abs(changePct) * 20, 100)}%` }}
                      ></div>
                    </div>
                  </Link>
                );
              })}
            </div>
          )}

          {/* 全部指数链接 */}
          <Link
            href="/virtual-market/indices"
            className="block w-full px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg text-center text-sm font-medium text-gray-700 transition-colors"
          >
            查看所有指数 →
          </Link>
        </div>

        {/* 右侧: 热门股票 (2/3 宽度) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-blue-600" />
              <h3 className="text-xl font-bold text-gray-900">热门股票</h3>
            </div>
            <Link
              href="/virtual-market"
              className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1"
            >
              进入交易
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          <HotStockList />
        </div>
      </div>

      {/* 底部 CTA */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-8 text-center border border-blue-100">
        <h3 className="text-2xl font-bold text-gray-900 mb-2">
          准备好开始您的投资之旅了吗?
        </h3>
        <p className="text-gray-600 mb-6">
          在真实的市场环境中练习交易,无需承担任何风险
        </p>
        <div className="flex flex-wrap justify-center gap-4">
          <Link
            href="/virtual-market"
            className="inline-flex items-center gap-2 px-8 py-4 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors shadow-lg hover:shadow-xl"
          >
            立即开始交易
            <ArrowRight className="w-5 h-5" />
          </Link>
          
          <Link
            href="/virtual-market/sectors"
            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition-colors border border-gray-200"
          >
            查看板块分析
          </Link>
        </div>
      </div>
    </div>
  );
}
