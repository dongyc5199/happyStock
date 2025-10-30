/**
 * HomePage Layout Container
 * 
 * 包装首页的布局增强功能:
 * - 整页滚动
 * - 导航点
 * - Intersection Observer
 * - 键盘导航
 */

'use client';

import { useEffect, useMemo } from 'react';
import { NavigationDots } from '@/components/layout/NavigationDots';
import { ScrollSettingsToggle } from '@/components/layout/ScrollSettingsToggle';
import { useLayoutStore } from '@/store/layoutStore';
import { useScrollSnap } from '@/hooks/useScrollSnap';
import { useIntersectionObserver } from '@/hooks/useIntersectionObserver';
import { useKeyboardNavigation } from '@/hooks/useKeyboardNavigation';
import { useDeviceInfo } from '@/hooks/useDeviceInfo';
import type { NavigationDot } from '@/types/layout';

export interface HomePageLayoutProps {
  children: React.ReactNode;
}

export function HomePageLayout({ children }: HomePageLayoutProps) {
  // Store 状态
  const sections = useLayoutStore((state) => state.sections);
  const currentSectionId = useLayoutStore(
    (state) => state.scrollState.currentSectionId
  );
  const updateNavigationDots = useLayoutStore(
    (state) => state.updateNavigationDots
  );
  const isScrollSnapEnabled = useLayoutStore(
    (state) => state.preferences.isScrollSnapEnabled
  );

  // Device info
  const { isMobile } = useDeviceInfo();

  // Hooks
  const { scrollToSectionById } = useScrollSnap({
    enabled: isScrollSnapEnabled,
  });

  useIntersectionObserver({
    enabled: true,
  });

  useKeyboardNavigation({
    enabled: true,
    onlyWhenSnapEnabled: true,
  });

  // 生成导航点数据
  const navigationDots = useMemo<NavigationDot[]>(() => {
    return sections.map((section, index) => ({
      sectionId: section.id,
      label: section.title,
      isActive: section.id === currentSectionId,
      index,
      isVisible: true,
    }));
  }, [sections, currentSectionId]);

  // 更新导航点到 store
  useEffect(() => {
    updateNavigationDots(navigationDots);
  }, [navigationDots, updateNavigationDots]);

  // 处理导航点点击
  const handleDotClick = (sectionId: string) => {
    scrollToSectionById(sectionId, true);
  };

  return (
    <>
      {children}
      
      {/* 导航点 - 桌面端右侧,移动端隐藏 */}
      {!isMobile && sections.length > 0 && (
        <NavigationDots
          dots={navigationDots}
          onDotClick={handleDotClick}
          position="right"
        />
      )}
      
      {/* 滚动设置切换 */}
      <ScrollSettingsToggle position="fixed" />
    </>
  );
}
