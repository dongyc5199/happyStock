'use client';

import { useMemo } from 'react';
import type { Holding, Asset } from '@/types/trading';
import { formatCurrency, getProfitColor } from '@/lib/utils/format';

interface HoldingsListProps {
  holdings: Holding[];
  onSelectHolding: (holding: Holding) => void;
  className?: string;
}

/**
 * 持仓列表组件
 */
export default function HoldingsList({ holdings, onSelectHolding, className = '' }: HoldingsListProps) {
  // 计算总计
  const summary = useMemo(() => {
    const totalCost = holdings.reduce((sum, h) => sum + parseFloat(h.cost), 0);
    const totalMarketValue = holdings.reduce((sum, h) => sum + parseFloat(h.market_value), 0);
    const totalProfit = totalMarketValue - totalCost;
    const totalProfitRate = totalCost > 0 ? (totalProfit / totalCost) * 100 : 0;

    return { totalCost, totalMarketValue, totalProfit, totalProfitRate };
  }, [holdings]);

  if (holdings.length === 0) {
    return (
      <div className={`flex items-center justify-center h-64 ${className}`}>
        <div className="text-center text-gray-500">
          <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
            />
          </svg>
          <p>暂无持仓</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`${className}`}>
      {/* 汇总信息 */}
      <div className="bg-[#0a0e14] border border-[#2a2e39] rounded px-3 py-2 mb-2">
        <div className="grid grid-cols-4 gap-3 text-xs">
          <div>
            <div className="text-gray-400 mb-0.5">总成本</div>
            <div className="text-white font-mono text-sm">{formatCurrency(summary.totalCost)}</div>
          </div>
          <div>
            <div className="text-gray-400 mb-0.5">总市值</div>
            <div className="text-white font-mono text-sm">{formatCurrency(summary.totalMarketValue)}</div>
          </div>
          <div>
            <div className="text-gray-400 mb-0.5">总盈亏</div>
            <div className={`font-mono font-semibold text-sm ${getProfitColor(summary.totalProfit)}`}>
              {formatCurrency(summary.totalProfit)}
            </div>
          </div>
          <div>
            <div className="text-gray-400 mb-0.5">盈亏率</div>
            <div className={`font-mono font-semibold text-sm ${getProfitColor(summary.totalProfit)}`}>
              {summary.totalProfit >= 0 ? '+' : ''}
              {summary.totalProfitRate.toFixed(2)}%
            </div>
          </div>
        </div>
      </div>

      {/* 持仓列表 */}
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead className="bg-[#0a0e14] border-b border-[#2a2e39]">
            <tr>
              <th className="px-3 py-1.5 text-left text-gray-400 font-medium">股票</th>
              <th className="px-3 py-1.5 text-right text-gray-400 font-medium">数量</th>
              <th className="px-3 py-1.5 text-right text-gray-400 font-medium">成本价</th>
              <th className="px-3 py-1.5 text-right text-gray-400 font-medium">现价</th>
              <th className="px-3 py-1.5 text-right text-gray-400 font-medium">市值</th>
              <th className="px-3 py-1.5 text-right text-gray-400 font-medium">盈亏</th>
              <th className="px-3 py-1.5 text-right text-gray-400 font-medium">盈亏率</th>
            </tr>
          </thead>
          <tbody>
            {holdings.map((holding) => {
              const profit = parseFloat(holding.profit);
              const profitRate = parseFloat(holding.profit_rate);

              return (
                <tr
                  key={holding.id}
                  onClick={() => onSelectHolding(holding)}
                  className="border-b border-[#2a2e39] hover:bg-[#1a1e2e] cursor-pointer transition-colors"
                >
                  <td className="px-3 py-1.5">
                    <div className="font-semibold text-white text-sm">{holding.asset_symbol}</div>
                    <div className="text-xs text-gray-500">{holding.asset_name}</div>
                  </td>
                  <td className="px-3 py-1.5 text-right text-white font-mono">{holding.quantity}</td>
                  <td className="px-3 py-1.5 text-right text-white font-mono">
                    {formatCurrency(holding.avg_price, 2)}
                  </td>
                  <td className="px-3 py-1.5 text-right text-white font-mono">
                    {formatCurrency(holding.current_price, 2)}
                  </td>
                  <td className="px-3 py-1.5 text-right text-white font-mono">
                    {formatCurrency(holding.market_value)}
                  </td>
                  <td className={`px-3 py-1.5 text-right font-mono font-semibold ${getProfitColor(profit)}`}>
                    {formatCurrency(profit)}
                  </td>
                  <td className={`px-3 py-1.5 text-right font-mono font-semibold ${getProfitColor(profit)}`}>
                    {profit >= 0 ? '+' : ''}
                    {profitRate.toFixed(2)}%
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
