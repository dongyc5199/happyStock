/**
 * Layout Store - 布局状态管理
 * 
 * 使用 Zustand 管理首页布局状态:
 * - 区块配置和顺序
 * - 用户偏好设置
 * - 滚动状态追踪
 * 
 * 对应需求: Feature 004
 * - US1: 内容组织 (FR-001 to FR-006)
 * - US2: 全屏滚动 (FR-007 to FR-012)
 * - US3: 可折叠区块 (FR-013 to FR-016)
 * - US4: 自定义排序 (FR-017 to FR-020)
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type {
  PageSection,
  LayoutPreferences,
  ScrollState,
  NavigationDot,
} from '@/types/layout';

/**
 * 布局 Store 状态接口
 */
interface LayoutState {
  // ==================== 状态 ====================
  
  /** 所有页面区块配置 */
  sections: PageSection[];
  
  /** 用户布局偏好 */
  preferences: LayoutPreferences;
  
  /** 当前滚动状态 */
  scrollState: ScrollState;
  
  /** 导航点数据 */
  navigationDots: NavigationDot[];
  
  /** Store 是否已初始化 */
  isInitialized: boolean;
  
  // ==================== Actions ====================
  
  /**
   * 初始化 Store
   * @param sections - 初始区块配置
   */
  initialize: (sections: PageSection[]) => void;
  
  /**
   * 更新区块配置
   * @param sectionId - 区块ID
   * @param updates - 部分更新数据
   */
  updateSection: (sectionId: string, updates: Partial<PageSection>) => void;
  
  /**
   * 切换区块折叠状态 (US3)
   * @param sectionId - 区块ID
   */
  toggleCollapse: (sectionId: string) => void;
  
  /**
   * 设置区块顺序 (US4)
   * @param sectionOrder - 新的区块ID顺序数组
   */
  setSectionOrder: (sectionOrder: string[]) => void;
  
  /**
   * 切换整页滚动开关 (US2, FR-009)
   * @param enabled - 是否启用
   */
  setScrollSnap: (enabled: boolean) => void;
  
  /**
   * 更新当前激活的区块 (US2)
   * @param sectionId - 当前激活的区块ID
   */
  setCurrentSection: (sectionId: string | null) => void;
  
  /**
   * 更新滚动状态
   * @param updates - 滚动状态部分更新
   */
  updateScrollState: (updates: Partial<ScrollState>) => void;
  
  /**
   * 更新导航点数据
   * @param dots - 新的导航点数组
   */
  updateNavigationDots: (dots: NavigationDot[]) => void;
  
  /**
   * 设置导航点位置
   * @param position - 'left' 或 'right'
   */
  setNavigationPosition: (position: 'left' | 'right') => void;
  
  /**
   * 重置为默认设置
   */
  reset: () => void;
  
  /**
   * 获取排序后的区块列表
   */
  getSortedSections: () => PageSection[];
}

/**
 * 默认布局偏好
 */
const defaultPreferences: LayoutPreferences = {
  isScrollSnapEnabled: true, // 默认启用整页滚动
  collapsedSections: [], // 默认所有区块展开
  sectionOrder: [], // 空数组表示使用默认顺序
  navigationPosition: 'right',
  lastUpdated: Date.now(),
};

/**
 * 默认滚动状态
 */
const defaultScrollState: ScrollState = {
  currentSectionId: null,
  isScrolling: false,
  scrollDirection: null,
  isAnimating: false,
  previousSectionId: null,
};

/**
 * Layout Store Hook
 */
export const useLayoutStore = create<LayoutState>()(
  devtools(
    persist(
      (set, get) => ({
        // ==================== 初始状态 ====================
        sections: [],
        preferences: defaultPreferences,
        scrollState: defaultScrollState,
        navigationDots: [],
        isInitialized: false,

        // ==================== Actions ====================
        
        initialize: (sections: PageSection[]) => {
          set((state) => {
            // 如果已初始化,不重复初始化
            if (state.isInitialized) {
              return state;
            }

            // 如果有保存的顺序,应用到区块
            const { sectionOrder } = state.preferences;
            const sortedSections = sectionOrder.length > 0
              ? sortSectionsByOrder(sections, sectionOrder)
              : sections;

            return {
              sections: sortedSections,
              isInitialized: true,
            };
          }, false, 'initialize');
        },

        updateSection: (sectionId: string, updates: Partial<PageSection>) => {
          set((state) => ({
            sections: state.sections.map((section) =>
              section.id === sectionId
                ? { ...section, ...updates }
                : section
            ),
          }), false, 'updateSection');
        },

        toggleCollapse: (sectionId: string) => {
          set((state) => {
            const { collapsedSections } = state.preferences;
            const isCollapsed = collapsedSections.includes(sectionId);

            const newCollapsedSections = isCollapsed
              ? collapsedSections.filter((id) => id !== sectionId)
              : [...collapsedSections, sectionId];

            return {
              preferences: {
                ...state.preferences,
                collapsedSections: newCollapsedSections,
                lastUpdated: Date.now(),
              },
            };
          }, false, 'toggleCollapse');
        },

        setSectionOrder: (sectionOrder: string[]) => {
          set((state) => {
            // 更新区块顺序
            const sortedSections = sortSectionsByOrder(state.sections, sectionOrder);

            return {
              sections: sortedSections,
              preferences: {
                ...state.preferences,
                sectionOrder,
                lastUpdated: Date.now(),
              },
            };
          }, false, 'setSectionOrder');
        },

        setScrollSnap: (enabled: boolean) => {
          set((state) => ({
            preferences: {
              ...state.preferences,
              isScrollSnapEnabled: enabled,
              lastUpdated: Date.now(),
            },
          }), false, 'setScrollSnap');
        },

        setCurrentSection: (sectionId: string | null) => {
          set((state) => ({
            scrollState: {
              ...state.scrollState,
              previousSectionId: state.scrollState.currentSectionId,
              currentSectionId: sectionId,
            },
          }), false, 'setCurrentSection');
        },

        updateScrollState: (updates: Partial<ScrollState>) => {
          set((state) => ({
            scrollState: {
              ...state.scrollState,
              ...updates,
            },
          }), false, 'updateScrollState');
        },

        updateNavigationDots: (dots: NavigationDot[]) => {
          set({ navigationDots: dots }, false, 'updateNavigationDots');
        },

        setNavigationPosition: (position: 'left' | 'right') => {
          set((state) => ({
            preferences: {
              ...state.preferences,
              navigationPosition: position,
              lastUpdated: Date.now(),
            },
          }), false, 'setNavigationPosition');
        },

        reset: () => {
          set({
            preferences: defaultPreferences,
            scrollState: defaultScrollState,
            navigationDots: [],
          }, false, 'reset');
        },

        getSortedSections: () => {
          const state = get();
          const { sectionOrder } = state.preferences;
          
          if (sectionOrder.length === 0) {
            // 使用默认顺序(按 order 字段排序)
            return [...state.sections].sort((a, b) => a.order - b.order);
          }
          
          return sortSectionsByOrder(state.sections, sectionOrder);
        },
      }),
      {
        name: 'layout-storage', // localStorage key
        partialize: (state) => ({
          // 只持久化 preferences,不持久化 sections 和临时状态
          preferences: state.preferences,
        }),
      }
    ),
    {
      name: 'LayoutStore', // Redux DevTools 名称
      enabled: process.env.NODE_ENV === 'development',
    }
  )
);

/**
 * 工具函数: 根据自定义顺序排序区块
 */
function sortSectionsByOrder(
  sections: PageSection[],
  sectionOrder: string[]
): PageSection[] {
  const orderMap = new Map(sectionOrder.map((id, index) => [id, index]));
  
  return [...sections].sort((a, b) => {
    const orderA = orderMap.get(a.id) ?? a.order;
    const orderB = orderMap.get(b.id) ?? b.order;
    return orderA - orderB;
  });
}

/**
 * 选择器 Hooks (用于性能优化)
 */

/** 获取排序后的区块列表 */
export const useSortedSections = () =>
  useLayoutStore((state) => state.getSortedSections());

/** 获取滚动锁定开关状态 */
export const useScrollSnapEnabled = () =>
  useLayoutStore((state) => state.preferences.isScrollSnapEnabled);

/** 获取折叠的区块列表 */
export const useCollapsedSections = () =>
  useLayoutStore((state) => state.preferences.collapsedSections);

/** 获取当前激活的区块ID */
export const useCurrentSectionId = () =>
  useLayoutStore((state) => state.scrollState.currentSectionId);

/** 获取导航点数据 */
export const useNavigationDots = () =>
  useLayoutStore((state) => state.navigationDots);

/** 检查区块是否折叠 */
export const useIsSectionCollapsed = (sectionId: string) =>
  useLayoutStore((state) => state.preferences.collapsedSections.includes(sectionId));
