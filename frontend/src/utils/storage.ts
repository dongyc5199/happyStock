/**
 * Storage Utilities - 布局偏好持久化工具
 * 
 * 提供 localStorage 操作的封装:
 * - 布局偏好的保存和加载
 * - 序列化/反序列化处理
 * - 错误处理和降级
 * 
 * 对应需求: FR-015, FR-018, FR-020
 */

import type { LayoutPreferences } from '@/types/layout';

/**
 * LocalStorage 键名常量
 */
export const STORAGE_KEYS = {
  LAYOUT_PREFERENCES: 'happystock:layout:preferences',
  LAYOUT_VERSION: 'happystock:layout:version',
} as const;

/**
 * 当前存储版本 (用于数据迁移)
 */
const STORAGE_VERSION = '1.0.0';

/**
 * 存储错误类型
 */
export class StorageError extends Error {
  constructor(message: string, public readonly cause?: unknown) {
    super(message);
    this.name = 'StorageError';
  }
}

/**
 * 检查 localStorage 是否可用
 */
export function isStorageAvailable(): boolean {
  try {
    const testKey = '__storage_test__';
    localStorage.setItem(testKey, 'test');
    localStorage.removeItem(testKey);
    return true;
  } catch {
    return false;
  }
}

/**
 * 保存布局偏好到 localStorage
 * 
 * @param preferences - 布局偏好对象
 * @throws {StorageError} 保存失败时抛出错误
 */
export function saveLayoutPreferences(preferences: LayoutPreferences): void {
  if (!isStorageAvailable()) {
    console.warn('[Storage] localStorage 不可用,无法保存偏好设置');
    return;
  }

  try {
    // 添加版本信息
    const data = {
      version: STORAGE_VERSION,
      preferences: {
        ...preferences,
        lastUpdated: Date.now(),
      },
    };

    const serialized = JSON.stringify(data);
    localStorage.setItem(STORAGE_KEYS.LAYOUT_PREFERENCES, serialized);
    
    if (process.env.NODE_ENV === 'development') {
      console.log('[Storage] 布局偏好已保存:', preferences);
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : '未知错误';
    throw new StorageError(`保存布局偏好失败: ${message}`, error);
  }
}

/**
 * 从 localStorage 加载布局偏好
 * 
 * @param defaultPreferences - 默认偏好设置(加载失败时使用)
 * @returns 布局偏好对象
 */
export function loadLayoutPreferences(
  defaultPreferences: LayoutPreferences
): LayoutPreferences {
  if (!isStorageAvailable()) {
    console.warn('[Storage] localStorage 不可用,使用默认偏好设置');
    return defaultPreferences;
  }

  try {
    const stored = localStorage.getItem(STORAGE_KEYS.LAYOUT_PREFERENCES);
    
    if (!stored) {
      if (process.env.NODE_ENV === 'development') {
        console.log('[Storage] 未找到保存的偏好设置,使用默认值');
      }
      return defaultPreferences;
    }

    const data = JSON.parse(stored);
    
    // 验证数据结构
    if (!data || typeof data !== 'object' || !data.preferences) {
      console.warn('[Storage] 存储的数据格式无效,使用默认值');
      return defaultPreferences;
    }

    // 版本检查 (可用于未来数据迁移)
    if (data.version !== STORAGE_VERSION) {
      console.warn(
        `[Storage] 存储版本不匹配 (存储: ${data.version}, 当前: ${STORAGE_VERSION})`
      );
      // 这里可以添加版本迁移逻辑
    }

    const preferences = data.preferences as LayoutPreferences;
    
    // 验证必需字段
    if (
      typeof preferences.isScrollSnapEnabled !== 'boolean' ||
      !Array.isArray(preferences.collapsedSections) ||
      !Array.isArray(preferences.sectionOrder)
    ) {
      console.warn('[Storage] 偏好设置数据不完整,使用默认值');
      return defaultPreferences;
    }

    if (process.env.NODE_ENV === 'development') {
      console.log('[Storage] 布局偏好已加载:', preferences);
    }

    return preferences;
  } catch (error) {
    const message = error instanceof Error ? error.message : '未知错误';
    console.error(`[Storage] 加载布局偏好失败: ${message}`, error);
    return defaultPreferences;
  }
}

/**
 * 清除布局偏好 (重置为默认)
 */
export function clearLayoutPreferences(): void {
  if (!isStorageAvailable()) {
    return;
  }

  try {
    localStorage.removeItem(STORAGE_KEYS.LAYOUT_PREFERENCES);
    
    if (process.env.NODE_ENV === 'development') {
      console.log('[Storage] 布局偏好已清除');
    }
  } catch (error) {
    console.error('[Storage] 清除布局偏好失败:', error);
  }
}

/**
 * 获取存储使用情况 (仅开发环境)
 */
export function getStorageInfo(): {
  isAvailable: boolean;
  hasPreferences: boolean;
  storageSize?: number;
} {
  const isAvailable = isStorageAvailable();
  
  if (!isAvailable) {
    return { isAvailable: false, hasPreferences: false };
  }

  try {
    const stored = localStorage.getItem(STORAGE_KEYS.LAYOUT_PREFERENCES);
    const hasPreferences = stored !== null;
    const storageSize = stored ? new Blob([stored]).size : 0;

    return {
      isAvailable,
      hasPreferences,
      storageSize,
    };
  } catch {
    return { isAvailable: true, hasPreferences: false };
  }
}

/**
 * 导出布局偏好为 JSON (用于备份)
 */
export function exportPreferences(): string | null {
  if (!isStorageAvailable()) {
    return null;
  }

  try {
    const stored = localStorage.getItem(STORAGE_KEYS.LAYOUT_PREFERENCES);
    if (!stored) {
      return null;
    }

    // 格式化 JSON 以便阅读
    const data = JSON.parse(stored);
    return JSON.stringify(data, null, 2);
  } catch (error) {
    console.error('[Storage] 导出偏好设置失败:', error);
    return null;
  }
}

/**
 * 从 JSON 导入布局偏好 (用于恢复)
 */
export function importPreferences(jsonString: string): boolean {
  if (!isStorageAvailable()) {
    console.warn('[Storage] localStorage 不可用');
    return false;
  }

  try {
    // 验证 JSON 格式
    const data = JSON.parse(jsonString);
    
    if (!data || !data.preferences) {
      throw new Error('无效的数据格式');
    }

    // 保存
    localStorage.setItem(STORAGE_KEYS.LAYOUT_PREFERENCES, JSON.stringify(data));
    
    if (process.env.NODE_ENV === 'development') {
      console.log('[Storage] 偏好设置已导入');
    }

    return true;
  } catch (error) {
    const message = error instanceof Error ? error.message : '未知错误';
    console.error(`[Storage] 导入偏好设置失败: ${message}`, error);
    return false;
  }
}

/**
 * 数据迁移函数 (预留用于未来版本升级)
 */
export function migrateStorageVersion(
  fromVersion: string,
  toVersion: string
): boolean {
  if (fromVersion === toVersion) {
    return true;
  }

  // 这里可以添加版本迁移逻辑
  console.log(`[Storage] 数据迁移: ${fromVersion} -> ${toVersion}`);

  // 示例:
  // if (fromVersion === '0.9.0' && toVersion === '1.0.0') {
  //   // 执行 0.9.0 -> 1.0.0 的数据迁移
  //   return true;
  // }

  return false;
}
