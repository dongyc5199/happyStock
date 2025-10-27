'use client';

import { useState, useMemo } from 'react';
import type { Trade, TradeType } from '@/types/trading';
import { formatCurrency } from '@/lib/utils/format';
import { formatDateTime } from '@/lib/utils/format';

interface TradeHistoryProps {
  trades: Trade[];
  className?: string;
}

/**
 * 交易历史组件
 */
export default function TradeHistory({ trades, className = '' }: TradeHistoryProps) {
  const [filterSymbol, setFilterSymbol] = useState('');
  const [filterType, setFilterType] = useState<TradeType | 'ALL'>('ALL');

  // 筛选交易记录
  const filteredTrades = useMemo(() => {
    let filtered = [...trades];

    if (filterSymbol) {
      filtered = filtered.filter((t) =>
        t.asset_symbol.toLowerCase().includes(filterSymbol.toLowerCase())
      );
    }

    if (filterType !== 'ALL') {
      filtered = filtered.filter((t) => t.trade_type === filterType);
    }

    return filtered;
  }, [trades, filterSymbol, filterType]);

  if (trades.length === 0) {
    return (
      <div className={`flex items-center justify-center h-64 ${className}`}>
        <div className="text-center text-gray-500">
          <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <p>暂无交易记录</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`${className}`}>
      {/* 筛选器 */}
      <div className="bg-[#0a0e14] border border-[#2a2e39] rounded px-3 py-2 mb-2 flex space-x-3 items-center">
        <input
          type="text"
          value={filterSymbol}
          onChange={(e) => setFilterSymbol(e.target.value)}
          placeholder="搜索股票代码..."
          className="flex-1 px-2 py-1 text-xs bg-[#131722] border border-[#2a2e39] rounded text-white placeholder-gray-600 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value as TradeType | 'ALL')}
          className="px-2 py-1 text-xs bg-[#131722] border border-[#2a2e39] rounded text-white focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="ALL">全部类型</option>
          <option value="BUY">买入</option>
          <option value="SELL">卖出</option>
        </select>
        <div className="text-gray-400 text-xs whitespace-nowrap">
          共 {filteredTrades.length} 条
        </div>
      </div>

      {/* 交易列表 */}
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead className="bg-[#0a0e14] border-b border-[#2a2e39]">
            <tr>
              <th className="px-3 py-1.5 text-left text-gray-400 font-medium">时间</th>
              <th className="px-3 py-1.5 text-left text-gray-400 font-medium">股票</th>
              <th className="px-3 py-1.5 text-center text-gray-400 font-medium">类型</th>
              <th className="px-3 py-1.5 text-right text-gray-400 font-medium">价格</th>
              <th className="px-3 py-1.5 text-right text-gray-400 font-medium">数量</th>
              <th className="px-3 py-1.5 text-right text-gray-400 font-medium">金额</th>
            </tr>
          </thead>
          <tbody>
            {filteredTrades.map((trade) => (
              <tr
                key={trade.id}
                className="border-b border-[#2a2e39] hover:bg-[#1a1e2e] transition-colors"
              >
                <td className="px-3 py-1.5 text-gray-400">
                  {formatDateTime(trade.trade_time)}
                </td>
                <td className="px-3 py-1.5">
                  <div className="font-semibold text-white text-sm">{trade.asset_symbol}</div>
                  <div className="text-xs text-gray-500">{trade.asset_name}</div>
                </td>
                <td className="px-3 py-1.5 text-center">
                  <span
                    className={`px-1.5 py-0.5 rounded text-xs font-semibold ${
                      trade.trade_type === 'BUY'
                        ? 'bg-green-500/20 text-green-500'
                        : 'bg-red-500/20 text-red-500'
                    }`}
                  >
                    {trade.trade_type === 'BUY' ? '买入' : '卖出'}
                  </span>
                </td>
                <td className="px-3 py-1.5 text-right text-white font-mono">
                  {formatCurrency(trade.price, 2)}
                </td>
                <td className="px-3 py-1.5 text-right text-white font-mono">{trade.quantity}</td>
                <td className="px-3 py-1.5 text-right text-white font-mono font-semibold">
                  {formatCurrency(trade.total_amount)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 无筛选结果 */}
      {filteredTrades.length === 0 && trades.length > 0 && (
        <div className="text-center py-8 text-gray-500">未找到匹配的交易记录</div>
      )}
    </div>
  );
}
