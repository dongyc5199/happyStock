import { useEffect, useRef, useState, useCallback } from 'react';
import {
  createChart,
  ColorType,
  IChartApi,
  ISeriesApi,
  CandlestickSeries,
  HistogramSeries,
  LineSeries,
  CandlestickSeriesPartialOptions,
  HistogramSeriesPartialOptions,
  LineSeriesPartialOptions
} from 'lightweight-charts';

/**
 * useChart Hook - 管理 Lightweight Charts 实例的生命周期
 *
 * @param containerRef - 图表容器的 ref
 * @returns 图表 API 实例和辅助方法
 *
 * @example
 * ```tsx
 * const containerRef = useRef<HTMLDivElement>(null);
 * const { chart, addCandlestickSeries, addHistogramSeries } = useChart(containerRef);
 *
 * useEffect(() => {
 *   if (chart) {
 *     const candlestickSeries = addCandlestickSeries();
 *     candlestickSeries.setData(data);
 *   }
 * }, [chart, data]);
 * ```
 */
export function useChart(containerRef: React.RefObject<HTMLDivElement>) {
  const [chart, setChart] = useState<IChartApi | null>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // 创建图表实例
    const chartInstance = createChart(containerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#0a0e14' },
        textColor: '#d1d4dc',
      },
      grid: {
        vertLines: { color: '#2a2e39' },
        horzLines: { color: '#2a2e39' },
      },
      crosshair: {
        mode: 1, // Normal crosshair mode
      },
      rightPriceScale: {
        borderColor: '#2a2e39',
      },
      timeScale: {
        borderColor: '#2a2e39',
        timeVisible: true,
        secondsVisible: false,
      },
      width: containerRef.current.clientWidth,
      height: containerRef.current.clientHeight || 500,
    });

    chartRef.current = chartInstance;
    setChart(chartInstance);

    // 响应式调整图表尺寸
    const handleResize = () => {
      if (containerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: containerRef.current.clientWidth,
          height: containerRef.current.clientHeight || 500,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    // 清理函数：移除图表实例
    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, [containerRef]);

  /**
   * 添加 K线图系列（使用 lightweight-charts 5.x API）
   */
  const addCandlestickSeries = useCallback((options?: CandlestickSeriesPartialOptions): ISeriesApi<'Candlestick'> | null => {
    if (!chartRef.current) {
      console.error('Chart instance not initialized');
      return null;
    }

    try {
      // lightweight-charts 5.x 使用 addSeries(SeriesType, options) 替代 addCandlestickSeries(options)
      const series = chartRef.current.addSeries(CandlestickSeries, {
        upColor: '#26a69a',
        downColor: '#ef5350',
        borderVisible: false,
        wickUpColor: '#26a69a',
        wickDownColor: '#ef5350',
        ...options,
      });

      // 配置K线的价格刻度选项（占据上方80%的空间）
      series.priceScale().applyOptions({
        scaleMargins: {
          top: 0.1,    // 顶部留10%空间
          bottom: 0.25, // 底部留25%空间给成交量
        },
      });

      return series;
    } catch (error) {
      console.error('Error adding candlestick series:', error);
      return null;
    }
  }, []);

  /**
   * 添加柱状图系列（用于成交量，使用 lightweight-charts 5.x API）
   */
  const addHistogramSeries = useCallback((options?: HistogramSeriesPartialOptions): ISeriesApi<'Histogram'> | null => {
    if (!chartRef.current) {
      console.error('Chart instance not initialized');
      return null;
    }

    try {
      // lightweight-charts 5.x 使用 addSeries(SeriesType, options) 替代 addHistogramSeries(options)
      const series = chartRef.current.addSeries(HistogramSeries, {
        color: '#26a69a',
        priceFormat: {
          type: 'volume',
        },
        priceScaleId: 'volume', // 使用独立的价格刻度ID
        ...options,
      });

      // 配置成交量的价格刻度选项（放在底部，占据较小高度）
      series.priceScale().applyOptions({
        scaleMargins: {
          top: 0.8,    // 成交量占据底部20%的空间
          bottom: 0,
        },
      });

      return series;
    } catch (error) {
      console.error('Error adding histogram series:', error);
      return null;
    }
  }, []);

  /**
   * 添加线性系列（用于技术指标如 EMA、MA 等）
   */
  const addLineSeries = useCallback((options?: LineSeriesPartialOptions): ISeriesApi<'Line'> | null => {
    if (!chartRef.current) {
      console.error('Chart instance not initialized');
      return null;
    }

    try {
      const series = chartRef.current.addSeries(LineSeries, {
        color: '#2962FF',
        lineWidth: 2,
        crosshairMarkerVisible: true,
        crosshairMarkerRadius: 4,
        ...options,
      });

      // 使用与K线相同的价格刻度
      series.priceScale().applyOptions({
        scaleMargins: {
          top: 0.1,
          bottom: 0.25,
        },
      });

      return series;
    } catch (error) {
      console.error('Error adding line series:', error);
      return null;
    }
  }, []);

  return {
    chart,
    chartRef, // 也返回 chartRef 以便外部直接访问
    addCandlestickSeries,
    addHistogramSeries,
    addLineSeries,
  };
}
