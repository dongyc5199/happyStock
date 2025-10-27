'use client';

import { useEffect, useRef, useState } from 'react';
import { useChart } from '@/hooks/useChart';
import { ISeriesApi, CandlestickData, HistogramData } from 'lightweight-charts';
import { getKlineData } from '@/lib/api/trading';

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
  const { chart, addCandlestickSeries, addHistogramSeries } = useChart(containerRef);

  const [timeframe, setTimeframe] = useState<Timeframe>('D');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null);

  // 加载 K线数据
  useEffect(() => {
    if (!chart || !assetSymbol) return;

    // 清理旧的 series
    if (candlestickSeriesRef.current) {
      try {
        chart.removeSeries(candlestickSeriesRef.current);
      } catch (e) {
        console.warn('Failed to remove candlestick series:', e);
      }
      candlestickSeriesRef.current = null;
    }
    if (volumeSeriesRef.current) {
      try {
        chart.removeSeries(volumeSeriesRef.current);
      } catch (e) {
        console.warn('Failed to remove volume series:', e);
      }
      volumeSeriesRef.current = null;
    }

    const loadChartData = async () => {
      setLoading(true);
      setError(null);

      try {
        // 将 timeframe 映射到 API interval 参数
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

        // 根据时间周期调整数据量
        const limitMap: Record<Timeframe, number> = {
          '5m': 200,   // 5分钟：200根 = 约16.7小时
          '15m': 200,  // 15分钟：200根 = 约2天
          '30m': 200,  // 30分钟：200根 = 约4天
          '60m': 200,  // 60分钟：200根 = 约8天
          '120m': 200, // 120分钟：200根 = 约16天
          'D': 90,     // 日K：90天
          'W': 52,     // 周K：52周
          'M': 24,     // 月K：24个月
        };
        const limit = limitMap[timeframe];

        // 调用真实 API 获取 K线数据
        const response = await getKlineData(assetSymbol, interval, limit);
        console.log('API Response:', response);
        console.log('First kline:', response.klines[0]);

        // 将后端返回的数据转换为 Lightweight Charts 格式
        // 注意：lightweight-charts 需要时间格式为 YYYY-MM-DD 字符串（日K及以上）或 UTC 时间戳（秒，分钟K）
        const candlestickData: CandlestickData[] = response.klines
          .map((kline) => {
            // 对于分钟级别，使用时间戳；对于日K及以上，使用日期字符串
            const isMinuteInterval = ['5m', '15m', '30m', '60m', '120m'].includes(interval);
            const date = new Date(kline.time * 1000);

            let timeValue: string | number;
            if (isMinuteInterval) {
              // 分钟级别：使用 UTC 时间戳（秒）
              timeValue = kline.time as any;
            } else {
              // 日K及以上：使用 YYYY-MM-DD 格式
              timeValue = date.toISOString().split('T')[0];
            }

            const open = parseFloat(kline.open);
            const high = parseFloat(kline.high);
            const low = parseFloat(kline.low);
            const close = parseFloat(kline.close);

            // 验证 OHLC 数据的有效性：low <= open,close <= high
            if (low > open || low > close || low > high || high < open || high < close) {
              console.warn('Invalid OHLC data:', { time: timeValue, open, high, low, close });
            }

            return {
              time: timeValue as any,
              open,
              high,
              low,
              close,
            };
          })
          .sort((a, b) => (a.time > b.time ? 1 : -1)); // 确保按时间升序排列

        console.log('Candlestick data (first 3):', candlestickData.slice(0, 3));
        console.log('Candlestick data (last 3):', candlestickData.slice(-3));

        // 生成成交量数据
        const volumeData: HistogramData[] = response.klines
          .map((kline) => {
            const isMinuteInterval = ['5m', '15m', '30m', '60m', '120m'].includes(interval);
            const date = new Date(kline.time * 1000);

            let timeValue: string | number;
            if (isMinuteInterval) {
              timeValue = kline.time as any;
            } else {
              timeValue = date.toISOString().split('T')[0];
            }

            return {
              time: timeValue as any,
              value: kline.volume || 0,
              color: parseFloat(kline.close) >= parseFloat(kline.open) ? '#26a69a' : '#ef5350',
            };
          })
          .sort((a, b) => (a.time > b.time ? 1 : -1)); // 确保按时间升序排列

        console.log('Volume data (first 3):', volumeData.slice(0, 3));

        // 创建 K线系列（使用 hook 提供的方法）
        console.log('Creating candlestick series...');

        try {
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
            console.log('Sample data point:', candlestickData[0]);
            candlestickSeriesRef.current.setData(candlestickData);
            console.log('Candlestick data set successfully');
          }
        } catch (error) {
          console.error('Error with candlestick chart:', error);
          console.error('Error stack:', (error as Error).stack);
          console.error('Data that failed:', candlestickData.slice(0, 5));
          throw error;
        }

        // 创建成交量系列（使用 hook 提供的方法）
        console.log('Creating volume series...');
        try {
          if (!volumeSeriesRef.current && addHistogramSeries) {
            volumeSeriesRef.current = addHistogramSeries({
              color: '#26a69a',
              priceFormat: {
                type: 'volume',
              },
              priceScaleId: '',
            });

            if (!volumeSeriesRef.current) {
              throw new Error('Failed to create volume series');
            }
            console.log('Volume series created successfully');
          }

          if (volumeSeriesRef.current) {
            console.log('Setting volume data...');
            volumeSeriesRef.current.setData(volumeData);
            console.log('Volume data set successfully');
          }
        } catch (error) {
          console.error('Error setting volume data:', error);
          console.error('Data that failed:', volumeData);
          throw error;
        }

        // 自动缩放到数据范围
        chart.timeScale().fitContent();

      } catch (err: any) {
        setError(err.message || '加载图表数据失败');
        console.error('加载K线数据失败:', err);
      } finally {
        setLoading(false);
      }
    };

    loadChartData();
  }, [chart, assetSymbol, timeframe, addCandlestickSeries, addHistogramSeries]);

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

      {/* 图表容器 */}
      <div ref={containerRef} className="w-full h-full" />

      {/* 加载状态 */}
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-[#0a0e14]/80">
          <div className="text-white">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
            <p className="mt-4 text-sm">加载图表数据...</p>
          </div>
        </div>
      )}

      {/* 错误状态 */}
      {error && !loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-[#0a0e14]/80">
          <div className="text-center">
            <svg className="w-16 h-16 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-red-500 mb-4">{error}</p>
            <button
              onClick={() => setError(null)}
              className="px-4 py-2 bg-[#2962ff] text-white rounded hover:bg-[#1e53e5] transition-colors"
            >
              重试
            </button>
          </div>
        </div>
      )}

      {/* 无数据状态 */}
      {!assetSymbol && !loading && !error && (
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
