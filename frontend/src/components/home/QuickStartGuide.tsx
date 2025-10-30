'use client';

import Link from 'next/link';
import { UserPlus, TrendingUp, Zap, ArrowRight } from 'lucide-react';

/**
 * QuickStartGuide Component
 * 
 * 展示3步快速开始流程,引导新用户快速上手:
 * 1. 创建账户 (注册/虚拟账户)
 * 2. 查看市场 (浏览股票行情)
 * 3. 开始交易 (下单买卖)
 * 
 * US3: 快速开始第一个交易体验 (P2)
 */

interface Step {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  number: number;
}

const QUICK_START_STEPS: Step[] = [
  {
    icon: UserPlus,
    title: '创建账户',
    description: '免费注册即可获得虚拟资金,无需真实投入',
    number: 1,
  },
  {
    icon: TrendingUp,
    title: '查看市场',
    description: '实时行情更新,100只股票任你选择',
    number: 2,
  },
  {
    icon: Zap,
    title: '开始交易',
    description: '模拟交易环境,零风险练习投资策略',
    number: 3,
  },
];

export default function QuickStartGuide() {
  return (
    <section className="py-16 bg-gradient-to-b from-white to-slate-50">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-slate-900 mb-4">
            3步开启您的投资之旅
          </h2>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            无需复杂操作,即刻体验专业级模拟交易平台
          </p>
        </div>

        {/* Steps Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          {QUICK_START_STEPS.map((step, index) => {
            const Icon = step.icon;
            return (
              <div
                key={step.number}
                className="relative group"
              >
                {/* Connection Line (desktop only) */}
                {index < QUICK_START_STEPS.length - 1 && (
                  <div className="hidden md:block absolute top-12 left-[60%] w-[80%] h-0.5 bg-gradient-to-r from-blue-300 to-transparent z-0" />
                )}

                {/* Step Card */}
                <div className="relative bg-white rounded-xl p-8 shadow-sm hover:shadow-md transition-all duration-300 border border-slate-200 group-hover:border-blue-300 z-10">
                  {/* Step Number Badge */}
                  <div className="absolute -top-4 -right-4 w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center text-white font-bold text-lg shadow-lg">
                    {step.number}
                  </div>

                  {/* Icon */}
                  <div className="w-16 h-16 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                    <Icon className="w-8 h-8 text-blue-600" />
                  </div>

                  {/* Content */}
                  <h3 className="text-xl font-semibold text-slate-900 mb-3">
                    {step.title}
                  </h3>
                  <p className="text-slate-600 leading-relaxed">
                    {step.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <Link
            href="/virtual-market"
            className="inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all duration-300 shadow-lg hover:shadow-xl hover:scale-105 group"
          >
            <span className="text-lg">开始体验</span>
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-300" />
          </Link>

          {/* Supporting Text */}
          <p className="mt-4 text-sm text-slate-500">
            无需下载,立即在线体验 • 完全免费 • 无风险交易
          </p>
        </div>

        {/* Stats Bar */}
        <div className="mt-12 pt-8 border-t border-slate-200">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            <div>
              <div className="text-2xl font-bold text-blue-600">100+</div>
              <div className="text-sm text-slate-600 mt-1">可交易股票</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-600">1,000,000</div>
              <div className="text-sm text-slate-600 mt-1">虚拟初始资金</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-600">3秒</div>
              <div className="text-sm text-slate-600 mt-1">实时数据更新</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-600">24/7</div>
              <div className="text-sm text-slate-600 mt-1">全天候交易</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
