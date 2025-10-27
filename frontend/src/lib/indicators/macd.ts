/**
 * MACD (指数平滑异同移动平均线) 技术指标计算
 *
 * MACD 是最常用的趋势跟踪指标之一，由 Gerald Appel 在 1970 年代发明
 *
 * 计算公式：
 * 1. DIFF (DIF) = EMA(12) - EMA(26)  // 快线
 * 2. DEA (DEM) = EMA(DIFF, 9)        // 慢线（信号线）
 * 3. MACD = (DIFF - DEA) × 2         // 柱状图（有的不乘2）
 *
 * 应用规则：
 * - DIFF 上穿 DEA：金叉，买入信号
 * - DIFF 下穿 DEA：死叉，卖出信号
 * - MACD 柱状图：正值（红色）表示多头，负值（绿色）表示空头
 * - 柱状图变长：趋势增强，柱状图变短：趋势减弱
 */

import { calculateEMA } from './ema';

export interface MACDResult {
  time: string | number;
  diff: number;      // DIFF 线（快线）
  dea: number;       // DEA 线（慢线/信号线）
  macd: number;      // MACD 柱状图
}

export interface MACDCrossSignal {
  time: string | number;
  type: 'golden' | 'death';  // golden = 金叉, death = 死叉
  diffValue: number;
  deaValue: number;
}

/**
 * 计算 MACD 指标
 *
 * @param data - 价格数据数组，每项包含 time 和 close 字段
 * @param fastPeriod - 快速 EMA 周期，默认 12
 * @param slowPeriod - 慢速 EMA 周期，默认 26
 * @param signalPeriod - 信号线（DEA）周期，默认 9
 * @returns MACD 数据数组
 */
export function calculateMACD(
  data: Array<{ time: string | number; close: number }>,
  fastPeriod: number = 12,
  slowPeriod: number = 26,
  signalPeriod: number = 9
): MACDResult[] {
  if (data.length === 0) {
    return [];
  }

  // 需要至少 slowPeriod 个数据点
  if (data.length < slowPeriod) {
    return [];
  }

  // 1. 计算快速 EMA 和慢速 EMA
  const fastEMA = calculateEMA(data, fastPeriod);
  const slowEMA = calculateEMA(data, slowPeriod);

  // 2. 计算 DIFF (快线 - 慢线)
  // 由于 slowEMA 起始更晚，以 slowEMA 为准
  const diffData: Array<{ time: string | number; close: number }> = [];

  // 找到两个 EMA 的公共时间范围
  const slowEMAMap = new Map(slowEMA.map(item => [item.time, item.value]));
  const fastEMAMap = new Map(fastEMA.map(item => [item.time, item.value]));

  for (const slowItem of slowEMA) {
    const fastValue = fastEMAMap.get(slowItem.time);
    if (fastValue !== undefined) {
      const diffValue = fastValue - slowItem.value;
      diffData.push({
        time: slowItem.time,
        close: diffValue,  // 将 DIFF 作为 close 用于计算 DEA
      });
    }
  }

  if (diffData.length === 0) {
    return [];
  }

  // 3. 计算 DEA (DIFF 的 EMA)
  const deaData = calculateEMA(diffData, signalPeriod);

  if (deaData.length === 0) {
    return [];
  }

  // 4. 构建最终结果（从 DEA 有值的时间开始）
  const result: MACDResult[] = [];
  const deaMap = new Map(deaData.map(item => [item.time, item.value]));
  const diffMap = new Map(diffData.map(item => [item.time, item.close]));

  for (const deaItem of deaData) {
    const diffValue = diffMap.get(deaItem.time);
    if (diffValue !== undefined) {
      const deaValue = deaItem.value;
      const macdValue = (diffValue - deaValue) * 2;  // MACD 柱状图

      result.push({
        time: deaItem.time,
        diff: diffValue,
        dea: deaValue,
        macd: macdValue,
      });
    }
  }

  return result;
}

/**
 * 检测 MACD 金叉和死叉信号
 *
 * @param macdData - MACD 数据数组
 * @returns 交叉信号数组
 */
export function detectMACDCross(macdData: MACDResult[]): MACDCrossSignal[] {
  if (macdData.length < 2) {
    return [];
  }

  const signals: MACDCrossSignal[] = [];

  for (let i = 1; i < macdData.length; i++) {
    const prev = macdData[i - 1];
    const curr = macdData[i];

    // 金叉：DIFF 从下方穿越 DEA
    if (prev.diff <= prev.dea && curr.diff > curr.dea) {
      signals.push({
        time: curr.time,
        type: 'golden',
        diffValue: curr.diff,
        deaValue: curr.dea,
      });
    }
    // 死叉：DIFF 从上方穿越 DEA
    else if (prev.diff >= prev.dea && curr.diff < curr.dea) {
      signals.push({
        time: curr.time,
        type: 'death',
        diffValue: curr.diff,
        deaValue: curr.dea,
      });
    }
  }

  return signals;
}

/**
 * MACD 参数预设
 */
export const MACD_PRESETS = {
  classic: { fast: 12, slow: 26, signal: 9 },    // 经典参数
  fast: { fast: 6, slow: 13, signal: 5 },        // 快速参数（更敏感）
  slow: { fast: 19, slow: 39, signal: 9 },       // 慢速参数（更平滑）
  custom: { fast: 12, slow: 26, signal: 9 },     // 自定义（默认同经典）
} as const;

/**
 * MACD 颜色配置
 */
export const MACD_COLORS = {
  diff: '#2962FF',      // DIFF 线：蓝色
  dea: '#FF6D00',       // DEA 线：橙色
  macdPositive: '#26a69a',  // MACD 柱正值：绿色（涨）
  macdNegative: '#ef5350',  // MACD 柱负值：红色（跌）
  zeroLine: '#787B86',      // 零轴线：灰色
} as const;

/**
 * 获取 MACD 样式配置
 */
export function getMACDStyle() {
  return {
    diff: {
      color: MACD_COLORS.diff,
      lineWidth: 2,
      title: 'DIFF',
    },
    dea: {
      color: MACD_COLORS.dea,
      lineWidth: 2,
      title: 'DEA',
    },
    macd: {
      positiveColor: MACD_COLORS.macdPositive,
      negativeColor: MACD_COLORS.macdNegative,
      title: 'MACD',
    },
  };
}

/**
 * 格式化 MACD 值用于显示（保留4位小数）
 */
export function formatMACDValue(value: number): string {
  return value.toFixed(4);
}
