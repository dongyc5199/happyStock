/**
 * IntegratedHeroSection - 整合的英雄区
 * 
 * 整合了欢迎信息、核心价值主张、快速开始和市场概览
 * 让用户在第一屏就能了解平台的核心价值
 */

'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Shield, LineChart, Zap, ArrowRight, Users } from 'lucide-react';

interface IntegratedHeroSectionProps {
  userCount: number;
}

export function IntegratedHeroSection({ 
  userCount
}: IntegratedHeroSectionProps) {
  const [currentFeature, setCurrentFeature] = useState(0);

  // 定义三个核心特性
  const features = [
    {
      icon: Shield,
      title: '零风险交易',
      description: '虚拟资金，真实体验，不用担心心金损失',
      gradient: 'from-blue-500 to-cyan-500',
      bgGradient: 'from-blue-50 to-cyan-50'
    },
    {
      icon: LineChart,
      title: '真实市场数据',
      description: '模拟 A 股 3000+ 股票，实时行情和 K 线图',
      gradient: 'from-green-500 to-emerald-500',
      bgGradient: 'from-green-50 to-emerald-50'
    },
    {
      icon: Zap,
      title: '即时交易反馈',
      description: '秒级成交，实时查看收益，快速迭代策略',
      gradient: 'from-purple-500 to-pink-500',
      bgGradient: 'from-purple-50 to-pink-50'
    }
  ];

  // 自动切换动画
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentFeature((prev) => (prev + 1) % features.length);
    }, 3000); // 每3秒切换一次

    return () => clearInterval(timer);
  }, [features.length]);

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

          {/* 右侧: 动画切换的核心特性展示 */}
          <div className="relative h-[400px] lg:h-[450px]">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              const isActive = currentFeature === index;
              
              return (
                <div
                  key={index}
                  className={`absolute inset-0 transition-all duration-700 ${
                    isActive 
                      ? 'opacity-100 scale-100 translate-y-0' 
                      : 'opacity-0 scale-95 translate-y-4 pointer-events-none'
                  }`}
                >
                  <div className={`h-full bg-gradient-to-br ${feature.bgGradient} rounded-3xl p-8 lg:p-10 shadow-2xl border border-white/50 backdrop-blur-sm`}>
                    {/* 图标背景 */}
                    <div className={`inline-flex p-4 rounded-2xl bg-gradient-to-br ${feature.gradient} mb-6 shadow-lg`}>
                      <Icon className="w-10 h-10 text-white" />
                    </div>

                    {/* 标题 */}
                    <h3 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
                      {feature.title}
                    </h3>

                    {/* 描述 */}
                    <p className="text-lg text-gray-700 leading-relaxed mb-8">
                      {feature.description}
                    </p>

                    {/* 装饰性图案 */}
                    <div className="absolute bottom-8 right-8 w-32 h-32 opacity-10">
                      <Icon className="w-full h-full" />
                    </div>
                  </div>
                </div>
              );
            })}

            {/* 指示器 */}
            <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 flex gap-2">
              {features.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentFeature(index)}
                  className={`transition-all ${
                    currentFeature === index 
                      ? 'w-8 h-2 bg-blue-600' 
                      : 'w-2 h-2 bg-gray-300 hover:bg-gray-400'
                  } rounded-full`}
                  aria-label={`切换到特性 ${index + 1}`}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
