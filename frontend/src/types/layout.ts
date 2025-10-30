/**
 * Layout Types - 布局系统类型定义
 * 
 * 对应需求: Feature 004 - 优化首页布局
 * - US1: 内容组织 (FR-001 to FR-006)
 * - US2: 全屏滚动 (FR-007 to FR-012)
 * - US3: 可折叠区块 (FR-013 to FR-016)
 * - US4: 自定义排序 (FR-017 to FR-020)
 */

/**
 * 页面区块定义
 * 用于配置主页各个内容区块
 */
export interface PageSection {
  /** 区块唯一标识符 */
  id: string;
  /** 区块标题(用于导航显示) */
  title: string;
  /** 区块渲染的 React 组件 */
  component: React.ComponentType;
  /** 是否可折叠 (US3) */
  isCollapsible: boolean;
  /** 显示顺序(越小越靠前, US4) */
  order: number;
  /** 区块描述(可选) */
  description?: string;
  /** 是否默认折叠 */
  defaultCollapsed?: boolean;
}

/**
 * 导航点数据
 * 用于页面滚动导航指示器
 */
export interface NavigationDot {
  /** 关联的区块ID */
  sectionId: string;
  /** 导航标签 */
  label: string;
  /** 是否当前激活 */
  isActive: boolean;
  /** 导航点索引 */
  index: number;
  /** 是否可见 */
  isVisible?: boolean;
}

/**
 * 布局偏好设置
 * 用户自定义的布局配置(持久化到 localStorage)
 */
export interface LayoutPreferences {
  /** 是否启用整页滚动 (FR-009) */
  isScrollSnapEnabled: boolean;
  /** 折叠的区块ID列表 (FR-015) */
  collapsedSections: string[];
  /** 自定义区块顺序 (FR-018) */
  sectionOrder: string[];
  /** 导航点位置 */
  navigationPosition?: 'left' | 'right';
  /** 上次更新时间戳 */
  lastUpdated?: number;
}

/**
 * 滚动状态
 * 当前页面滚动状态追踪
 */
export interface ScrollState {
  /** 当前激活的区块ID */
  currentSectionId: string | null;
  /** 是否正在滚动 */
  isScrolling: boolean;
  /** 滚动方向 */
  scrollDirection: 'up' | 'down' | null;
  /** 是否正在执行动画 */
  isAnimating: boolean;
  /** 上一个区块ID */
  previousSectionId?: string | null;
}

/**
 * 区块可见性状态
 * 用于 Intersection Observer 追踪
 */
export interface SectionVisibility {
  /** 区块ID */
  sectionId: string;
  /** 是否可见 */
  isVisible: boolean;
  /** 可见比例 (0-1) */
  intersectionRatio: number;
  /** 是否在视口内 */
  isIntersecting: boolean;
}

/**
 * 拖拽状态 (US4-P3)
 * 用于区块拖拽排序
 */
export interface DragState {
  /** 是否正在拖拽 */
  isDragging: boolean;
  /** 拖拽的区块ID */
  draggedSectionId: string | null;
  /** 拖拽的源索引 */
  sourceIndex: number | null;
  /** 拖拽的目标索引 */
  targetIndex: number | null;
}

/**
 * 滚动配置选项
 */
export interface ScrollOptions {
  /** 滚动行为 */
  behavior?: ScrollBehavior;
  /** 滚动对齐方式 */
  block?: ScrollLogicalPosition;
  /** 是否内联滚动 */
  inline?: ScrollLogicalPosition;
  /** 自定义持续时间(毫秒) */
  duration?: number;
}

/**
 * 布局事件类型
 */
export type LayoutEventType =
  | 'section-change' // 区块切换
  | 'scroll-start' // 滚动开始
  | 'scroll-end' // 滚动结束
  | 'section-collapse' // 区块折叠
  | 'section-expand' // 区块展开
  | 'order-change' // 顺序改变
  | 'snap-toggle'; // 滚动锁定切换

/**
 * 布局事件数据
 */
export interface LayoutEvent {
  /** 事件类型 */
  type: LayoutEventType;
  /** 事件时间戳 */
  timestamp: number;
  /** 相关区块ID */
  sectionId?: string;
  /** 额外数据 */
  data?: Record<string, unknown>;
}

/**
 * 性能指标
 * 用于监控布局性能
 */
export interface LayoutPerformanceMetrics {
  /** 滚动帧率 */
  scrollFPS: number;
  /** 滚动响应时间(ms) */
  scrollResponseTime: number;
  /** 动画帧率 */
  animationFPS: number;
  /** 布局重排次数 */
  layoutReflowCount: number;
  /** 最后测量时间 */
  lastMeasured: number;
}

/**
 * 响应式断点
 */
export enum Breakpoint {
  Mobile = 'mobile', // < 768px
  Tablet = 'tablet', // 768px - 1023px
  Desktop = 'desktop', // >= 1024px
}

/**
 * 设备类型
 */
export interface DeviceInfo {
  /** 当前断点 */
  breakpoint: Breakpoint;
  /** 是否触摸设备 */
  isTouchDevice: boolean;
  /** 是否移动设备 */
  isMobile: boolean;
  /** 视口宽度 */
  viewportWidth: number;
  /** 视口高度 */
  viewportHeight: number;
}
