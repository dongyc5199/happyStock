/**
 * EMA (指数移动平均线) 技术指标计算
 *
 * EMA 给予近期价格更高的权重，对价格变化反应更灵敏
 *
 * 计算公式：
 * EMA(t) = Price(t) × K + EMA(t-1) × (1 - K)
 * 其中 K = 2 / (N + 1)
 * N 为周期数
 */

export interface EMAResult {
  time: string | number;
  value: number;
}

/**
 * 计算 EMA 指标
 *
 * @param data - 价格数据数组，每项包含 time 和 close 字段
 * @param period - EMA 周期（常用值：5, 10, 20, 30, 60, 120）
 * @returns EMA 数据数组
 */
export function calculateEMA(
  data: Array<{ time: string | number; close: number }>,
  period: number
): EMAResult[] {
  if (data.length === 0 || period <= 0) {
    return [];
  }

  // 如果数据量少于周期，返回空数组
  if (data.length < period) {
    return [];
  }

  const result: EMAResult[] = [];
  const k = 2 / (period + 1); // 平滑系数

  // 第一个 EMA 值使用 SMA (简单移动平均)
  let ema = 0;
  for (let i = 0; i < period; i++) {
    ema += data[i].close;
  }
  ema = ema / period;

  // 添加第一个 EMA 值
  result.push({
    time: data[period - 1].time,
    value: ema,
  });

  // 从第 period 个数据开始计算 EMA
  for (let i = period; i < data.length; i++) {
    ema = data[i].close * k + ema * (1 - k);
    result.push({
      time: data[i].time,
      value: ema,
    });
  }

  return result;
}

/**
 * 计算多条 EMA 线
 *
 * @param data - 价格数据数组
 * @param periods - EMA 周期数组，如 [5, 10, 20, 30]
 * @returns 每个周期对应的 EMA 数据数组
 */
export function calculateMultipleEMA(
  data: Array<{ time: string | number; close: number }>,
  periods: number[]
): Record<number, EMAResult[]> {
  const result: Record<number, EMAResult[]> = {};

  for (const period of periods) {
    result[period] = calculateEMA(data, period);
  }

  return result;
}

/**
 * EMA 预设周期配置
 */
export const EMA_PRESETS = {
  short: [5, 10, 20],           // 短期：5日、10日、20日
  medium: [30, 60],              // 中期：30日、60日
  long: [120, 250],              // 长期：120日、250日
  classic: [12, 26],             // 经典 MACD 参数
  all: [5, 10, 20, 30, 60, 120], // 全部常用周期
} as const;

/**
 * EMA 线条颜色配置
 */
export const EMA_COLORS: Record<number, string> = {
  5: '#FF6B6B',    // 红色 - 短期
  10: '#4ECDC4',   // 青色 - 短期
  20: '#FFE66D',   // 黄色 - 短期
  30: '#A8E6CF',   // 浅绿 - 中期
  60: '#FF8B94',   // 粉色 - 中期
  120: '#C7CEEA',  // 浅紫 - 长期
  250: '#FFDAB9',  // 浅橙 - 长期
};

/**
 * 获取 EMA 线条样式配置
 */
export function getEMAStyle(period: number) {
  return {
    color: EMA_COLORS[period] || '#888888',
    lineWidth: period <= 20 ? 2 : 1.5,
    lineStyle: 0, // 实线
    title: `EMA${period}`,
  };
}
