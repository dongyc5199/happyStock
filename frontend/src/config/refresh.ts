/**
 * 自动刷新配置
 * 
 * 基于真实A股市场特征设计:
 * - A股交易时段: 09:30-11:30, 13:00-15:00
 * - Level-1 行情更新: 每3秒
 * - 主流券商APP: 3-5秒刷新
 * - 交易所官方快照: 3秒
 */

/**
 * 刷新间隔配置 (毫秒)
 */
export const REFRESH_INTERVALS = {
  /**
   * 股票列表页刷新间隔
   * 模拟 Level-1 行情更新频率
   */
  MARKET_PAGE: 5000, // 5秒
  
  /**
   * 指数看板刷新间隔
   * 指数更新频率与个股相同
   */
  INDICES_PAGE: 5000, // 5秒
  
  /**
   * 股票详情页刷新间隔
   * 详情页需要更实时的数据
   */
  STOCK_DETAIL: 3000, // 3秒
  
  /**
   * 分时图刷新间隔
   * 每分钟新增一个数据点
   */
  INTRADAY_CHART: 30000, // 30秒
  
  /**
   * K线图刷新间隔
   * 历史数据，无需频繁刷新
   */
  KLINE_CHART: 0, // 不自动刷新
  
  /**
   * 板块页面刷新间隔
   */
  SECTOR_PAGE: 5000, // 5秒
} as const;

/**
 * 用户活动检测配置
 */
export const ACTIVITY_CONFIG = {
  /**
   * 检测间隔 (毫秒)
   * 每30秒检查一次用户活动状态
   */
  CHECK_INTERVAL: 30000, // 30秒
  
  /**
   * 不活跃阈值 (毫秒)
   * 5分钟无操作视为不活跃
   */
  INACTIVE_THRESHOLD: 5 * 60 * 1000, // 5分钟
} as const;

/**
 * 交易时段配置 (可选功能)
 * 用于在交易时段外降低刷新频率或停止刷新
 */
export const TRADING_HOURS = {
  /**
   * 上午交易时段
   */
  MORNING: {
    start: { hour: 9, minute: 30 },
    end: { hour: 11, minute: 30 },
  },
  
  /**
   * 下午交易时段
   */
  AFTERNOON: {
    start: { hour: 13, minute: 0 },
    end: { hour: 15, minute: 0 },
  },
  
  /**
   * 集合竞价时段
   */
  AUCTION: {
    morning: { hour: 9, minute: 15 }, // 09:15-09:25
    closing: { hour: 14, minute: 57 }, // 14:57-15:00
  },
} as const;

/**
 * 判断当前是否在交易时段
 * @returns true 如果在交易时段内
 */
export function isInTradingHours(): boolean {
  const now = new Date();
  const hour = now.getHours();
  const minute = now.getMinutes();
  const currentTime = hour * 60 + minute;
  
  // 上午交易时段: 09:30-11:30
  const morningStart = TRADING_HOURS.MORNING.start.hour * 60 + TRADING_HOURS.MORNING.start.minute;
  const morningEnd = TRADING_HOURS.MORNING.end.hour * 60 + TRADING_HOURS.MORNING.end.minute;
  
  // 下午交易时段: 13:00-15:00
  const afternoonStart = TRADING_HOURS.AFTERNOON.start.hour * 60 + TRADING_HOURS.AFTERNOON.start.minute;
  const afternoonEnd = TRADING_HOURS.AFTERNOON.end.hour * 60 + TRADING_HOURS.AFTERNOON.end.minute;
  
  return (currentTime >= morningStart && currentTime <= morningEnd) ||
         (currentTime >= afternoonStart && currentTime <= afternoonEnd);
}

/**
 * 判断是否为交易日 (周一到周五，不含节假日)
 * 注意: 此函数不处理节假日，仅判断周末
 * @returns true 如果是工作日
 */
export function isTradingDay(): boolean {
  const day = new Date().getDay();
  return day >= 1 && day <= 5; // 周一到周五
}

/**
 * 获取适应性刷新间隔
 * 在交易时段外可以降低刷新频率以节省资源
 * 
 * @param baseInterval 基础刷新间隔
 * @param offHoursMultiplier 非交易时段倍率 (默认3倍)
 * @returns 实际刷新间隔
 */
export function getAdaptiveInterval(
  baseInterval: number,
  offHoursMultiplier: number = 3
): number {
  if (!isTradingDay() || !isInTradingHours()) {
    return baseInterval * offHoursMultiplier;
  }
  return baseInterval;
}

/**
 * 刷新策略说明
 */
export const REFRESH_STRATEGY = {
  description: '基于真实A股市场特征的刷新策略',
  features: [
    'Level-1 行情模拟: 3-5秒更新',
    '用户活动检测: 5分钟不活跃自动暂停',
    '交易时段适配: 盘后可降低频率',
    '资源优化: 避免不必要的API请求',
  ],
  references: [
    'A股Level-1行情: 3秒快照',
    '主流券商APP: 3-5秒刷新',
    '分时图更新: 1分钟粒度',
  ],
} as const;
