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
      className={`w-full px-3 py-2 text-left transition-colors border-b border-[#2a2e39] ${
        isSelected
          ? 'bg-[#2962ff]/20 border-l-4 border-l-[#2962ff]'
          : 'hover:bg-[#1a1e2e] border-l-4 border-l-transparent'
      }`}
    >
      {/* 第一行：代码 + 名称 */}
      <div className="flex items-baseline gap-2 mb-1">
        <span className="font-semibold text-white text-sm">{asset.symbol}</span>
        <span className="text-xs text-gray-500 truncate flex-1">{asset.name}</span>
      </div>

      {/* 第二行：价格 + 涨跌幅 */}
      {asset.current_price && (
        <div className="flex items-center justify-between">
          <span className="text-white font-mono text-xs">
            {formatCurrency(currentPrice, 2)}
          </span>
          <div className={`text-xs font-medium ${getProfitColor(change)}`}>
            {change >= 0 ? '+' : ''}
            {changePercent.toFixed(2)}%
          </div>
        </div>
      )}
    </button>
  );
}
