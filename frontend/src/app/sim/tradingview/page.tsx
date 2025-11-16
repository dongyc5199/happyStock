'use client';

import { useEffect, useState } from 'react';
import ManualTickForm from '@/components/sim/ManualTickForm';

const ENV_WS_BASE = process.env.NEXT_PUBLIC_SIM_WS_URL?.trim();
const ENV_API_BASE = process.env.NEXT_PUBLIC_API_URL?.trim();
const DEFAULT_SYMBOL =
  process.env.NEXT_PUBLIC_TV_SYMBOL || 'NASDAQ:AAPL';

type SnapshotDto = {
  session_id: number;
  tick: number;
  timestamp: string;
  last_price: number | null;
  total_volume: number | null;
};

declare global {
  interface Window {
    TradingView?: {
      widget: (options: Record<string, unknown>) => void;
    };
  }
}

const TRADING_VIEW_SCRIPT_SRC =
  'https://s3.tradingview.com/external-embedding/tv.js';
const CHART_CONTAINER_ID = 'tv-chart-widget';
let tradingViewScriptPromise: Promise<void> | null = null;

function loadTradingViewScript(): Promise<void> {
  if (typeof window === 'undefined') {
    return Promise.resolve();
  }
  if (window.TradingView) {
    return Promise.resolve();
  }
  if (!tradingViewScriptPromise) {
    tradingViewScriptPromise = new Promise((resolve) => {
      const script = document.createElement('script');
      script.id = 'tradingview-widget-script';
      script.type = 'text/javascript';
      script.async = true;
      script.src = TRADING_VIEW_SCRIPT_SRC;
      script.onload = () => resolve();
      script.onerror = () => resolve();
      document.head.appendChild(script);
    });
  }
  return tradingViewScriptPromise;
}

export default function TradingViewSimPage() {
  const [sessionId, setSessionId] = useState(1);
  const [limit, setLimit] = useState(80);
  const [symbol, setSymbol] = useState(DEFAULT_SYMBOL);
  const [snapshots, setSnapshots] = useState<SnapshotDto[]>([]);
  const [wsError, setWsError] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }
    const base =
      (ENV_WS_BASE && ENV_WS_BASE.length > 0
        ? ENV_WS_BASE
        : ENV_API_BASE && ENV_API_BASE.length > 0
          ? ENV_API_BASE
          : window.location.origin) || window.location.origin;
    const normalizedBase = base.replace(/^ws/i, 'http').replace(/^wss/i, 'https');
    let target = normalizedBase;
    try {
      const parsed = new URL(normalizedBase);
      if (!ENV_WS_BASE || !ENV_WS_BASE.includes('/api/')) {
        parsed.pathname = '/api/sim/ws/ticks';
      }
      target = parsed.toString();
    } catch {
      const fallback = new URL('/api/sim/ws/ticks', window.location.origin);
      target = fallback.toString();
    }
    const wsUrl = new URL(target);
    const secure =
      ENV_WS_BASE?.startsWith('wss://') ||
      ENV_WS_BASE?.startsWith('https://') ||
      wsUrl.protocol === 'https:';
    wsUrl.protocol = secure ? 'wss:' : 'ws:';
    wsUrl.searchParams.set('session_id', sessionId.toString());
    wsUrl.searchParams.set('limit', limit.toString());
    wsUrl.searchParams.set('interval_ms', '1000');

    let shouldIgnoreClose = false;
    const ws = new WebSocket(wsUrl.toString());
    ws.onopen = () => setWsError(null);
    ws.onerror = () => setWsError('WebSocket 连接失败');
    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data) as {
          type: string;
          snapshots: SnapshotDto[];
        };
        if (payload.type === 'tick_update') {
          setSnapshots(payload.snapshots.slice().reverse());
        }
      } catch (error) {
        console.error('无法解析 websocket 消息', error);
      }
    };
    ws.onclose = () => {
      if (!shouldIgnoreClose) {
        setWsError('连接已关闭');
      }
    };

    return () => {
      shouldIgnoreClose = true;
      ws.close();
    };
  }, [limit, sessionId]);

  useEffect(() => {
    let cancelled = false;
    loadTradingViewScript().then(() => {
      if (cancelled || !window.TradingView) return;
      window.TradingView.widget({
        autosize: true,
        symbol,
        interval: '1',
        timezone: 'Asia/Shanghai',
        theme: 'light',
        style: '1',
        locale: 'zh_CN',
        container_id: CHART_CONTAINER_ID,
        hide_side_toolbar: false,
        allow_symbol_change: true,
        studies: ['Volume@tv-basicstudies'],
      });
    });

    return () => {
      cancelled = true;
      const container = document.getElementById(CHART_CONTAINER_ID);
      if (container) {
        container.innerHTML = '';
      }
    };
  }, [symbol]);

  const current = snapshots[0];
  const previous = snapshots[1];
  const currentPrice = current?.last_price ?? null;
  const priceDelta =
    current?.last_price && previous?.last_price
      ? current.last_price - previous.last_price
      : null;
  const priceDeltaPct =
    priceDelta !== null && previous?.last_price
      ? (priceDelta / previous.last_price) * 100
      : null;
  const currentVolume = current?.total_volume ?? null;

  const recentRows = snapshots.slice(0, 8);

  return (
    <div className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <header className="space-y-2">
        <p className="text-sm text-blue-600">TradingView 集成体验</p>
        <h1 className="text-2xl font-semibold">
          实时行情 + TradingView 可视化 + 手动下单
        </h1>
        <p className="text-sm text-gray-600">
          这个页面将 Simulation WebSocket 的 Tick 数据接入 TradingView 小部件，提供实时价格、成交量卡片，并允许玩家直接以 Tick
          API 下单。
        </p>
      </header>

      <section className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-4 rounded-xl border border-gray-200 bg-white p-4 shadow-sm lg:col-span-2">
          <div className="grid gap-4 md:grid-cols-3">
            <label className="flex flex-col text-sm">
              Session ID
              <input
                type="number"
                min={1}
                className="mt-1 rounded-md border border-gray-300 px-3 py-2"
                value={sessionId}
                onChange={(event) => setSessionId(Number(event.target.value))}
              />
            </label>
            <label className="flex flex-col text-sm">
              WebSocket 样本数
              <input
                type="number"
                min={20}
                max={200}
                className="mt-1 rounded-md border border-gray-300 px-3 py-2"
                value={limit}
                onChange={(event) => setLimit(Number(event.target.value))}
              />
            </label>
            <label className="flex flex-col text-sm">
              TradingView Symbol
              <input
                type="text"
                className="mt-1 rounded-md border border-gray-300 px-3 py-2"
                value={symbol}
                onChange={(event) => setSymbol(event.target.value)}
              />
            </label>
          </div>
          {wsError && (
            <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-600">
              {wsError}
            </div>
          )}
          <div className="h-[480px] w-full overflow-hidden rounded-lg border border-gray-100">
            <div id={CHART_CONTAINER_ID} className="h-full w-full" />
          </div>
        </div>

        <div className="space-y-4 rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
          <div>
            <h2 className="text-lg font-medium">实时快照</h2>
            <p className="text-xs text-gray-500">
              来自 `/api/sim/ws/ticks` 的最新数据。
            </p>
          </div>
          <div className="space-y-3 text-sm">
            <div className="rounded-lg border border-gray-100 bg-gray-50 p-3">
              <div className="text-gray-500">最新价格</div>
              <div className="text-2xl font-semibold">
                {currentPrice ? currentPrice.toFixed(2) : '--'}
              </div>
              {priceDelta !== null && (
                <div
                  className={`text-xs ${
                    priceDelta >= 0 ? 'text-green-600' : 'text-red-500'
                  }`}
                >
                  {priceDelta >= 0 ? '+' : ''}
                  {priceDelta.toFixed(2)} ({priceDeltaPct?.toFixed(2) ?? '--'}%)
                </div>
              )}
            </div>
            <div className="rounded-lg border border-gray-100 bg-gray-50 p-3">
              <div className="text-gray-500">累计成交量</div>
              <div className="text-2xl font-semibold">
                {currentVolume ? currentVolume.toFixed(0) : '--'}
              </div>
              <div className="text-xs text-gray-500">
                Tick #{current?.tick ?? '--'} ·{' '}
                {current
                  ? new Date(current.timestamp).toLocaleTimeString()
                  : '--'}
              </div>
            </div>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-700">
              最新 8 条 Tick
            </h3>
            <div className="mt-2 max-h-64 overflow-auto">
              <table className="w-full text-xs text-gray-600">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-2 py-1 text-left">Tick</th>
                    <th className="px-2 py-1 text-left">价格</th>
                    <th className="px-2 py-1 text-left">成交量</th>
                    <th className="px-2 py-1 text-left">时间</th>
                  </tr>
                </thead>
                <tbody>
                  {recentRows.map((row) => (
                    <tr key={row.tick} className="border-b">
                      <td className="px-2 py-1">{row.tick}</td>
                      <td className="px-2 py-1">
                        {row.last_price?.toFixed(2) ?? '--'}
                      </td>
                      <td className="px-2 py-1">
                        {row.total_volume?.toFixed(0) ?? '--'}
                      </td>
                      <td className="px-2 py-1">
                        {new Date(row.timestamp).toLocaleTimeString()}
                      </td>
                    </tr>
                  ))}
                  {!recentRows.length && (
                    <tr>
                      <td
                        className="px-2 py-3 text-center text-gray-400"
                        colSpan={4}
                      >
                        暂无数据
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      <section>
        <ManualTickForm
          defaultSessionId={sessionId}
          defaultSessionCode="autoplay-demo"
          title="手动下单 / Tick 播放器"
        />
      </section>
    </div>
  );
}
