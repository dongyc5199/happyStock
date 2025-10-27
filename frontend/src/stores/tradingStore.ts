/**
 * 交易系统 Zustand Store
 */
import { create } from 'zustand';
import type { Account, Asset, Holding, Trade } from '@/types/trading';
import * as api from '@/lib/api/trading';

interface TradingState {
  // 状态
  currentAccount: Account | null;
  accounts: Account[];
  holdings: Holding[];
  selectedAsset: Asset | null;
  recentTrades: Trade[];
  assets: Asset[];
  loading: boolean;
  error: string | null;

  // Actions
  setCurrentAccount: (account: Account | null) => void;
  setSelectedAsset: (asset: Asset | null) => void;
  setError: (error: string | null) => void;

  // 异步操作
  fetchAccount: (accountId: number) => Promise<void>;
  fetchHoldings: (accountId: number) => Promise<void>;
  fetchTradeHistory: (accountId: number, page?: number, pageSize?: number) => Promise<void>;
  fetchAssets: (page?: number, pageSize?: number) => Promise<void>;
  searchAssets: (keyword: string) => Promise<Asset[]>;

  // 交易操作
  executeBuy: (accountId: number, assetSymbol: string, quantity: string, price: string) => Promise<Trade>;
  executeSell: (accountId: number, assetSymbol: string, quantity: string, price: string) => Promise<Trade>;

  // 刷新数据
  refreshData: (accountId: number) => Promise<void>;
}

export const useTradingStore = create<TradingState>((set, get) => ({
  // 初始状态
  currentAccount: null,
  accounts: [],
  holdings: [],
  selectedAsset: null,
  recentTrades: [],
  assets: [],
  loading: false,
  error: null,

  // Setters
  setCurrentAccount: (account) => set({ currentAccount: account }),
  setSelectedAsset: (asset) => set({ selectedAsset: asset }),
  setError: (error) => set({ error }),

  // 获取账户信息
  fetchAccount: async (accountId: number) => {
    set({ loading: true, error: null });
    try {
      const account = await api.getAccount(accountId);
      set({ currentAccount: account, loading: false });
    } catch (error: any) {
      set({ error: error.message || '获取账户信息失败', loading: false });
      throw error;
    }
  },

  // 获取持仓列表
  fetchHoldings: async (accountId: number) => {
    set({ loading: true, error: null });
    try {
      const data = await api.getHoldings(accountId);
      set({ holdings: data.holdings, loading: false });
    } catch (error: any) {
      set({ error: error.message || '获取持仓列表失败', loading: false });
      throw error;
    }
  },

  // 获取交易历史
  fetchTradeHistory: async (accountId: number, page = 1, pageSize = 20) => {
    set({ loading: true, error: null });
    try {
      const data = await api.getTradeHistory({ account_id: accountId, page, page_size: pageSize });
      set({ recentTrades: data.trades, loading: false });
    } catch (error: any) {
      set({ error: error.message || '获取交易历史失败', loading: false });
      throw error;
    }
  },

  // 获取资产列表
  fetchAssets: async (page = 1, pageSize = 50) => {
    set({ loading: true, error: null });
    try {
      const data = await api.getAssets({ page, page_size: pageSize });
      set({ assets: data.assets, loading: false });
    } catch (error: any) {
      set({ error: error.message || '获取资产列表失败', loading: false });
      throw error;
    }
  },

  // 搜索资产
  searchAssets: async (keyword: string) => {
    try {
      const assets = await api.searchAssets(keyword);
      return assets;
    } catch (error: any) {
      set({ error: error.message || '搜索资产失败' });
      throw error;
    }
  },

  // 买入操作
  executeBuy: async (accountId: number, assetSymbol: string, quantity: string, price: string) => {
    set({ loading: true, error: null });
    try {
      const trade = await api.buyAsset({
        account_id: accountId,
        asset_symbol: assetSymbol,
        quantity,
        price,
      });

      // 买入成功后刷新数据
      await get().refreshData(accountId);

      set({ loading: false });
      return trade;
    } catch (error: any) {
      set({ error: error.message || '买入失败', loading: false });
      throw error;
    }
  },

  // 卖出操作
  executeSell: async (accountId: number, assetSymbol: string, quantity: string, price: string) => {
    set({ loading: true, error: null });
    try {
      const trade = await api.sellAsset({
        account_id: accountId,
        asset_symbol: assetSymbol,
        quantity,
        price,
      });

      // 卖出成功后刷新数据
      await get().refreshData(accountId);

      set({ loading: false });
      return trade;
    } catch (error: any) {
      set({ error: error.message || '卖出失败', loading: false });
      throw error;
    }
  },

  // 刷新所有数据
  refreshData: async (accountId: number) => {
    try {
      await Promise.all([
        get().fetchAccount(accountId),
        get().fetchHoldings(accountId),
        get().fetchTradeHistory(accountId, 1, 10),
      ]);
    } catch (error: any) {
      console.error('刷新数据失败:', error);
    }
  },
}));
