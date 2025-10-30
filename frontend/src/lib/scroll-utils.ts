/**
 * Scroll Utilities - 滚动计算和工具函数
 * 
 * 提供滚动相关的计算和辅助函数:
 * - 滚动目标计算
 * - 缓慢滚动检测
 * - 区块位置计算
 * 
 * 对应需求: US2 (FR-007, FR-008)
 */

/**
 * 计算滚动目标区块
 * 
 * @param currentScrollY - 当前滚动位置
 * @param direction - 滚动方向 ('up' | 'down')
 * @returns 目标区块的元素
 */
export function calculateScrollTarget(
  currentScrollY: number,
  direction: 'up' | 'down'
): HTMLElement | null {
  const sections = Array.from(
    document.querySelectorAll('[data-section-id]')
  ) as HTMLElement[];

  if (sections.length === 0) return null;

  // 找到当前最接近的区块
  let closestSection: HTMLElement | null = null;
  let minDistance = Infinity;

  sections.forEach((section) => {
    const rect = section.getBoundingClientRect();
    const distance = Math.abs(rect.top);

    if (distance < minDistance) {
      minDistance = distance;
      closestSection = section;
    }
  });

  if (!closestSection) return sections[0];

  const currentIndex = sections.indexOf(closestSection);

  // 根据方向返回目标区块
  if (direction === 'down') {
    return sections[currentIndex + 1] || closestSection;
  } else {
    return sections[currentIndex - 1] || closestSection;
  }
}

/**
 * 检测是否为缓慢滚动
 * 
 * @param deltaY - 滚动增量
 * @param threshold - 阈值(默认 50)
 * @returns 是否为缓慢滚动
 */
export function isSlowScroll(deltaY: number, threshold = 50): boolean {
  return Math.abs(deltaY) < threshold;
}

/**
 * 获取区块的滚动位置
 * 
 * @param sectionId - 区块ID
 * @returns 滚动位置(像素),如果未找到返回 null
 */
export function getSectionScrollPosition(sectionId: string): number | null {
  const section = document.querySelector(
    `[data-section-id="${sectionId}"]`
  ) as HTMLElement;

  if (!section) return null;

  return section.offsetTop;
}

/**
 * 获取当前可见的区块
 * 
 * @param threshold - 可见度阈值 (0-1, 默认 0.5)
 * @returns 当前可见的区块ID
 */
export function getCurrentVisibleSection(threshold = 0.5): string | null {
  const sections = Array.from(
    document.querySelectorAll('[data-section-id]')
  ) as HTMLElement[];

  let mostVisibleSection: HTMLElement | null = null;
  let maxVisibility = 0;

  sections.forEach((section: HTMLElement) => {
    const rect = section.getBoundingClientRect();
    const viewportHeight = window.innerHeight;

    // 计算可见比例
    const visibleHeight = Math.min(rect.bottom, viewportHeight) - Math.max(rect.top, 0);
    const sectionHeight = rect.height;
    const visibility = visibleHeight / sectionHeight;

    if (visibility > maxVisibility && visibility >= threshold) {
      maxVisibility = visibility;
      mostVisibleSection = section;
    }
  });

  if (mostVisibleSection) {
    const sectionId = (mostVisibleSection as HTMLElement).getAttribute('data-section-id');
    return sectionId;
  }
  return null;
}

/**
 * 平滑滚动到指定区块
 * 
 * @param sectionId - 区块ID
 * @param options - 滚动选项
 */
export function scrollToSection(
  sectionId: string,
  options: ScrollIntoViewOptions = {}
): void {
  const section = document.querySelector(
    `[data-section-id="${sectionId}"]`
  ) as HTMLElement;

  if (!section) {
    console.warn(`Section with id "${sectionId}" not found`);
    return;
  }

  section.scrollIntoView({
    behavior: 'smooth',
    block: 'start',
    ...options,
  });
}

/**
 * 获取所有区块的ID列表
 * 
 * @returns 区块ID数组
 */
export function getAllSectionIds(): string[] {
  const sections = document.querySelectorAll('[data-section-id]');
  return Array.from(sections)
    .map((section) => section.getAttribute('data-section-id'))
    .filter((id): id is string => id !== null);
}

/**
 * 获取区块索引
 * 
 * @param sectionId - 区块ID
 * @returns 区块索引,如果未找到返回 -1
 */
export function getSectionIndex(sectionId: string): number {
  const sectionIds = getAllSectionIds();
  return sectionIds.indexOf(sectionId);
}

/**
 * 获取下一个区块ID
 * 
 * @param currentSectionId - 当前区块ID
 * @returns 下一个区块ID,如果是最后一个则返回 null
 */
export function getNextSectionId(currentSectionId: string): string | null {
  const sectionIds = getAllSectionIds();
  const currentIndex = sectionIds.indexOf(currentSectionId);

  if (currentIndex === -1 || currentIndex === sectionIds.length - 1) {
    return null;
  }

  return sectionIds[currentIndex + 1];
}

/**
 * 获取上一个区块ID
 * 
 * @param currentSectionId - 当前区块ID
 * @returns 上一个区块ID,如果是第一个则返回 null
 */
export function getPreviousSectionId(currentSectionId: string): string | null {
  const sectionIds = getAllSectionIds();
  const currentIndex = sectionIds.indexOf(currentSectionId);

  if (currentIndex <= 0) {
    return null;
  }

  return sectionIds[currentIndex - 1];
}

/**
 * 检查区块是否在视口内
 * 
 * @param sectionId - 区块ID
 * @returns 是否在视口内
 */
export function isSectionInViewport(sectionId: string): boolean {
  const section = document.querySelector(
    `[data-section-id="${sectionId}"]`
  ) as HTMLElement;

  if (!section) return false;

  const rect = section.getBoundingClientRect();
  const viewportHeight = window.innerHeight;

  return rect.top < viewportHeight && rect.bottom > 0;
}

/**
 * 节流函数
 * 
 * @param func - 要节流的函数
 * @param delay - 延迟时间(毫秒)
 * @returns 节流后的函数
 */
export function throttle<T extends (...args: unknown[]) => void>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let lastCall = 0;

  return function (...args: Parameters<T>) {
    const now = Date.now();

    if (now - lastCall >= delay) {
      lastCall = now;
      func(...args);
    }
  };
}

/**
 * 防抖函数
 * 
 * @param func - 要防抖的函数
 * @param delay - 延迟时间(毫秒)
 * @returns 防抖后的函数
 */
export function debounce<T extends (...args: unknown[]) => void>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout;

  return function (...args: Parameters<T>) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
}
