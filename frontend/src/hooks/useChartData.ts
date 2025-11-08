/**
 * 图表数据加载 Hook
 *
 * 用于动态加载K线数据，支持：
 * - 滑动加载历史和最新数据
 * - IndexedDB 缓存
 * - LRU 淘汰策略
 * - 防抖优化
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { IChartApi, CandlestickData } from 'lightweight-charts';
import { getKlineData } from '@/lib/api/trading';
import { mergeKlineData, LRUCache } from '@/lib/utils/cacheUtils';
import { Timeframe } from '@/lib/utils/timeUtils';
import type { LoadedRange, LoadingState } from '@/types/chart';

export interface UseChartDataOptions {
  /** 图表实例 */
  chart: IChartApi | null;
  /** 股票代码 */
  symbol: string | null;
  /** 时间周期 */
  interval: Timeframe;
  /** 是否启用动态加载 */
  enabled?: boolean;
  /** 缓冲区大小（根K线数量），默认 50 */
  loadBuffer?: number;
  /** 每次加载的数据量，默认 200 */
  loadLimit?: number;
}

export interface UseChartDataReturn {
  /** K线数据 */
  data: CandlestickData[];
  /** 已加载的范围 */
  loadedRange: LoadedRange;
  /** 加载状态 */
  loadingState: LoadingState;
  /** 加载历史数据 */
  loadHistoricalData: () => Promise<void>;
  /** 加载最新数据 */
  loadLatestData: () => Promise<void>;
  /** 重新加载数据 */
  reload: () => Promise<void>;
  /** 清除缓存 */
  clearCache: () => void;
}

// IndexedDB 数据库名称
const DB_NAME = 'happystock_kline_cache';
const DB_VERSION = 1;
const STORE_NAME = 'klines';

// LRU 缓存实例（内存缓存，最多缓存 10 只股票的数据）
const memoryCache = new LRUCache<string, CandlestickData[]>(10);

/**
 * 使用图表数据
 *
 * @param options - 配置选项
 * @returns 数据和控制函数
 *
 * @example
 * ```tsx
 * const { data, loadingState, loadHistoricalData, loadLatestData } = useChartData({
 *   chart,
 *   symbol: 'AAPL',
 *   interval: '5m',
 *   enabled: true,
 * });
 * ```
 */
export function useChartData({
  chart,
  symbol,
  interval,
  enabled = true,
  loadBuffer = 50,
  loadLimit = 200,
}: UseChartDataOptions): UseChartDataReturn {
  const [data, setData] = useState<CandlestickData[]>([]);
  const [loadedRange, setLoadedRange] = useState<LoadedRange>({
    from: 0,
    to: 0,
    reachedStart: false,
    reachedEnd: false,
  });
  const [loadingState, setLoadingState] = useState<LoadingState>({
    loading: false,
    direction: undefined,
    error: null,
  });

  // IndexedDB 实例引用
  const dbRef = useRef<IDBDatabase | null>(null);

  // 防抖计时器
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);

  // 当前请求控制器（用于取消请求）
  const abortControllerRef = useRef<AbortController | null>(null);

  /**
   * 防抖函数
   *
   * 延迟执行函数，如果在延迟期间再次调用，则重新计时
   *
   * @param fn - 要执行的函数
   * @param delay - 延迟时间（毫秒），默认 200ms
   */
  const debounce = useCallback((fn: () => void, delay: number = 200) => {
    // 清除之前的计时器
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    // 设置新的计时器
    debounceTimerRef.current = setTimeout(() => {
      fn();
      debounceTimerRef.current = null;
    }, delay);
  }, []);

  // 初始化 IndexedDB
  useEffect(() => {
    const initDB = async () => {
      return new Promise<IDBDatabase>((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, DB_VERSION);

        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);

        request.onupgradeneeded = (event) => {
          const db = (event.target as IDBOpenDBRequest).result;

          // 创建对象存储（如果不存在）
          if (!db.objectStoreNames.contains(STORE_NAME)) {
            const store = db.createObjectStore(STORE_NAME, { keyPath: 'key' });
            store.createIndex('symbol', 'symbol', { unique: false });
            store.createIndex('interval', 'interval', { unique: false });
            store.createIndex('timestamp', 'timestamp', { unique: false });
          }
        };
      });
    };

    let isSubscribed = true;

    initDB()
      .then(db => {
        if (isSubscribed) {
          dbRef.current = db;
          console.log('IndexedDB initialized successfully');
        } else {
          // 如果组件已卸载，立即关闭数据库
          db.close();
        }
      })
      .catch(error => {
        console.error('Failed to initialize IndexedDB:', error);
      });

    return () => {
      isSubscribed = false;
      if (dbRef.current) {
        try {
          dbRef.current.close();
          dbRef.current = null;
        } catch (error) {
          console.error('Error closing IndexedDB:', error);
        }
      }
    };
  }, []);

  // 生成缓存键
  const getCacheKey = useCallback((sym: string, int: Timeframe) => {
    return `${sym}:${int}`;
  }, []);

  // 从 IndexedDB 读取数据
  const readFromDB = useCallback(async (key: string): Promise<CandlestickData[] | null> => {
    if (!dbRef.current) return null;

    return new Promise((resolve, reject) => {
      const transaction = dbRef.current!.transaction([STORE_NAME], 'readonly');
      const store = transaction.objectStore(STORE_NAME);
      const request = store.get(key);

      request.onsuccess = () => {
        const result = request.result;
        if (result && result.data) {
          resolve(result.data as CandlestickData[]);
        } else {
          resolve(null);
        }
      };

      request.onerror = () => reject(request.error);
    });
  }, []);

  // 写入 IndexedDB
  const writeToDB = useCallback(async (
    key: string,
    klineData: CandlestickData[],
    sym: string,
    int: Timeframe
  ): Promise<void> => {
    if (!dbRef.current) return;

    return new Promise((resolve, reject) => {
      try {
        // 检查数据库是否已关闭
        if (!dbRef.current || !dbRef.current.objectStoreNames.contains(STORE_NAME)) {
          console.warn('IndexedDB is not available or closing');
          resolve(); // 静默失败，不中断流程
          return;
        }

        const transaction = dbRef.current.transaction([STORE_NAME], 'readwrite');
        const store = transaction.objectStore(STORE_NAME);
        const request = store.put({
          key,
          symbol: sym,
          interval: int,
          data: klineData,
          timestamp: Date.now(),
        });

        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
      } catch (error) {
        console.warn('Failed to write to IndexedDB:', error);
        resolve(); // 静默失败，不中断流程
      }
    });
  }, []);

  // 从缓存读取数据（先内存，后 IndexedDB）
  const readFromCache = useCallback(async (key: string): Promise<CandlestickData[] | null> => {
    // 1. 尝试从内存缓存读取
    const memoryData = memoryCache.get(key);
    if (memoryData) {
      console.log('Cache hit (memory):', key);
      return memoryData;
    }

    // 2. 尝试从 IndexedDB 读取
    const dbData = await readFromDB(key);
    if (dbData) {
      console.log('Cache hit (IndexedDB):', key);
      // 写入内存缓存
      memoryCache.set(key, dbData);
      return dbData;
    }

    console.log('Cache miss:', key);
    return null;
  }, [readFromDB]);

  // 写入缓存（内存 + IndexedDB）
  const writeToCache = useCallback(async (
    key: string,
    klineData: CandlestickData[],
    sym: string,
    int: Timeframe
  ): Promise<void> => {
    // 写入内存缓存
    memoryCache.set(key, klineData);

    // 写入 IndexedDB
    try {
      await writeToDB(key, klineData, sym, int);
      console.log('Cache written:', key);
    } catch (error) {
      console.error('Failed to write to IndexedDB:', error);
    }
  }, [writeToDB]);

  // 清除缓存
  const clearCache = useCallback(() => {
    memoryCache.clear();

    if (dbRef.current) {
      const transaction = dbRef.current.transaction([STORE_NAME], 'readwrite');
      const store = transaction.objectStore(STORE_NAME);
      store.clear();
      console.log('Cache cleared');
    }
  }, []);

  // 加载历史数据（向左滑动）
  // 注意：当前后端 API 不支持指定时间范围，所以这个功能暂时模拟
  const loadHistoricalData = useCallback(async () => {
    if (!symbol || !chart || !enabled || loadingState.loading) return;
    if (loadedRange.reachedStart) {
      console.log('✅ 已到达历史数据起点');
      return;
    }

    console.log('📥 触发历史数据加载（向左滑动）');
    console.log('⚠️ 注意：当前后端 API 不支持时间范围参数，动态加载暂时禁用');

    // 暂时标记为已到达起点，避免重复触发
    setLoadedRange(prev => ({ ...prev, reachedStart: true }));
    return;

    /* 以下代码需要后端支持 startTime/endTime 参数才能工作 - Dead code, 暂时注释
    setLoadingState({ loading: true, direction: 'historical', error: null });

    try {
      // 计算要加载的时间范围
      let startTime: number;
      let endTime: number;

      if (data.length === 0) {
        // 初始加载：加载最近的数据
        endTime = Math.floor(Date.now() / 1000);
        startTime = 0; // 让后端决定起始时间
      } else {
        // 获取当前最早的数据时间
        const firstBar = data[0];
        const firstTime = (typeof firstBar.time === 'number'
          ? firstBar.time
          : Math.floor(Date.parse(firstBar.time as string) / 1000)) as number;

        endTime = firstTime;
        startTime = 0; // 加载更早的数据
      }

      // 尝试从缓存读取
      const cacheKey = getCacheKey(symbol!, interval);
      const cachedData = await readFromCache(cacheKey);

      let historicalData: CandlestickData[];

      if (cachedData !== null && cachedData.length > 0) {
        // 从缓存中筛选出需要的历史数据
        historicalData = cachedData.filter(item => {
          const time = typeof item.time === 'number'
            ? item.time
            : Math.floor(Date.parse(item.time as string) / 1000);
          return time < endTime;
        }).slice(-loadLimit); // 取最新的 loadLimit 条
      } else {
        // 从 API 加载
        const response = await getKlineData(symbol, interval, loadLimit);

        // 转换数据格式
        const isMinuteInterval = ['5m', '15m', '30m', '60m', '120m'].includes(interval);
        historicalData = response.klines.map(kline => {
          let timeValue: string | number;
          if (isMinuteInterval) {
            timeValue = kline.time as any;
          } else {
            const date = new Date(kline.time * 1000);
            timeValue = date.toISOString().split('T')[0];
          }

          return {
            time: timeValue as any,
            open: parseFloat(kline.open),
            high: parseFloat(kline.high),
            low: parseFloat(kline.low),
            close: parseFloat(kline.close),
          };
        }).sort((a, b) => (a.time > b.time ? 1 : -1));
      }

      if (historicalData.length === 0) {
        // 没有更多历史数据
        setLoadedRange(prev => ({ ...prev, reachedStart: true }));
        setLoadingState({ loading: false, direction: undefined, error: null });
        return;
      }

      // 合并数据
      const mergedData = mergeKlineData(historicalData, data);
      setData(mergedData);

      // 更新缓存
      await writeToCache(cacheKey, mergedData, symbol, interval);

      // 更新加载范围
      if (mergedData.length > 0) {
        const firstTime = typeof mergedData[0].time === 'number'
          ? mergedData[0].time
          : Math.floor(Date.parse(mergedData[0].time as string) / 1000);
        const lastTime = typeof mergedData[mergedData.length - 1].time === 'number'
          ? mergedData[mergedData.length - 1].time
          : Math.floor(Date.parse(mergedData[mergedData.length - 1].time as string) / 1000);

        setLoadedRange({
          from: 0, // 逻辑索引从 0 开始
          to: mergedData.length - 1,
          reachedStart: historicalData.length < loadLimit, // 如果返回数据少于请求量，说明到头了
          reachedEnd: loadedRange.reachedEnd,
        });
      }

      setLoadingState({ loading: false, direction: undefined, error: null });
      console.log('Historical data loaded:', historicalData.length, 'bars');
    } catch (error: any) {
      console.error('Failed to load historical data:', error);
      setLoadingState({
        loading: false,
        direction: undefined,
        error: error.message || '加载历史数据失败',
      });
    }
    */
  }, [symbol, chart, enabled, loadingState.loading, loadedRange, data, interval, loadLimit, getCacheKey, readFromCache, writeToCache]);

  // 加载最新数据（向右滑动）
  // 注意：当前后端 API 不支持指定时间范围，所以这个功能暂时模拟
  const loadLatestData = useCallback(async () => {
    if (!symbol || !chart || !enabled || loadingState.loading) return;
    if (loadedRange.reachedEnd) {
      console.log('✅ 已到达最新数据');
      return;
    }

    console.log('📥 触发最新数据加载（向右滑动）');
    console.log('⚠️ 注意：当前后端 API 不支持时间范围参数，动态加载暂时禁用');

    // 暂时标记为已到达终点，避免重复触发
    setLoadedRange(prev => ({ ...prev, reachedEnd: true }));
    return;

    // 以下代码需要后端支持 startTime/endTime 参数才能工作
    setLoadingState({ loading: true, direction: 'latest', error: null });

    try {
      // 计算要加载的时间范围
      let startTime: number;

      if (data.length === 0) {
        // 初始加载
        startTime = 0;
      } else {
        // 获取当前最新的数据时间
        const lastBar = data[data.length - 1];
        startTime = typeof lastBar.time === 'number'
          ? lastBar.time
          : Math.floor(Date.parse(lastBar.time as string) / 1000);
      }

      // 从 API 加载最新数据
      const response = await getKlineData(symbol, interval, loadLimit);

      // 转换数据格式
      const isMinuteInterval = ['5m', '15m', '30m', '60m', '120m'].includes(interval);
      const latestData = response.klines
        .map(kline => {
          let timeValue: string | number;
          if (isMinuteInterval) {
            timeValue = kline.time as any;
          } else {
            const date = new Date(kline.time * 1000);
            timeValue = date.toISOString().split('T')[0];
          }

          return {
            time: timeValue as any,
            open: parseFloat(kline.open),
            high: parseFloat(kline.high),
            low: parseFloat(kline.low),
            close: parseFloat(kline.close),
          };
        })
        .filter(item => {
          // 只保留比当前最新时间更新的数据
          const time = typeof item.time === 'number'
            ? item.time
            : Math.floor(Date.parse(item.time as string) / 1000);
          return time > startTime;
        })
        .sort((a, b) => (a.time > b.time ? 1 : -1));

      if (latestData.length === 0) {
        // 没有更多新数据，说明已经是最新的了
        setLoadedRange(prev => ({ ...prev, reachedEnd: true }));
        setLoadingState({ loading: false, direction: undefined, error: null });
        console.log('Already at the latest data');
        return;
      }

      // 合并数据
      const mergedData = mergeKlineData(data, latestData);
      setData(mergedData);

      // 更新缓存
      const cacheKey = getCacheKey(symbol, interval);
      await writeToCache(cacheKey, mergedData, symbol, interval);

      // 更新加载范围
      if (mergedData.length > 0) {
        setLoadedRange({
          from: 0,
          to: mergedData.length - 1,
          reachedStart: loadedRange.reachedStart,
          reachedEnd: latestData.length < loadLimit, // 如果返回数据少于请求量，说明到头了
        });
      }

      setLoadingState({ loading: false, direction: undefined, error: null });
      console.log('Latest data loaded:', latestData.length, 'bars');
    } catch (error: any) {
      console.error('Failed to load latest data:', error);
      setLoadingState({
        loading: false,
        direction: undefined,
        error: error.message || '加载最新数据失败',
      });
    }
  }, [symbol, chart, enabled, loadingState.loading, loadedRange, data, interval, loadLimit, getCacheKey, writeToCache]);

  // 重新加载数据（初始加载）
  const reload = useCallback(async () => {
    if (!symbol || !chart) return;

    console.log('Loading initial chart data...');
    setLoadingState({ loading: true, direction: undefined, error: null });

    try {
      // 从 API 加载初始数据
      const response = await getKlineData(symbol, interval, loadLimit);

      // 转换数据格式
      const isMinuteInterval = ['5m', '15m', '30m', '60m', '120m'].includes(interval);
      const initialData = response.klines.map(kline => {
        let timeValue: string | number;
        if (isMinuteInterval) {
          timeValue = kline.time as any;
        } else {
          const date = new Date(kline.time * 1000);
          timeValue = date.toISOString().split('T')[0];
        }

        return {
          time: timeValue as any,
          open: parseFloat(kline.open),
          high: parseFloat(kline.high),
          low: parseFloat(kline.low),
          close: parseFloat(kline.close),
        };
      }).sort((a, b) => (a.time > b.time ? 1 : -1));

      setData(initialData);

      // 更新缓存
      const cacheKey = getCacheKey(symbol, interval);
      await writeToCache(cacheKey, initialData, symbol, interval);

      // 更新加载范围
      if (initialData.length > 0) {
        setLoadedRange({
          from: 0,
          to: initialData.length - 1,
          reachedStart: false, // 允许加载更早的数据
          reachedEnd: false, // 允许加载更新的数据（实际API可能返回更新数据）
        });
      }

      setLoadingState({ loading: false, direction: undefined, error: null });
      console.log('Initial data loaded:', initialData.length, 'bars');
    } catch (error: any) {
      console.error('Failed to load initial data:', error);
      setLoadingState({
        loading: false,
        direction: undefined,
        error: error.message || '加载数据失败',
      });
    }
  }, [symbol, chart, interval, loadLimit, getCacheKey, writeToCache]);

  // 初始数据加载
  useEffect(() => {
    if (!symbol || !chart || !enabled) return;

    // 当 symbol 或 interval 变化时重新加载数据
    reload();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [symbol, interval, chart, enabled]);

  // 监听可见范围变化（T023, T024）
  useEffect(() => {
    if (!chart || !enabled) return;

    const handleVisibleRangeChange = () => {
      debounce(() => {
        try {
          const timeScale = chart.timeScale();
          const logicalRange = timeScale.getVisibleLogicalRange();

          if (!logicalRange) return;

          const { from: visibleFrom, to: visibleTo } = logicalRange;

          console.log('Visible range changed:', { visibleFrom, visibleTo });
          console.log('Loaded range:', loadedRange);

          // 判断是否需要加载历史数据（向左滑动）
          // 如果可见范围的左边界接近已加载范围的左边界（buffer 缓冲区内）
          if (
            !loadedRange.reachedStart &&
            !loadingState.loading &&
            data.length > 0
          ) {
            const leftBuffer = visibleFrom - loadedRange.from;
            console.log('Left buffer:', leftBuffer, 'Load buffer:', loadBuffer);

            if (leftBuffer < loadBuffer) {
              console.log('Triggering historical data load');
              loadHistoricalData();
            }
          }

          // 判断是否需要加载最新数据（向右滑动）
          // 如果可见范围的右边界接近已加载范围的右边界（buffer 缓冲区内）
          if (
            !loadedRange.reachedEnd &&
            !loadingState.loading &&
            data.length > 0
          ) {
            const rightBuffer = loadedRange.to - visibleTo;
            console.log('Right buffer:', rightBuffer, 'Load buffer:', loadBuffer);

            if (rightBuffer < loadBuffer) {
              console.log('Triggering latest data load');
              loadLatestData();
            }
          }
        } catch (error) {
          console.error('Error handling visible range change:', error);
        }
      }, 200);
    };

    // 订阅可见范围变化事件
    const unsubscribe = chart.timeScale().subscribeVisibleLogicalRangeChange(handleVisibleRangeChange);

    return () => {
      // 安全调用 unsubscribe
      if (unsubscribe && typeof unsubscribe === 'function') {
        unsubscribe();
      }
      // 清理防抖计时器
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [chart, enabled, data.length, loadedRange, loadingState.loading, loadBuffer, debounce, loadHistoricalData, loadLatestData]);

  return {
    data,
    loadedRange,
    loadingState,
    loadHistoricalData,
    loadLatestData,
    reload,
    clearCache,
  };
}
