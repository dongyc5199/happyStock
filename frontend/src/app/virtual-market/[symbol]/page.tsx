'use client';

import { useEffect, useState, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { createChart, ColorType, IChartApi, ISeriesApi } from 'lightweight-charts';
import { stocksApi } from '@/lib/api/virtual-market';
import type { StockDetail, KlineData } from '@/types/virtual-market';

export default function StockDetailPage() {
  const params = useParams();
  const router = useRouter();
  const symbol = params.symbol as string;

  const [stock, setStock] = useState<StockDetail | null>(null);
  const [klineData, setKlineData] = useState<KlineData[]>([]);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('1d');

  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);

  useEffect(() => {
    loadStockData();
  }, [symbol]);

  useEffect(() => {
    loadKlineData();
  }, [symbol, period]);

  useEffect(() => {
    if (chartContainerRef.current && klineData.length > 0) {
      initChart();
    }

    return () => {
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, [klineData]);

  async function loadStockData() {
    try {
      setLoading(true);
      const response = await stocksApi.getStockDetail(symbol);

      if (response.success) {
        setStock(response.data);
      }
    } catch (error) {
      console.error('Failed to load stock detail:', error);
    } finally {
      setLoading(false);
    }
  }

  async function loadKlineData() {
    try {
      const response = await stocksApi.getStockKlines(symbol, {
        period,
        limit: 200,
      });

      if (response.success) {
        setKlineData(response.data);
      }
    } catch (error) {
      console.error('Failed to load K-line data:', error);
    }
  }

  function initChart() {
    if (!chartContainerRef.current || klineData.length === 0) return;

    // Clear previous chart
    if (chartRef.current) {
      chartRef.current.remove();
    }

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: 'white' },
        textColor: '#333',
      },
      width: chartContainerRef.current.clientWidth,
      height: 500,
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
      grid: {
        vertLines: { color: '#f0f0f0' },
        horzLines: { color: '#f0f0f0' },
      },
    });

    chartRef.current = chart;

    // Add candlestick series
    const candlestickSeries = chart.addSeries({
      type: 'Candlestick',
      upColor: '#ef5350',
      downColor: '#26a69a',
      borderVisible: false,
      wickUpColor: '#ef5350',
      wickDownColor: '#26a69a',
    });

    candlestickSeriesRef.current = candlestickSeries;

    // Transform data for Lightweight Charts
    const chartData = klineData.map((item) => ({
      time: item.timestamp / 1000, // Convert to seconds
      open: item.open,
      high: item.high,
      low: item.low,
      close: item.close,
    }));

    candlestickSeries.setData(chartData);

    // Handle resize
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
    };
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6 flex items-center justify-center">
        <div className="text-gray-500">加载中...</div>
      </div>
    );
  }

  if (!stock) {
    return (
      <div className="min-h-screen bg-gray-50 p-6 flex items-center justify-center">
        <div className="text-gray-500">股票不存在</div>
      </div>
    );
  }

  const changePctColor =
    stock.change_pct > 0 ? 'text-red-600' : stock.change_pct < 0 ? 'text-green-600' : 'text-gray-600';

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => router.back()}
            className="mb-4 px-4 py-2 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors"
          >
            ← 返回列表
          </button>
          <div className="flex items-baseline gap-4">
            <h1 className="text-3xl font-bold text-gray-900">
              {stock.name} ({stock.symbol})
            </h1>
            <div className="text-2xl font-semibold">{stock.current_price.toFixed(2)}</div>
            <div className={`text-xl font-semibold ${changePctColor}`}>
              {stock.change_pct > 0 ? '+' : ''}
              {stock.change_pct.toFixed(2)}%
            </div>
            <div className={`text-lg ${changePctColor}`}>
              {stock.change_value > 0 ? '+' : ''}
              {stock.change_value.toFixed(2)}
            </div>
          </div>
        </div>

        {/* Stock Info */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">基本信息</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="text-sm text-gray-500">昨收</div>
              <div className="text-lg font-semibold">{stock.previous_close.toFixed(2)}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">市值(亿)</div>
              <div className="text-lg font-semibold">
                {stock.market_cap ? (stock.market_cap / 100000000).toFixed(2) : '-'}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Beta系数</div>
              <div className="text-lg font-semibold">{stock.beta?.toFixed(2) || '-'}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">波动率</div>
              <div className="text-lg font-semibold">{(stock.volatility * 100).toFixed(2)}%</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">总股本(亿)</div>
              <div className="text-lg font-semibold">{(stock.outstanding_shares / 100000000).toFixed(2)}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">成交量(万)</div>
              <div className="text-lg font-semibold">{(stock.volume / 10000).toFixed(2)}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">成交额(万)</div>
              <div className="text-lg font-semibold">{(stock.turnover / 10000).toFixed(2)}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">上市日期</div>
              <div className="text-lg font-semibold">{stock.listing_date}</div>
            </div>
          </div>
        </div>

        {/* Chart */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">K线图</h2>
            <div className="flex gap-2">
              {['1d', '1w', '1M'].map((p) => (
                <button
                  key={p}
                  onClick={() => setPeriod(p)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    period === p
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {p === '1d' ? '日线' : p === '1w' ? '周线' : '月线'}
                </button>
              ))}
            </div>
          </div>
          <div ref={chartContainerRef} className="w-full" />
        </div>

        {/* Recent K-line Data */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold">最近K线数据</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">日期</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">开盘</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">最高</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">最低</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">收盘</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">涨跌幅</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">成交量</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {klineData.slice(-10).reverse().map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{item.datetime.split('T')[0]}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm">{item.open.toFixed(2)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm">{item.high.toFixed(2)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm">{item.low.toFixed(2)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm">{item.close.toFixed(2)}</td>
                    <td
                      className={`px-6 py-4 whitespace-nowrap text-right text-sm font-semibold ${
                        item.change_pct > 0
                          ? 'text-red-600'
                          : item.change_pct < 0
                          ? 'text-green-600'
                          : 'text-gray-600'
                      }`}
                    >
                      {item.change_pct > 0 ? '+' : ''}
                      {item.change_pct.toFixed(2)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">
                      {(item.volume / 10000).toFixed(2)}万
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
