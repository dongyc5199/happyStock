/**
 * K线倒计时 Hook
 *
 * 用于实时显示当前K线的剩余时间
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { calculateRemainingTime, formatCountdown, Timeframe } from '@/lib/utils/timeUtils';
import type { CountdownState } from '@/types/chart';

export interface UseCountdownOptions {
  /** 时间周期 */
  interval: Timeframe;
  /** 最后一根K线的时间戳（秒） */
  lastBarTime: number;
  /** 倒计时归零回调 */
  onZero?: () => void;
  /** 是否启用 */
  enabled?: boolean;
}

export interface UseCountdownReturn {
  /** 倒计时状态 */
  countdown: CountdownState;
  /** 重置倒计时 */
  reset: () => void;
}

/**
 * 使用倒计时
 *
 * @param options - 配置选项
 * @returns 倒计时状态和控制函数
 *
 * @example
 * ```tsx
 * const { countdown, reset } = useCountdown({
 *   interval: '5m',
 *   lastBarTime: 1640000000,
 *   onZero: () => console.log('Time is up!'),
 * });
 *
 * return <div>{countdown.formatted}</div>;
 * ```
 */
export function useCountdown({
  interval,
  lastBarTime,
  onZero,
  enabled = true,
}: UseCountdownOptions): UseCountdownReturn {
  const [countdown, setCountdown] = useState<CountdownState>(() => {
    const remaining = calculateRemainingTime(interval, lastBarTime);
    return {
      remaining,
      formatted: formatCountdown(remaining, interval),
      isZero: remaining === 0,
    };
  });

  const onZeroRef = useRef(onZero);
  const hasCalledOnZeroRef = useRef(false);

  // 更新 onZero ref
  useEffect(() => {
    onZeroRef.current = onZero;
  }, [onZero]);

  // 重置倒计时
  const reset = useCallback(() => {
    const remaining = calculateRemainingTime(interval, lastBarTime);
    setCountdown({
      remaining,
      formatted: formatCountdown(remaining, interval),
      isZero: remaining === 0,
    });
    hasCalledOnZeroRef.current = false;
  }, [interval, lastBarTime]);

  // 倒计时逻辑
  useEffect(() => {
    if (!enabled) {
      return;
    }

    let rafId: number;
    let lastUpdate = 0;

    const update = (timestamp: number) => {
      // 限制更新频率为每秒一次（避免过度渲染）
      if (timestamp - lastUpdate >= 1000) {
        const remaining = calculateRemainingTime(interval, lastBarTime);
        const formatted = formatCountdown(remaining, interval);
        const isZero = remaining === 0;

        setCountdown({ remaining, formatted, isZero });

        // 倒计时归零时触发回调（只触发一次）
        if (isZero && !hasCalledOnZeroRef.current && onZeroRef.current) {
          hasCalledOnZeroRef.current = true;
          onZeroRef.current();
        }

        lastUpdate = timestamp;
      }

      rafId = requestAnimationFrame(update);
    };

    rafId = requestAnimationFrame(update);

    return () => {
      cancelAnimationFrame(rafId);
    };
  }, [enabled, interval, lastBarTime]);

  // 当 interval 或 lastBarTime 变化时重置
  useEffect(() => {
    reset();
  }, [reset]);

  return { countdown, reset };
}
