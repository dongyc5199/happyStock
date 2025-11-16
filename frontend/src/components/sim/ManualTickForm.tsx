'use client';

import { FormEvent, useState } from 'react';
import {
  sendTickRequest,
  TickOrder,
  TickRequestPayload,
  TickResponse,
} from '@/services/simService';

const createOrder = (): TickOrder => ({
  order_id: `test-${crypto.randomUUID().slice(0, 8)}`,
  participant_id: 'manual-user',
  participant_code: 'manual-user',
  participant_type: 'player',
  side: 'BUY',
  type: 'MARKET',
  quantity: 10,
});

interface ManualTickFormProps {
  defaultSessionId?: number;
  defaultSessionCode?: string;
  title?: string;
}

export default function ManualTickForm({
  defaultSessionId = 1,
  defaultSessionCode = 'autoplay-demo',
  title = '手动提交 Tick',
}: ManualTickFormProps) {
  const [sessionId, setSessionId] = useState<number>(defaultSessionId);
  const [sessionCode, setSessionCode] = useState<string>(defaultSessionCode);
  const [tick, setTick] = useState<number>(1);
  const [orders, setOrders] = useState<TickOrder[]>([createOrder()]);
  const [timestamp, setTimestamp] = useState<string>(
    new Date().toISOString()
  );
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<TickResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleOrderChange = (
    index: number,
    field: keyof TickOrder,
    value: unknown
  ) => {
    setOrders((prev) =>
      prev.map((order, idx) =>
        idx === index
          ? {
              ...order,
              [field]:
                field === 'quantity' || field === 'price'
                  ? value === ''
                    ? undefined
                    : Number(value)
                  : value,
            }
          : order
      )
    );
  };

  const addOrder = () => setOrders((prev) => [...prev, createOrder()]);

  const removeOrder = (index: number) =>
    setOrders((prev) => prev.filter((_, idx) => idx !== index));

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const payload: TickRequestPayload = {
        session_id: sessionId,
        session_code: sessionCode,
        tick,
        timestamp,
        orders: orders.map((order) => ({
          ...order,
          price: order.type === 'LIMIT' ? order.price ?? 0 : undefined,
        })),
      };
      const response = await sendTickRequest(payload);
      setResult(response);
      setTick((prev) => prev + 1);
      setTimestamp(new Date().toISOString());
    } catch (err) {
      const message =
        err instanceof Error ? err.message : '下单失败，请检查日志';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4 rounded-lg border border-gray-200 p-4 shadow-sm">
      <h2 className="text-lg font-semibold">{title}</h2>
      <form className="space-y-4" onSubmit={handleSubmit}>
        <div className="grid gap-4 md:grid-cols-3">
          <label className="flex flex-col text-sm">
            Session ID
            <input
              type="number"
              className="mt-1 rounded-md border border-gray-300 px-3 py-2"
              value={sessionId}
              onChange={(e) => setSessionId(Number(e.target.value))}
              required
            />
          </label>
          <label className="flex flex-col text-sm">
            Session Code
            <input
              type="text"
              className="mt-1 rounded-md border border-gray-300 px-3 py-2"
              value={sessionCode}
              onChange={(e) => setSessionCode(e.target.value)}
              required
            />
          </label>
          <label className="flex flex-col text-sm">
            Tick
            <input
              type="number"
              className="mt-1 rounded-md border border-gray-300 px-3 py-2"
              value={tick}
              onChange={(e) => setTick(Number(e.target.value))}
              required
            />
          </label>
        </div>

        <label className="flex flex-col text-sm">
          Timestamp (ISO)
          <input
            type="text"
            className="mt-1 rounded-md border border-gray-300 px-3 py-2"
            value={timestamp}
            onChange={(e) => setTimestamp(e.target.value)}
          />
        </label>

        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-medium">订单列表</h3>
            <button
              type="button"
              className="rounded-md border border-blue-500 px-3 py-1 text-sm text-blue-600 hover:bg-blue-50"
              onClick={addOrder}
            >
              新增订单
            </button>
          </div>

          {orders.map((order, index) => (
            <div
              key={order.order_id}
              className="space-y-2 rounded-md border border-gray-200 p-3"
            >
              <div className="flex flex-wrap gap-3 text-sm">
                <label className="flex flex-1 min-w-[150px] flex-col">
                  Order ID
                  <input
                    type="text"
                    className="mt-1 rounded-md border border-gray-300 px-2 py-1"
                    value={order.order_id}
                    onChange={(e) =>
                      handleOrderChange(index, 'order_id', e.target.value)
                    }
                    required
                  />
                </label>
                <label className="flex flex-1 min-w-[150px] flex-col">
                  Participant ID
                  <input
                    type="text"
                    className="mt-1 rounded-md border border-gray-300 px-2 py-1"
                    value={order.participant_id}
                    onChange={(e) =>
                      handleOrderChange(
                        index,
                        'participant_id',
                        e.target.value,
                      )
                    }
                    required
                  />
                </label>
                <label className="flex flex-1 min-w-[150px] flex-col">
                  Participant Code
                  <input
                    type="text"
                    className="mt-1 rounded-md border border-gray-300 px-2 py-1"
                    value={order.participant_code ?? ''}
                    onChange={(e) =>
                      handleOrderChange(
                        index,
                        'participant_code',
                        e.target.value || undefined,
                      )
                    }
                  />
                </label>
                <label className="flex flex-1 min-w-[150px] flex-col">
                  Type
                  <select
                    className="mt-1 rounded-md border border-gray-300 px-2 py-1"
                    value={order.participant_type ?? 'player'}
                    onChange={(e) =>
                      handleOrderChange(
                        index,
                        'participant_type',
                        e.target.value as TickOrder['participant_type'],
                      )
                    }
                  >
                    <option value="player">Player</option>
                    <option value="agent">Agent</option>
                  </select>
                </label>
              </div>

              <div className="flex flex-wrap gap-3 text-sm">
                <label className="flex flex-1 min-w-[120px] flex-col">
                  Side
                  <select
                    className="mt-1 rounded-md border border-gray-300 px-2 py-1"
                    value={order.side}
                    onChange={(e) =>
                      handleOrderChange(
                        index,
                        'side',
                        e.target.value as TickOrder['side'],
                      )
                    }
                  >
                    <option value="BUY">BUY</option>
                    <option value="SELL">SELL</option>
                  </select>
                </label>
                <label className="flex flex-1 min-w-[120px] flex-col">
                  Type
                  <select
                    className="mt-1 rounded-md border border-gray-300 px-2 py-1"
                    value={order.type}
                    onChange={(e) =>
                      handleOrderChange(
                        index,
                        'type',
                        e.target.value as TickOrder['type'],
                      )
                    }
                  >
                    <option value="MARKET">MARKET</option>
                    <option value="LIMIT">LIMIT</option>
                  </select>
                </label>
                <label className="flex flex-1 min-w-[120px] flex-col">
                  Quantity
                  <input
                    type="number"
                    className="mt-1 rounded-md border border-gray-300 px-2 py-1"
                    min={1}
                    step={1}
                    value={order.quantity}
                    onChange={(e) =>
                      handleOrderChange(index, 'quantity', e.target.value)
                    }
                  />
                </label>
                {order.type === 'LIMIT' && (
                  <label className="flex flex-1 min-w-[120px] flex-col">
                    Price
                    <input
                      type="number"
                      className="mt-1 rounded-md border border-gray-300 px-2 py-1"
                      step={0.01}
                      value={order.price ?? ''}
                      onChange={(e) =>
                        handleOrderChange(index, 'price', e.target.value)
                      }
                    />
                  </label>
                )}
              </div>
              <div className="text-right">
                <button
                  type="button"
                  className="text-sm text-red-500 hover:underline"
                  onClick={() => removeOrder(index)}
                  disabled={orders.length === 1}
                >
                  删除
                </button>
              </div>
            </div>
          ))}
        </section>

        <div className="flex items-center gap-4 text-sm">
          <button
            type="submit"
            disabled={loading}
            className="rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-500 disabled:bg-blue-300"
          >
            {loading ? '提交中...' : '提交 Tick'}
          </button>
          {error && <span className="text-red-500">{error}</span>}
        </div>
      </form>

      {result && (
        <div className="rounded-md bg-gray-50 p-3 text-sm">
          <div>状态：{result.status}</div>
          <div>Trace ID：{result.trace_id}</div>
          <div>订单数：{result.orders.length}</div>
          <div>成交数：{result.trades.length}</div>
          {!!result.trades.length && (
            <pre className="mt-2 max-h-48 overflow-auto bg-white p-2 text-xs">
              {JSON.stringify(result.trades, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}
