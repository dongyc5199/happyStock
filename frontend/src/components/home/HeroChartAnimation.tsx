/**
 * HeroChartAnimation Component - Animated chart carousel
 * 
 * Three rotating scenes:
 * 1. Real-time market data (K-line, volume, price changes)
 * 2. Professional tools in action (trend lines, indicators, AI)
 * 3. Learning and improvement (trading simulation)
 */

'use client';

import React, { useState, useEffect } from 'react';
import { TrendingUp, Activity, BarChart3, Brain, Target, Zap } from 'lucide-react';

export function HeroChartAnimation() {
  const [activeScene, setActiveScene] = useState(0);
  
  // Auto-rotate scenes every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveScene((prev) => (prev + 1) % 3);
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="relative max-w-lg mx-auto">
      {/* Animated gradient glow */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 rounded-3xl opacity-20 blur-3xl animate-pulse" />
      
      {/* Main Chart Card - Fixed height to prevent jumping */}
      <div className="relative bg-gradient-to-br from-gray-50 to-white dark:from-gray-900 dark:to-gray-800 rounded-3xl shadow-2xl p-6 border border-gray-200 dark:border-gray-700 overflow-hidden h-[520px]">
        
        {/* Scene Indicators */}
        <div className="flex justify-center gap-2 mb-4 relative z-20">
          {[0, 1, 2].map((i) => (
            <button
              key={i}
              onClick={() => setActiveScene(i)}
              className={`h-1.5 rounded-full transition-all duration-500 ease-out ${
                activeScene === i ? 'w-8 bg-blue-500' : 'w-1.5 bg-gray-300 dark:bg-gray-600 hover:bg-gray-400 dark:hover:bg-gray-500'
              }`}
              aria-label={`切换到场景 ${i + 1}`}
            />
          ))}
        </div>

        {/* Scene 1: Real-time Market Data */}
        <div className={`absolute inset-6 transition-opacity duration-700 ease-in-out flex flex-col ${activeScene === 0 ? 'opacity-100 z-10' : 'opacity-0 z-0 pointer-events-none'}`}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">实时行情数据</span>
            </div>
            <div className="flex items-center gap-2 px-3 py-1 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <TrendingUp className="w-4 h-4 text-green-600" />
              <span className="text-sm font-bold text-green-600">+5.23%</span>
            </div>
          </div>

          {/* K-line Chart */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-4 mb-3 border border-gray-100 dark:border-gray-700 flex-1">
            <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">K线图</div>
            <div className="h-32 flex items-end justify-around gap-1">
              {[
                { h: 85, l: 60, o: 70, c: 80, up: true },
                { h: 90, l: 75, o: 80, c: 78, up: false },
                { h: 95, l: 70, o: 78, c: 90, up: true },
                { h: 92, l: 82, o: 90, c: 85, up: false },
                { h: 88, l: 80, o: 85, c: 87, up: true },
                { h: 95, l: 83, o: 87, c: 92, up: true },
              ].map((k, i) => (
                <div key={i} className="flex-1 relative flex flex-col items-center justify-end">
                  <div 
                    className="w-px bg-gray-400"
                    style={{ height: `${k.h - k.l}%`, marginBottom: `${k.l}%` }}
                  />
                  <div 
                    className={`absolute w-full ${k.up ? 'bg-red-500' : 'bg-green-500'} transition-all duration-700`}
                    style={{ 
                      height: `${Math.abs(k.c - k.o)}%`,
                      bottom: `${Math.min(k.o, k.c)}%`,
                      animationDelay: `${i * 100}ms`,
                    }}
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Volume */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-4 mb-3 border border-gray-100 dark:border-gray-700">
            <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">成交量</div>
            <div className="flex items-end justify-around gap-1 h-12">
              {[40, 60, 35, 70, 50, 80].map((h, i) => (
                <div 
                  key={i}
                  className="flex-1 bg-gradient-to-t from-blue-400 to-blue-500 rounded-t transition-all duration-500"
                  style={{ 
                    height: `${h}%`,
                    animationDelay: `${i * 100}ms`,
                  }}
                />
              ))}
            </div>
          </div>

          {/* Real-time Stats */}
          <div className="grid grid-cols-3 gap-2">
            <div className="text-center p-2 bg-blue-50 dark:bg-blue-900/20 rounded">
              <div className="text-xs text-gray-600 dark:text-gray-400">最高</div>
              <div className="text-sm font-bold text-blue-600">105.32</div>
            </div>
            <div className="text-center p-2 bg-purple-50 dark:bg-purple-900/20 rounded">
              <div className="text-xs text-gray-600 dark:text-gray-400">最低</div>
              <div className="text-sm font-bold text-purple-600">98.76</div>
            </div>
            <div className="text-center p-2 bg-pink-50 dark:bg-pink-900/20 rounded">
              <div className="text-xs text-gray-600 dark:text-gray-400">成交</div>
              <div className="text-sm font-bold text-pink-600">2.5亿</div>
            </div>
          </div>
        </div>

        {/* Scene 2: Professional Tools */}
        <div className={`absolute inset-6 transition-opacity duration-700 ease-in-out flex flex-col ${activeScene === 1 ? 'opacity-100 z-10' : 'opacity-0 z-0 pointer-events-none'}`}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-purple-500" />
              <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">专业图表工具</span>
            </div>
            <div className="flex gap-1">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
              <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }} />
              <div className="w-2 h-2 bg-pink-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }} />
            </div>
          </div>

          {/* Chart with Tools */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-4 mb-3 border border-gray-100 dark:border-gray-700 relative flex-1">
            {/* Base Chart */}
            <svg className="w-full h-full" viewBox="0 0 300 200">
              {/* Price Line */}
              <path
                d="M 10 150 Q 50 120, 80 140 T 140 100 T 200 120 T 260 80 T 290 70"
                fill="none"
                stroke="url(#gradient)"
                strokeWidth="3"
                className="animate-pulse"
              />
              {/* Gradient */}
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#3b82f6" />
                  <stop offset="50%" stopColor="#a855f7" />
                  <stop offset="100%" stopColor="#ec4899" />
                </linearGradient>
              </defs>
              
              {/* Trend Line */}
              <line x1="30" y1="160" x2="270" y2="60" stroke="#10b981" strokeWidth="2" strokeDasharray="5,5" className="animate-pulse" />
              
              {/* Support/Resistance Lines */}
              <line x1="0" y1="130" x2="300" y2="130" stroke="#f59e0b" strokeWidth="1" strokeDasharray="3,3" opacity="0.5" />
              <line x1="0" y1="90" x2="300" y2="90" stroke="#ef4444" strokeWidth="1" strokeDasharray="3,3" opacity="0.5" />
            </svg>

            {/* Tool Annotations */}
            <div className="absolute top-4 right-4 space-y-2">
              <div className="flex items-center gap-2 text-xs bg-green-50 dark:bg-green-900/30 px-2 py-1 rounded animate-pulse">
                <div className="w-3 h-0.5 bg-green-500" />
                <span className="text-green-700 dark:text-green-300">趋势线</span>
              </div>
              <div className="flex items-center gap-2 text-xs bg-yellow-50 dark:bg-yellow-900/30 px-2 py-1 rounded animate-pulse" style={{ animationDelay: '0.3s' }}>
                <div className="w-3 h-0.5 bg-yellow-500 border-t border-dashed" />
                <span className="text-yellow-700 dark:text-yellow-300">支撑位</span>
              </div>
              <div className="flex items-center gap-2 text-xs bg-red-50 dark:bg-red-900/30 px-2 py-1 rounded animate-pulse" style={{ animationDelay: '0.6s' }}>
                <div className="w-3 h-0.5 bg-red-500 border-t border-dashed" />
                <span className="text-red-700 dark:text-red-300">阻力位</span>
              </div>
            </div>
          </div>

          {/* AI Assistant */}
          <div className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-xl p-4 border border-purple-200 dark:border-purple-700">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-purple-500 rounded-lg">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1">
                <div className="text-sm font-semibold text-purple-900 dark:text-purple-100 mb-1">AI 智能分析</div>
                <div className="text-xs text-purple-700 dark:text-purple-300">
                  检测到上升趋势，建议关注 98.5 支撑位，目标位 108.0
                </div>
                <div className="flex gap-2 mt-2">
                  <span className="text-xs px-2 py-1 bg-purple-200 dark:bg-purple-800 text-purple-900 dark:text-purple-100 rounded">趋势向上</span>
                  <span className="text-xs px-2 py-1 bg-purple-200 dark:bg-purple-800 text-purple-900 dark:text-purple-100 rounded">建议持有</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Scene 3: Learning & Improvement */}
        <div className={`absolute inset-6 transition-opacity duration-700 ease-in-out flex flex-col ${activeScene === 2 ? 'opacity-100 z-10' : 'opacity-0 z-0 pointer-events-none'}`}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Target className="w-5 h-5 text-blue-500" />
              <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">模拟交易学习</span>
            </div>
            <div className="flex items-center gap-1 px-2 py-1 bg-green-50 dark:bg-green-900/20 rounded">
              <Zap className="w-3 h-3 text-green-600" />
              <span className="text-xs font-bold text-green-600">提升中</span>
            </div>
          </div>

          {/* Trading Simulation */}
          <div className="flex flex-col gap-3 flex-1">
            {/* Trade Entry */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-3 border border-gray-100 dark:border-gray-700">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs text-gray-500 dark:text-gray-400">模拟交易</span>
                <span className="text-xs px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-600 rounded">买入</span>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-semibold text-gray-900 dark:text-white">浦发银行</div>
                  <div className="text-xs text-gray-500">SH600000</div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-bold text-gray-900 dark:text-white">¥10.25</div>
                  <div className="text-xs text-green-600">1000 股</div>
                </div>
              </div>
            </div>

            {/* Performance Chart */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-3 border border-gray-100 dark:border-gray-700 flex-1">
              <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">收益曲线</div>
              <div className="h-24 flex items-end justify-around gap-0.5">
                {[100, 102, 98, 103, 105, 107, 104, 108, 112, 110, 115].map((val, i) => (
                  <div 
                    key={i}
                    className={`flex-1 rounded-t transition-all duration-500 ${
                      val >= 100 ? 'bg-gradient-to-t from-green-400 to-green-500' : 'bg-gradient-to-t from-red-400 to-red-500'
                    }`}
                    style={{ 
                      height: `${val - 85}%`,
                      animationDelay: `${i * 50}ms`,
                    }}
                  />
                ))}
              </div>
            </div>

            {/* Learning Stats */}
            <div className="grid grid-cols-3 gap-2">
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-lg p-3 text-center border border-blue-200 dark:border-blue-700">
                <div className="text-xs text-blue-600 dark:text-blue-400 mb-1">成功率</div>
                <div className="text-xl font-bold text-blue-700 dark:text-blue-300">68%</div>
                <TrendingUp className="w-4 h-4 text-blue-600 mx-auto mt-1" />
              </div>
              <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-lg p-3 text-center border border-green-200 dark:border-green-700">
                <div className="text-xs text-green-600 dark:text-green-400 mb-1">总收益</div>
                <div className="text-xl font-bold text-green-700 dark:text-green-300">+15%</div>
                <Activity className="w-4 h-4 text-green-600 mx-auto mt-1" />
              </div>
              <div className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-lg p-3 text-center border border-purple-200 dark:border-purple-700">
                <div className="text-xs text-purple-600 dark:text-purple-400 mb-1">交易次数</div>
                <div className="text-xl font-bold text-purple-700 dark:text-purple-300">24</div>
                <BarChart3 className="w-4 h-4 text-purple-600 mx-auto mt-1" />
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* Floating Scene Labels */}
      <div className="absolute -bottom-4 left-1/2 -translate-x-1/2 flex gap-2">
        <div className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-500 ease-out backdrop-blur-sm ${
          activeScene === 0 
            ? 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300 shadow-lg scale-110' 
            : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 opacity-60 hover:opacity-100'
        }`}>
          实时行情
        </div>
        <div className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-500 ease-out backdrop-blur-sm ${
          activeScene === 1 
            ? 'bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300 shadow-lg scale-110' 
            : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 opacity-60 hover:opacity-100'
        }`}>
          专业工具
        </div>
        <div className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-500 ease-out backdrop-blur-sm ${
          activeScene === 2 
            ? 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 shadow-lg scale-110' 
            : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 opacity-60 hover:opacity-100'
        }`}>
          模拟学习
        </div>
      </div>
    </div>
  );
}
