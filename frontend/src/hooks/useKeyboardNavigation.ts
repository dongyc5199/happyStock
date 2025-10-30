/**
 * useKeyboardNavigation Hook - 键盘导航支持
 * 
 * 功能:
 * - 箭头键上下切换区块
 * - Home/End 键跳转首尾
 * - PageUp/PageDown 快速导航
 * - 可访问性支持
 * 
 * 对应需求: US2 (FR-012), 可访问性
 */

import { useEffect, useCallback, useMemo } from 'react';
import { useLayoutStore } from '@/store/layoutStore';

/**
 * useKeyboardNavigation 配置选项
 */
export interface UseKeyboardNavigationOptions {
  /** 是否启用 */
  enabled?: boolean;
  /** 是否启用箭头键导航 */
  enableArrowKeys?: boolean;
  /** 是否启用 Home/End 键 */
  enableHomeEnd?: boolean;
  /** 是否启用 PageUp/PageDown */
  enablePageKeys?: boolean;
  /** 是否只在滚动锁定时启用 */
  onlyWhenSnapEnabled?: boolean;
  /** 自定义按键处理 */
  onKeyPress?: (event: KeyboardEvent) => void;
}

/**
 * 默认配置
 */
const DEFAULT_OPTIONS: Required<Omit<UseKeyboardNavigationOptions, 'onKeyPress'>> = {
  enabled: true,
  enableArrowKeys: true,
  enableHomeEnd: true,
  enablePageKeys: true,
  onlyWhenSnapEnabled: true,
};

/**
 * useKeyboardNavigation Hook
 */
export function useKeyboardNavigation(
  options: UseKeyboardNavigationOptions = {}
) {
  const config = useMemo(() => ({ ...DEFAULT_OPTIONS, ...options }), [options]);
  
  // Store 状态
  const sections = useLayoutStore((state) => state.sections);
  const isScrollSnapEnabled = useLayoutStore(
    (state) => state.preferences.isScrollSnapEnabled
  );
  const currentSectionId = useLayoutStore(
    (state) => state.scrollState.currentSectionId
  );
  const setCurrentSection = useLayoutStore((state) => state.setCurrentSection);
  
  /**
   * 获取所有区块元素
   */
  const getSectionElements = useCallback((): HTMLElement[] => {
    return Array.from(
      document.querySelectorAll('[data-section-id]')
    ) as HTMLElement[];
  }, []);
  
  /**
   * 获取当前区块索引
   */
  const getCurrentIndex = useCallback((): number => {
    if (!currentSectionId) return 0;
    
    const sectionElements = getSectionElements();
    const currentElement = sectionElements.find(
      (el) => el.getAttribute('data-section-id') === currentSectionId
    );
    
    return currentElement ? sectionElements.indexOf(currentElement) : 0;
  }, [currentSectionId, getSectionElements]);
  
  /**
   * 滚动到指定索引的区块
   */
  const scrollToIndex = useCallback(
    (index: number, smooth = true) => {
      const sectionElements = getSectionElements();
      
      // 边界检查
      if (index < 0 || index >= sectionElements.length) {
        return;
      }
      
      const targetElement = sectionElements[index];
      const sectionId = targetElement.getAttribute('data-section-id');
      
      if (sectionId) {
        // 更新 store
        setCurrentSection(sectionId);
        
        // 滚动到目标
        targetElement.scrollIntoView({
          behavior: smooth ? 'smooth' : 'auto',
          block: 'start',
        });
      }
    },
    [getSectionElements, setCurrentSection]
  );
  
  /**
   * 滚动到下一个区块
   */
  const scrollToNext = useCallback(() => {
    const currentIndex = getCurrentIndex();
    scrollToIndex(currentIndex + 1);
  }, [getCurrentIndex, scrollToIndex]);
  
  /**
   * 滚动到上一个区块
   */
  const scrollToPrevious = useCallback(() => {
    const currentIndex = getCurrentIndex();
    scrollToIndex(currentIndex - 1);
  }, [getCurrentIndex, scrollToIndex]);
  
  /**
   * 滚动到第一个区块
   */
  const scrollToFirst = useCallback(() => {
    scrollToIndex(0);
  }, [scrollToIndex]);
  
  /**
   * 滚动到最后一个区块
   */
  const scrollToLast = useCallback(() => {
    const sectionElements = getSectionElements();
    scrollToIndex(sectionElements.length - 1);
  }, [getSectionElements, scrollToIndex]);
  
  /**
   * 处理键盘事件
   */
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      // 检查是否启用
      if (!config.enabled) return;
      
      // 如果设置了只在滚动锁定时启用,检查滚动锁定状态
      if (config.onlyWhenSnapEnabled && !isScrollSnapEnabled) {
        return;
      }
      
      // 如果焦点在输入框等元素上,不处理
      const target = event.target as HTMLElement;
      if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable
      ) {
        return;
      }
      
      // 调用自定义处理器
      if (config.onKeyPress) {
        config.onKeyPress(event);
      }
      
      let handled = false;
      
      // 箭头键导航
      if (config.enableArrowKeys) {
        if (event.key === 'ArrowDown') {
          event.preventDefault();
          scrollToNext();
          handled = true;
        } else if (event.key === 'ArrowUp') {
          event.preventDefault();
          scrollToPrevious();
          handled = true;
        }
      }
      
      // Home/End 键
      if (config.enableHomeEnd) {
        if (event.key === 'Home') {
          event.preventDefault();
          scrollToFirst();
          handled = true;
        } else if (event.key === 'End') {
          event.preventDefault();
          scrollToLast();
          handled = true;
        }
      }
      
      // PageUp/PageDown
      if (config.enablePageKeys) {
        if (event.key === 'PageDown') {
          event.preventDefault();
          scrollToNext();
          handled = true;
        } else if (event.key === 'PageUp') {
          event.preventDefault();
          scrollToPrevious();
          handled = true;
        }
      }
      
      // Space 键 (向下滚动)
      if (event.key === ' ' && !event.shiftKey) {
        event.preventDefault();
        scrollToNext();
        handled = true;
      }
      
      // Shift + Space (向上滚动)
      if (event.key === ' ' && event.shiftKey) {
        event.preventDefault();
        scrollToPrevious();
        handled = true;
      }
      
      // 如果事件被处理,触发 ARIA 实时区域更新
      if (handled && currentSectionId) {
        announceNavigation(currentSectionId);
      }
    },
    [
      config,
      isScrollSnapEnabled,
      currentSectionId,
      scrollToNext,
      scrollToPrevious,
      scrollToFirst,
      scrollToLast,
    ]
  );
  
  /**
   * 监听键盘事件
   */
  useEffect(() => {
    if (!config.enabled) return;
    
    window.addEventListener('keydown', handleKeyDown);
    
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [config.enabled, handleKeyDown]);
  
  /**
   * 返回工具函数
   */
  return {
    /** 滚动到下一个区块 */
    scrollToNext,
    /** 滚动到上一个区块 */
    scrollToPrevious,
    /** 滚动到第一个区块 */
    scrollToFirst,
    /** 滚动到最后一个区块 */
    scrollToLast,
    /** 滚动到指定索引 */
    scrollToIndex,
    /** 当前区块索引 */
    currentIndex: getCurrentIndex(),
    /** 区块总数 */
    totalSections: sections.length,
  };
}

/**
 * ARIA 实时区域公告 (用于屏幕阅读器)
 */
function announceNavigation(sectionId: string) {
  // 查找或创建 ARIA live region
  let liveRegion = document.getElementById('layout-navigation-announcer');
  
  if (!liveRegion) {
    liveRegion = document.createElement('div');
    liveRegion.id = 'layout-navigation-announcer';
    liveRegion.setAttribute('role', 'status');
    liveRegion.setAttribute('aria-live', 'polite');
    liveRegion.setAttribute('aria-atomic', 'true');
    liveRegion.style.position = 'absolute';
    liveRegion.style.left = '-10000px';
    liveRegion.style.width = '1px';
    liveRegion.style.height = '1px';
    liveRegion.style.overflow = 'hidden';
    document.body.appendChild(liveRegion);
  }
  
  // 获取区块标题
  const sectionElement = document.querySelector(`[data-section-id="${sectionId}"]`);
  const sectionTitle = sectionElement?.getAttribute('data-section-title') || sectionId;
  
  // 更新公告内容
  liveRegion.textContent = `导航到 ${sectionTitle}`;
}
