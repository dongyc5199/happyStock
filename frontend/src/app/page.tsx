'use client';

import { useEffect, useState, useMemo } from 'react';
import Link from 'next/link';
import { marketApi } from '@/lib/api/virtual-market';
import type { MarketOverview as MarketOverviewType } from '@/types/virtual-market';
import type { PageSection as PageSectionType } from '@/types/layout';
import { IntegratedHeroSection } from '@/components/home/IntegratedHeroSection';
import { QuickActionsSection } from '@/components/home/QuickActionsSection';
import { PageSection } from '@/components/layout/PageSection';
import { HomePageLayout } from '@/components/layout/HomePageLayout';
import { ErrorBoundary } from '@/components/ui/ErrorBoundary';
import { useLayoutStore } from '@/store/layoutStore';
import { enablePerformanceMonitoring } from '@/lib/performance-monitor';

// 不再需要 lazy load,新组件更轻量

export default function Home() {
  const [marketOverview, setMarketOverview] = useState<MarketOverviewType | null>(null);
  const [loading, setLoading] = useState(true);

  // Layout store
  const initializeLayout = useLayoutStore((state) => state.initialize);
  const isLayoutInitialized = useLayoutStore((state) => state.isInitialized);
  const setCurrentSection = useLayoutStore((state) => state.setCurrentSection);

  // 定义页面区块配置 (T009)
  // Note: component 字段使用占位组件,实际渲染在 JSX 中完成
  const DummyComponent = () => null;
  
  const pageSections = useMemo<PageSectionType[]>(() => [
    {
      id: 'hero',
      title: '欢迎使用 happyStock',
      component: DummyComponent,
      isCollapsible: false,
      order: 0,
      description: '欢迎区块 + 核心价值',
    },
    {
      id: 'quick-actions',
      title: '快速操作与学习资源',
      component: DummyComponent,
      isCollapsible: false,
      order: 1,
      description: '功能入口 + 投资教育',
    },
  ], []);

  // 初始化布局系统
  useEffect(() => {
    if (!isLayoutInitialized) {
      initializeLayout(pageSections);
      // 设置第一个区块为初始激活状态
      if (pageSections.length > 0) {
        setCurrentSection(pageSections[0].id);
      }
    }
  }, [isLayoutInitialized, initializeLayout, pageSections, setCurrentSection]);

  // 启用性能监控 (仅开发环境)
  useEffect(() => {
    enablePerformanceMonitoring();
  }, []);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      setLoading(true);
      const marketResponse = await marketApi.getMarketOverview();

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
    <HomePageLayout>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 overflow-y-auto scroll-smooth" style={{ scrollSnapType: 'y proximity' }}>
        {/* Header */}
        <header className="sticky top-0 z-50 bg-gradient-to-r from-blue-50/95 via-indigo-50/95 to-purple-50/95 backdrop-blur-md border-b border-blue-100/50 shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center shadow-md">
                    <span className="text-white font-bold text-sm">H</span>
                  </div>
                  <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                    happyStock
                  </h1>
                </div>
                <span className="px-3 py-1 text-xs font-medium text-indigo-700 bg-indigo-100 rounded-full border border-indigo-200">
                  虚拟市场
                </span>
              </div>
              <nav className="flex gap-6">
                <Link 
                  href="/virtual-market" 
                  className="text-gray-700 hover:text-indigo-600 font-medium transition-colors relative group"
                >
                  市场首页
                  <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-indigo-600 transition-all group-hover:w-full"></span>
                </Link>
                <Link 
                  href="/virtual-market/indices" 
                  className="text-gray-700 hover:text-indigo-600 font-medium transition-colors relative group"
                >
                  指数看板
                  <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-indigo-600 transition-all group-hover:w-full"></span>
                </Link>
                <Link 
                  href="/virtual-market/sectors" 
                  className="text-gray-700 hover:text-indigo-600 font-medium transition-colors relative group"
                >
                  板块分析
                  <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-indigo-600 transition-all group-hover:w-full"></span>
                </Link>
              </nav>
            </div>
          </div>
        </header>

        {/* 区块 1: 整合的英雄区 (欢迎 + 核心价值 + 市场数据) */}
        <PageSection id="hero" title="欢迎使用 happyStock" isCollapsible={false}>
          <ErrorBoundary>
            <IntegratedHeroSection 
              userCount={15234} 
              marketOverview={marketOverview}
              loading={loading}
            />
          </ErrorBoundary>
        </PageSection>

        {/* 区块 2: 快速操作与学习资源 (功能入口 + 投资教育 + FAQ) */}
        <PageSection id="quick-actions" title="快速操作与学习资源" isCollapsible={false}>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <ErrorBoundary>
              <QuickActionsSection />
            </ErrorBoundary>
          </div>
        </PageSection>

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
    </HomePageLayout>
  );
}
