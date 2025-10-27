'use client';

import { useEffect, useRef } from 'react';
import {
  createChart,
  IChartApi,
  ISeriesApi,
  ColorType,
  HistogramData,
  HistogramSeries,
  HistogramSeriesPartialOptions,
} from 'lightweight-charts';

interface VolumeChartProps {
  data: Array<{ time: string | number; volume: number; isUp: boolean }>;
  className?: string;
  height?: number;
}

/**
 * 成交量子图组件
 */
export default function VolumeChart({ data, className = '', height = 100 }: VolumeChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null);

  // 初始化图表（仅在组件挂载时创建一次）
  useEffect(() => {
    if (!containerRef.current) return;

    const chart = createChart(containerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#0a0e14' },
        textColor: '#d1d4dc',
      },
      grid: {
        vertLines: { color: '#2a2e39' },
        horzLines: { color: '#2a2e39' },
      },
      crosshair: {
        mode: 1,
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
      height: height,
    });

    chartRef.current = chart;

    // 响应式调整图表尺寸
    const handleResize = () => {
      if (containerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: containerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, []); // 空依赖数组，仅在挂载时执行

  // 当高度变化时，更新图表尺寸
  useEffect(() => {
    if (chartRef.current) {
      chartRef.current.applyOptions({
        height: height,
      });
    }
  }, [height]);

  // 更新成交量数据
  useEffect(() => {
    if (!chartRef.current || data.length === 0) return;

    // 清理旧的 series
    if (volumeSeriesRef.current) {
      try {
        if (chartRef.current && typeof chartRef.current.removeSeries === 'function') {
          chartRef.current.removeSeries(volumeSeriesRef.current);
        }
      } catch (e) {
        // 忽略错误
      }
      volumeSeriesRef.current = null;
    }

    try {
      // 创建成交量柱状图（使用 lightweight-charts 5.x API）
      const volumeSeries = chartRef.current.addSeries(HistogramSeries, {
        priceScaleId: 'right',
        priceFormat: {
          type: 'volume',
        },
      });

      const volumeData: HistogramData[] = data.map(item => ({
        time: item.time as any,
        value: item.volume,
        color: item.isUp ? '#26a69a' : '#ef5350',
      }));

      volumeSeries.setData(volumeData);
      volumeSeriesRef.current = volumeSeries;

      // 自动缩放
      chartRef.current.timeScale().fitContent();

      console.log(`Volume chart updated: ${volumeData.length} data points`);
    } catch (error) {
      console.error('Error creating volume chart:', error);
    }
  }, [data]);

  return (
    <div className={`relative ${className}`}>
      {/* 标题 */}
      <div className="absolute top-2 left-2 z-10">
        <div className="bg-[#131722]/90 px-3 py-1 rounded text-xs text-gray-300">
          成交量
        </div>
      </div>

      {/* 图表容器 */}
      <div ref={containerRef} className="w-full" style={{ height: `${height}px` }} />
    </div>
  );
}
