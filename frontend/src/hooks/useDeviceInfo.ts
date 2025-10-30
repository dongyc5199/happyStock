/**
 * useDeviceInfo Hook - 设备信息和响应式断点
 * 
 * 功能:
 * - 检测设备类型(桌面/平板/移动)
 * - 监听视口尺寸变化
 * - 提供响应式断点
 * - 检测触摸设备
 * 
 * 对应需求: 响应式设计支持
 */

import { useState, useEffect, useCallback } from 'react';
import { Breakpoint } from '@/types/layout';
import type { DeviceInfo } from '@/types/layout';

/**
 * 断点配置
 */
const BREAKPOINTS = {
  mobile: 768, // < 768px
  tablet: 1024, // 768px - 1023px
  desktop: 1024, // >= 1024px
} as const;

/**
 * 获取当前断点
 */
function getBreakpoint(width: number): Breakpoint {
  if (width < BREAKPOINTS.mobile) {
    return Breakpoint.Mobile;
  } else if (width < BREAKPOINTS.desktop) {
    return Breakpoint.Tablet;
  } else {
    return Breakpoint.Desktop;
  }
}

/**
 * 检测是否为触摸设备
 */
function isTouchDevice(): boolean {
  if (typeof window === 'undefined') return false;
  
  return (
    'ontouchstart' in window ||
    navigator.maxTouchPoints > 0 ||
    ('msMaxTouchPoints' in navigator && (navigator as { msMaxTouchPoints: number }).msMaxTouchPoints > 0)
  );
}

/**
 * 获取视口尺寸
 */
function getViewportSize() {
  if (typeof window === 'undefined') {
    return { width: 0, height: 0 };
  }
  
  return {
    width: window.innerWidth,
    height: window.innerHeight,
  };
}

/**
 * 获取设备信息
 */
function getDeviceInfo(): DeviceInfo {
  const { width, height } = getViewportSize();
  const breakpoint = getBreakpoint(width);
  
  return {
    breakpoint,
    isTouchDevice: isTouchDevice(),
    isMobile: breakpoint === 'mobile',
    viewportWidth: width,
    viewportHeight: height,
  };
}

/**
 * useDeviceInfo Hook
 */
export function useDeviceInfo() {
  const [deviceInfo, setDeviceInfo] = useState<DeviceInfo>(() => getDeviceInfo());
  
  /**
   * 处理窗口尺寸变化
   */
  const handleResize = useCallback(() => {
    setDeviceInfo(getDeviceInfo());
  }, []);
  
  /**
   * 防抖版 resize 处理
   */
  useEffect(() => {
    let timeoutId: NodeJS.Timeout;
    
    const debouncedResize = () => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(handleResize, 150); // 150ms 防抖
    };
    
    window.addEventListener('resize', debouncedResize);
    
    // 初始化时立即执行一次
    handleResize();
    
    return () => {
      clearTimeout(timeoutId);
      window.removeEventListener('resize', debouncedResize);
    };
  }, [handleResize]);
  
  return deviceInfo;
}

/**
 * 检查是否为指定断点
 */
export function useBreakpoint(targetBreakpoint: Breakpoint): boolean {
  const { breakpoint } = useDeviceInfo();
  return breakpoint === targetBreakpoint;
}

/**
 * 检查是否为移动设备
 */
export function useIsMobile(): boolean {
  const { isMobile } = useDeviceInfo();
  return isMobile;
}

/**
 * 检查是否为触摸设备
 */
export function useIsTouchDevice(): boolean {
  const { isTouchDevice: isTouch } = useDeviceInfo();
  return isTouch;
}

/**
 * 获取视口尺寸
 */
export function useViewportSize() {
  const { viewportWidth, viewportHeight } = useDeviceInfo();
  return { width: viewportWidth, height: viewportHeight };
}

/**
 * 媒体查询 Hook
 */
export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(() => {
    if (typeof window === 'undefined') return false;
    return window.matchMedia(query).matches;
  });
  
  useEffect(() => {
    const mediaQuery = window.matchMedia(query);
    
    const handleChange = (event: MediaQueryListEvent) => {
      setMatches(event.matches);
    };
    
    // 初始检查
    setMatches(mediaQuery.matches);
    
    // 添加监听器
    mediaQuery.addEventListener('change', handleChange);
    
    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  }, [query]);
  
  return matches;
}

/**
 * 检查是否偏好减少动画
 */
export function usePrefersReducedMotion(): boolean {
  return useMediaQuery('(prefers-reduced-motion: reduce)');
}

/**
 * 检查是否为深色模式
 */
export function usePrefersDarkMode(): boolean {
  return useMediaQuery('(prefers-color-scheme: dark)');
}
