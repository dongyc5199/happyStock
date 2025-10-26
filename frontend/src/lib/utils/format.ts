/**
 * 格式化工具函数
 */

/**
 * 格式化金额
 * @param value 金额字符串或数字
 * @param decimals 小数位数，默认2位
 */
export function formatCurrency(value: string | number, decimals: number = 2): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '0.00';

  return num.toLocaleString('zh-CN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/**
 * 格式化百分比
 * @param value 百分比数值
 * @param decimals 小数位数，默认2位
 */
export function formatPercent(value: string | number, decimals: number = 2): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '0.00%';

  const formatted = num.toFixed(decimals);
  return `${formatted}%`;
}

/**
 * 格式化数字（添加千分位分隔符）
 * @param value 数字
 * @param decimals 小数位数
 */
export function formatNumber(value: string | number, decimals: number = 0): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '0';

  return num.toLocaleString('zh-CN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/**
 * 格式化日期时间
 * @param dateStr 日期字符串
 * @param format 格式类型
 */
export function formatDateTime(
  dateStr: string,
  format: 'full' | 'date' | 'time' | 'short' = 'full'
): string {
  const date = new Date(dateStr);

  if (isNaN(date.getTime())) return '';

  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');

  switch (format) {
    case 'date':
      return `${year}-${month}-${day}`;
    case 'time':
      return `${hours}:${minutes}:${seconds}`;
    case 'short':
      return `${month}-${day} ${hours}:${minutes}`;
    case 'full':
    default:
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  }
}

/**
 * 格式化大数字（K, M, B）
 * @param value 数字
 */
export function formatLargeNumber(value: string | number): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '0';

  if (num >= 1_000_000_000) {
    return `${(num / 1_000_000_000).toFixed(2)}B`;
  } else if (num >= 1_000_000) {
    return `${(num / 1_000_000).toFixed(2)}M`;
  } else if (num >= 1_000) {
    return `${(num / 1_000).toFixed(2)}K`;
  }

  return num.toFixed(2);
}

/**
 * 根据盈亏返回颜色类名
 * @param value 盈亏值
 */
export function getProfitColor(value: string | number): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num) || num === 0) return 'text-gray-400';
  return num > 0 ? 'text-green-500' : 'text-red-500';
}

/**
 * 根据盈亏返回带符号的格式化字符串
 * @param value 盈亏值
 * @param decimals 小数位数
 */
export function formatProfitWithSign(value: string | number, decimals: number = 2): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '0.00';

  const formatted = Math.abs(num).toFixed(decimals);
  if (num > 0) return `+${formatted}`;
  if (num < 0) return `-${formatted}`;
  return formatted;
}
