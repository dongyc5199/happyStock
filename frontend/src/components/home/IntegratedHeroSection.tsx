/**
 * IntegratedHeroSection - 整合的英雄区
 * 
 * 整合了欢迎信息、核心价值主张、快速开始和市场概览
 * 让用户在第一屏就能了解平台的核心价值
 */

import Link from 'next/link';
import { TrendingUp, Shield, LineChart, Zap, ArrowRight, Users } from 'lucide-react';
import type { MarketOverview } from '@/types/virtual-market';

interface IntegratedHeroSectionProps {
  userCount: number;
  marketOverview: MarketOverview | null;
  loading?: boolean;
}

export function IntegratedHeroSection({ 
  userCount, 
  marketOverview,
  loading = false 
}: IntegratedHeroSectionProps) {
  return (
    <div className="relative bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 text-gray-900 overflow-hidden">
      {/* 背景装饰 */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-100/50 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-100/50 rounded-full blur-3xl"></div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 lg:py-24">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* 左侧: 欢迎信息 + 核心价值 */}
          <div className="space-y-8">
            {/* 欢迎标题 */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-blue-600">
                <Users className="w-5 h-5" />
                <span className="text-sm font-medium">已有 {userCount.toLocaleString()} 位用户加入</span>
              </div>
              
              <h1 className="text-4xl lg:text-5xl font-bold leading-tight text-gray-900">
                零风险探索
                <br />
                <span className="text-blue-600">真实市场交易</span>
              </h1>
              
              <p className="text-xl text-gray-700 leading-relaxed">
                happyStock 提供完全模拟的 A 股交易环境
                <br />
                让您在无风险的环境中学习投资、积累经验
              </p>
            </div>

            {/* 3大核心特性 */}
            <div className="grid grid-cols-1 gap-4">
              <div className="flex items-start gap-3 bg-white/80 backdrop-blur-sm rounded-lg p-4 shadow-sm border border-blue-100">
                <div className="flex-shrink-0 w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Shield className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg text-gray-900">零风险交易</h3>
                  <p className="text-sm text-gray-600 mt-1">虚拟资金,真实体验,不用担心资金损失</p>
                </div>
              </div>

              <div className="flex items-start gap-3 bg-white/80 backdrop-blur-sm rounded-lg p-4 shadow-sm border border-indigo-100">
                <div className="flex-shrink-0 w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
                  <LineChart className="w-5 h-5 text-indigo-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg text-gray-900">真实市场数据</h3>
                  <p className="text-sm text-gray-600 mt-1">模拟 A 股 3000+ 股票,实时行情和 K 线图</p>
                </div>
              </div>

              <div className="flex items-start gap-3 bg-white/80 backdrop-blur-sm rounded-lg p-4 shadow-sm border border-purple-100">
                <div className="flex-shrink-0 w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                  <Zap className="w-5 h-5 text-purple-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg text-gray-900">即时交易反馈</h3>
                  <p className="text-sm text-gray-600 mt-1">秒级成交,实时查看收益,快速迭代策略</p>
                </div>
              </div>
            </div>

            {/* CTA 按钮 */}
            <div className="flex flex-wrap gap-4">
              <Link
                href="/virtual-market"
                className="inline-flex items-center gap-2 px-8 py-4 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors shadow-lg hover:shadow-xl"
              >
                开始交易
                <ArrowRight className="w-5 h-5" />
              </Link>
              
              <Link
                href="/virtual-market/indices"
                className="inline-flex items-center gap-2 px-8 py-4 bg-white text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition-colors border border-gray-200 shadow-sm"
              >
                查看市场行情
              </Link>
            </div>
          </div>

          {/* 右侧: 实时市场数据卡片 */}
          <div className="space-y-4">
            {loading ? (
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 animate-pulse border border-gray-200">
                <div className="h-8 bg-gray-200 rounded w-1/2 mb-6"></div>
                <div className="space-y-4">
                  <div className="h-6 bg-gray-200 rounded"></div>
                  <div className="h-6 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-6 bg-gray-200 rounded w-5/6"></div>
                </div>
              </div>
            ) : marketOverview ? (
              <div className="bg-white/90 backdrop-blur-md rounded-2xl p-6 border border-blue-100 shadow-2xl">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-bold text-gray-900">实时市场数据</h3>
                  <div className="flex items-center gap-1 text-sm">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-gray-600">实时更新</span>
                  </div>
                </div>

                <div className="space-y-4">
                  {/* 市场状态 */}
                  <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg border border-blue-100">
                    <span className="text-gray-700">市场状态</span>
                    <span className={`font-semibold ${
                      marketOverview.market_state === 'open' ? 'text-green-600' : 'text-gray-600'
                    }`}>
                      {marketOverview.market_state === 'open' ? '开市' : '休市'}
                    </span>
                  </div>

                  {/* 统计数据 */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-green-50 rounded-lg border border-green-100">
                      <div className="text-sm text-gray-600 mb-1">上涨股票</div>
                      <div className="text-2xl font-bold text-green-600">
                        {marketOverview.rising || 0}
                      </div>
                    </div>
                    
                    <div className="p-4 bg-red-50 rounded-lg border border-red-100">
                      <div className="text-sm text-gray-600 mb-1">下跌股票</div>
                      <div className="text-2xl font-bold text-red-600">
                        {marketOverview.falling || 0}
                      </div>
                    </div>

                    <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                      <div className="text-sm text-gray-600 mb-1">平盘股票</div>
                      <div className="text-2xl font-bold text-gray-700">
                        {marketOverview.unchanged || 0}
                      </div>
                    </div>

                    <div className="p-4 bg-purple-50 rounded-lg border border-purple-100">
                      <div className="text-sm text-gray-600 mb-1">成交量</div>
                      <div className="text-lg font-bold text-gray-900">
                        {marketOverview.total_volume
                          ? `${(marketOverview.total_volume / 1e8).toFixed(2)}亿`
                          : '-'}
                      </div>
                    </div>
                  </div>

                  {/* 涨跌比 */}
                  <div className="p-4 bg-indigo-50 rounded-lg border border-indigo-100">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-gray-600">市场情绪</span>
                      <span className="text-sm font-medium text-gray-900">
                        {marketOverview.rising > marketOverview.falling 
                          ? '多头市场' 
                          : marketOverview.rising < marketOverview.falling
                          ? '空头市场'
                          : '平衡市场'}
                      </span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-green-500 to-red-500 transition-all duration-500"
                        style={{
                          width: `${
                            ((marketOverview.rising || 0) / 
                            ((marketOverview.rising || 0) + (marketOverview.falling || 1))) * 100
                          }%`
                        }}
                      ></div>
                    </div>
                  </div>
                </div>

                <Link
                  href="/virtual-market"
                  className="mt-6 w-full inline-flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors shadow-md"
                >
                  查看完整市场数据
                  <TrendingUp className="w-4 h-4" />
                </Link>
              </div>
            ) : (
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 text-center border border-gray-200">
                <p className="text-gray-600">市场数据加载中...</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
