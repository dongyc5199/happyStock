'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { indicesApi, marketApi } from '@/lib/api/virtual-market';
import type { Index, MarketOverview as MarketOverviewType } from '@/types/virtual-market';
import { HeroSection } from '@/components/home/HeroSection';
import { Badge } from '@/components/ui/Badge';
import { FlashChange } from '@/components/ui/FlashChange';
import {
  MarketOverviewSkeleton,
  HotStockListSkeleton,
  QuickStartGuideSkeleton,
  FeatureShowcaseSkeleton,
  EducationFooterSkeleton,
} from '@/components/ui/Skeleton';
import { ErrorBoundary } from '@/components/ui/ErrorBoundary';

// Lazy load heavy components with skeleton loading states
const MarketOverview = dynamic(() => import('@/components/home/MarketOverview').then(mod => ({ default: mod.MarketOverview })), {
  loading: () => <MarketOverviewSkeleton />,
  ssr: true,
});

const HotStockList = dynamic(() => import('@/components/home/HotStockList').then(mod => ({ default: mod.HotStockList })), {
  loading: () => <HotStockListSkeleton />,
  ssr: true,
});

const QuickStartGuide = dynamic(() => import('@/components/home/QuickStartGuide'), {
  loading: () => <QuickStartGuideSkeleton />,
  ssr: true,
});

const FeatureShowcase = dynamic(() => import('@/components/home/FeatureShowcase'), {
  loading: () => <FeatureShowcaseSkeleton />,
  ssr: true,
});

const EducationFooter = dynamic(() => import('@/components/home/EducationFooter'), {
  loading: () => <EducationFooterSkeleton />,
  ssr: true,
});

export default function Home() {
  const [coreIndices, setCoreIndices] = useState<Index[]>([]);
  const [marketOverview, setMarketOverview] = useState<MarketOverviewType | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      setLoading(true);
      const [indicesResponse, marketResponse] = await Promise.all([
        indicesApi.getIndices('CORE'),
        marketApi.getMarketOverview(),
      ]);

      if (indicesResponse.success && indicesResponse.data) {
        setCoreIndices(indicesResponse.data);
      }

      if (marketResponse.success && marketResponse.data) {
        setMarketOverview(marketResponse.data);
      }
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">happyStock</h1>
              <span className="ml-3 px-3 py-1 text-xs font-medium text-blue-600 bg-blue-100 rounded-full">
                虚拟市场
              </span>
            </div>
            <nav className="flex gap-6">
              <Link href="/virtual-market" className="text-gray-600 hover:text-gray-900 font-medium">
                市场首页
              </Link>
              <Link href="/virtual-market/indices" className="text-gray-600 hover:text-gray-900 font-medium">
                指数看板
              </Link>
              <Link href="/virtual-market/sectors" className="text-gray-600 hover:text-gray-900 font-medium">
                板块分析
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <HeroSection userCount={15234} />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-12">

        {/* Market Overview - US2 */}
        <ErrorBoundary>
          {marketOverview && <MarketOverview data={marketOverview} loading={loading} />}
        </ErrorBoundary>

        {/* Quick Start Guide - US3 */}
        <ErrorBoundary>
          <QuickStartGuide />
        </ErrorBoundary>

        {/* Feature Showcase - US4 */}
        <ErrorBoundary>
          <FeatureShowcase />
        </ErrorBoundary>

        {/* Education Footer - US5 */}
        <ErrorBoundary>
          <EducationFooter />
        </ErrorBoundary>

        {/* Hot Stocks and Core Indices - US2 */}
        <div className="grid grid-cols-1 lg:grid-cols-[3fr_2fr] gap-6">
          {/* Hot Stock List - Takes 60% width */}
          <ErrorBoundary>
            <HotStockList />
          </ErrorBoundary>

          {/* Core Indices - Takes 40% width */}
          <ErrorBoundary>
            <div className="space-y-4">
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white">核心指数</h3>
              {/* Vertical stack of index cards */}
              <div className="space-y-4">
                {coreIndices.map((index) => {
                const changeValue = index.change_value ?? 0;
                const changePct = index.change_pct ?? 0;
                
                return (
                  <Link
                    key={index.code}
                    href={`/virtual-market/indices/${index.code}`}
                    className="block bg-white dark:bg-gray-800 rounded-xl shadow-lg p-5 border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-200 hover:scale-[1.02]"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h4 className="text-lg font-bold text-gray-900 dark:text-white mb-1">
                          {index.name}
                        </h4>
                        <p className="text-xs text-gray-500 dark:text-gray-400 uppercase">
                          {index.code}
                        </p>
                      </div>
                      <Badge value={changePct} size="md" />
                    </div>
                    
                    <div className="flex items-baseline justify-between">
                      <div>
                        <FlashChange value={index.current_value}>
                          <span className="text-2xl font-bold text-gray-900 dark:text-white">
                            {index.current_value.toFixed(2)}
                          </span>
                        </FlashChange>
                        <div className="flex items-center gap-2 mt-1">
                          <FlashChange value={changeValue}>
                            <span className={`text-sm font-medium ${
                              changeValue > 0 ? 'text-red-600' : 
                              changeValue < 0 ? 'text-green-600' : 
                              'text-gray-500'
                            }`}>
                              {changeValue > 0 ? '+' : ''}{changeValue.toFixed(2)}
                            </span>
                          </FlashChange>
                          {changeValue > 0 ? (
                            <TrendingUp className="w-4 h-4 text-red-600" />
                          ) : changeValue < 0 ? (
                            <TrendingDown className="w-4 h-4 text-green-600" />
                          ) : (
                            <Minus className="w-4 h-4 text-gray-500" />
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-1.5 px-2 py-1 bg-gray-50 dark:bg-gray-700/50 rounded">
                        <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                        <span className="text-xs text-gray-600 dark:text-gray-400">实时</span>
                      </div>
                    </div>
                  </Link>
                );
              })}
              
              {loading && (
                <div className="space-y-4">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-5 border border-gray-200 dark:border-gray-700">
                      <div className="animate-pulse">
                        <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-32 mb-2"></div>
                        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-20 mb-4"></div>
                        <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-28"></div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              
              {!loading && coreIndices.length === 0 && (
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 border border-gray-200 dark:border-gray-700 text-center">
                  <p className="text-gray-500 dark:text-gray-400">暂无指数数据</p>
                </div>
              )}
            </div>
          </div>
          </ErrorBoundary>
        </div>

        {/* Quick Navigation */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link
            href="/virtual-market"
            className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-shadow group"
          >
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-xl font-semibold text-gray-900">股票市场</h4>
              <svg className="w-8 h-8 text-blue-600 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <p className="text-gray-600">
              浏览100只虚拟股票，查看实时价格、涨跌幅和市值数据
            </p>
          </Link>

          <Link
            href="/virtual-market/indices"
            className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-shadow group"
          >
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-xl font-semibold text-gray-900">指数看板</h4>
              <svg className="w-8 h-8 text-blue-600 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <p className="text-gray-600">
              查看核心指数和板块指数，了解市场整体走势
            </p>
          </Link>

          <Link
            href="/virtual-market/sectors"
            className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-shadow group"
          >
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-xl font-semibold text-gray-900">板块分析</h4>
              <svg className="w-8 h-8 text-blue-600 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1H5a1 1 0 01-1-1v-3zM14 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1h-4a1 1 0 01-1-1v-3z" />
              </svg>
            </div>
            <p className="text-gray-600">
              通过热力图查看10大行业板块的涨跌表现
            </p>
          </Link>
        </div>

        {/* Features */}
        <div className="mt-16 bg-white rounded-xl shadow-lg p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">核心特性</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">实时更新</h4>
              <p className="text-sm text-gray-600">每分钟自动刷新市场数据</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">市场联动</h4>
              <p className="text-sm text-gray-600">模拟真实的大盘与个股联动</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">零风险学习</h4>
              <p className="text-sm text-gray-600">虚拟资金，真实体验</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">专业数据</h4>
              <p className="text-sm text-gray-600">Beta系数、市值等级</p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-500 text-sm">
            <p>happyStock 虚拟股票市场 - 学习投资的最佳平台</p>
            <p className="mt-2">© 2025 happyStock. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
