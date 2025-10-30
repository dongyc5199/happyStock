/**
 * Formatter utilities for displaying prices, percentages, and numbers
 */

/**
 * Format price in CNY (e.g., 123456.78 → ¥123,456.78)
 */
export function formatPrice(value: number, decimals: number = 2): string {
  return `¥${value.toLocaleString('zh-CN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })}`;
}

/**
 * Format percentage (e.g., 5.23 → +5.23%)
 */
export function formatPercentage(value: number, decimals: number = 2): string {
  const sign = value > 0 ? '+' : '';
  return `${sign}${value.toFixed(decimals)}%`;
}

/**
 * Format large numbers with K/M/B suffixes
 * @example
 * formatNumber(1500) → "1.5K"
 * formatNumber(2500000) → "2.5M"
 * formatNumber(3500000000) → "3.5B"
 */
export function formatNumber(value: number): string {
  if (value >= 1_000_000_000) {
    return `${(value / 1_000_000_000).toFixed(1)}B`;
  }
  if (value >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(1)}M`;
  }
  if (value >= 1_000) {
    return `${(value / 1_000).toFixed(1)}K`;
  }
  return value.toString();
}

/**
 * Format volume/turnover with Chinese units (万/亿)
 * @example
 * formatVolumeZh(15000) → "1.5万"
 * formatVolumeZh(250000000) → "2.5亿"
 */
export function formatVolumeZh(value: number): string {
  if (value >= 100_000_000) {
    return `${(value / 100_000_000).toFixed(2)}亿`;
  }
  if (value >= 10_000) {
    return `${(value / 10_000).toFixed(2)}万`;
  }
  return value.toString();
}
