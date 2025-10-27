'use client';

import { useEffect, useRef, useState } from 'react';
import {
  createChart,
  IChartApi,
  ISeriesApi,
  ColorType,
  LineData,
  HistogramData,
  HistogramSeries,
  LineSeries,
} from 'lightweight-charts';
import { calculateMACD, getMACDStyle, MACD_PRESETS } from '@/lib/indicators/macd';

interface MACDChartProps {
  data: Array<{ time: string | number; close: number }>;
  className?: string;
  height?: number;
}

/**
 * MACD 子图组件
 *
 * 显示 MACD 指标的三个要素：
 * - DIFF 线（蓝色）
 * - DEA 线（橙色）
 * - MACD 柱状图（红绿）
 */
export default function MACDChart({ data, className = '', height = 200 }: MACDChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const diffSeriesRef = useRef<ISeriesApi<'Line'> | null>(null);
  const deaSeriesRef = useRef<ISeriesApi<'Line'> | null>(null);
  const macdSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null);

  const [params, setParams] = useState(MACD_PRESETS.classic);
  const [showConfig, setShowConfig] = useState(false);

  // 初始化图表
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
          height: height,
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
  }, [height]);

  // 更新 MACD 数据
  useEffect(() => {
    if (!chartRef.current || data.length === 0) return;

    // 清理旧的 series
    if (diffSeriesRef.current) {
      try {
        chartRef.current.removeSeries(diffSeriesRef.current);
      } catch (e) {
        console.warn('Failed to remove DIFF series:', e);
      }
      diffSeriesRef.current = null;
    }
    if (deaSeriesRef.current) {
      try {
        chartRef.current.removeSeries(deaSeriesRef.current);
      } catch (e) {
        console.warn('Failed to remove DEA series:', e);
      }
      deaSeriesRef.current = null;
    }
    if (macdSeriesRef.current) {
      try {
        chartRef.current.removeSeries(macdSeriesRef.current);
      } catch (e) {
        console.warn('Failed to remove MACD series:', e);
      }
      macdSeriesRef.current = null;
    }

    // 计算 MACD
    const macdData = calculateMACD(data, params.fast, params.slow, params.signal);

    if (macdData.length === 0) {
      console.warn('MACD data is empty');
      return;
    }

    const style = getMACDStyle();

    try {
      // 1. 添加 MACD 柱状图（先添加，作为背景）
      const macdSeries = chartRef.current.addSeries(HistogramSeries, {
        priceScaleId: 'right',
        priceFormat: {
          type: 'price',
          precision: 4,
          minMove: 0.0001,
        },
      });

      const macdHistogramData: HistogramData[] = macdData.map(item => ({
        time: item.time as any,
        value: item.macd,
        color: item.macd >= 0 ? style.macd.positiveColor : style.macd.negativeColor,
      }));

      macdSeries.setData(macdHistogramData);
      macdSeriesRef.current = macdSeries;

      // 2. 添加 DIFF 线
      const diffSeries = chartRef.current.addSeries(LineSeries, {
        color: style.diff.color,
        lineWidth: style.diff.lineWidth,
        crosshairMarkerVisible: true,
        crosshairMarkerRadius: 4,
        priceScaleId: 'right',
        priceFormat: {
          type: 'price',
          precision: 4,
          minMove: 0.0001,
        },
      });

      const diffLineData: LineData[] = macdData.map(item => ({
        time: item.time as any,
        value: item.diff,
      }));

      diffSeries.setData(diffLineData);
      diffSeriesRef.current = diffSeries;

      // 3. 添加 DEA 线
      const deaSeries = chartRef.current.addSeries(LineSeries, {
        color: style.dea.color,
        lineWidth: style.dea.lineWidth,
        crosshairMarkerVisible: true,
        crosshairMarkerRadius: 4,
        priceScaleId: 'right',
        priceFormat: {
          type: 'price',
          precision: 4,
          minMove: 0.0001,
        },
      });

      const deaLineData: LineData[] = macdData.map(item => ({
        time: item.time as any,
        value: item.dea,
      }));

      deaSeries.setData(deaLineData);
      deaSeriesRef.current = deaSeries;

      // 自动缩放
      chartRef.current.timeScale().fitContent();

      console.log(`MACD chart updated: ${macdData.length} data points`);
    } catch (error) {
      console.error('Error creating MACD chart:', error);
    }
  }, [data, params]);

  const handlePresetChange = (preset: keyof typeof MACD_PRESETS) => {
    setParams(MACD_PRESETS[preset]);
    setShowConfig(false);
  };

  return (
    <div className={`relative ${className}`}>
      {/* 标题和控制栏 */}
      <div className="absolute top-2 left-2 z-10 flex items-center space-x-2">
        <div className="bg-[#131722]/90 px-3 py-1 rounded text-xs text-gray-300">
          MACD({params.fast}, {params.slow}, {params.signal})
        </div>

        {/* 参数配置按钮 */}
        <div className="relative">
          <button
            onClick={() => setShowConfig(!showConfig)}
            className="bg-[#131722]/90 px-2 py-1 rounded text-xs text-gray-400 hover:text-white transition-colors"
            title="MACD 参数"
          >
            ⚙️
          </button>

          {/* 配置面板 */}
          {showConfig && (
            <div className="absolute top-full left-0 mt-1 bg-[#131722] border border-gray-700 rounded shadow-lg p-3 min-w-[200px] z-20">
              <div className="text-xs text-gray-400 mb-2">参数预设</div>
              <div className="flex flex-col gap-2">
                <button
                  onClick={() => handlePresetChange('classic')}
                  className="px-3 py-1 text-xs bg-[#2a2e39] text-gray-300 rounded hover:bg-[#3a3e49] transition-colors text-left"
                >
                  经典 (12, 26, 9)
                </button>
                <button
                  onClick={() => handlePresetChange('fast')}
                  className="px-3 py-1 text-xs bg-[#2a2e39] text-gray-300 rounded hover:bg-[#3a3e49] transition-colors text-left"
                >
                  快速 (6, 13, 5)
                </button>
                <button
                  onClick={() => handlePresetChange('slow')}
                  className="px-3 py-1 text-xs bg-[#2a2e39] text-gray-300 rounded hover:bg-[#3a3e49] transition-colors text-left"
                >
                  慢速 (19, 39, 9)
                </button>
              </div>
            </div>
          )}
        </div>

        {/* 图例 */}
        <div className="bg-[#131722]/90 px-3 py-1 rounded flex items-center space-x-3 text-xs">
          <span className="flex items-center">
            <span className="w-3 h-0.5 bg-[#2962FF] mr-1"></span>
            <span className="text-gray-400">DIFF</span>
          </span>
          <span className="flex items-center">
            <span className="w-3 h-0.5 bg-[#FF6D00] mr-1"></span>
            <span className="text-gray-400">DEA</span>
          </span>
          <span className="flex items-center">
            <span className="w-2 h-3 bg-[#26a69a] mr-1"></span>
            <span className="w-2 h-3 bg-[#ef5350] mr-1"></span>
            <span className="text-gray-400">MACD</span>
          </span>
        </div>
      </div>

      {/* 图表容器 */}
      <div ref={containerRef} className="w-full" style={{ height: `${height}px` }} />
    </div>
  );
}
