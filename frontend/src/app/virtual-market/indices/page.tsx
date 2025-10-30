'use client';

import { useEffect, useState, useCallback } from 'react';
import { MainNav } from '@/components/layout/MainNav';
import { indicesApi } from '@/lib/api/virtual-market';
import type { Index } from '@/types/virtual-market';
import Link from 'next/link';
import { REFRESH_INTERVALS, ACTIVITY_CONFIG } from '@/config/refresh';

/**
 * 指数看板页面
 * T049-T052: 指数列表页面实现
 * T087: 自动刷新功能
 */
export default function IndicesPage() {
  const [coreIndices, setCoreIndices] = useState<Index[]>([]);
  const [sectorIndices, setSectorIndices] = useState<Index[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdateTime, setLastUpdateTime] = useState<Date>(new Date());
  const [isUserActive, setIsUserActive] = useState(true);
  const [lastActivityTime, setLastActivityTime] = useState<Date>(new Date());

  // 用户活动检测 (T089)
  useEffect(() => {
    const handleActivity = () => {
      setLastActivityTime(new Date());
      setIsUserActive(true);
    };

    window.addEventListener('mousemove', handleActivity);
    window.addEventListener('keydown', handleActivity);
    window.addEventListener('click', handleActivity);
    window.addEventListener('scroll', handleActivity);

    return () => {
      window.removeEventListener('mousemove', handleActivity);
      window.removeEventListener('keydown', handleActivity);
      window.removeEventListener('click', handleActivity);
      window.removeEventListener('scroll', handleActivity);
    };
  }, []);

  // 检查用户是否超过5分钟无活动 (T089)
  useEffect(() => {
    const checkInactivity = setInterval(() => {
      const inactiveTime = Date.now() - lastActivityTime.getTime();
      
      if (inactiveTime > ACTIVITY_CONFIG.INACTIVE_THRESHOLD && isUserActive) {
        setIsUserActive(false);
        console.log('[Auto-refresh] Paused due to user inactivity');
      }
    }, ACTIVITY_CONFIG.CHECK_INTERVAL);

    return () => clearInterval(checkInactivity);
  }, [lastActivityTime, isUserActive]);

  // 后台静默刷新 (T087, T088)
  const refreshIndices = useCallback(async () => {
    try {
      setIsRefreshing(true);
      console.log('[Auto-refresh] Refreshing indices...');

      const [coreResponse, sectorResponse] = await Promise.all([
        indicesApi.getIndices('CORE'),
        indicesApi.getIndices('SECTOR'),
      ]);

      if (coreResponse.success && coreResponse.data) {
        setCoreIndices(coreResponse.data);
      }

      if (sectorResponse.success && sectorResponse.data) {
        setSectorIndices(sectorResponse.data);
      }

      setLastUpdateTime(new Date());
      console.log('[Auto-refresh] Indices refreshed successfully');
    } catch (err) {
      console.error('[Auto-refresh] Failed to refresh:', err);
    } finally {
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadIndices();
  }, []);

  // 自动刷新机制 (T087)
  useEffect(() => {
    const refreshInterval = setInterval(() => {
      if (isUserActive) {
        refreshIndices();
      } else {
        console.log('[Auto-refresh] Skipped refresh - user inactive');
      }
    }, REFRESH_INTERVALS.INDICES_PAGE);

    return () => clearInterval(refreshInterval);
  }, [isUserActive, refreshIndices]);

  async function loadIndices() {
    try {
      setLoading(true);
      setError(null);

      // 获取核心指数
      const coreResponse = await indicesApi.getIndices('CORE');
      if (coreResponse.success && coreResponse.data) {
        setCoreIndices(coreResponse.data);
      }

      // 获取板块指数
      const sectorResponse = await indicesApi.getIndices('SECTOR');
      if (sectorResponse.success && sectorResponse.data) {
        setSectorIndices(sectorResponse.data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载失败');
      console.error('Failed to load indices:', err);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <MainNav />
        <div className="flex items-center justify-center" style={{ minHeight: 'calc(100vh - 64px)' }}>
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">加载指数数据...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <MainNav />
        <div className="flex items-center justify-center" style={{ minHeight: 'calc(100vh - 64px)' }}>
          <div className="text-center">
          <svg
            className="w-16 h-16 text-red-500 mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={loadIndices}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            重试
          </button>
        </div>
      </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <MainNav />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 页面标题 */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">市场指数</h1>
              <p className="mt-2 text-sm text-gray-600">
                查看核心指数和板块指数的实时行情
              </p>
            </div>
            <div className="text-right">
              {isRefreshing && (
                <div className="flex items-center gap-2 text-sm text-blue-600 mb-1">
                  <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>更新中...</span>
                </div>
              )}
              <div className="text-sm text-gray-500">
                最后更新: {lastUpdateTime.toLocaleTimeString('zh-CN')}
              </div>
              <div className="text-xs text-gray-400 mt-1">
                {isUserActive ? '自动刷新已启用 (5秒)' : '自动刷新已暂停 (用户不活跃)'}
              </div>
            </div>
          </div>
        </div>

        {/* 核心指数 */}
        <section className="mb-12">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">核心指数</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {coreIndices.map((index) => (
              <IndexCard key={index.code} index={index} />
            ))}
          </div>
        </section>

        {/* 板块指数 */}
        <section>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">板块指数</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {sectorIndices.map((index) => (
              <IndexCard key={index.code} index={index} compact />
            ))}
          </div>
        </section>

        {/* 返回按钮 */}
        <div className="mt-8">
          <Link
            href="/virtual-market"
            className="inline-flex items-center text-blue-600 hover:text-blue-800"
          >
            <svg
              className="w-5 h-5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 19l-7-7m0 0l7-7m-7 7h18"
              />
            </svg>
            返回股票列表
          </Link>
        </div>
      </div>
    </div>
  );
}

/**
 * 指数卡片组件
 * T050: IndexCard component
 */
interface IndexCardProps {
  index: Index;
  compact?: boolean;
}

function IndexCard({ index, compact = false }: IndexCardProps) {
  const changeValue = index.change_value || 0;
  const changePct = index.change_pct || 0;
  const isUp = changePct >= 0;
  const isFlat = Math.abs(changePct) < 0.01;

  return (
    <Link href={`/virtual-market/indices/${index.code}`}>
      <div
        className={`
          bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer
          border-l-4 
          ${isFlat ? 'border-gray-400' : isUp ? 'border-red-500' : 'border-green-500'}
          ${compact ? 'p-4' : 'p-6'}
        `}
      >
        {/* 指数名称和代码 */}
        <div className="mb-3">
          <h3 className={`font-semibold text-gray-900 ${compact ? 'text-base' : 'text-lg'}`}>
            {index.name}
          </h3>
          <p className="text-xs text-gray-500 mt-1">{index.code}</p>
        </div>

        {/* 当前点位 */}
        <div className="mb-2">
          <div className={`font-bold ${compact ? 'text-xl' : 'text-2xl'} text-gray-900`}>
            {index.current_value?.toFixed(2) || '--'}
          </div>
        </div>

        {/* 涨跌信息 */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {/* 涨跌箭头 */}
            {!isFlat && (
              <svg
                className={`w-4 h-4 ${isUp ? 'text-red-500' : 'text-green-500'}`}
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                {isUp ? (
                  <path
                    fillRule="evenodd"
                    d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z"
                    clipRule="evenodd"
                  />
                ) : (
                  <path
                    fillRule="evenodd"
                    d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                )}
              </svg>
            )}

            {/* 涨跌值 */}
            <span
              className={`
                text-sm font-medium
                ${isFlat ? 'text-gray-600' : isUp ? 'text-red-600' : 'text-green-600'}
              `}
            >
              {isUp && changePct > 0 ? '+' : ''}
              {changeValue.toFixed(2)}
            </span>
          </div>

          {/* 涨跌幅 */}
          <div
            className={`
              px-2 py-1 rounded text-xs font-semibold
              ${
                isFlat
                  ? 'bg-gray-100 text-gray-700'
                  : isUp
                  ? 'bg-red-100 text-red-700'
                  : 'bg-green-100 text-green-700'
              }
            `}
          >
            {isUp && changePct > 0 ? '+' : ''}
            {changePct.toFixed(2)}%
          </div>
        </div>

        {/* 成分股数量（仅非紧凑模式） */}
        {!compact && index.constituent_count && (
          <div className="mt-3 pt-3 border-t border-gray-200">
            <p className="text-xs text-gray-500">
              成分股: {index.constituent_count} 只
            </p>
          </div>
        )}
      </div>
    </Link>
  );
}
