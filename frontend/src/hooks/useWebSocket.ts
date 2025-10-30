/**
 * WebSocket Hook - 实时数据推送
 * 
 * 支持功能:
 * - 自动连接和重连
 * - 心跳保活 (ping/pong)
 * - 分级节流 (根据场景调整接收频率)
 * - 订阅管理
 * - 错误处理
 * 
 * @example
 * ```tsx
 * const { data, isConnected, error } = useWebSocket('/ws/market', {
 *   throttle: 3000, // 3秒节流
 *   autoConnect: true,
 * });
 * ```
 */

import { useState, useEffect, useRef, useCallback } from 'react';

// 推送频率预设
export const PUSH_INTERVALS = {
  REALTIME: 1000,    // 1秒 - 交易页面、自选股
  NORMAL: 3000,      // 3秒 - 市场页面、行情列表 (默认)
  SLOW: 10000,       // 10秒 - K线图、资讯页
  LAZY: 60000,       // 60秒 - 后台/最小化时
} as const;

export type PushInterval = typeof PUSH_INTERVALS[keyof typeof PUSH_INTERVALS];

interface UseWebSocketOptions {
  /** 是否自动连接 */
  autoConnect?: boolean;
  
  /** 节流间隔 (毫秒)，默认3000ms */
  throttle?: PushInterval | number;
  
  /** 重连延迟 (毫秒) */
  reconnectDelay?: number;
  
  /** 最大重连次数，0表示无限重连 */
  maxReconnectAttempts?: number;
  
  /** 心跳间隔 (毫秒) */
  heartbeatInterval?: number;
  
  /** 页面失焦时是否自动降频到LAZY模式 */
  autoSlowDownOnBlur?: boolean;
  
  /** 调试模式 */
  debug?: boolean;
}

interface WebSocketMessage {
  type: 'connected' | 'pong' | 'market_update' | 'error';
  client_id?: string;
  message?: string;
  data?: any;
  timestamp?: number;
}

interface UseWebSocketReturn<T = any> {
  /** 最新的数据 */
  data: T | null;
  
  /** 连接状态 */
  isConnected: boolean;
  
  /** 错误信息 */
  error: string | null;
  
  /** 手动连接 */
  connect: () => void;
  
  /** 手动断开 */
  disconnect: () => void;
  
  /** 发送消息 */
  send: (message: any) => void;
  
  /** 订阅频道 */
  subscribe: (channel: string, filters?: any) => void;
  
  /** 取消订阅 */
  unsubscribe: (channel: string) => void;
  
  /** 当前节流间隔 */
  currentThrottle: number;
  
  /** 设置节流间隔 */
  setThrottle: (interval: number) => void;
}

/**
 * WebSocket Hook
 */
export function useWebSocket<T = any>(
  endpoint: string,
  options: UseWebSocketOptions = {}
): UseWebSocketReturn<T> {
  const {
    autoConnect = true,
    throttle = PUSH_INTERVALS.NORMAL,
    reconnectDelay = 3000,
    maxReconnectAttempts = 0, // 无限重连
    heartbeatInterval = 30000,
    autoSlowDownOnBlur = true,
    debug = false,
  } = options;

  // 状态
  const [data, setData] = useState<T | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentThrottle, setCurrentThrottle] = useState(throttle);

  // Refs
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectCountRef = useRef(0);
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const lastUpdateTimeRef = useRef<number>(0);
  const pendingDataRef = useRef<T | null>(null);
  const throttleTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const log = useCallback((...args: any[]) => {
    if (debug) {
      console.log('[useWebSocket]', ...args);
    }
  }, [debug]);

  // 节流更新数据
  const updateDataThrottled = useCallback((newData: T) => {
    const now = Date.now();
    const timeSinceLastUpdate = now - lastUpdateTimeRef.current;

    if (timeSinceLastUpdate >= currentThrottle) {
      // 立即更新
      setData(newData);
      lastUpdateTimeRef.current = now;
      pendingDataRef.current = null;
      log('Data updated (immediate)', newData);
    } else {
      // 缓存数据，等待节流时间到
      pendingDataRef.current = newData;
      
      if (!throttleTimeoutRef.current) {
        const delay = currentThrottle - timeSinceLastUpdate;
        throttleTimeoutRef.current = setTimeout(() => {
          if (pendingDataRef.current) {
            setData(pendingDataRef.current);
            lastUpdateTimeRef.current = Date.now();
            pendingDataRef.current = null;
            log('Data updated (throttled)', pendingDataRef.current);
          }
          throttleTimeoutRef.current = null;
        }, delay);
      }
    }
  }, [currentThrottle, log]);

  // 发送心跳
  const sendHeartbeat = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'ping' }));
      log('Heartbeat sent');
    }
  }, [log]);

  // 启动心跳
  const startHeartbeat = useCallback(() => {
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
    }
    heartbeatIntervalRef.current = setInterval(sendHeartbeat, heartbeatInterval);
    log('Heartbeat started');
  }, [sendHeartbeat, heartbeatInterval, log]);

  // 停止心跳
  const stopHeartbeat = useCallback(() => {
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
      heartbeatIntervalRef.current = null;
      log('Heartbeat stopped');
    }
  }, [log]);

  // 连接 WebSocket
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      log('Already connected');
      return;
    }

    try {
      // 构建 WebSocket URL
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = process.env.NEXT_PUBLIC_WS_HOST || 'localhost:8000';
      const wsUrl = `${protocol}//${host}/api/v1${endpoint}`;
      
      log('Connecting to', wsUrl);
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        log('Connected');
        setIsConnected(true);
        setError(null);
        reconnectCountRef.current = 0;
        startHeartbeat();
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          log('Message received:', message.type);

          switch (message.type) {
            case 'connected':
              log('Welcome message:', message.client_id);
              break;

            case 'pong':
              // 心跳响应，不需要处理
              break;

            case 'market_update':
              // 市场数据更新 (节流处理)
              if (message.data) {
                // 后端发送格式: { type: 'market_update', data: [股票数组], timestamp: 时间戳 }
                // 前端期望格式: { stocks: StockData[], timestamp: number }
                const marketData = {
                  stocks: Array.isArray(message.data) ? message.data : [],
                  timestamp: message.timestamp || Date.now(),
                };
                updateDataThrottled(marketData as T);
              }
              break;

            case 'error':
              setError(message.message || 'Unknown error');
              log('Error:', message.message);
              break;

            default:
              log('Unknown message type:', message.type);
          }
        } catch (err) {
          log('Failed to parse message:', err);
        }
      };

      ws.onerror = (event) => {
        log('WebSocket error:', event);
        setError('Connection error');
      };

      ws.onclose = (event) => {
        log('Disconnected:', event.code, event.reason);
        setIsConnected(false);
        stopHeartbeat();

        // 自动重连
        if (maxReconnectAttempts === 0 || reconnectCountRef.current < maxReconnectAttempts) {
          reconnectCountRef.current++;
          log(`Reconnecting in ${reconnectDelay}ms (attempt ${reconnectCountRef.current})...`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectDelay);
        } else {
          setError('Max reconnection attempts reached');
        }
      };

      wsRef.current = ws;
    } catch (err) {
      log('Failed to connect:', err);
      setError('Failed to establish connection');
    }
  }, [endpoint, reconnectDelay, maxReconnectAttempts, startHeartbeat, stopHeartbeat, updateDataThrottled, log]);

  // 断开连接
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    stopHeartbeat();

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setIsConnected(false);
    log('Disconnected manually');
  }, [stopHeartbeat, log]);

  // 发送消息
  const send = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
      log('Message sent:', message);
    } else {
      log('Cannot send message: not connected');
    }
  }, [log]);

  // 订阅频道
  const subscribe = useCallback((channel: string, filters?: any) => {
    send({ type: 'subscribe', channel, filters });
  }, [send]);

  // 取消订阅
  const unsubscribe = useCallback((channel: string) => {
    send({ type: 'unsubscribe', channel });
  }, [send]);

  // 动态设置节流间隔
  const setThrottleInterval = useCallback((interval: number) => {
    setCurrentThrottle(interval);
    log('Throttle interval changed to', interval, 'ms');
  }, [log]);

  // 页面可见性变化处理
  useEffect(() => {
    if (!autoSlowDownOnBlur) return;

    const handleVisibilityChange = () => {
      if (document.hidden) {
        // 页面失焦，降低到 LAZY 模式
        log('Page hidden, switching to LAZY mode');
        setCurrentThrottle(PUSH_INTERVALS.LAZY);
      } else {
        // 页面恢复，恢复到原始节流间隔
        log('Page visible, restoring to', throttle, 'ms');
        setCurrentThrottle(throttle);
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [autoSlowDownOnBlur, throttle, log]);

  // 自动连接
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
      if (throttleTimeoutRef.current) {
        clearTimeout(throttleTimeoutRef.current);
      }
    };
  }, [autoConnect, connect, disconnect]);

  return {
    data,
    isConnected,
    error,
    connect,
    disconnect,
    send,
    subscribe,
    unsubscribe,
    currentThrottle,
    setThrottle: setThrottleInterval,
  };
}
