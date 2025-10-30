'use client';

import { useEffect, useState, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { indicesApi } from '@/lib/api/virtual-market';
import type { KlineData } from '@/types/virtual-market';
import Link from 'next/link';
import { createChart, IChartApi, ISeriesApi, CandlestickData } from 'lightweight-charts';

/**
 * 指数详情页面
 * T053-T056: 指数详情页面和K线图实现
 */
export default function IndexDetailPage() {
  const params = useParams();
  const router = useRouter();
  const code = params.symbol as string;

  const [indexInfo, setIndexInfo] = useState<any>(null);
  const [klineData, setKlineData] = useState<KlineData[]>([]);
  const [period, setPeriod] = useState<'1d' | '1w' | '1M'>('1d');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // K线图相关
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);

  useEffect(() => {
    loadIndexData();
  }, [code, period]);

  useEffect(() => {
    // 初始化图表
    if (chartContainerRef.current && !chartRef.current) {
      const chart = createChart(chartContainerRef.current, {
        width: chartContainerRef.current.clientWidth,
        height: 500,
        layout: {
          background: { color: '#ffffff' },
          textColor: '#333',
        },
        grid: {
          vertLines: { color: '#f0f0f0' },
          horzLines: { color: '#f0f0f0' },
        },
        timeScale: {
          borderColor: '#ddd',
          timeVisible: true,
          secondsVisible: false,
        },
        rightPriceScale: {
          borderColor: '#ddd',
        },
      });

      chartRef.current = chart;

      // 创建蜡烛图系列
      const candlestickSeries = chart.addCandlestickSeries({
        upColor: '#ef5350',
        downColor: '#26a69a',
        borderUpColor: '#ef5350',
        borderDownColor: '#26a69a',
        wickUpColor: '#ef5350',
        wickDownColor: '#26a69a',
      });

      seriesRef.current = candlestickSeries;

      // 响应式调整
      const handleResize = () => {
        if (chartContainerRef.current && chartRef.current) {
          chartRef.current.applyOptions({
            width: chartContainerRef.current.clientWidth,
          });
        }
      };

      window.addEventListener('resize', handleResize);

      return () => {
        window.removeEventListener('resize', handleResize);
        chart.remove();
        chartRef.current = null;
        seriesRef.current = null;
      };
    }
  }, []);

  useEffect(() => {
    // 更新K线数据
    if (seriesRef.current && klineData.length > 0) {
      const formattedData: CandlestickData[] = klineData.map((item) => ({
        time: item.datetime.split('T')[0], // 只取日期部分
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
      }));

      seriesRef.current.setData(formattedData);
      chartRef.current?.timeScale().fitContent();
    }
  }, [klineData]);

  async function loadIndexData() {
    try {
      setLoading(true);
      setError(null);

      // 获取指数详情
      const detailResponse = await indicesApi.getIndexDetail(code);
      if (detailResponse.success && detailResponse.data) {
        setIndexInfo(detailResponse.data);
      }

      // 获取K线数据
      const klineResponse = await indicesApi.getIndexKlines(code, {
        period,
        limit: 200,
      });
      if (klineResponse.success && klineResponse.data) {
        setKlineData(klineResponse.data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载失败');
      console.error('Failed to load index data:', err);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">加载指数数据...</p>
        </div>
      </div>
    );
  }

  if (error || !indexInfo) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <svg
            className="w-16 h-16 text-red-500 mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p className="text-red-600 mb-4">{error || '指数不存在'}</p>
          <Link
            href="/virtual-market/indices"
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 inline-block"
          >
            返回指数列表
          </Link>
        </div>
      </div>
    );
  }

  const changeValue = indexInfo.change_value || 0;
  const changePct = indexInfo.change_pct || 0;
  const isUp = changePct >= 0;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 返回按钮 */}
        <div className="mb-4">
          <Link
            href="/virtual-market/indices"
            className="inline-flex items-center text-blue-600 hover:text-blue-800"
          >
            <svg
              className="w-5 h-5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 19l-7-7m0 0l7-7m-7 7h18"
              />
            </svg>
            返回指数列表
          </Link>
        </div>

        {/* 指数信息卡片 */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{indexInfo.name}</h1>
              <p className="text-sm text-gray-500 mt-1">
                {indexInfo.code} | 基点: {indexInfo.base_point}
              </p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-gray-900">
                {indexInfo.current_value?.toFixed(2)}
              </div>
              <div className="flex items-center justify-end space-x-2 mt-2">
                <span
                  className={`text-lg font-semibold ${
                    isUp ? 'text-red-600' : 'text-green-600'
                  }`}
                >
                  {isUp ? '+' : ''}
                  {changeValue.toFixed(2)}
                </span>
                <span
                  className={`px-3 py-1 rounded text-sm font-semibold ${
                    isUp
                      ? 'bg-red-100 text-red-700'
                      : 'bg-green-100 text-green-700'
                  }`}
                >
                  {isUp ? '+' : ''}
                  {changePct.toFixed(2)}%
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* K线图 */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-800">K线走势</h2>

                {/* 周期选择器 */}
                <div className="flex space-x-2">
                  {[
                    { value: '1d' as const, label: '日K' },
                    { value: '1w' as const, label: '周K' },
                    { value: '1M' as const, label: '月K' },
                  ].map((p) => (
                    <button
                      key={p.value}
                      onClick={() => setPeriod(p.value)}
                      className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
                        period === p.value
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {p.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* K线图容器 */}
              <div ref={chartContainerRef} className="w-full" style={{ height: '500px' }} />

              {/* 最近K线数据表格 */}
              <div className="mt-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-3">最近K线</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          日期
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                          开盘
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                          最高
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                          最低
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                          收盘
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                          涨跌幅
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {klineData.slice(-10).reverse().map((item, idx) => {
                        const itemChangePct = item.change_pct || 0;
                        const itemIsUp = itemChangePct >= 0;
                        return (
                          <tr key={idx}>
                            <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                              {item.datetime.split('T')[0]}
                            </td>
                            <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">
                              {item.open.toFixed(2)}
                            </td>
                            <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">
                              {item.high.toFixed(2)}
                            </td>
                            <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">
                              {item.low.toFixed(2)}
                            </td>
                            <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">
                              {item.close.toFixed(2)}
                            </td>
                            <td
                              className={`px-4 py-3 whitespace-nowrap text-sm text-right font-medium ${
                                itemIsUp ? 'text-red-600' : 'text-green-600'
                              }`}
                            >
                              {itemIsUp ? '+' : ''}
                              {itemChangePct.toFixed(2)}%
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>

          {/* 成分股列表 */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                成分股 ({indexInfo.constituents?.length || 0})
              </h2>

              <div className="space-y-2 max-h-[600px] overflow-y-auto">
                {indexInfo.constituents?.map((constituent: any, idx: number) => (
                  <Link
                    key={constituent.stock_symbol}
                    href={`/virtual-market/${constituent.stock_symbol}`}
                  >
                    <div className="flex items-center justify-between p-3 rounded hover:bg-gray-50 transition-colors cursor-pointer border border-gray-100">
                      <div className="flex items-center space-x-3">
                        <span className="text-xs text-gray-500 w-8">{idx + 1}</span>
                        <div>
                          <div className="font-medium text-gray-900 text-sm">
                            {constituent.stock_name}
                          </div>
                          <div className="text-xs text-gray-500">
                            {constituent.stock_symbol}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium text-blue-600">
                          {(constituent.weight * 100).toFixed(2)}%
                        </div>
                        {constituent.current_price && (
                          <div className="text-xs text-gray-500">
                            ¥{constituent.current_price.toFixed(2)}
                          </div>
                        )}
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
