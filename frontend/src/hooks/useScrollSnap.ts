/**
 * useScrollSnap Hook - 整页滚动逻辑
 * 
 * 功能:
 * - 监听滚轮/触摸事件
 * - 防抖动处理,避免快速连续滚动
 * - 平滑滚动到目标区块
 * - 支持禁用滚动锁定
 * - 性能监控 (开发环境)
 * 
 * 对应需求: US2 (FR-007, FR-008, FR-009)
 */

import { useEffect, useCallback, useRef, useState } from 'react';
import { useLayoutStore } from '@/store/layoutStore';
import { recordScrollStart, recordScrollEnd } from '@/lib/performance-monitor';

/**
 * useScrollSnap 配置选项
 */
export interface UseScrollSnapOptions {
  /** 是否启用滚动锁定 (可被 store 中的设置覆盖) */
  enabled?: boolean;
  /** 滚动防抖延迟(毫秒) */
  debounceDelay?: number;
  /** 滚动动画持续时间(毫秒) */
  scrollDuration?: number;
  /** 滚动阈值(0-1),超过此比例才触发滚动 */
  threshold?: number;
  /** 是否在移动设备上禁用 */
  disableOnMobile?: boolean;
}

/**
 * 默认配置
 */
const DEFAULT_OPTIONS: Required<UseScrollSnapOptions> = {
  enabled: true,
  debounceDelay: 1000, // 1秒防抖
  scrollDuration: 800, // 800ms 动画
  threshold: 0.5, // 50% 可见度
  disableOnMobile: false,
};

/**
 * useScrollSnap Hook
 */
export function useScrollSnap(options: UseScrollSnapOptions = {}) {
  const config = { ...DEFAULT_OPTIONS, ...options };
  
  // Store 状态
  const isScrollSnapEnabled = useLayoutStore(
    (state) => state.preferences.isScrollSnapEnabled
  );
  const updateScrollState = useLayoutStore((state) => state.updateScrollState);
  
  // 检测用户是否偏好减少动画
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  
  useEffect(() => {
    // 检查 prefers-reduced-motion 媒体查询
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);
    
    // 监听变化
    const handleChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches);
    };
    
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);
  
  // Refs
  const isScrollingRef = useRef(false);
  const scrollTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const lastScrollTimeRef = useRef(0);
  
  /**
   * 向屏幕阅读器宣布信息
   */
  const announceToScreenReader = useCallback((message: string) => {
    // 查找或创建 ARIA live region
    let liveRegion = document.getElementById('scroll-snap-announcer');
    
    if (!liveRegion) {
      liveRegion = document.createElement('div');
      liveRegion.id = 'scroll-snap-announcer';
      liveRegion.setAttribute('role', 'status');
      liveRegion.setAttribute('aria-live', 'polite');
      liveRegion.setAttribute('aria-atomic', 'true');
      liveRegion.className = 'sr-only';
      
      // 添加 sr-only 样式
      liveRegion.style.position = 'absolute';
      liveRegion.style.width = '1px';
      liveRegion.style.height = '1px';
      liveRegion.style.padding = '0';
      liveRegion.style.margin = '-1px';
      liveRegion.style.overflow = 'hidden';
      liveRegion.style.clip = 'rect(0, 0, 0, 0)';
      liveRegion.style.whiteSpace = 'nowrap';
      liveRegion.style.border = '0';
      
      document.body.appendChild(liveRegion);
    }
    
    // 更新内容
    liveRegion.textContent = message;
    
    // 3秒后清空,避免重复宣布
    setTimeout(() => {
      if (liveRegion) {
        liveRegion.textContent = '';
      }
    }, 3000);
  }, []);
  
  /**
   * 获取当前视口中的区块
   */
  const getCurrentSection = useCallback((): HTMLElement | null => {
    const sectionElements = document.querySelectorAll('[data-section-id]');
    let closestSection: HTMLElement | null = null;
    let minDistance = Infinity;
    
    sectionElements.forEach((element) => {
      const rect = element.getBoundingClientRect();
      const distance = Math.abs(rect.top);
      
      if (distance < minDistance) {
        minDistance = distance;
        closestSection = element as HTMLElement;
      }
    });
    
    return closestSection;
  }, []);
  
  /**
   * 获取下一个区块
   */
  const getNextSection = useCallback(
    (direction: 'up' | 'down'): HTMLElement | null => {
      const currentSection = getCurrentSection();
      if (!currentSection) return null;
      
      const sectionElements = Array.from(
        document.querySelectorAll('[data-section-id]')
      ) as HTMLElement[];
      
      const currentIndex = sectionElements.indexOf(currentSection);
      
      if (direction === 'down') {
        return sectionElements[currentIndex + 1] || null;
      } else {
        return sectionElements[currentIndex - 1] || null;
      }
    },
    [getCurrentSection]
  );
  
  /**
   * 平滑滚动到指定区块
   */
  const scrollToSection = useCallback(
    (sectionElement: HTMLElement, smooth = true) => {
      if (!sectionElement) return;
      
      // 性能监控 - 记录滚动开始
      recordScrollStart();
      
      // 更新滚动状态
      updateScrollState({
        isScrolling: true,
        isAnimating: true,
      });
      
      // 屏幕阅读器宣布
      const sectionTitle = sectionElement.getAttribute('data-section-title') || '未知区块';
      const allSections = document.querySelectorAll('[data-section-id]');
      const currentIndex = Array.from(allSections).indexOf(sectionElement);
      const totalSections = allSections.length;
      
      announceToScreenReader(
        `正在导航到 ${sectionTitle}，第 ${currentIndex + 1} 个区块，共 ${totalSections} 个区块`
      );
      
      // 执行滚动
      sectionElement.scrollIntoView({
        behavior: smooth ? 'smooth' : 'auto',
        block: 'start',
      });
      
      // 滚动完成后重置状态
      setTimeout(() => {
        updateScrollState({
          isScrolling: false,
          isAnimating: false,
        });
        isScrollingRef.current = false;
        
        // 性能监控 - 记录滚动结束
        recordScrollEnd();
      }, config.scrollDuration);
    },
    [config.scrollDuration, updateScrollState, announceToScreenReader]
  );
  
  /**
   * 根据区块ID滚动
   */
  const scrollToSectionById = useCallback(
    (sectionId: string, smooth = true) => {
      const element = document.querySelector(
        `[data-section-id="${sectionId}"]`
      ) as HTMLElement;
      
      if (element) {
        scrollToSection(element, smooth);
      }
    },
    [scrollToSection]
  );
  
  /**
   * 处理滚轮事件
   */
  const handleWheel = useCallback(
    (event: WheelEvent) => {
      // 检查是否启用 (包括 prefers-reduced-motion 检查)
      if (!config.enabled || !isScrollSnapEnabled || prefersReducedMotion) {
        return;
      }
      
      // 防抖检查
      const now = Date.now();
      const timeSinceLastScroll = now - lastScrollTimeRef.current;
      
      if (timeSinceLastScroll < config.debounceDelay && isScrollingRef.current) {
        event.preventDefault();
        return;
      }
      
      // 检查是否正在滚动
      if (isScrollingRef.current) {
        event.preventDefault();
        return;
      }
      
      // 确定滚动方向
      const direction = event.deltaY > 0 ? 'down' : 'up';
      const nextSection = getNextSection(direction);
      
      if (nextSection) {
        event.preventDefault();
        
        // 标记正在滚动
        isScrollingRef.current = true;
        lastScrollTimeRef.current = now;
        
        // 更新滚动方向
        updateScrollState({
          scrollDirection: direction,
        });
        
        // 滚动到下一个区块
        scrollToSection(nextSection);
      }
    },
    [
      config.enabled,
      config.debounceDelay,
      isScrollSnapEnabled,
      prefersReducedMotion,
      getNextSection,
      scrollToSection,
      updateScrollState,
    ]
  );
  
  /**
   * 处理触摸事件 (移动设备)
   */
  const touchStartY = useRef(0);
  
  const handleTouchStart = useCallback((event: TouchEvent) => {
    touchStartY.current = event.touches[0].clientY;
  }, []);
  
  const handleTouchEnd = useCallback(
    (event: TouchEvent) => {
      if (!config.enabled || !isScrollSnapEnabled || prefersReducedMotion) {
        return;
      }
      
      if (config.disableOnMobile) {
        return;
      }
      
      const touchEndY = event.changedTouches[0].clientY;
      const deltaY = touchStartY.current - touchEndY;
      
      // 最小滑动距离(50px)
      if (Math.abs(deltaY) < 50) {
        return;
      }
      
      // 防抖检查
      if (isScrollingRef.current) {
        event.preventDefault();
        return;
      }
      
      const direction = deltaY > 0 ? 'down' : 'up';
      const nextSection = getNextSection(direction);
      
      if (nextSection) {
        event.preventDefault();
        isScrollingRef.current = true;
        
        updateScrollState({
          scrollDirection: direction,
        });
        
        scrollToSection(nextSection);
      }
    },
    [
      config.enabled,
      config.disableOnMobile,
      isScrollSnapEnabled,
      prefersReducedMotion,
      getNextSection,
      scrollToSection,
      updateScrollState,
    ]
  );
  
  /**
   * 清理定时器
   */
  useEffect(() => {
    return () => {
      const timeout = scrollTimeoutRef.current;
      if (timeout) {
        clearTimeout(timeout);
      }
    };
  }, []);
  
  /**
   * 监听滚轮和触摸事件
   */
  useEffect(() => {
    if (!config.enabled || !isScrollSnapEnabled) {
      return;
    }
    
    // 添加事件监听器 (passive: false 允许 preventDefault)
    window.addEventListener('wheel', handleWheel, { passive: false });
    window.addEventListener('touchstart', handleTouchStart, { passive: true });
    window.addEventListener('touchend', handleTouchEnd, { passive: false });
    
    return () => {
      window.removeEventListener('wheel', handleWheel);
      window.removeEventListener('touchstart', handleTouchStart);
      window.removeEventListener('touchend', handleTouchEnd);
    };
  }, [
    config.enabled,
    isScrollSnapEnabled,
    handleWheel,
    handleTouchStart,
    handleTouchEnd,
  ]);
  
  /**
   * 返回工具函数
   */
  return {
    /** 滚动到指定区块 */
    scrollToSection,
    /** 根据ID滚动到区块 */
    scrollToSectionById,
    /** 滚动到下一个区块 */
    scrollToNext: useCallback(() => {
      const nextSection = getNextSection('down');
      if (nextSection) {
        scrollToSection(nextSection);
      }
    }, [getNextSection, scrollToSection]),
    /** 滚动到上一个区块 */
    scrollToPrevious: useCallback(() => {
      const prevSection = getNextSection('up');
      if (prevSection) {
        scrollToSection(prevSection);
      }
    }, [getNextSection, scrollToSection]),
    /** 获取当前区块 */
    getCurrentSection,
    /** 是否正在滚动 */
    isScrolling: isScrollingRef.current,
  };
}
