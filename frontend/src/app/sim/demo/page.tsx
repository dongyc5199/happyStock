'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import ManualTickForm from '@/components/sim/ManualTickForm';

const WS_BASE =
  process.env.NEXT_PUBLIC_SIM_WS_URL || 'ws://localhost:8000';
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

interface SnapshotDto {
  session_id: number;
  tick: number;
  timestamp: string;
  last_price: number | null;
  total_volume: number | null;
}

export default function SimDemoPage() {
  const [sessionId, setSessionId] = useState(1);
  const [limit, setLimit] = useState(60);
  const [interval, setInterval] = useState(1000);
  const [snapshots, setSnapshots] = useState<SnapshotDto[]>([]);
  const [wsError, setWsError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const url = new URL('/api/sim/ws/ticks', WS_BASE.replace(/^ws/, 'http'));
    url.protocol = WS_BASE.startsWith('wss') ? 'wss:' : 'ws:';
    url.searchParams.set('session_id', sessionId.toString());
    url.searchParams.set('limit', limit.toString());
    url.searchParams.set('interval_ms', interval.toString());

    const ws = new WebSocket(url.toString());
    wsRef.current = ws;
    ws.onopen = () => setWsError(null);
    ws.onerror = () => setWsError('WebSocket 连接失败');
    ws.onclose = () => {
      if (!wsError) {
        setWsError('连接已关闭');
      }
    };
    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data) as {
          type: string;
          snapshots: SnapshotDto[];
        };
        if (payload.type === 'tick_update') {
          setSnapshots(payload.snapshots.slice().reverse());
        }
      } catch (err) {
        console.error('Failed to parse message', err);
      }
    };

    return () => {
      ws.close();
    };
  }, [sessionId, limit, interval]);

  const currentPrice = snapshots[0]?.last_price ?? null;
  const currentVolume = snapshots[0]?.total_volume ?? null;
  const priceSeries = useMemo(() => {
    return snapshots.map((snapshot, idx, arr) => {
      if (idx === arr.length - 1) {
        return '─';
      }
      const prev = arr[idx + 1];
      if (!prev?.last_price || !snapshot.last_price) return '─';
      if (snapshot.last_price > prev.last_price) return '▲';
      if (snapshot.last_price < prev.last_price) return '▼';
      return '─';
    });
  }, [snapshots]);

  return (
    <div className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <header>
        <h1 className="text-2xl font-semibold">实时行情 + 手动下单 Demo</h1>
        <p className="text-sm text-gray-600">
          使用 WebSocket 订阅 `/api/sim/ws/ticks` 实时更新价格/成交量，并可直接在页面上提交 Tick。
        </p>
      </header>

      <section className="rounded-lg border border-gray-200 p-4 shadow-sm space-y-4">
        <div className="grid gap-4 md:grid-cols-4">
          <label className="flex flex-col text-sm">
            Session ID
            <input
              type="number"
              className="mt-1 rounded-md border px-2 py-1"
              value={sessionId}
              onChange={(e) => setSessionId(Number(e.target.value))}
              min={1}
            />
          </label>
          <label className="flex flex-col text-sm">
            Tick 采样数量
            <input
              type="number"
              className="mt-1 rounded-md border px-2 py-1"
              value={limit}
              min={10}
              max={400}
              onChange={(e) => setLimit(Number(e.target.value))}
            />
          </label>
          <label className="flex flex-col text-sm">
            WebSocket 间隔 (ms)
            <input
              type="number"
              className="mt-1 rounded-md border px-2 py-1"
              value={interval}
              min={200}
              max={10000}
              onChange={(e) => setInterval(Number(e.target.value))}
            />
          </label>
          <div className="text-sm">
            当前价格：{' '}
            <span className="font-semibold">
              {currentPrice ? currentPrice.toFixed(2) : '--'}
            </span>
            <br />
            当前成交量：{' '}
            <span className="font-semibold">
              {currentVolume ? currentVolume.toFixed(0) : '--'}
            </span>
          </div>
        </div>
        {wsError && <div className="text-sm text-red-500">{wsError}</div>}
      </section>

      <section className="grid gap-6 md:grid-cols-2">
        <div className="rounded-lg border border-gray-200 p-4 shadow-sm">
          <h2 className="mb-2 text-lg font-medium">价格走势</h2>
          <div className="h-64 overflow-auto">
            <table className="w-full text-xs text-gray-700">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-2 py-1 text-left">Tick</th>
                  <th className="px-2 py-1 text-left">Time</th>
                  <th className="px-2 py-1 text-left">Price</th>
                  <th className="px-2 py-1 text-left">Δ</th>
                </tr>
              </thead>
              <tbody>
                {snapshots.map((snap, idx) => (
                  <tr key={snap.tick} className="border-b">
                    <td className="px-2 py-1">{snap.tick}</td>
                    <td className="px-2 py-1">
                      {new Date(snap.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="px-2 py-1">
                      {snap.last_price?.toFixed(2) ?? '--'}
                    </td>
                    <td className="px-2 py-1 text-lg">
                      {priceSeries[idx] ?? '─'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="rounded-lg border border-gray-200 p-4 shadow-sm">
          <h2 className="mb-2 text-lg font-medium">成交量</h2>
          <div className="h-64 overflow-auto">
            <table className="w-full text-xs text-gray-700">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-2 py-1 text-left">Tick</th>
                  <th className="px-2 py-1 text-left">Volume</th>
                  <th className="px-2 py-1 text-left">Time</th>
                </tr>
              </thead>
              <tbody>
                {snapshots.map((snap) => (
                  <tr key={`vol-${snap.tick}`} className="border-b">
                    <td className="px-2 py-1">{snap.tick}</td>
                    <td className="px-2 py-1">
                      {snap.total_volume?.toFixed(0) ?? '--'}
                    </td>
                    <td className="px-2 py-1">
                      {new Date(snap.timestamp).toLocaleTimeString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section>
        <ManualTickForm
          defaultSessionId={sessionId}
          defaultSessionCode="autoplay-demo"
          title="在此页面直接提交订单"
        />
      </section>

      <section className="rounded-lg border border-yellow-200 bg-yellow-50 p-4 text-sm text-yellow-800">
        <p>
          WebSocket 端点： <code>{`${API_BASE_URL}/api/sim/ws/ticks`}</code>
        </p>
        <p>
          通过 <code>session_id</code>、<code>limit</code>、<code>interval_ms</code>{' '}
          查询参数控制推送内容。
        </p>
      </section>
    </div>
  );
}
