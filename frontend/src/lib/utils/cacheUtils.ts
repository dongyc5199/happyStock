/**
 * 缓存工具函数
 *
 * 用于K线数据缓存和合并
 */

import { CandlestickData } from 'lightweight-charts';

/**
 * 合并K线数据
 *
 * 将新加载的K线数据与已有数据合并，按时间去重并排序
 *
 * @param existing - 已有的K线数据
 * @param newData - 新加载的K线数据
 * @returns 合并后的K线数据（按时间升序）
 *
 * @example
 * ```ts
 * const existing = [
 *   { time: 1000, open: 100, high: 105, low: 95, close: 102 },
 *   { time: 2000, open: 102, high: 107, low: 100, close: 105 },
 * ];
 * const newData = [
 *   { time: 2000, open: 102, high: 108, low: 100, close: 106 }, // 更新
 *   { time: 3000, open: 106, high: 110, low: 104, close: 108 }, // 新增
 * ];
 * const merged = mergeKlineData(existing, newData);
 * // merged 包含3条数据，time=2000的数据被更新
 * ```
 */
export function mergeKlineData(
  existing: CandlestickData[],
  newData: CandlestickData[]
): CandlestickData[] {
  // 使用 Map 来去重，key 为时间戳
  const merged = new Map<number, CandlestickData>();

  // 先添加已有数据
  existing.forEach(item => {
    const time = normalizeTime(item.time);
    merged.set(time, item);
  });

  // 新数据覆盖（处理数据更新的情况）
  newData.forEach(item => {
    const time = normalizeTime(item.time);
    merged.set(time, item);
  });

  // 按时间排序（升序）
  return Array.from(merged.values()).sort((a, b) => {
    const timeA = normalizeTime(a.time);
    const timeB = normalizeTime(b.time);
    return timeA - timeB;
  });
}

/**
 * 标准化时间值
 *
 * lightweight-charts 的 time 可以是 number（Unix时间戳秒） 或 string（YYYY-MM-DD）
 *
 * @param time - 时间值
 * @returns Unix 时间戳（秒）
 */
function normalizeTime(time: string | number): number {
  if (typeof time === 'number') {
    return time;
  }
  return Math.floor(Date.parse(time) / 1000);
}

/**
 * 生成缓存键
 *
 * @param symbol - 股票代码
 * @param interval - 时间周期
 * @param startTime - 开始时间（秒）
 * @param endTime - 结束时间（秒）
 * @returns 缓存键字符串
 */
export function generateCacheKey(
  symbol: string,
  interval: string,
  startTime: number,
  endTime: number
): string {
  return `kline:${symbol}:${interval}:${startTime}:${endTime}`;
}

/**
 * 从缓存键解析参数
 *
 * @param cacheKey - 缓存键
 * @returns 解析后的参数对象，解析失败返回 null
 */
export function parseCacheKey(cacheKey: string): {
  symbol: string;
  interval: string;
  startTime: number;
  endTime: number;
} | null {
  const parts = cacheKey.split(':');
  if (parts.length !== 5 || parts[0] !== 'kline') {
    return null;
  }

  return {
    symbol: parts[1],
    interval: parts[2],
    startTime: parseInt(parts[3], 10),
    endTime: parseInt(parts[4], 10),
  };
}

/**
 * LRU 缓存管理器
 *
 * 实现最近最少使用（Least Recently Used）缓存淘汰策略
 */
export class LRUCache<K, V> {
  private cache: Map<K, V>;
  private maxSize: number;

  constructor(maxSize: number = 10) {
    this.cache = new Map();
    this.maxSize = maxSize;
  }

  /**
   * 获取缓存值
   *
   * @param key - 缓存键
   * @returns 缓存值，不存在返回 undefined
   */
  get(key: K): V | undefined {
    if (!this.cache.has(key)) {
      return undefined;
    }

    // 获取后移到最后（最近使用）
    const value = this.cache.get(key)!;
    this.cache.delete(key);
    this.cache.set(key, value);

    return value;
  }

  /**
   * 设置缓存值
   *
   * @param key - 缓存键
   * @param value - 缓存值
   */
  set(key: K, value: V): void {
    // 如果已存在，先删除
    if (this.cache.has(key)) {
      this.cache.delete(key);
    }

    // 如果达到最大容量，删除最旧的（第一个）
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }

    // 添加到最后
    this.cache.set(key, value);
  }

  /**
   * 检查缓存是否存在
   *
   * @param key - 缓存键
   * @returns 是否存在
   */
  has(key: K): boolean {
    return this.cache.has(key);
  }

  /**
   * 删除缓存
   *
   * @param key - 缓存键
   */
  delete(key: K): void {
    this.cache.delete(key);
  }

  /**
   * 清空缓存
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * 获取缓存大小
   */
  size(): number {
    return this.cache.size;
  }
}

/**
 * 计算两个时间范围的重叠部分
 *
 * @param range1 - 范围1
 * @param range2 - 范围2
 * @returns 重叠部分，无重叠返回 null
 */
export function getOverlap(
  range1: { start: number; end: number },
  range2: { start: number; end: number }
): { start: number; end: number } | null {
  const start = Math.max(range1.start, range2.start);
  const end = Math.min(range1.end, range2.end);

  if (start >= end) {
    return null; // 无重叠
  }

  return { start, end };
}

/**
 * 检查范围是否完全包含另一个范围
 *
 * @param container - 容器范围
 * @param contained - 被包含的范围
 * @returns 是否完全包含
 */
export function containsRange(
  container: { start: number; end: number },
  contained: { start: number; end: number }
): boolean {
  return container.start <= contained.start && container.end >= contained.end;
}
