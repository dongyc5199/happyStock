'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { stocksApi, sectorsApi, marketApi } from '@/lib/api/virtual-market';
import type { Stock, Sector, MarketOverview } from '@/types/virtual-market';

export default function VirtualMarketPage() {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [sectors, setSectors] = useState<Sector[]>([]);
  const [marketOverview, setMarketOverview] = useState<MarketOverview | null>(null);
  const [selectedSector, setSelectedSector] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 20;

  useEffect(() => {
    loadData();
  }, [selectedSector, page]);

  useEffect(() => {
    loadSectors();
    loadMarketOverview();
  }, []);

  async function loadData() {
    try {
      setLoading(true);
      const response = await stocksApi.getStocks({
        sector: selectedSector || undefined,
        page,
        page_size: pageSize,
      });

      if (response.success) {
        setStocks(response.data);
        setTotal(response.total || 0);
      }
    } catch (error) {
      console.error('Failed to load stocks:', error);
    } finally {
      setLoading(false);
    }
  }

  async function loadSectors() {
    try {
      const response = await sectorsApi.getSectors();
      if (response.success) {
        setSectors(response.data);
      }
    } catch (error) {
      console.error('Failed to load sectors:', error);
    }
  }

  async function loadMarketOverview() {
    try {
      const response = await marketApi.getMarketOverview();
      if (response.success) {
        setMarketOverview(response.data);
      }
    } catch (error) {
      console.error('Failed to load market overview:', error);
    }
  }

  const filteredStocks = stocks.filter(stock =>
    stock.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    stock.symbol.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">虚拟市场</h1>
          <p className="text-gray-600">A股模拟交易市场 - 实时行情数据</p>
        </div>

        {/* Market Overview */}
        {marketOverview && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-lg font-semibold mb-4">市场概览</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
              <div>
                <div className="text-sm text-gray-500">总股票数</div>
                <div className="text-xl font-semibold">{marketOverview.total_stocks}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">上涨</div>
                <div className="text-xl font-semibold text-red-600">{marketOverview.rising}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">下跌</div>
                <div className="text-xl font-semibold text-green-600">{marketOverview.falling}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">平盘</div>
                <div className="text-xl font-semibold text-gray-600">{marketOverview.unchanged}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">涨停</div>
                <div className="text-xl font-semibold text-red-600">{marketOverview.limit_up}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">跌停</div>
                <div className="text-xl font-semibold text-green-600">{marketOverview.limit_down}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">市场状态</div>
                <div className="text-xl font-semibold">{marketOverview.market_state}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">市场趋势</div>
                <div className="text-xl font-semibold">{marketOverview.market_trend.toFixed(2)}%</div>
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <input
                type="text"
                placeholder="搜索股票名称或代码..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Sector Filter */}
            <div className="w-full md:w-48">
              <select
                value={selectedSector}
                onChange={(e) => {
                  setSelectedSector(e.target.value);
                  setPage(1);
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">所有板块</option>
                {sectors.map((sector) => (
                  <option key={sector.code} value={sector.code}>
                    {sector.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Stock Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {loading ? (
            <div className="p-8 text-center text-gray-500">加载中...</div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        代码
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        名称
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        最新价
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        涨跌幅
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        涨跌额
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        成交量
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        市值(亿)
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredStocks.map((stock) => (
                      <tr key={stock.symbol} className="hover:bg-gray-50 cursor-pointer">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <Link
                            href={`/virtual-market/${stock.symbol}`}
                            className="text-blue-600 hover:text-blue-800 font-medium"
                          >
                            {stock.symbol}
                          </Link>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">{stock.name}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right">
                          <div className="text-sm font-medium">{stock.current_price.toFixed(2)}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right">
                          <div
                            className={`text-sm font-semibold ${
                              stock.change_pct > 0
                                ? 'text-red-600'
                                : stock.change_pct < 0
                                ? 'text-green-600'
                                : 'text-gray-600'
                            }`}
                          >
                            {stock.change_pct > 0 ? '+' : ''}
                            {stock.change_pct.toFixed(2)}%
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right">
                          <div
                            className={`text-sm ${
                              stock.change_value > 0
                                ? 'text-red-600'
                                : stock.change_value < 0
                                ? 'text-green-600'
                                : 'text-gray-600'
                            }`}
                          >
                            {stock.change_value > 0 ? '+' : ''}
                            {stock.change_value.toFixed(2)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">
                          {(stock.volume / 10000).toFixed(2)}万
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">
                          {stock.market_cap ? (stock.market_cap / 100000000).toFixed(2) : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <div className="bg-gray-50 px-6 py-4 flex items-center justify-between border-t border-gray-200">
                <div className="text-sm text-gray-700">
                  显示 {(page - 1) * pageSize + 1} 到 {Math.min(page * pageSize, total)} 条，共 {total} 条
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPage(Math.max(1, page - 1))}
                    disabled={page === 1}
                    className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    上一页
                  </button>
                  <span className="px-4 py-2 text-sm text-gray-700">
                    第 {page} / {totalPages} 页
                  </span>
                  <button
                    onClick={() => setPage(Math.min(totalPages, page + 1))}
                    disabled={page === totalPages}
                    className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    下一页
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
