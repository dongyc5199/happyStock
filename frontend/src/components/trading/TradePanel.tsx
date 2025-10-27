'use client';

import { useState, useEffect, useMemo } from 'react';
import { useTradingStore } from '@/stores/tradingStore';
import { useTrade } from '@/hooks/useTrade';
import TradeConfirmDialog from './TradeConfirmDialog';
import type { OrderSide, Asset, Account, Holding } from '@/types/trading';
import { formatCurrency } from '@/lib/utils/format';

interface TradePanelProps {
  className?: string;
}

/**
 * 交易面板组件 - 买入/卖出表单
 */
export default function TradePanel({ className = '' }: TradePanelProps) {
  const { currentAccount, selectedAsset, holdings } = useTradingStore();
  const { executeTrade, submitting, tradeError, validateForm, clearError } = useTrade();

  const [side, setSide] = useState<OrderSide>('buy');
  const [assetSymbol, setAssetSymbol] = useState('');
  const [price, setPrice] = useState('');
  const [quantity, setQuantity] = useState('');
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // 自动填充股票代码和价格
  useEffect(() => {
    if (selectedAsset) {
      setAssetSymbol(selectedAsset.symbol);
      if (selectedAsset.current_price) {
        setPrice(selectedAsset.current_price);
      }
    }
  }, [selectedAsset]);

  // 查找当前股票的持仓
  const currentHolding = useMemo(() => {
    if (!assetSymbol || !holdings) return null;
    return holdings.find((h) => h.asset_symbol === assetSymbol) || null;
  }, [assetSymbol, holdings]);

  // 计算预估金额
  const estimatedAmount = useMemo(() => {
    const p = parseFloat(price);
    const q = parseFloat(quantity);
    if (isNaN(p) || isNaN(q)) return 0;
    return p * q;
  }, [price, quantity]);

  // 切换买入/卖出
  const handleSideChange = (newSide: OrderSide) => {
    setSide(newSide);
    setErrors({});
    clearError();
    setSuccessMessage(null);
  };

  // 提交表单
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});
    clearError();
    setSuccessMessage(null);

    // 验证表单
    const validationErrors = validateForm(
      { assetSymbol, price, quantity },
      side,
      currentAccount?.current_balance,
      currentHolding?.quantity
    );

    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    // 显示确认对话框
    setShowConfirmDialog(true);
  };

  // 确认交易
  const handleConfirm = async () => {
    if (!currentAccount) return;

    try {
      await executeTrade(
        side,
        { assetSymbol, price, quantity },
        currentAccount.id
      );

      // 交易成功
      setSuccessMessage(
        `${side === 'buy' ? '买入' : '卖出'}成功！${assetSymbol} ${quantity}股`
      );
      setShowConfirmDialog(false);

      // 重置表单（保留股票代码和价格）
      setQuantity('');
      setErrors({});
      clearError();

      // 3秒后清除成功消息
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (error: any) {
      setShowConfirmDialog(false);
      // 错误已由 useTrade Hook 处理
    }
  };

  // 取消确认
  const handleCancel = () => {
    setShowConfirmDialog(false);
  };

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Tab 切换 */}
      <div className="flex border-b border-[#2a2e39]">
        <button
          onClick={() => handleSideChange('buy')}
          className={`flex-1 py-3 font-semibold transition-colors ${
            side === 'buy'
              ? 'text-green-500 border-b-2 border-green-500'
              : 'text-gray-500 hover:text-gray-300'
          }`}
        >
          买入
        </button>
        <button
          onClick={() => handleSideChange('sell')}
          className={`flex-1 py-3 font-semibold transition-colors ${
            side === 'sell'
              ? 'text-red-500 border-b-2 border-red-500'
              : 'text-gray-500 hover:text-gray-300'
          }`}
        >
          卖出
        </button>
      </div>

      {/* 表单 */}
      <form onSubmit={handleSubmit} className="flex-1 p-4 space-y-4 overflow-y-auto">
        {/* 股票代码 */}
        <div>
          <label htmlFor="assetSymbol" className="block text-sm font-medium text-gray-400 mb-2">
            股票代码
          </label>
          <input
            id="assetSymbol"
            type="text"
            value={assetSymbol}
            onChange={(e) => {
              setAssetSymbol(e.target.value.toUpperCase());
              setErrors({ ...errors, assetSymbol: '' });
            }}
            placeholder="如: 600000.SH"
            className={`w-full px-3 py-2 bg-[#0a0e14] border rounded text-white placeholder-gray-600 focus:outline-none focus:ring-2 ${
              errors.assetSymbol
                ? 'border-red-500 focus:ring-red-500'
                : 'border-[#2a2e39] focus:ring-blue-500'
            }`}
          />
          {errors.assetSymbol && (
            <p className="mt-1 text-sm text-red-500">{errors.assetSymbol}</p>
          )}
        </div>

        {/* 价格 */}
        <div>
          <label htmlFor="price" className="block text-sm font-medium text-gray-400 mb-2">
            价格
          </label>
          <input
            id="price"
            type="number"
            step="0.01"
            value={price}
            onChange={(e) => {
              setPrice(e.target.value);
              setErrors({ ...errors, price: '' });
            }}
            placeholder="0.00"
            className={`w-full px-3 py-2 bg-[#0a0e14] border rounded text-white placeholder-gray-600 focus:outline-none focus:ring-2 ${
              errors.price
                ? 'border-red-500 focus:ring-red-500'
                : 'border-[#2a2e39] focus:ring-blue-500'
            }`}
          />
          {errors.price && <p className="mt-1 text-sm text-red-500">{errors.price}</p>}
        </div>

        {/* 数量 */}
        <div>
          <label htmlFor="quantity" className="block text-sm font-medium text-gray-400 mb-2">
            数量
          </label>
          <input
            id="quantity"
            type="number"
            step="1"
            value={quantity}
            onChange={(e) => {
              setQuantity(e.target.value);
              setErrors({ ...errors, quantity: '' });
            }}
            placeholder="0"
            className={`w-full px-3 py-2 bg-[#0a0e14] border rounded text-white placeholder-gray-600 focus:outline-none focus:ring-2 ${
              errors.quantity
                ? 'border-red-500 focus:ring-red-500'
                : 'border-[#2a2e39] focus:ring-blue-500'
            }`}
          />
          {errors.quantity && <p className="mt-1 text-sm text-red-500">{errors.quantity}</p>}
        </div>

        {/* 预估金额 */}
        {estimatedAmount > 0 && (
          <div className="p-3 bg-[#0a0e14] border border-[#2a2e39] rounded">
            <div className="flex justify-between items-center">
              <span className="text-gray-400 text-sm">
                {side === 'buy' ? '需要资金' : '预计收入'}
              </span>
              <span className={`font-mono font-semibold ${side === 'buy' ? 'text-green-500' : 'text-red-500'}`}>
                {formatCurrency(estimatedAmount)}
              </span>
            </div>
          </div>
        )}

        {/* 账户信息 */}
        {currentAccount && (
          <div className="p-3 bg-[#0a0e14] border border-[#2a2e39] rounded space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">可用资金</span>
              <span className="text-white font-mono">
                {formatCurrency(currentAccount.current_balance)}
              </span>
            </div>
            {side === 'sell' && currentHolding && (
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">可用数量</span>
                <span className="text-white font-mono">{currentHolding.quantity}</span>
              </div>
            )}
          </div>
        )}

        {/* 成功消息 */}
        {successMessage && (
          <div className="p-3 bg-green-500/10 border border-green-500/30 rounded text-sm text-green-500">
            <div className="flex items-center space-x-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{successMessage}</span>
            </div>
          </div>
        )}

        {/* 错误消息 */}
        {tradeError && (
          <div className="p-3 bg-red-500/10 border border-red-500/30 rounded text-sm text-red-500">
            <div className="flex items-center space-x-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{tradeError}</span>
            </div>
          </div>
        )}

        {/* 提交按钮 */}
        <button
          type="submit"
          disabled={submitting || !currentAccount}
          className={`w-full py-3 rounded font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
            side === 'buy'
              ? 'bg-green-500 text-white hover:bg-green-600'
              : 'bg-red-500 text-white hover:bg-red-600'
          }`}
        >
          {side === 'buy' ? '确认买入' : '确认卖出'}
        </button>
      </form>

      {/* 交易确认对话框 */}
      <TradeConfirmDialog
        isOpen={showConfirmDialog}
        side={side}
        assetSymbol={assetSymbol}
        assetName={selectedAsset?.name}
        price={price}
        quantity={quantity}
        onConfirm={handleConfirm}
        onCancel={handleCancel}
        submitting={submitting}
      />
    </div>
  );
}
