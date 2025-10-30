'use client';

import { useState, useEffect } from 'react';
import { useDebounce } from '@/hooks/useDebounce';
import { useTradingStore } from '@/stores/tradingStore';
import StockListItem from './StockListItem';
import type { Asset } from '@/types/trading';

interface StockSearchProps {
  onSelectStock: (asset: Asset) => void;
  className?: string;
}

/**
 * 股票搜索组件
 */
export default function StockSearch({ onSelectStock, className = '' }: StockSearchProps) {
  const { searchAssets } = useTradingStore();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(false);

  const debouncedQuery = useDebounce(query, 300);

  // 执行搜索
  useEffect(() => {
    const performSearch = async () => {
      if (!debouncedQuery || debouncedQuery.trim() === '') {
        setResults([]);
        return;
      }

      setLoading(true);
      try {
        const searchResults = await searchAssets(debouncedQuery.trim());
        setResults(searchResults);
      } catch (error) {
        console.error('搜索失败:', error);
        setResults([]);
      } finally {
        setLoading(false);
      }
    };

    performSearch();
  }, [debouncedQuery, searchAssets]);

  // 选择股票
  const handleSelectStock = (asset: Asset) => {
    onSelectStock(asset);
    setQuery('');
    setResults([]);
  };

  return (
    <div className={`relative ${className}`}>
      {/* 搜索框 */}
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="搜索股票代码或名称..."
          className="w-full px-4 py-2 pl-10 bg-[#0a0e14] border border-[#2a2e39] rounded text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <svg
          className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
        {loading && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          </div>
        )}
      </div>

      {/* 搜索结果 */}
      {results.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-[#131722] border border-[#2a2e39] rounded shadow-lg max-h-80 overflow-y-auto z-20">
          {results.map((asset) => (
            <StockListItem key={asset.id} asset={asset} onClick={handleSelectStock} />
          ))}
        </div>
      )}

      {/* 无结果 */}
      {query && !loading && debouncedQuery && results.length === 0 && (
        <div className="absolute top-full left-0 right-0 mt-2 p-4 bg-[#131722] border border-[#2a2e39] rounded text-center text-gray-500 z-20">
          未找到匹配的股票
        </div>
      )}
    </div>
  );
}
