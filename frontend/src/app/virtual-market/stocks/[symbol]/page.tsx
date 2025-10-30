'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import { MainNav } from '@/components/layout/MainNav';

// 动态导入K线图组件(避免SSR问题)
const CandlestickChart = dynamic(
  () => import('@/components/trading/CandlestickChart'),
  { ssr: false }
);

interface StockDetail {
  symbol: string;
  name: string;
  current_price: number;
  previous_close: number;
  change_value: number;
  change_pct: number;
  sector_code: string;
  sector_name: string;
  market_cap: number;
  market_cap_tier: string;
  beta: number;
  volatility: number;
  outstanding_shares: number;
  listing_date: string;
  is_happy300: boolean;
  weight_in_happy300: number | null;
  indices: Array<{
    index_code: string;
    index_name: string;
    weight: number;
  }>;
}

export default function StockDetailPage() {
  const params = useParams();
  const symbol = params?.symbol as string;

  const [stock, setStock] = useState<StockDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (symbol) {
      fetchStockDetail();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [symbol]);

  const fetchStockDetail = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`http://localhost:8000/api/v1/stocks/${symbol}`);
      const data = await response.json();

      if (data.success && data.data) {
        setStock(data.data);
      } else {
        setError(data.error?.message || '股票不存在');
      }
    } catch (err) {
      setError('加载失败');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <MainNav />
        <div className="flex items-center justify-center" style={{ minHeight: 'calc(100vh - 64px)' }}>
          <div className="text-center">
            <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600">加载中...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !stock) {
    return (
      <div className="min-h-screen bg-gray-50">
        <MainNav />
        <div className="flex items-center justify-center" style={{ minHeight: 'calc(100vh - 64px)' }}>
          <div className="text-center text-red-600">
            <p className="text-xl font-bold mb-2">⚠️ {error || '股票不存在'}</p>
            <Link href="/virtual-market" className="text-blue-600 hover:underline">
              返回股票列表
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const isUp = stock.change_pct > 0;
  const isFlat = Math.abs(stock.change_pct) < 0.01;

  return (
    <div className="min-h-screen bg-gray-50">
      <MainNav />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 面包屑导航 */}
        <div className="mb-6">
          <nav className="flex text-sm" aria-label="Breadcrumb">
            <ol className="flex items-center space-x-2">
              <li>
                <Link href="/virtual-market" className="text-gray-500 hover:text-gray-700">
                  市场首页
                </Link>
              </li>
              <li><span className="text-gray-400">/</span></li>
              <li>
                <span className="text-gray-900 font-medium">{stock.name} ({stock.symbol})</span>
              </li>
            </ol>
          </nav>
        </div>

        {/* 股票头部信息 */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {stock.name}
                <span className="text-xl text-gray-500 ml-3">{stock.symbol}</span>
              </h1>
              <Link
                href={`/virtual-market/sectors/${stock.sector_code}`}
                className="text-blue-600 hover:text-blue-800 hover:underline"
              >
                {stock.sector_name} ({stock.sector_code})
              </Link>
            </div>
            <div className="text-right">
              <div className="text-4xl font-bold text-gray-900 mb-1">
                ¥{stock.current_price.toFixed(2)}
              </div>
              <div className={`text-lg ${
                isUp ? 'text-red-600' : isFlat ? 'text-gray-600' : 'text-green-600'
              }`}>
                {isUp ? '+' : ''}{stock.change_value.toFixed(2)} ({isUp ? '+' : ''}{stock.change_pct.toFixed(2)}%)
              </div>
            </div>
          </div>

          {/* HAPPY300 成分股标识 - T095/T096 */}
          {stock.is_happy300 ? (
            <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border-2 border-yellow-400 rounded-lg p-4">
              <div className="flex items-center gap-3">
                <svg className="w-8 h-8 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
                <div>
                  <div className="text-lg font-bold text-yellow-900">HAPPY300 成分股</div>
                  <div className="text-sm text-yellow-800">
                    权重: {(stock.weight_in_happy300! * 100).toFixed(2)}%
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
              <div className="text-sm text-gray-600">💡 非 HAPPY300 成分股</div>
            </div>
          )}
        </div>

        {/* 价格走势图 - 添加时间轴 */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden mb-6">
          <div className="p-4 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900">价格走势</h2>
          </div>
          <div className="w-full" style={{ height: '500px' }}>
            <CandlestickChart assetSymbol={stock.symbol} />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 左侧:元数据 - T094 */}
          <div className="lg:col-span-2 space-y-6">
            {/* 基本信息卡片 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">基本信息</h2>
              <div className="grid grid-cols-2 gap-4">
                <InfoItem label="昨收" value={`¥${stock.previous_close.toFixed(2)}`} />
                <InfoItem label="总市值" value={`${(stock.market_cap / 100000000).toFixed(2)}亿`} />
                <div>
                  <div className="text-sm text-gray-500 mb-1">市值等级</div>
                  <div>
                    <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                      stock.market_cap_tier === '超大盘' 
                        ? 'bg-purple-100 text-purple-700'
                        : stock.market_cap_tier === '大盘'
                        ? 'bg-blue-100 text-blue-700'
                        : stock.market_cap_tier === '中盘'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}>
                      {stock.market_cap_tier}
                    </span>
                  </div>
                </div>
                <InfoItem label="流通股本" value={`${(stock.outstanding_shares / 100000000).toFixed(2)}亿股`} />
                <InfoItem label="上市日期" value={stock.listing_date} />
              </div>
            </div>

            {/* 风险指标卡片 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">风险指标</h2>
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-600">Beta 系数</span>
                    <span className="text-lg font-bold text-gray-900">{stock.beta.toFixed(2)}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        stock.beta > 1.2 ? 'bg-red-500' : stock.beta > 0.8 ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${Math.min(stock.beta * 50, 100)}%` }}
                    ></div>
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {stock.beta > 1.2 ? '高波动性（进攻型）' : stock.beta > 0.8 ? '中等波动性' : '低波动性（防守型）'}
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-600">波动率</span>
                    <span className="text-lg font-bold text-gray-900">{(stock.volatility * 100).toFixed(2)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        stock.volatility > 0.04 ? 'bg-red-500' : stock.volatility > 0.025 ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${Math.min(stock.volatility * 1000, 100)}%` }}
                    ></div>
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {stock.volatility > 0.04 ? '波动较大' : stock.volatility > 0.025 ? '波动适中' : '波动较小'}
                  </div>
                </div>
              </div>

              {/* Beta 系数说明 */}
              <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-3">
                <div className="text-sm text-blue-900">
                  <strong>什么是 Beta 系数？</strong>
                  <p className="mt-1 text-blue-800">
                    Beta 衡量股票相对大盘的波动性。Beta = 1 表示与大盘同步，
                    Beta &gt; 1 表示比大盘波动更大（进攻型），
                    Beta &lt; 1 表示波动较小（防守型）。
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* 右侧：所属指数 - T097 */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6 sticky top-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">所属指数</h2>
              {stock.indices && stock.indices.length > 0 ? (
                <div className="space-y-3">
                  {stock.indices.map((index) => (
                    <div
                      key={index.index_code}
                      className="border border-gray-200 rounded-lg p-4 hover:border-blue-400 hover:shadow-md transition-all"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <div className="font-semibold text-gray-900 mb-1">
                            {index.index_name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {index.index_code}
                          </div>
                        </div>
                        {index.index_code === 'HAPPY300' && (
                          <svg className="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                          </svg>
                        )}
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-500">权重</span>
                        <span className="text-sm font-semibold text-blue-600">
                          {(index.weight * 100).toFixed(2)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-1.5 mt-2">
                        <div
                          className="bg-blue-600 h-1.5 rounded-full"
                          style={{ width: `${index.weight * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <svg
                    className="w-12 h-12 mx-auto mb-3 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                  <p>未加入任何指数</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function InfoItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-sm text-gray-500 mb-1">{label}</div>
      <div className="text-lg font-semibold text-gray-900">{value}</div>
    </div>
  );
}
