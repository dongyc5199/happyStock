'use client';

import { useEffect, useState } from 'react';
import { stocksApi, sectorsApi } from '@/lib/api/virtual-market';
import type { Stock, Sector } from '@/types/virtual-market';

interface VirtualMarketStockListProps {
  onSelectStock?: (stock: Stock) => void;
  selectedSymbol?: string;
}

export default function VirtualMarketStockList({
  onSelectStock,
  selectedSymbol,
}: VirtualMarketStockListProps) {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [sectors, setSectors] = useState<Sector[]>([]);
  const [selectedSector, setSelectedSector] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [selectedSector]);

  useEffect(() => {
    loadSectors();
  }, []);

  async function loadData() {
    try {
      setLoading(true);
      const response = await stocksApi.getStocks({
        sector: selectedSector || undefined,
        page: 1,
        page_size: 100,
      });

      if (response.success) {
        setStocks(response.data);
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

  const filteredStocks = stocks.filter(
    (stock) =>
      stock.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      stock.symbol.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex flex-col h-full">
      {/* 搜索框 */}
      <div className="p-3 border-b border-[#2a2e39]">
        <input
          type="text"
          placeholder="搜索股票..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-3 py-2 text-sm bg-[#1e2532] border border-[#2a2e39] text-white rounded focus:ring-1 focus:ring-blue-500 focus:border-blue-500 placeholder-gray-500"
        />
      </div>

      {/* 板块筛选 */}
      <div className="p-3 border-b border-[#2a2e39]">
        <select
          value={selectedSector}
          onChange={(e) => setSelectedSector(e.target.value)}
          className="w-full px-3 py-2 text-sm bg-[#1e2532] border border-[#2a2e39] text-white rounded focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">所有板块</option>
          {sectors.map((sector) => (
            <option key={sector.code} value={sector.code}>
              {sector.name}
            </option>
          ))}
        </select>
      </div>

      {/* 股票列表 */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="p-4 text-center text-sm text-gray-500">加载中...</div>
        ) : filteredStocks.length === 0 ? (
          <div className="p-4 text-center text-sm text-gray-500">暂无数据</div>
        ) : (
          <div className="divide-y divide-[#2a2e39]">
            {filteredStocks.map((stock) => {
              const isSelected = stock.symbol === selectedSymbol;
              const changePctColor =
                stock.change_pct > 0
                  ? 'text-red-500'
                  : stock.change_pct < 0
                  ? 'text-green-500'
                  : 'text-gray-400';

              return (
                <button
                  key={stock.symbol}
                  onClick={() => onSelectStock?.(stock)}
                  className={`w-full p-3 text-left hover:bg-[#1e2532] transition-colors ${
                    isSelected ? 'bg-[#1e2532] border-l-2 border-blue-500' : ''
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-sm text-white">{stock.symbol}</span>
                      <span className="text-xs text-gray-400">{stock.name}</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold text-white">{stock.current_price.toFixed(2)}</span>
                    <span className={`text-xs font-medium ${changePctColor}`}>
                      {stock.change_pct > 0 ? '+' : ''}
                      {stock.change_pct.toFixed(2)}%
                    </span>
                  </div>
                  {stock.market_cap && (
                    <div className="text-xs text-gray-500 mt-1">
                      市值: {(stock.market_cap / 100000000).toFixed(0)}亿
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
