/**
 * 时间工具函数
 *
 * 用于K线倒计时计算和格式化
 */

/**
 * 时间周期类型
 */
export type Timeframe = '5m' | '15m' | '30m' | '60m' | '120m' | '1d' | '1w' | '1M';

/**
 * 各时间周期对应的秒数
 *
 * 注意：
 * - 分钟级按实际分钟数计算
 * - 日K按交易日的交易时间计算（简化为24小时）
 * - 周K和月K按自然周期计算
 */
export const INTERVAL_SECONDS: Record<Timeframe, number> = {
  '5m': 5 * 60,              // 300秒
  '15m': 15 * 60,            // 900秒
  '30m': 30 * 60,            // 1800秒
  '60m': 60 * 60,            // 3600秒 (1小时)
  '120m': 120 * 60,          // 7200秒 (2小时)
  '1d': 24 * 60 * 60,        // 86400秒 (24小时)
  '1w': 7 * 24 * 60 * 60,    // 604800秒 (7天)
  '1M': 30 * 24 * 60 * 60,   // 2592000秒 (30天，近似)
};

/**
 * 计算当前K线的剩余时间
 *
 * @param interval - 时间周期
 * @param lastBarTime - 最后一根K线的时间戳（秒）
 * @returns 剩余秒数
 *
 * @example
 * ```ts
 * // 假设当前时间是 10:07:30，最后一根5分钟K线时间是 10:05:00
 * const remaining = calculateRemainingTime('5m', 1640000000);
 * // remaining = 150 (还剩2分30秒)
 * ```
 */
export function calculateRemainingTime(
  interval: Timeframe,
  lastBarTime: number
): number {
  const now = Math.floor(Date.now() / 1000); // 当前时间戳（秒）
  const intervalSec = INTERVAL_SECONDS[interval];

  // 计算从 lastBarTime 开始已经过去的时间
  const elapsed = now - lastBarTime;

  // 计算在当前周期内已经过去的时间（取模）
  const elapsedInPeriod = elapsed % intervalSec;

  // 剩余时间 = 周期总时间 - 已过去时间
  const remaining = intervalSec - elapsedInPeriod;

  return Math.max(0, remaining);
}

/**
 * 格式化倒计时显示
 *
 * @param seconds - 剩余秒数
 * @param interval - 时间周期
 * @returns 格式化的倒计时字符串
 *
 * @example
 * ```ts
 * formatCountdown(150, '5m')   // "02:30"
 * formatCountdown(3665, '1d')  // "01:01:05"
 * ```
 */
export function formatCountdown(seconds: number, interval: Timeframe): string {
  const hours = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  const pad = (num: number): string => num.toString().padStart(2, '0');

  // 日K、周K、月K 显示 HH:MM:SS 格式
  if (interval === '1d' || interval === '1w' || interval === '1M') {
    return `${pad(hours)}:${pad(mins)}:${pad(secs)}`;
  }

  // 分钟级显示 MM:SS 格式
  return `${pad(mins)}:${pad(secs)}`;
}

/**
 * 获取时间周期的显示名称
 *
 * @param interval - 时间周期
 * @returns 中文显示名称
 */
export function getIntervalDisplayName(interval: Timeframe): string {
  const names: Record<Timeframe, string> = {
    '5m': '5分钟',
    '15m': '15分钟',
    '30m': '30分钟',
    '60m': '60分钟',
    '120m': '120分钟',
    '1d': '日K',
    '1w': '周K',
    '1M': '月K',
  };
  return names[interval];
}

/**
 * 判断是否为分钟级时间周期
 *
 * @param interval - 时间周期
 * @returns 是否为分钟级
 */
export function isMinuteInterval(interval: Timeframe): boolean {
  return ['5m', '15m', '30m', '60m', '120m'].includes(interval);
}

/**
 * 计算下一根K线的开始时间
 *
 * @param interval - 时间周期
 * @param currentBarTime - 当前K线的时间戳（秒）
 * @returns 下一根K线的时间戳（秒）
 */
export function getNextBarTime(interval: Timeframe, currentBarTime: number): number {
  return currentBarTime + INTERVAL_SECONDS[interval];
}
