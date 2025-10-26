'use client';

import type { Asset } from '@/types/trading';
import { formatCurrency, getProfitColor } from '@/lib/utils/format';

interface StockListItemProps {
  asset: Asset;
  isSelected?: boolean;
  onClick: (asset: Asset) => void;
}

/**
 * 股票列表项组件
 *
 * @param asset - 股票数据
 * @param isSelected - 是否选中
 * @param onClick - 点击回调
 */
export default function StockListItem({ asset, isSelected = false, onClick }: StockListItemProps) {
  const currentPrice = asset.current_price ? parseFloat(asset.current_price) : 0;
  // Mock 涨跌幅数据（实际应从后端获取）
  const change = currentPrice * (Math.random() * 0.1 - 0.05); // -5% to +5%
  const changePercent = currentPrice > 0 ? (change / currentPrice) * 100 : 0;

  return (
    <button
      onClick={() => onClick(asset)}
      className={`w-full px-4 py-3 text-left transition-colors border-b border-[#2a2e39] ${
        isSelected
          ? 'bg-[#2962ff]/20 border-l-4 border-l-[#2962ff]'
          : 'hover:bg-[#1a1e2e] border-l-4 border-l-transparent'
      }`}
    >
      <div className="flex items-center justify-between mb-1">
        <div className="flex-1 min-w-0">
          <div className="font-semibold text-white truncate">{asset.symbol}</div>
          <div className="text-xs text-gray-500 truncate">{asset.name}</div>
        </div>
      </div>

      {asset.current_price && (
        <div className="flex items-center justify-between mt-2">
          <span className="text-white font-mono text-sm">
            {formatCurrency(currentPrice, 2)}
          </span>
          <div className={`text-xs font-medium ${getProfitColor(change)}`}>
            {change >= 0 ? '+' : ''}
            {change.toFixed(2)} ({change >= 0 ? '+' : ''}
            {changePercent.toFixed(2)}%)
          </div>
        </div>
      )}
    </button>
  );
}
