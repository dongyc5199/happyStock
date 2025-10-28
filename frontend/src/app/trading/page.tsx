'use client';

/**
 * 交易主页 - TradingView 风格布局
 *
 * 布局结构：
 * ┌─────────────────────────────────────────────────────────┐
 * │  Header (账户信息 + 导航)                                │
 * ├──────────────┬──────────────────────┬───────────────────┤
 * │              │                      │                   │
 * │  股票列表    │     K线图表区域       │   交易面板        │
 * │  (左侧栏)    │     (中间主区域)      │   (右侧栏)        │
 * │              │                      │                   │
 * ├──────────────┴──────────────────────┴───────────────────┤
 * │  底部 Tabs: 持仓 | 交易历史 | 订单                       │
 * └─────────────────────────────────────────────────────────┘
 */

import { useEffect, useState, useRef } from 'react';
import { useTradingStore } from '@/stores/tradingStore';
import CandlestickChart from '@/components/trading/CandlestickChart';
import TradePanel from '@/components/trading/TradePanel';
import VirtualMarketStockList from '@/components/trading/VirtualMarketStockList';
import HoldingsList from '@/components/trading/HoldingsList';
import TradeHistory from '@/components/trading/TradeHistory';
import type { Asset, Holding } from '@/types/trading';
import type { Stock } from '@/types/virtual-market';
import { formatCurrency } from '@/lib/utils/format';

type BottomTab = 'holdings' | 'history' | 'orders';

export default function TradingPage() {
  const {
    currentAccount,
    selectedAsset,
    assets,
    holdings,
    recentTrades,
    loading,
    error,
    fetchAccount,
    fetchHoldings,
    fetchAssets,
    fetchTradeHistory,
    setSelectedAsset,
  } = useTradingStore();

  const [activeTab, setActiveTab] = useState<BottomTab>('holdings');
  const [bottomHeight, setBottomHeight] = useState(192); // 默认 192px (h-48)
  const [isDragging, setIsDragging] = useState(false);
  const [isBottomCollapsed, setIsBottomCollapsed] = useState(false);
  const [savedBottomHeight, setSavedBottomHeight] = useState(192); // 保存展开时的高度

  // 保存图表的 resize 方法
  const chartResizeRef = useRef<(() => void) | null>(null);

  // 初始化数据
  useEffect(() => {
    // 使用测试账户 ID = 1
    fetchAccount(1);
    fetchHoldings(1);
    fetchAssets();
    fetchTradeHistory(1);
  }, []);

  // 处理拖动
  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  useEffect(() => {
    if (!isDragging) return;

    const handleMouseMove = (e: MouseEvent) => {
      const windowHeight = window.innerHeight;
      const headerHeight = 56; // 顶部导航栏高度
      const newBottomHeight = windowHeight - e.clientY;

      // 限制最小和最大高度
      const minHeight = 100;
      const maxHeight = windowHeight - headerHeight - 200;

      if (newBottomHeight >= minHeight && newBottomHeight <= maxHeight) {
        setBottomHeight(newBottomHeight);
      }
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging]);

  // 选择虚拟市场股票
  const handleSelectVirtualStock = (stock: Stock) => {
    // 将虚拟市场Stock转换为Asset类型
    const asset: Asset = {
      id: 0, // 虚拟市场股票没有id，使用0
      symbol: stock.symbol,
      name: stock.name,
      asset_type: 'stock',
      current_price: stock.current_price.toString(),
      change_percent: stock.change_pct.toString(),
      volume: stock.volume,
      market_cap: stock.market_cap?.toString() || '0',
      is_active: stock.is_active === 1,
      created_at: stock.created_at,
      updated_at: stock.updated_at,
    };
    setSelectedAsset(asset);
  };

  // 选择持仓行（切换到该股票并切换到卖出模式）
  const handleSelectHolding = (holding: Holding) => {
    const asset = assets.find((a) => a.symbol === holding.asset_symbol);
    if (asset) {
      setSelectedAsset(asset);
    }
  };

  // 切换底部区域折叠状态
  const toggleBottomCollapse = () => {
    if (isBottomCollapsed) {
      // 展开：恢复之前的高度
      setBottomHeight(savedBottomHeight);
      setIsBottomCollapsed(false);
    } else {
      // 收起：保存当前高度，然后设置为最小高度（只显示 tabs 标签）
      setSavedBottomHeight(bottomHeight);
      setBottomHeight(40); // 只显示 tabs 栏的高度
      setIsBottomCollapsed(true);
    }
  };

  // 监听收起/展开状态变化，自动调用 resize
  useEffect(() => {
    // 延迟调用图表 resize，等待 DOM 更新和过渡动画完成
    const timer = setTimeout(() => {
      if (chartResizeRef.current) {
        chartResizeRef.current();
      }
    }, 350); // 等待过渡动画完成（transition-all duration-300 + 50ms 缓冲）

    return () => clearTimeout(timer);
  }, [isBottomCollapsed]); // 只在收起/展开状态变化时触发，避免拖动时频繁调用

  return (
    <div className="h-screen flex flex-col bg-[#0a0e14] text-white">
      {/* 顶部导航栏 */}
      <header className="h-14 bg-[#131722] border-b border-[#2a2e39] flex items-center px-4">
        <div className="flex items-center space-x-6">
          <h1 className="text-xl font-bold text-white">HappyStock</h1>

          {/* 账户信息 */}
          {currentAccount && (
            <div className="flex items-center space-x-4 text-sm">
              <div>
                <span className="text-gray-400">账户:</span>
                <span className="ml-2 text-white">{currentAccount.account_name}</span>
              </div>
              <div>
                <span className="text-gray-400">可用资金:</span>
                <span className="ml-2 text-green-400 font-semibold">
                  ¥{parseFloat(currentAccount.current_balance).toLocaleString('zh-CN', { minimumFractionDigits: 2 })}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* 右侧快捷操作 */}
        <div className="ml-auto flex items-center space-x-4">
          <button className="px-4 py-1.5 bg-[#1e2532] hover:bg-[#252b3b] rounded text-sm transition-colors">
            账户管理
          </button>
        </div>
      </header>

      {/* 主内容区域 */}
      <div className="flex-1 flex overflow-hidden">
        {/* 左侧：虚拟市场股票列表 */}
        <aside className="w-64 bg-[#131722] border-r border-[#2a2e39] flex flex-col">
          <VirtualMarketStockList
            onSelectStock={handleSelectVirtualStock}
            selectedSymbol={selectedAsset?.symbol}
          />
        </aside>

        {/* 中间：图表区域 */}
        <main className="flex-1 flex flex-col bg-[#0a0e14]">
          {/* K线图表区域 */}
          <div className="flex-1 min-h-0">
            <CandlestickChart
              assetSymbol={selectedAsset?.symbol || null}
              onChartReady={(resize) => {
                chartResizeRef.current = resize;
              }}
            />
          </div>

          {/* 可拖动分隔条 */}
          <div
            onMouseDown={handleMouseDown}
            className={`h-1 bg-[#2a2e39] hover:bg-blue-500 cursor-ns-resize transition-colors relative group ${
              isDragging ? 'bg-blue-500' : ''
            }`}
          >
            {/* 拖动提示图标 */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-8 h-0.5 bg-gray-600 group-hover:bg-blue-400 transition-colors"></div>
            </div>
          </div>

          {/* 底部 Tabs 区域 */}
          <div
            style={{ height: `${bottomHeight}px` }}
            className="bg-[#131722] border-t border-[#2a2e39] flex flex-col flex-shrink-0 transition-all duration-300"
          >
            {/* Tabs 切换 */}
            <div className="flex border-b border-[#2a2e39]">
              <button
                onClick={() => setActiveTab('holdings')}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  activeTab === 'holdings'
                    ? 'text-white border-b-2 border-blue-500'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                持仓
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  activeTab === 'history'
                    ? 'text-white border-b-2 border-blue-500'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                交易历史
              </button>
              <button
                onClick={() => setActiveTab('orders')}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  activeTab === 'orders'
                    ? 'text-white border-b-2 border-blue-500'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                订单
              </button>

              {/* 收起/展开按钮 */}
              <button
                onClick={toggleBottomCollapse}
                className="ml-auto px-3 py-2 text-gray-400 hover:text-white transition-colors"
                title={isBottomCollapsed ? '展开' : '收起'}
              >
                <svg
                  className={`w-4 h-4 transition-transform duration-300 ${
                    isBottomCollapsed ? 'rotate-180' : ''
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </button>
            </div>

            {/* Tabs 内容 */}
            <div className={`flex-1 p-2 overflow-y-auto ${isBottomCollapsed ? 'hidden' : ''}`}>
              {activeTab === 'holdings' && (
                <HoldingsList holdings={holdings} onSelectHolding={handleSelectHolding} />
              )}
              {activeTab === 'history' && <TradeHistory trades={recentTrades} />}
              {activeTab === 'orders' && (
                <div className="flex items-center justify-center h-full text-gray-500">
                  订单功能即将推出
                </div>
              )}
            </div>
          </div>
        </main>

        {/* 右侧：交易面板 */}
        <aside className="w-80 bg-[#131722] border-l border-[#2a2e39]">
          <TradePanel />
        </aside>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="fixed top-20 right-4 bg-red-600 text-white px-4 py-3 rounded shadow-lg">
          {error}
        </div>
      )}

      {/* Loading 提示 */}
      {loading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-[#131722] px-6 py-4 rounded-lg">
            <div className="text-white">加载中...</div>
          </div>
        </div>
      )}
    </div>
  );
}
