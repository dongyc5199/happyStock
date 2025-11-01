'use client';

import { useEffect, useMemo } from 'react';
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

  return (
    <HomePageLayout>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 overflow-y-auto scroll-smooth" style={{ scrollSnapType: 'y proximity' }}>
        {/* 区块 1: 整合的英雄区 (欢迎 + 核心价值 + 市场数据) */}
        <PageSection id="hero" title="欢迎使用 happyStock" isCollapsible={false}>
          <ErrorBoundary>
            <IntegratedHeroSection 
              userCount={15234}
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
