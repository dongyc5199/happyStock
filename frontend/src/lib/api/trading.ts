/**
 * 交易相关 API 封装
 */
import apiClient from './client';
import type {
  ApiResponse,
  Account,
  AccountSummary,
  Asset,
  Trade,
  BuyTradeRequest,
  SellTradeRequest,
  TradeHistoryParams,
  Holding,
  HoldingsSummary,
  AssetAllocation,
  KlineResponse,
  KlineData,
} from '@/types/trading';

// ============ 账户相关 API ============

/**
 * 获取账户信息
 */
export async function getAccount(accountId: number): Promise<Account> {
  const response: ApiResponse<Account> = await apiClient.get(`/api/v1/accounts/${accountId}`);
  if (!response.success || !response.data) {
    throw new Error('获取账户信息失败');
  }
  return response.data;
}

/**
 * 获取用户所有账户
 */
export async function getUserAccounts(userId: number): Promise<Account[]> {
  const response: ApiResponse<Account[]> = await apiClient.get(`/api/v1/accounts/user/${userId}`);
  if (!response.success || !response.data) {
    throw new Error('获取账户列表失败');
  }
  return response.data;
}

/**
 * 创建账户
 */
export async function createAccount(data: {
  user_id: number;
  account_name: string;
  initial_balance?: string;
}): Promise<Account> {
  const response: ApiResponse<Account> = await apiClient.post('/api/v1/accounts', data);
  if (!response.success || !response.data) {
    throw new Error('创建账户失败');
  }
  return response.data;
}

/**
 * 重置账户
 */
export async function resetAccount(accountId: number): Promise<Account> {
  const response: ApiResponse<Account> = await apiClient.put(`/api/v1/accounts/${accountId}/reset`);
  if (!response.success || !response.data) {
    throw new Error('重置账户失败');
  }
  return response.data;
}

// ============ 资产相关 API ============

/**
 * 获取资产列表
 */
export async function getAssets(params?: {
  asset_type?: string;
  page?: number;
  page_size?: number;
}): Promise<{ assets: Asset[]; total: number }> {
  const response: ApiResponse<{ assets: Asset[]; total: number }> = await apiClient.get('/api/v1/assets', { params });
  if (!response.success || !response.data) {
    throw new Error('获取资产列表失败');
  }
  return response.data;
}

/**
 * 搜索资产
 */
export async function searchAssets(keyword: string, pageSize: number = 20): Promise<Asset[]> {
  const response: ApiResponse<{ assets: Asset[]; total: number }> = await apiClient.get('/api/v1/assets/search', {
    params: { keyword, page_size: pageSize },
  });
  if (!response.success || !response.data) {
    throw new Error('搜索资产失败');
  }
  return response.data.assets;
}

/**
 * 根据代码获取资产
 */
export async function getAssetBySymbol(symbol: string): Promise<Asset> {
  const response: ApiResponse<Asset> = await apiClient.get(`/api/v1/assets/${symbol}`);
  if (!response.success || !response.data) {
    throw new Error('获取资产信息失败');
  }
  return response.data;
}

/**
 * 获取资产价格
 */
export async function getAssetPrice(symbol: string): Promise<string> {
  const response: ApiResponse<{ price: string }> = await apiClient.get(`/api/v1/assets/${symbol}/price`);
  if (!response.success || !response.data) {
    throw new Error('获取资产价格失败');
  }
  return response.data.price;
}

// ============ 交易相关 API ============

/**
 * 买入资产
 */
export async function buyAsset(data: BuyTradeRequest): Promise<Trade> {
  const response: ApiResponse<Trade> = await apiClient.post('/api/v1/trades/buy', data);
  if (!response.success || !response.data) {
    throw new Error('买入失败');
  }
  return response.data;
}

/**
 * 卖出资产
 */
export async function sellAsset(data: SellTradeRequest): Promise<Trade> {
  const response: ApiResponse<Trade> = await apiClient.post('/api/v1/trades/sell', data);
  if (!response.success || !response.data) {
    throw new Error('卖出失败');
  }
  return response.data;
}

/**
 * 获取交易历史
 */
export async function getTradeHistory(
  params: TradeHistoryParams
): Promise<{ trades: Trade[]; total: number; page: number; page_size: number }> {
  const response: ApiResponse<{ trades: Trade[]; total: number; page: number; page_size: number }> =
    await apiClient.get('/api/v1/trades/history', { params });
  if (!response.success || !response.data) {
    throw new Error('获取交易历史失败');
  }
  return response.data;
}

// ============ 持仓相关 API ============

/**
 * 获取持仓列表
 */
export async function getHoldings(
  accountId: number
): Promise<{ holdings: Holding[]; summary: HoldingsSummary }> {
  const response: ApiResponse<{ holdings: Holding[]; summary: HoldingsSummary }> = await apiClient.get(
    `/api/v1/holdings/${accountId}`
  );
  if (!response.success || !response.data) {
    throw new Error('获取持仓列表失败');
  }
  return response.data;
}

/**
 * 获取持仓汇总
 */
export async function getHoldingsSummary(accountId: number): Promise<{
  account_balance: string;
  total_market_value: string;
  total_assets: string;
  total_cost: string;
  total_profit: string;
  total_profit_rate: string;
  holdings_count: number;
  asset_allocation: AssetAllocation[];
}> {
  const response: ApiResponse<{
    account_balance: string;
    total_market_value: string;
    total_assets: string;
    total_cost: string;
    total_profit: string;
    total_profit_rate: string;
    holdings_count: number;
    asset_allocation: AssetAllocation[];
  }> = await apiClient.get(`/api/v1/holdings/${accountId}/summary`);
  if (!response.success || !response.data) {
    throw new Error('获取持仓汇总失败');
  }
  return response.data;
}

// ============ K线数据相关 API ============

/**
 * 获取K线数据
 */
export async function getKlineData(
  symbol: string,
  interval: '1d' | '1w' | '1M' = '1d',
  limit: number = 90
): Promise<KlineResponse> {
  const response: ApiResponse<KlineResponse> = await apiClient.get(
    `/api/v1/klines/${symbol}`,
    { params: { interval, limit } }
  );
  if (!response.success || !response.data) {
    throw new Error('获取K线数据失败');
  }
  return response.data;
}
