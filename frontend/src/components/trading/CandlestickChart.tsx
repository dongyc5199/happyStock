'use client';

import { useEffect, useRef, useState } from 'react';
import { useChart } from '@/hooks/useChart';
import { useChartData } from '@/hooks/useChartData';
import { ISeriesApi, CandlestickData, HistogramData, LineData } from 'lightweight-charts';
import { getKlineData } from '@/lib/api/trading';
import { calculateEMA, getEMAStyle, EMA_PRESETS } from '@/lib/indicators/ema';
import MACDChart from './MACDChart';
import VolumeChart from './VolumeChart';
import KlineCountdown from './KlineCountdown';
import { Timeframe as TimeframeType } from '@/lib/utils/timeUtils';

type Timeframe = '5m' | '15m' | '30m' | '60m' | '120m' | 'D' | 'W' | 'M';

interface CandlestickChartProps {
  assetSymbol: string | null;
  className?: string;
}

/**
 * K线图表组件 - 使用 Lightweight Charts 5.x 显示股票 K线数据
 *
 * @param assetSymbol - 股票代码
 * @param className - 自定义样式类名
 */
export default function CandlestickChart({ assetSymbol, className = '' }: CandlestickChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const { chart, addCandlestickSeries, addHistogramSeries, addLineSeries } = useChart(containerRef);

  const [timeframe, setTimeframe] = useState<Timeframe>('D');

  // 将 Timeframe 转换为 TimeframeType
  const getIntervalForHook = (tf: Timeframe): TimeframeType => {
    const map: Record<Timeframe, TimeframeType> = {
      '5m': '5m',
      '15m': '15m',
      '30m': '30m',
      '60m': '60m',
      '120m': '120m',
      'D': '1d',
      'W': '1w',
      'M': '1M',
    };
    return map[tf];
  };

  // 使用 useChartData Hook 进行动态数据加载
  const {
    data: chartData,
    loadedRange,
    loadingState,
    loadHistoricalData,
    loadLatestData,
  } = useChartData({
    chart,
    symbol: assetSymbol,
    interval: getIntervalForHook(timeframe),
    enabled: true,
    loadBuffer: 50,
    loadLimit: 200,
  });

  // 图表类型配置（从 LocalStorage 加载用户偏好）
  const [chartType, setChartType] = useState<'candlestick' | 'line'>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('chartType');
      return (saved === 'line' ? 'line' : 'candlestick') as 'candlestick' | 'line';
    }
    return 'candlestick';
  });

  // EMA 显示配置
  const [enabledEMAs, setEnabledEMAs] = useState<number[]>([5, 10, 20, 30]); // 默认显示 EMA5, 10, 20, 30
  const [showEMAConfig, setShowEMAConfig] = useState(false);

  // MACD 显示配置
  const [showMACD, setShowMACD] = useState(true); // 默认显示 MACD
  const [macdData, setMacdData] = useState<Array<{ time: string | number; close: number }>>([]);

  // 倒计时配置
  const [showCountdown, setShowCountdown] = useState(true); // 默认显示倒计时
  const [lastBarTime, setLastBarTime] = useState<number>(0); // 最后一根K线的时间戳（秒）

  // 成交量显示和高度配置
  const [showVolume, setShowVolume] = useState(true); // 默认显示成交量
  const [volumeHeight, setVolumeHeight] = useState(100); // 默认 100px
  const [isDraggingVolume, setIsDraggingVolume] = useState(false);
  const [volumeData, setVolumeData] = useState<Array<{ time: string | number; volume: number; isUp: boolean }>>([]);

  // MACD 高度配置
  const [macdHeight, setMacdHeight] = useState(200); // 默认 200px
  const [isDraggingMACD, setIsDraggingMACD] = useState(false);

  const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const lineSeriesRef = useRef<ISeriesApi<'Line'> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null);
  const emaSeriesRef = useRef<Map<number, ISeriesApi<'Line'>>>(new Map());
  const emaConfigRef = useRef<HTMLDivElement>(null);

  // 保存用户偏好到 LocalStorage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('chartType', chartType);
    }
  }, [chartType]);

  // 点击外部关闭 EMA 配置面板
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (emaConfigRef.current && !emaConfigRef.current.contains(event.target as Node)) {
        setShowEMAConfig(false);
      }
    };

    if (showEMAConfig) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showEMAConfig]);

  // 渲染图表数据（当 chartData 变化时更新图表）
  useEffect(() => {
    if (!chart || !chartData || chartData.length === 0) return;

    // 清理旧的 series
    if (candlestickSeriesRef.current) {
      try {
        chart.removeSeries(candlestickSeriesRef.current);
      } catch (e) {
        console.warn('Failed to remove candlestick series:', e);
      }
      candlestickSeriesRef.current = null;
    }
    if (lineSeriesRef.current) {
      try {
        chart.removeSeries(lineSeriesRef.current);
      } catch (e) {
        console.warn('Failed to remove line series:', e);
      }
      lineSeriesRef.current = null;
    }
    // 清理所有 EMA 线
    emaSeriesRef.current.forEach((series, period) => {
      try {
        chart.removeSeries(series);
      } catch (e) {
        console.warn(`Failed to remove EMA${period} series:`, e);
      }
    });
    emaSeriesRef.current.clear();

    console.log('Rendering chart with data:', chartData.length, 'bars');

    // 生成成交量数据（使用随机值，因为 chartData 不包含 volume）
    const generatedVolumeData = chartData.map((item) => ({
      time: item.time,
      volume: Math.random() * 1000000, // 随机成交量
      isUp: item.close >= item.open,
    }));
    setVolumeData(generatedVolumeData);

    // 根据 chartType 创建不同的系列
    console.log('Creating chart series, type:', chartType);

    try {
      if (chartType === 'candlestick') {
        // 创建蜡烛图系列
        if (!candlestickSeriesRef.current && addCandlestickSeries) {
          candlestickSeriesRef.current = addCandlestickSeries({
            upColor: '#26a69a',
            downColor: '#ef5350',
            borderVisible: false,
            wickUpColor: '#26a69a',
            wickDownColor: '#ef5350',
          });

          if (!candlestickSeriesRef.current) {
            throw new Error('Failed to create candlestick series');
          }
          console.log('Candlestick series created successfully');
        }

        if (candlestickSeriesRef.current) {
          console.log('Setting candlestick data...');
          candlestickSeriesRef.current.setData(chartData);
          console.log('Candlestick data set successfully');
        }
      } else {
        // 创建线形图系列
        if (!lineSeriesRef.current && addLineSeries) {
          lineSeriesRef.current = addLineSeries({
            color: '#2962FF',
            lineWidth: 2,
            title: '收盘价',
          });

          if (!lineSeriesRef.current) {
            throw new Error('Failed to create line series');
          }
          console.log('Line series created successfully');
        }

        if (lineSeriesRef.current) {
          console.log('Setting line data...');
          // 线形图只需要时间和收盘价
          const lineData: LineData[] = chartData.map(item => ({
            time: item.time,
            value: item.close,
          }));
          lineSeriesRef.current.setData(lineData);
          console.log('Line data set successfully');
        }
      }
    } catch (error) {
      console.error('Error creating chart series:', error);
      console.error('Error stack:', (error as Error).stack);
      console.error('Data that failed:', chartData.slice(0, 5));
    }

    // 准备价格数据用于指标计算
    const priceData = chartData.map(item => ({
      time: item.time,
      close: item.close,
    }));

    // 更新 MACD 数据
    setMacdData(priceData);

    // 更新最后一根K线时间（用于倒计时）
    if (chartData.length > 0) {
      const lastBar = chartData[chartData.length - 1];
      const lastTime = typeof lastBar.time === 'number'
        ? lastBar.time
        : Math.floor(Date.parse(lastBar.time as string) / 1000);
      setLastBarTime(lastTime);
    }

    // 计算并添加 EMA 指标线
    if (enabledEMAs.length > 0 && addLineSeries) {
      console.log('Calculating and adding EMA indicators...');

      // 为每个启用的 EMA 周期创建线系列
      enabledEMAs.forEach(period => {
        try {
          // 计算 EMA
          const emaData = calculateEMA(priceData, period);

          if (emaData.length > 0) {
            // 获取 EMA 样式
            const style = getEMAStyle(period);

            // 创建 EMA 线系列
            const emaSeries = addLineSeries({
              color: style.color,
              lineWidth: style.lineWidth,
              title: style.title,
            });

            if (emaSeries) {
              // 设置 EMA 数据
              emaSeries.setData(emaData as LineData[]);
              // 保存到 ref
              emaSeriesRef.current.set(period, emaSeries);
              console.log(`EMA${period} added successfully`);
            }
          }
        } catch (error) {
          console.error(`Error adding EMA${period}:`, error);
        }
      });
    }

    // 自动缩放到数据范围
    chart.timeScale().fitContent();
  }, [chart, chartData, chartType, enabledEMAs, addCandlestickSeries, addHistogramSeries, addLineSeries]);

  // 切换时间周期
  const handleTimeframeChange = (newTimeframe: Timeframe) => {
    setTimeframe(newTimeframe);
  };

  // 重置缩放
  const handleResetZoom = () => {
    if (chart) {
      chart.timeScale().fitContent();
    }
  };

  // 切换 EMA 显示
  const toggleEMA = (period: number) => {
    setEnabledEMAs(prev => {
      if (prev.includes(period)) {
        // 移除该周期
        return prev.filter(p => p !== period);
      } else {
        // 添加该周期
        return [...prev, period].sort((a, b) => a - b);
      }
    });
  };

  // 快速设置预设组合
  const setEMAPreset = (preset: keyof typeof EMA_PRESETS) => {
    setEnabledEMAs([...EMA_PRESETS[preset]]);
    setShowEMAConfig(false);
  };

  // 将 Timeframe 转换为 TimeframeType
  const getCountdownInterval = (tf: Timeframe): TimeframeType => {
    const intervalMap: Record<Timeframe, TimeframeType> = {
      '5m': '5m',
      '15m': '15m',
      '30m': '30m',
      '60m': '60m',
      '120m': '120m',
      'D': '1d',
      'W': '1w',
      'M': '1M',
    };
    return intervalMap[tf];
  };

  // 处理成交量拖动
  const volumeDragStartY = useRef<number>(0);
  const volumeStartHeight = useRef<number>(0);

  const handleVolumeMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    volumeDragStartY.current = e.clientY;
    volumeStartHeight.current = volumeHeight;
    setIsDraggingVolume(true);
  };

  useEffect(() => {
    if (!isDraggingVolume) return;

    const handleMouseMove = (e: MouseEvent) => {
      // 计算鼠标移动的距离（向上为正，向下为负）
      const deltaY = volumeDragStartY.current - e.clientY;
      const newHeight = volumeStartHeight.current + deltaY;

      // 限制最小和最大高度
      const minHeight = 60;
      const maxHeight = 200;

      if (newHeight >= minHeight && newHeight <= maxHeight) {
        setVolumeHeight(newHeight);
      }
    };

    const handleMouseUp = () => {
      setIsDraggingVolume(false);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDraggingVolume, volumeHeight]);

  // 处理 MACD 拖动
  const macdDragStartY = useRef<number>(0);
  const macdStartHeight = useRef<number>(0);

  const handleMACDMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    macdDragStartY.current = e.clientY;
    macdStartHeight.current = macdHeight;
    setIsDraggingMACD(true);
  };

  useEffect(() => {
    if (!isDraggingMACD) return;

    const handleMouseMove = (e: MouseEvent) => {
      // 计算鼠标移动的距离（向上为正，向下为负）
      const deltaY = macdDragStartY.current - e.clientY;
      const newHeight = macdStartHeight.current + deltaY;

      // 限制最小和最大高度
      const minHeight = 100;
      const maxHeight = 300;

      if (newHeight >= minHeight && newHeight <= maxHeight) {
        setMacdHeight(newHeight);
      }
    };

    const handleMouseUp = () => {
      setIsDraggingMACD(false);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDraggingMACD, macdHeight]);

  // 倒计时归零回调：刷新最新K线数据
  const handleCountdownZero = async () => {
    if (!chart || !assetSymbol) return;

    try {
      // 获取最新的一根K线
      const intervalMap: Record<Timeframe, '5m' | '15m' | '30m' | '60m' | '120m' | '1d' | '1w' | '1M'> = {
        '5m': '5m',
        '15m': '15m',
        '30m': '30m',
        '60m': '60m',
        '120m': '120m',
        'D': '1d',
        'W': '1w',
        'M': '1M',
      };
      const interval = intervalMap[timeframe];

      // 只获取最新1根K线
      const response = await getKlineData(assetSymbol, interval, 1);

      if (response.klines.length > 0 && candlestickSeriesRef.current) {
        const latestKline = response.klines[0];
        const isMinuteInterval = ['5m', '15m', '30m', '60m', '120m'].includes(interval);

        let timeValue: string | number;
        if (isMinuteInterval) {
          timeValue = latestKline.time as any;
        } else {
          const date = new Date(latestKline.time * 1000);
          timeValue = date.toISOString().split('T')[0];
        }

        const newBar: CandlestickData = {
          time: timeValue as any,
          open: parseFloat(latestKline.open),
          high: parseFloat(latestKline.high),
          low: parseFloat(latestKline.low),
          close: parseFloat(latestKline.close),
        };

        // 更新图表数据（追加或更新最后一根K线）
        candlestickSeriesRef.current.update(newBar);

        // 更新最后一根K线时间
        const newLastTime = typeof newBar.time === 'number'
          ? newBar.time
          : Math.floor(Date.parse(newBar.time as string) / 1000);
        setLastBarTime(newLastTime);

        console.log('Updated latest kline:', newBar);
      }
    } catch (error) {
      console.error('Failed to refresh kline data:', error);
    }
  };

  return (
    <div className={`relative h-full w-full ${className}`}>
      {/* 顶部工具栏 */}
      <div className="absolute top-4 left-4 z-10 flex items-center space-x-4">
        {/* 股票信息 */}
        {assetSymbol && (
          <div className="bg-[#131722]/90 px-4 py-2 rounded">
            <span className="text-white font-semibold text-lg">{assetSymbol}</span>
          </div>
        )}

        {/* 时间周期选择器 */}
        <div className="bg-[#131722]/90 px-2 py-1 rounded flex space-x-2">
          {/* 分钟级别 */}
          <div className="flex space-x-1 pr-2 border-r border-gray-700">
            {(['5m', '15m', '30m', '60m', '120m'] as Timeframe[]).map((tf) => (
              <button
                key={tf}
                onClick={() => handleTimeframeChange(tf)}
                className={`px-2 py-1 rounded text-xs transition-colors ${
                  timeframe === tf
                    ? 'bg-[#2962ff] text-white'
                    : 'text-gray-400 hover:text-white hover:bg-[#2a2e39]'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>

          {/* 日、周、月级别 */}
          <div className="flex space-x-1">
            {(['D', 'W', 'M'] as Timeframe[]).map((tf) => (
              <button
                key={tf}
                onClick={() => handleTimeframeChange(tf)}
                className={`px-3 py-1 rounded text-sm transition-colors ${
                  timeframe === tf
                    ? 'bg-[#2962ff] text-white'
                    : 'text-gray-400 hover:text-white hover:bg-[#2a2e39]'
                }`}
              >
                {tf === 'D' ? '日K' : tf === 'W' ? '周K' : '月K'}
              </button>
            ))}
          </div>
        </div>

        {/* EMA 指标配置 */}
        <div className="relative" ref={emaConfigRef}>
          <button
            onClick={() => setShowEMAConfig(!showEMAConfig)}
            className={`bg-[#131722]/90 px-3 py-1 rounded text-sm transition-colors ${
              enabledEMAs.length > 0
                ? 'text-[#26a69a] hover:bg-[#2a2e39]'
                : 'text-gray-400 hover:text-white hover:bg-[#2a2e39]'
            }`}
            title="EMA 技术指标"
          >
            EMA {enabledEMAs.length > 0 && `(${enabledEMAs.length})`}
          </button>

          {/* EMA 配置面板 */}
          {showEMAConfig && (
            <div className="absolute top-full left-0 mt-2 bg-[#131722] border border-gray-700 rounded shadow-lg p-4 min-w-[280px] z-20">
              {/* 快速预设 */}
              <div className="mb-4">
                <div className="text-xs text-gray-400 mb-2">快速预设</div>
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => setEMAPreset('short')}
                    className="px-3 py-1 text-xs bg-[#2a2e39] text-gray-300 rounded hover:bg-[#3a3e49] transition-colors"
                  >
                    短期 (5,10,20)
                  </button>
                  <button
                    onClick={() => setEMAPreset('medium')}
                    className="px-3 py-1 text-xs bg-[#2a2e39] text-gray-300 rounded hover:bg-[#3a3e49] transition-colors"
                  >
                    中期 (30,60)
                  </button>
                  <button
                    onClick={() => setEMAPreset('long')}
                    className="px-3 py-1 text-xs bg-[#2a2e39] text-gray-300 rounded hover:bg-[#3a3e49] transition-colors"
                  >
                    长期 (120,250)
                  </button>
                  <button
                    onClick={() => setEMAPreset('all')}
                    className="px-3 py-1 text-xs bg-[#2a2e39] text-gray-300 rounded hover:bg-[#3a3e49] transition-colors"
                  >
                    全部
                  </button>
                </div>
              </div>

              {/* 自定义选择 */}
              <div>
                <div className="text-xs text-gray-400 mb-2">自定义周期</div>
                <div className="grid grid-cols-3 gap-2">
                  {[5, 10, 20, 30, 60, 120].map(period => {
                    const isEnabled = enabledEMAs.includes(period);
                    const style = getEMAStyle(period);
                    return (
                      <button
                        key={period}
                        onClick={() => toggleEMA(period)}
                        className={`px-3 py-2 text-xs rounded transition-colors flex items-center justify-between ${
                          isEnabled
                            ? 'bg-[#2a2e39] text-white border border-gray-600'
                            : 'bg-[#1a1e29] text-gray-400 hover:bg-[#2a2e39]'
                        }`}
                      >
                        <span>EMA{period}</span>
                        {isEnabled && (
                          <span
                            className="w-3 h-3 rounded-full ml-2"
                            style={{ backgroundColor: style.color }}
                          />
                        )}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* 清除全部 */}
              <div className="mt-4 pt-3 border-t border-gray-700">
                <button
                  onClick={() => {
                    setEnabledEMAs([]);
                    setShowEMAConfig(false);
                  }}
                  className="w-full px-3 py-1 text-xs bg-red-900/30 text-red-400 rounded hover:bg-red-900/50 transition-colors"
                >
                  清除全部
                </button>
              </div>
            </div>
          )}
        </div>

        {/* 图表类型切换 */}
        <div className="bg-[#131722]/90 rounded flex">
          <button
            onClick={() => setChartType('candlestick')}
            className={`px-3 py-1 text-sm transition-colors rounded-l ${
              chartType === 'candlestick'
                ? 'bg-[#2962ff] text-white'
                : 'text-gray-400 hover:text-white hover:bg-[#2a2e39]'
            }`}
            title="蜡烛图"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
              <path d="M8 1v2M8 13v2M3 5h2v6H3zM11 3h2v10h-2zM4 6h1v4H4zM12 4h1v8h-1z"/>
            </svg>
          </button>
          <button
            onClick={() => setChartType('line')}
            className={`px-3 py-1 text-sm transition-colors rounded-r ${
              chartType === 'line'
                ? 'bg-[#2962ff] text-white'
                : 'text-gray-400 hover:text-white hover:bg-[#2a2e39]'
            }`}
            title="线形图"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 16 16" strokeWidth="2">
              <path d="M2 12L5 8L8 10L14 4" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </div>

        {/* 成交量指标开关 */}
        <button
          onClick={() => setShowVolume(!showVolume)}
          className={`bg-[#131722]/90 px-3 py-1 rounded text-sm transition-colors ${
            showVolume
              ? 'text-[#26a69a] hover:bg-[#2a2e39]'
              : 'text-gray-400 hover:text-white hover:bg-[#2a2e39]'
          }`}
          title="成交量"
        >
          VOL
        </button>

        {/* MACD 指标开关 */}
        <button
          onClick={() => setShowMACD(!showMACD)}
          className={`bg-[#131722]/90 px-3 py-1 rounded text-sm transition-colors ${
            showMACD
              ? 'text-[#2962FF] hover:bg-[#2a2e39]'
              : 'text-gray-400 hover:text-white hover:bg-[#2a2e39]'
          }`}
          title="MACD 指标"
        >
          MACD
        </button>

        {/* 重置缩放按钮 */}
        <button
          onClick={handleResetZoom}
          className="bg-[#131722]/90 px-3 py-1 rounded text-sm text-gray-400 hover:text-white hover:bg-[#2a2e39] transition-colors"
          title="重置缩放"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
          </svg>
        </button>
      </div>

      {/* 主图表容器 */}
      <div
        className="relative w-full"
        style={{
          height: `calc(100% - ${showVolume ? volumeHeight + 4 : 0}px - ${showMACD ? macdHeight + 4 : 0}px)`
        }}
      >
        <div ref={containerRef} className="w-full h-full" />

        {/* K线倒计时 */}
        {chart && lastBarTime > 0 && (
          <KlineCountdown
            chart={chart}
            interval={getCountdownInterval(timeframe)}
            lastBarTime={lastBarTime}
            onZero={handleCountdownZero}
            show={showCountdown}
          />
        )}
      </div>

      {/* 成交量子图 */}
      {showVolume && volumeData.length > 0 && (
        <>
          {/* 可拖动分隔条 */}
          <div
            onMouseDown={handleVolumeMouseDown}
            className={`h-1 bg-[#2a2e39] hover:bg-green-500 cursor-ns-resize transition-colors relative group ${
              isDraggingVolume ? 'bg-green-500' : ''
            }`}
          >
            {/* 拖动提示图标 */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-8 h-0.5 bg-gray-600 group-hover:bg-green-400 transition-colors"></div>
            </div>
          </div>

          <div className="w-full border-t border-gray-800">
            <VolumeChart data={volumeData} height={volumeHeight} />
          </div>
        </>
      )}

      {/* MACD 子图 */}
      {showMACD && macdData.length > 0 && (
        <>
          {/* 可拖动分隔条 */}
          <div
            onMouseDown={handleMACDMouseDown}
            className={`h-1 bg-[#2a2e39] hover:bg-blue-500 cursor-ns-resize transition-colors relative group ${
              isDraggingMACD ? 'bg-blue-500' : ''
            }`}
          >
            {/* 拖动提示图标 */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-8 h-0.5 bg-gray-600 group-hover:bg-blue-400 transition-colors"></div>
            </div>
          </div>

          <div className="w-full border-t border-gray-800">
            <MACDChart data={macdData} height={macdHeight} />
          </div>
        </>
      )}

      {/* 加载状态 */}
      {loadingState.loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-[#0a0e14]/80">
          <div className="text-white">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
            <p className="mt-4 text-sm">
              {loadingState.direction === 'historical' ? '加载历史数据...' :
               loadingState.direction === 'latest' ? '加载最新数据...' :
               '加载图表数据...'}
            </p>
          </div>
        </div>
      )}

      {/* 错误状态 */}
      {loadingState.error && !loadingState.loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-[#0a0e14]/80">
          <div className="text-center">
            <svg className="w-16 h-16 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-red-500 mb-4">{loadingState.error}</p>
          </div>
        </div>
      )}

      {/* 数据加载边界提示 */}
      {loadedRange.reachedStart && chartData.length > 0 && (
        <div className="absolute top-20 left-4 bg-[#131722]/90 px-3 py-1 rounded text-xs text-gray-400">
          已加载全部历史数据
        </div>
      )}
      {loadedRange.reachedEnd && chartData.length > 0 && (
        <div className="absolute top-20 right-4 bg-[#131722]/90 px-3 py-1 rounded text-xs text-gray-400">
          已是最新数据
        </div>
      )}

      {/* 无数据状态 */}
      {!assetSymbol && !loadingState.loading && !loadingState.error && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center text-gray-500">
            <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <p>请选择股票查看K线图表</p>
          </div>
        </div>
      )}
    </div>
  );
}
