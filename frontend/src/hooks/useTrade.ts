import { useState } from 'react';
import { useTradingStore } from '@/stores/tradingStore';
import type { Trade, OrderSide } from '@/types/trading';

interface TradeFormData {
  assetSymbol: string;
  price: string;
  quantity: string;
}

interface ValidationErrors {
  assetSymbol?: string;
  price?: string;
  quantity?: string;
}

/**
 * useTrade Hook - 封装交易操作逻辑
 *
 * @returns 交易方法和状态
 *
 * @example
 * ```tsx
 * const { executeTrade, submitting, tradeError, validateForm } = useTrade();
 *
 * const handleBuy = async () => {
 *   const errors = validateForm(formData, 'buy', accountBalance);
 *   if (Object.keys(errors).length === 0) {
 *     await executeTrade('buy', formData, accountId);
 *   }
 * };
 * ```
 */
export function useTrade() {
  const { executeBuy, executeSell, refreshData } = useTradingStore();
  const [submitting, setSubmitting] = useState(false);
  const [tradeError, setTradeError] = useState<string | null>(null);

  /**
   * 验证交易表单数据
   */
  const validateForm = (
    data: TradeFormData,
    side: OrderSide,
    accountBalance?: string,
    holdingQuantity?: string
  ): ValidationErrors => {
    const errors: ValidationErrors = {};

    // 验证股票代码
    if (!data.assetSymbol || data.assetSymbol.trim() === '') {
      errors.assetSymbol = '请输入股票代码';
    }

    // 验证价格
    const price = parseFloat(data.price);
    if (!data.price || isNaN(price) || price <= 0) {
      errors.price = '请输入有效的价格（大于0）';
    }

    // 验证数量
    const quantity = parseFloat(data.quantity);
    if (!data.quantity || isNaN(quantity) || quantity <= 0) {
      errors.quantity = '请输入有效的数量（大于0）';
    }

    // 买入时验证余额
    if (side === 'buy' && accountBalance !== undefined) {
      const totalAmount = price * quantity;
      const balance = parseFloat(accountBalance);
      if (!isNaN(totalAmount) && !isNaN(balance) && totalAmount > balance) {
        errors.quantity = `余额不足，可用资金: ${balance.toFixed(2)}`;
      }
    }

    // 卖出时验证持仓
    if (side === 'sell' && holdingQuantity !== undefined) {
      const holding = parseFloat(holdingQuantity);
      if (!isNaN(quantity) && !isNaN(holding) && quantity > holding) {
        errors.quantity = `持仓不足，可用数量: ${holding}`;
      }
    }

    return errors;
  };

  /**
   * 执行交易
   */
  const executeTrade = async (
    side: OrderSide,
    data: TradeFormData,
    accountId: number
  ): Promise<Trade | null> => {
    setSubmitting(true);
    setTradeError(null);

    try {
      let trade: Trade;

      if (side === 'buy') {
        trade = await executeBuy(
          accountId,
          data.assetSymbol,
          data.quantity,
          data.price
        );
      } else {
        trade = await executeSell(
          accountId,
          data.assetSymbol,
          data.quantity,
          data.price
        );
      }

      // 交易成功后刷新数据
      await refreshData(accountId);

      return trade;
    } catch (error: any) {
      const errorMessage = error.message || '交易失败，请稍后重试';
      setTradeError(errorMessage);
      throw error;
    } finally {
      setSubmitting(false);
    }
  };

  /**
   * 清除交易错误
   */
  const clearError = () => {
    setTradeError(null);
  };

  return {
    executeTrade,
    submitting,
    tradeError,
    validateForm,
    clearError,
  };
}
