/**
 * useIntersectionObserver Hook - 区块可见性监听
 * 
 * 功能:
 * - 封装 Intersection Observer API
 * - 监听区块可见性变化
 * - 自动更新激活状态
 * - 性能优化(单例模式)
 * 
 * 对应需求: US2 (FR-010, FR-011)
 */

import { useEffect, useRef, useCallback } from 'react';
import { useLayoutStore } from '@/store/layoutStore';
import type { SectionVisibility } from '@/types/layout';

/**
 * useIntersectionObserver 配置选项
 */
export interface UseIntersectionObserverOptions {
  /** 根元素(默认为 viewport) */
  root?: Element | null;
  /** 根元素外边距 */
  rootMargin?: string;
  /** 可见度阈值 */
  threshold?: number | number[];
  /** 是否启用 */
  enabled?: boolean;
  /** 可见性变化回调 */
  onChange?: (entries: IntersectionObserverEntry[]) => void;
}

/**
 * 默认配置
 */
const DEFAULT_OPTIONS: Required<Omit<UseIntersectionObserverOptions, 'onChange'>> = {
  root: null,
  rootMargin: '0px',
  threshold: [0, 0.25, 0.5, 0.75, 1.0], // 多个阈值以获得精确的可见度
  enabled: true,
};

/**
 * useIntersectionObserver Hook
 */
export function useIntersectionObserver(
  options: UseIntersectionObserverOptions = {}
) {
  const config = useRef({ ...DEFAULT_OPTIONS, ...options }).current;
  
  // Store 状态
  const setCurrentSection = useLayoutStore((state) => state.setCurrentSection);
  
  // Refs
  const observerRef = useRef<IntersectionObserver | null>(null);
  const sectionsMapRef = useRef<Map<Element, SectionVisibility>>(new Map());
  
  /**
   * 处理 Intersection 变化
   */
  const handleIntersection = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      // 更新 sections map
      entries.forEach((entry) => {
        const sectionId = entry.target.getAttribute('data-section-id');
        
        if (sectionId) {
          const visibility: SectionVisibility = {
            sectionId,
            isVisible: entry.isIntersecting,
            intersectionRatio: entry.intersectionRatio,
            isIntersecting: entry.isIntersecting,
          };
          
          sectionsMapRef.current.set(entry.target, visibility);
        }
      });
      
      // 找到最可见的区块(intersectionRatio 最大)
      let mostVisibleSectionId: string | null = null;
      let maxRatio = 0;
      
      sectionsMapRef.current.forEach((visibility) => {
        if (visibility.isIntersecting && visibility.intersectionRatio > maxRatio) {
          maxRatio = visibility.intersectionRatio;
          mostVisibleSectionId = visibility.sectionId;
        }
      });
      
      // 更新当前激活区块 (降低阈值到 0.3，使导航点更灵敏)
      if (mostVisibleSectionId && maxRatio >= 0.3) {
        setCurrentSection(mostVisibleSectionId);
      }
      
      // 调用自定义回调
      if (config.onChange) {
        config.onChange(entries);
      }
    },
    [config, setCurrentSection]
  );
  
  /**
   * 创建 Observer
   */
  const createObserver = useCallback(() => {
    // 销毁旧的 observer
    if (observerRef.current) {
      observerRef.current.disconnect();
    }
    
    // 创建新的 observer
    observerRef.current = new IntersectionObserver(handleIntersection, {
      root: config.root,
      rootMargin: config.rootMargin,
      threshold: config.threshold,
    });
    
    return observerRef.current;
  }, [config.root, config.rootMargin, config.threshold, handleIntersection]);
  
  /**
   * 观察指定元素
   */
  const observe = useCallback(
    (element: Element) => {
      if (!config.enabled) return;
      
      const observer = observerRef.current || createObserver();
      observer.observe(element);
    },
    [config.enabled, createObserver]
  );
  
  /**
   * 取消观察指定元素
   */
  const unobserve = useCallback((element: Element) => {
    if (observerRef.current) {
      observerRef.current.unobserve(element);
      sectionsMapRef.current.delete(element);
    }
  }, []);
  
  /**
   * 观察所有区块
   */
  const observeAllSections = useCallback(() => {
    if (!config.enabled) return;
    
    const sectionElements = document.querySelectorAll('[data-section-id]');
    const observer = observerRef.current || createObserver();
    
    sectionElements.forEach((element) => {
      observer.observe(element);
    });
  }, [config.enabled, createObserver]);
  
  /**
   * 取消观察所有区块
   */
  const unobserveAll = useCallback(() => {
    if (observerRef.current) {
      observerRef.current.disconnect();
      sectionsMapRef.current.clear();
    }
  }, []);
  
  /**
   * 获取指定区块的可见性信息
   */
  const getSectionVisibility = useCallback((element: Element): SectionVisibility | null => {
    return sectionsMapRef.current.get(element) || null;
  }, []);
  
  /**
   * 自动观察所有区块
   */
  useEffect(() => {
    if (!config.enabled) return;
    
    // 初始化 observer
    const observer = createObserver();
    const sectionsMap = sectionsMapRef.current;
    
    // 观察所有现有的区块
    observeAllSections();
    
    // 清理函数
    return () => {
      observer.disconnect();
      sectionsMap.clear();
    };
  }, [config.enabled, createObserver, observeAllSections]);
  
  /**
   * 返回工具函数
   */
  return {
    /** 观察指定元素 */
    observe,
    /** 取消观察指定元素 */
    unobserve,
    /** 观察所有区块 */
    observeAllSections,
    /** 取消观察所有区块 */
    unobserveAll,
    /** 获取区块可见性信息 */
    getSectionVisibility,
    /** Observer 实例 */
    observer: observerRef.current,
  };
}

/**
 * 简化版 Hook - 自动观察单个元素
 */
export function useSectionObserver(
  elementRef: React.RefObject<Element>,
  options: UseIntersectionObserverOptions = {}
) {
  const { observe, unobserve } = useIntersectionObserver(options);
  
  useEffect(() => {
    const element = elementRef.current;
    
    if (element && options.enabled !== false) {
      observe(element);
      
      return () => {
        unobserve(element);
      };
    }
  }, [elementRef, observe, unobserve, options.enabled]);
}
