'use client';

import { useEffect, useState, useMemo } from 'react';
import Link from 'next/link';
import { MainNav } from '@/components/layout/MainNav';
import { sectorsApi } from '@/lib/api/virtual-market';
import type { Sector } from '@/types/virtual-market';
import { useWebSocketContext } from '@/contexts/WebSocketContext';

export default function VirtualMarketPage() {
  // WebSocket 实时数据
  const { marketData, isConnected, error: wsError, currentThrottle } = useWebSocketContext();
  
  // 本地状态
  const [sectors, setSectors] = useState<Sector[]>([]);
  const [selectedSector, setSelectedSector] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [lastUpdateTime, setLastUpdateTime] = useState<Date>(new Date());
  const pageSize = 20;

  // 从 WebSocket 数据中获取股票列表 (实时更新)
  const allStocks = useMemo(() => {
    if (!marketData?.stocks) return [];
    return marketData.stocks;
  }, [marketData]);

  // 过滤和分页逻辑
  const filteredStocks = useMemo(() => {
    let result = allStocks;

    // 板块筛选
    if (selectedSector) {
      result = result.filter(stock => stock.sector === selectedSector);
    }

    // 搜索筛选
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      result = result.filter(stock =>
        stock.name.toLowerCase().includes(term) ||
        stock.symbol.toLowerCase().includes(term)
      );
    }

    return result;
  }, [allStocks, selectedSector, searchTerm]);

  // 分页数据
  const paginatedStocks = useMemo(() => {
    const start = (page - 1) * pageSize;
    const end = start + pageSize;
    return filteredStocks.slice(start, end);
  }, [filteredStocks, page, pageSize]);

  const totalPages = Math.ceil(filteredStocks.length / pageSize);

  // 计算市场概览 (从 WebSocket 数据实时计算)
  const marketOverview = useMemo(() => {
    if (!allStocks.length) return null;

    const overview = {
      total_stocks: allStocks.length,
      rising: allStocks.filter(s => s.change_pct > 0).length,
      falling: allStocks.filter(s => s.change_pct < 0).length,
      unchanged: allStocks.filter(s => s.change_pct === 0).length,
      limit_up: allStocks.filter(s => s.change_pct >= 9.9).length,
      limit_down: allStocks.filter(s => s.change_pct <= -9.9).length,
      market_state: isConnected ? '交易中' : '连接中...',
      market_trend: allStocks.reduce((sum, s) => sum + s.change_pct, 0) / allStocks.length,
    };

    return overview;
  }, [allStocks, isConnected]);

  // WebSocket 数据更新时触发
  useEffect(() => {
    if (marketData) {
      setLastUpdateTime(new Date());
      setLoading(false);
    }
  }, [marketData]);

  // 初始化加载板块数据
  useEffect(() => {
    loadSectors();
  }, []);

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

  // 连接状态显示
  const connectionStatus = useMemo(() => {
    if (wsError) return { text: '连接错误', color: 'text-red-600' };
    if (!isConnected) return { text: '连接中...', color: 'text-yellow-600' };
    return { text: '实时推送中', color: 'text-green-600' };
  }, [isConnected, wsError]);

  // 推送频率显示
  const throttleDisplay = useMemo(() => {
    if (currentThrottle >= 60000) return '60秒';
    if (currentThrottle >= 10000) return '10秒';
    if (currentThrottle >= 3000) return '3秒';
    return '1秒';
  }, [currentThrottle]);

  return (
    <div className="min-h-screen bg-gray-50">
      <MainNav />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">虚拟市场</h1>
              <p className="text-gray-600">A股模拟交易市场 - WebSocket实时行情</p>
            </div>
            <div className="text-right">
              <div className={`flex items-center gap-2 text-sm ${connectionStatus.color} mb-1`}>
                <div className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-yellow-500'}`}></div>
                <span>{connectionStatus.text}</span>
              </div>
              <div className="text-sm text-gray-500">
                最后更新: {lastUpdateTime.toLocaleTimeString('zh-CN')}
              </div>
              <div className="text-xs text-gray-400 mt-1">
                推送频率: {throttleDisplay} (自动调整)
              </div>
            </div>
          </div>
        </div>

        {/* Market Overview */}
        {marketOverview && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-lg font-semibold mb-4">市场概览 (实时)</h2>
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
                <div className={`text-xl font-semibold ${marketOverview.market_trend > 0 ? 'text-red-600' : marketOverview.market_trend < 0 ? 'text-green-600' : 'text-gray-600'}`}>
                  {marketOverview.market_trend.toFixed(2)}%
                </div>
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
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setPage(1); // 重置页码
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Sector Filter */}
            <div className="w-full md:w-48">
              <select
                value={selectedSector}
                onChange={(e) => {
                  setSelectedSector(e.target.value);
                  setPage(1); // 重置页码
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
            <div className="p-8 text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-2 text-gray-500">正在连接 WebSocket...</p>
            </div>
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
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        板块
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {paginatedStocks.map((stock) => (
                      <tr key={stock.symbol} className="hover:bg-gray-50 cursor-pointer transition-colors">
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
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {stock.sector || '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <div className="bg-gray-50 px-6 py-4 flex items-center justify-between border-t border-gray-200">
                <div className="text-sm text-gray-700">
                  显示 {(page - 1) * pageSize + 1} 到 {Math.min(page * pageSize, filteredStocks.length)} 条，共 {filteredStocks.length} 条
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPage(Math.max(1, page - 1))}
                    disabled={page === 1}
                    className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    上一页
                  </button>
                  <span className="px-4 py-2 text-sm text-gray-700">
                    第 {page} / {totalPages} 页
                  </span>
                  <button
                    onClick={() => setPage(Math.min(totalPages, page + 1))}
                    disabled={page === totalPages}
                    className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
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
