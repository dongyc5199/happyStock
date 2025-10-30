'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { MainNav } from '@/components/layout/MainNav';

interface Stock {
  symbol: string;
  name: string;
  current_price: number;
  previous_close: number;
  change_value: number;
  change_pct: number;
  market_cap: number;
  market_cap_tier: string;
  beta: number;
  volume: number;
}

interface SectorDetail {
  code: string;
  name: string;
  name_en: string;
  beta: number;
  description: string;
  stock_count: number;
  stocks: Stock[];
}

export default function SectorDetailPage() {
  const params = useParams();
  const code = params?.code as string;

  const [sector, setSector] = useState<SectorDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<'market_cap' | 'change_pct' | 'beta'>('market_cap');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  useEffect(() => {
    if (code) {
      fetchSectorDetail();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [code]);

  const fetchSectorDetail = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`http://localhost:8000/api/v1/sectors/${code}`);
      const data = await response.json();

      if (data.success && data.data) {
        setSector(data.data);
      } else {
        setError(data.error?.message || '板块不存在');
      }
    } catch (err) {
      setError('加载失败');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (field: 'market_cap' | 'change_pct' | 'beta') => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const getSortedStocks = () => {
    if (!sector?.stocks) return [];

    const sorted = [...sector.stocks].sort((a, b) => {
      let aValue = a[sortBy];
      let bValue = b[sortBy];

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    return sorted;
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

  if (error || !sector) {
    return (
      <div className="min-h-screen bg-gray-50">
        <MainNav />
        <div className="flex items-center justify-center" style={{ minHeight: 'calc(100vh - 64px)' }}>
          <div className="text-center text-red-600">
            <p className="text-xl font-bold mb-2">⚠️ {error || '板块不存在'}</p>
            <Link href="/virtual-market/sectors" className="text-blue-600 hover:underline">
              返回板块列表
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // 计算板块统计数据
  const totalMarketCap = sector.stocks.reduce((sum, stock) => sum + (stock.market_cap || 0), 0);
  const avgChangePct = sector.stocks.length > 0
    ? sector.stocks.reduce((sum, stock) => sum + stock.change_pct, 0) / sector.stocks.length
    : 0;
  const avgBeta = sector.stocks.length > 0
    ? sector.stocks.reduce((sum, stock) => sum + stock.beta, 0) / sector.stocks.length
    : 0;

  const sortedStocks = getSortedStocks();

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
                <Link href="/virtual-market/sectors" className="text-gray-500 hover:text-gray-700">
                  板块分析
                </Link>
              </li>
              <li><span className="text-gray-400">/</span></li>
              <li>
                <span className="text-gray-900 font-medium">{sector.name}</span>
              </li>
            </ol>
          </nav>
        </div>

        {/* 板块头部信息 */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {sector.name}
                <span className="text-xl text-gray-500 ml-3">({sector.name_en})</span>
              </h1>
              <p className="text-gray-600">{sector.description}</p>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-500 mb-1">板块代码</div>
              <div className="text-2xl font-bold text-gray-900">{sector.code}</div>
            </div>
          </div>
        </div>

        {/* 板块统计信息 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-500 mb-1">股票数量</div>
            <div className="text-3xl font-bold text-gray-900">{sector.stock_count}</div>
            <div className="text-xs text-gray-400 mt-1">个股票</div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-500 mb-1">总市值</div>
            <div className="text-3xl font-bold text-gray-900">
              {(totalMarketCap / 100000000).toFixed(0)}
            </div>
            <div className="text-xs text-gray-400 mt-1">亿元</div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-500 mb-1">平均涨跌幅</div>
            <div className={`text-3xl font-bold ${
              avgChangePct > 0 ? 'text-red-600' : avgChangePct < 0 ? 'text-green-600' : 'text-gray-600'
            }`}>
              {avgChangePct > 0 ? '+' : ''}{avgChangePct.toFixed(2)}%
            </div>
            <div className="text-xs text-gray-400 mt-1">板块整体表现</div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-500 mb-1">平均 Beta</div>
            <div className="text-3xl font-bold text-gray-900">{avgBeta.toFixed(2)}</div>
            <div className="text-xs text-gray-400 mt-1">
              {avgBeta > 1.2 ? '高波动板块' : avgBeta > 0.8 ? '中等波动' : '低波动板块'}
            </div>
          </div>
        </div>

        {/* 板块成分股列表 - T099 */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900">板块成分股</h2>
            <p className="text-sm text-gray-500 mt-1">共 {sector.stock_count} 只股票</p>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    股票代码
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    股票名称
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    最新价
                  </th>
                  <th
                    className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('change_pct')}
                  >
                    涨跌幅 {sortBy === 'change_pct' && (sortOrder === 'desc' ? '↓' : '↑')}
                  </th>
                  <th
                    className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('market_cap')}
                  >
                    市值 {sortBy === 'market_cap' && (sortOrder === 'desc' ? '↓' : '↑')}
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    等级
                  </th>
                  <th
                    className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('beta')}
                  >
                    Beta {sortBy === 'beta' && (sortOrder === 'desc' ? '↓' : '↑')}
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {sortedStocks.map((stock) => (
                  <tr key={stock.symbol} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Link
                        href={`/virtual-market/stocks/${stock.symbol}`}
                        className="text-blue-600 hover:text-blue-800 font-medium"
                      >
                        {stock.symbol}
                      </Link>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{stock.name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <div className="text-sm text-gray-900">¥{stock.current_price.toFixed(2)}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <div className={`text-sm font-semibold ${
                        stock.change_pct > 0 ? 'text-red-600' : stock.change_pct < 0 ? 'text-green-600' : 'text-gray-600'
                      }`}>
                        {stock.change_pct > 0 ? '+' : ''}{stock.change_pct.toFixed(2)}%
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <div className="text-sm text-gray-900">
                        {(stock.market_cap / 100000000).toFixed(2)}亿
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
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
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <div className="text-sm text-gray-900">{stock.beta.toFixed(2)}</div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Beta 说明 */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">
            💡 关于板块 Beta 系数
          </h3>
          <div className="text-blue-800 text-sm leading-relaxed space-y-2">
            <p>
              <strong>当前板块平均 Beta: {avgBeta.toFixed(2)}</strong>
            </p>
            <p>
              板块 Beta 系数表示该板块整体相对大盘的波动性。
              {avgBeta > 1.2 && '该板块属于高波动板块，在牛市中涨幅较大，但在熊市中跌幅也较深。'}
              {avgBeta >= 0.8 && avgBeta <= 1.2 && '该板块波动性适中，与大盘整体走势基本同步。'}
              {avgBeta < 0.8 && '该板块属于防守型板块，波动相对较小，适合稳健型投资者。'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
