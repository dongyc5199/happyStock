'use client';

import { useMemo } from 'react';
import { IChartApi } from 'lightweight-charts';
import { useCountdown } from '@/hooks/useCountdown';
import { Timeframe } from '@/lib/utils/timeUtils';

export interface KlineCountdownProps {
  /** 图表实例 */
  chart: IChartApi | null;
  /** 时间周期 */
  interval: Timeframe;
  /** 最后一根K线的时间戳（秒） */
  lastBarTime: number;
  /** 倒计时归零回调 */
  onZero?: () => void;
  /** 是否显示 */
  show?: boolean;
  /** 自定义样式类名 */
  className?: string;
}

/**
 * K线倒计时组件
 *
 * 显示当前K线的剩余时间，叠加在图表最后一根K线上方
 *
 * @example
 * ```tsx
 * <KlineCountdown
 *   chart={chartInstance}
 *   interval="5m"
 *   lastBarTime={1640000000}
 *   onZero={() => loadNewData()}
 * />
 * ```
 */
export default function KlineCountdown({
  chart,
  interval,
  lastBarTime,
  onZero,
  show = true,
  className = '',
}: KlineCountdownProps) {
  // 使用倒计时 Hook
  const { countdown } = useCountdown({
    interval,
    lastBarTime,
    onZero,
    enabled: show,
  });

  // 计算倒计时的 X 坐标（显示在时间轴上）
  const position = useMemo(() => {
    if (!chart || !show) {
      return null;
    }

    try {
      const timeScale = chart.timeScale();

      // 获取最后一根K线的X坐标
      const coordinate = timeScale.timeToCoordinate(lastBarTime as any);

      if (coordinate === null) {
        return null;
      }

      // 倒计时显示在时间轴上，X坐标对齐最后一根K线
      return {
        x: coordinate,
      };
    } catch (error) {
      console.error('Error calculating countdown position:', error);
      return null;
    }
  }, [chart, lastBarTime, show]);

  if (!show || !position || countdown.remaining === 0) {
    return null;
  }

  return (
    <div
      className={`absolute pointer-events-none ${className}`}
      style={{
        left: `${position.x}px`,
        bottom: '0px', // 显示在图表底部（时间轴位置）
        transform: 'translate(-50%, -2px)', // 中心对齐，略微上移
        zIndex: 10,
      }}
    >
      <div className="bg-[#2962ff]/90 px-2 py-0.5 rounded-sm text-xs text-white whitespace-nowrap font-mono">
        {countdown.formatted}
      </div>
    </div>
  );
}
