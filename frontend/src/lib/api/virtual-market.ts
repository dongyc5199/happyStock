/**
 * Virtual Market API Client
 * 虚拟市场API客户端
 */

import type {
  Stock,
  StockDetail,
  KlineData,
  Index,
  Sector,
  MarketState,
  MarketOverview,
  ApiResponse,
} from '@/types/virtual-market';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Fetch wrapper with error handling
 */
async function apiFetch<T>(endpoint: string): Promise<ApiResponse<T>> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`);

  if (!response.ok) {
    throw new Error(`API request failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Stock APIs
 */
export const stocksApi = {
  /**
   * Get stock list
   */
  async getStocks(params?: {
    sector?: string;
    page?: number;
    page_size?: number;
  }): Promise<ApiResponse<Stock[]>> {
    const queryParams = new URLSearchParams();
    if (params?.sector) queryParams.append('sector', params.sector);
    if (params?.page) queryParams.append('page', String(params.page));
    if (params?.page_size) queryParams.append('page_size', String(params.page_size));

    const query = queryParams.toString();
    return apiFetch<Stock[]>(`/api/v1/stocks${query ? `?${query}` : ''}`);
  },

  /**
   * Get stock detail
   */
  async getStockDetail(symbol: string): Promise<ApiResponse<StockDetail>> {
    return apiFetch<StockDetail>(`/api/v1/stocks/${symbol}`);
  },

  /**
   * Get stock K-line data
   */
  async getStockKlines(
    symbol: string,
    params?: { period?: string; limit?: number }
  ): Promise<ApiResponse<KlineData[]>> {
    const queryParams = new URLSearchParams();
    if (params?.period) queryParams.append('period', params.period);
    if (params?.limit) queryParams.append('limit', String(params.limit));

    const query = queryParams.toString();
    return apiFetch<KlineData[]>(
      `/api/v1/stocks/${symbol}/klines${query ? `?${query}` : ''}`
    );
  },

  /**
   * Get stock metadata
   */
  async getStockMetadata(symbol: string): Promise<ApiResponse<any>> {
    return apiFetch(`/api/v1/stocks/${symbol}/metadata`);
  },
};

/**
 * Index APIs
 */
export const indicesApi = {
  /**
   * Get index list
   */
  async getIndices(indexType?: string): Promise<ApiResponse<Index[]>> {
    const query = indexType ? `?index_type=${indexType}` : '';
    return apiFetch<Index[]>(`/api/v1/indices${query}`);
  },

  /**
   * Get index detail
   */
  async getIndexDetail(code: string): Promise<ApiResponse<any>> {
    return apiFetch(`/api/v1/indices/${code}`);
  },

  /**
   * Get index K-line data
   */
  async getIndexKlines(
    code: string,
    params?: { period?: string; limit?: number }
  ): Promise<ApiResponse<KlineData[]>> {
    const queryParams = new URLSearchParams();
    if (params?.period) queryParams.append('period', params.period);
    if (params?.limit) queryParams.append('limit', String(params.limit));

    const query = queryParams.toString();
    return apiFetch<KlineData[]>(
      `/api/v1/indices/${code}/klines${query ? `?${query}` : ''}`
    );
  },
};

/**
 * Sector APIs
 */
export const sectorsApi = {
  /**
   * Get sector list
   */
  async getSectors(): Promise<ApiResponse<Sector[]>> {
    return apiFetch<Sector[]>('/api/v1/sectors');
  },

  /**
   * Get sector detail
   */
  async getSectorDetail(code: string): Promise<ApiResponse<any>> {
    return apiFetch(`/api/v1/sectors/${code}`);
  },
};

/**
 * Market APIs
 */
export const marketApi = {
  /**
   * Get current market state
   */
  async getMarketState(): Promise<ApiResponse<MarketState>> {
    return apiFetch<MarketState>('/api/v1/market/state');
  },

  /**
   * Get market history
   */
  async getMarketHistory(limit?: number): Promise<ApiResponse<MarketState[]>> {
    const query = limit ? `?limit=${limit}` : '';
    return apiFetch<MarketState[]>(`/api/v1/market/history${query}`);
  },

  /**
   * Get market overview
   */
  async getMarketOverview(): Promise<ApiResponse<MarketOverview>> {
    return apiFetch<MarketOverview>('/api/v1/market/overview');
  },
};
