'use client';

import { useEffect } from 'react';
import type { OrderSide } from '@/types/trading';
import { formatCurrency } from '@/lib/utils/format';

interface TradeConfirmDialogProps {
  isOpen: boolean;
  side: OrderSide;
  assetSymbol: string;
  assetName?: string;
  price: string;
  quantity: string;
  onConfirm: () => void;
  onCancel: () => void;
  submitting?: boolean;
}

/**
 * 交易确认对话框组件
 *
 * @param isOpen - 是否显示对话框
 * @param side - 交易方向（buy/sell）
 * @param assetSymbol - 股票代码
 * @param assetName - 股票名称
 * @param price - 价格
 * @param quantity - 数量
 * @param onConfirm - 确认回调
 * @param onCancel - 取消回调
 * @param submitting - 是否提交中
 */
export default function TradeConfirmDialog({
  isOpen,
  side,
  assetSymbol,
  assetName,
  price,
  quantity,
  onConfirm,
  onCancel,
  submitting = false,
}: TradeConfirmDialogProps) {
  // 计算总金额
  const totalAmount = parseFloat(price) * parseFloat(quantity);
  const isBuy = side === 'buy';

  // ESC 键关闭对话框
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen && !submitting) {
        onCancel();
      }
      if (e.key === 'Enter' && isOpen && !submitting) {
        onConfirm();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onCancel, onConfirm, submitting]);

  // 防止背景滚动
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* 背景遮罩 */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={submitting ? undefined : onCancel}
      />

      {/* 对话框内容 */}
      <div
        className="relative bg-[#131722] rounded-lg shadow-2xl w-full max-w-md mx-4 border border-[#2a2e39]"
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
      >
        {/* 头部 */}
        <div className={`px-6 py-4 border-b border-[#2a2e39] ${isBuy ? 'bg-green-500/10' : 'bg-red-500/10'}`}>
          <h3
            id="dialog-title"
            className={`text-lg font-semibold ${isBuy ? 'text-green-500' : 'text-red-500'}`}
          >
            {isBuy ? '确认买入' : '确认卖出'}
          </h3>
        </div>

        {/* 内容 */}
        <div className="px-6 py-6 space-y-4">
          {/* 股票信息 */}
          <div className="flex justify-between items-center">
            <span className="text-gray-400">股票</span>
            <div className="text-right">
              <div className="text-white font-semibold">{assetSymbol}</div>
              {assetName && <div className="text-sm text-gray-500">{assetName}</div>}
            </div>
          </div>

          {/* 价格 */}
          <div className="flex justify-between items-center">
            <span className="text-gray-400">价格</span>
            <span className="text-white font-mono">{formatCurrency(price)}</span>
          </div>

          {/* 数量 */}
          <div className="flex justify-between items-center">
            <span className="text-gray-400">数量</span>
            <span className="text-white font-mono">{quantity}</span>
          </div>

          {/* 分隔线 */}
          <div className="border-t border-[#2a2e39] my-4"></div>

          {/* 总金额 */}
          <div className="flex justify-between items-center">
            <span className="text-gray-400 font-semibold">
              {isBuy ? '需要资金' : '预计收入'}
            </span>
            <span className={`text-xl font-bold font-mono ${isBuy ? 'text-green-500' : 'text-red-500'}`}>
              {formatCurrency(totalAmount)}
            </span>
          </div>

          {/* 提示信息 */}
          <div className="mt-4 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded text-sm text-yellow-500">
            <div className="flex items-start space-x-2">
              <svg className="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>
                {isBuy
                  ? '请确认交易信息，买入后将扣除账户资金。'
                  : '请确认交易信息，卖出后将增加账户资金。'}
              </span>
            </div>
          </div>
        </div>

        {/* 底部按钮 */}
        <div className="px-6 py-4 bg-[#0a0e14] border-t border-[#2a2e39] flex space-x-3">
          <button
            onClick={onCancel}
            disabled={submitting}
            className="flex-1 px-4 py-2 bg-[#2a2e39] text-white rounded hover:bg-[#363a45] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            取消
          </button>
          <button
            onClick={onConfirm}
            disabled={submitting}
            className={`flex-1 px-4 py-2 rounded font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
              isBuy
                ? 'bg-green-500 text-white hover:bg-green-600'
                : 'bg-red-500 text-white hover:bg-red-600'
            }`}
          >
            {submitting ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                提交中...
              </span>
            ) : (
              `确认${isBuy ? '买入' : '卖出'}`
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
