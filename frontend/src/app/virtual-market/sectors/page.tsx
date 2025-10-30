'use client';

import { useEffect, useState } from 'react';
import { MainNav } from '@/components/layout/MainNav';

interface Sector {
  code: string;
  name: string;
  name_en: string;
  beta: number;
  description: string;
  stock_count: number;
  avg_change_pct: number;
  total_market_cap: number;
}

interface MarketState {
  state: string;
  state_name: string;
  daily_trend: number;
  description: string;
}

export default function SectorsPage() {
  const [sectors, setSectors] = useState<Sector[]>([]);
  const [marketState, setMarketState] = useState<MarketState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch sectors
      const sectorsRes = await fetch('http://localhost:8000/api/v1/sectors');
      const sectorsData = await sectorsRes.json();

      // Fetch market state
      const stateRes = await fetch('http://localhost:8000/api/v1/market/state');
      const stateData = await stateRes.json();

      if (sectorsData.success) {
        setSectors(sectorsData.data);
      }

      if (stateData.success) {
        setMarketState(stateData.data);
      }
    } catch (err) {
      setError('加载数据失败');
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

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <MainNav />
        <div className="flex items-center justify-center" style={{ minHeight: 'calc(100vh - 64px)' }}>
          <div className="text-center text-red-600">
            <p className="text-xl font-bold mb-2">⚠️ 错误</p>
            <p>{error}</p>
            <button
              onClick={fetchData}
              className="mt-4 px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              重试
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <MainNav />
      <div className="container mx-auto px-4 py-8">
        {/* 页面标题 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">板块热力图</h1>
          <p className="text-gray-600">
            观察不同行业板块的表现，理解市场联动效果
          </p>
        </div>

      {/* 市场状态卡片 */}
      {marketState && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-1">
                当前市场状态
              </h2>
              <p className="text-gray-600">{marketState.description}</p>
            </div>
            <div className="text-right">
              <div
                className={`text-2xl font-bold ${
                  marketState.state === 'BULL'
                    ? 'text-red-600'
                    : marketState.state === 'BEAR'
                    ? 'text-green-600'
                    : 'text-gray-600'
                }`}
              >
                {marketState.state_name}
              </div>
              <div className="text-sm text-gray-500">
                日均趋势: {(marketState.daily_trend * 100).toFixed(2)}%
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 板块热力图 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          板块表现 (Beta系数 × 涨跌幅)
        </h2>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {sectors.map((sector) => (
            <SectorCard key={sector.code} sector={sector} />
          ))}
        </div>

        {/* 图例 */}
        <div className="mt-8 pt-6 border-t border-gray-200">
          <div className="flex items-center justify-center gap-8 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-red-100 border border-red-300"></div>
              <span>大幅上涨 (&gt;2%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-red-50 border border-red-200"></div>
              <span>微涨 (0~2%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-gray-100 border border-gray-300"></div>
              <span>平盘 (±0.5%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-green-50 border border-green-200"></div>
              <span>微跌 (0~-2%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-green-100 border border-green-300"></div>
              <span>大幅下跌 (&lt;-2%)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Beta说明 */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">
          💡 什么是Beta系数？
        </h3>
        <p className="text-blue-800 text-sm leading-relaxed">
          Beta系数衡量板块相对大盘的波动性。Beta &gt; 1
          表示该板块比大盘波动更大（如科技、新能源），Beta &lt; 1
          表示波动较小（如公用事业、金融）。当大盘上涨1%时，高Beta板块可能涨1.3%，而低Beta板块可能只涨0.7%。
        </p>
      </div>
      </div>
    </div>
  );
}

interface SectorCardProps {
  sector: Sector;
}

function SectorCard({ sector }: SectorCardProps) {
  // 根据涨跌幅计算背景色
  const getBackgroundColor = (changePct: number) => {
    if (changePct > 2) {
      return 'bg-red-100 border-red-300 text-red-900';
    } else if (changePct > 0.5) {
      return 'bg-red-50 border-red-200 text-red-800';
    } else if (changePct >= -0.5) {
      return 'bg-gray-100 border-gray-300 text-gray-900';
    } else if (changePct >= -2) {
      return 'bg-green-50 border-green-200 text-green-800';
    } else {
      return 'bg-green-100 border-green-300 text-green-900';
    }
  };

  const colorClass = getBackgroundColor(sector.avg_change_pct || 0);
  const changePct = sector.avg_change_pct || 0;
  const changeColor = changePct >= 0 ? 'text-red-600' : 'text-green-600';

  return (
    <div
      className={`p-4 rounded-lg border-2 transition-all hover:scale-105 cursor-pointer ${colorClass}`}
    >
      <div className="text-center">
        <div className="text-lg font-bold mb-1">{sector.name}</div>
        <div className="text-xs text-gray-600 mb-2">{sector.name_en}</div>

        <div className={`text-2xl font-bold ${changeColor} mb-2`}>
          {changePct >= 0 ? '+' : ''}
          {changePct.toFixed(2)}%
        </div>

        <div className="text-xs space-y-1 text-gray-700">
          <div>Beta: {sector.beta.toFixed(2)}</div>
          <div>股票数: {sector.stock_count}</div>
          <div>
            市值: {(sector.total_market_cap / 100000000).toFixed(0)}亿
          </div>
        </div>
      </div>
    </div>
  );
}
