'use client';

import Link from 'next/link';
import { BarChart3, Brain, Users, ArrowRight } from 'lucide-react';

/**
 * FeatureShowcase Component
 * 
 * 展示平台三大核心功能:
 * 1. 专业图表工具 - Professional charting tools
 * 2. AI交易助手 - AI trading assistant
 * 3. 投资社交平台 - Investment social platform
 * 
 * US4: 了解平台三大核心功能 (P2)
 */

interface Feature {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  highlights: string[];
  href: string;
  available: boolean;
  badge?: string;
  color: {
    bg: string;
    icon: string;
    hover: string;
    border: string;
  };
}

const FEATURES: Feature[] = [
  {
    icon: BarChart3,
    title: '专业图表工具',
    description: '集成 TradingView 级别的专业K线图表，支持多种技术指标和画线工具',
    highlights: [
      '20+ 技术指标 (MA, MACD, RSI, KDJ...)',
      '多周期切换 (分时/日K/周K/月K)',
      '画线工具 (趋势线/通道/斐波那契)',
      '实时数据推送，零延迟刷新',
    ],
    href: '/virtual-market',
    available: true,
    color: {
      bg: 'from-blue-50 to-blue-100',
      icon: 'text-blue-600',
      hover: 'hover:shadow-blue-200',
      border: 'border-blue-200',
    },
  },
  {
    icon: Brain,
    title: 'AI交易助手',
    description: '基于机器学习的智能交易建议，帮助您做出更明智的投资决策',
    highlights: [
      'AI驱动的市场分析与预测',
      '个性化交易策略推荐',
      '风险评估与仓位管理',
      '自动止损止盈提醒',
    ],
    href: '#',
    available: false,
    badge: '即将推出',
    color: {
      bg: 'from-purple-50 to-purple-100',
      icon: 'text-purple-600',
      hover: 'hover:shadow-purple-200',
      border: 'border-purple-200',
    },
  },
  {
    icon: Users,
    title: '投资社交平台',
    description: '与其他投资者交流心得，分享策略，共同成长',
    highlights: [
      '投资组合分享与讨论',
      '跟随优秀投资者操作',
      '实时交易动态订阅',
      '投资教育社区',
    ],
    href: '#',
    available: false,
    badge: '敬请期待',
    color: {
      bg: 'from-green-50 to-green-100',
      icon: 'text-green-600',
      hover: 'hover:shadow-green-200',
      border: 'border-green-200',
    },
  },
];

export default function FeatureShowcase() {
  return (
    <section className="py-16 bg-white">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-slate-900 mb-4">
            三大核心功能，助力投资成长
          </h2>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            从专业工具到智能助手，再到社交学习，全方位提升您的投资能力
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {FEATURES.map((feature) => {
            const Icon = feature.icon;
            const cardContent = (
              <>
                {/* Badge for unavailable features */}
                {feature.badge && (
                  <div className="absolute top-4 right-4 px-3 py-1 bg-white/90 backdrop-blur-sm rounded-full text-xs font-semibold text-slate-700 shadow-sm">
                    {feature.badge}
                  </div>
                )}

                {/* Icon */}
                <div className={`
                  w-16 h-16 bg-white rounded-xl flex items-center justify-center mb-6 
                  shadow-md group-hover:shadow-lg transition-shadow duration-300
                  ${feature.available ? 'group-hover:scale-110' : ''}
                `}>
                  <Icon className={`w-8 h-8 ${feature.color.icon}`} />
                </div>

                {/* Title */}
                <h3 className="text-2xl font-bold text-slate-900 mb-3">
                  {feature.title}
                </h3>

                {/* Description */}
                <p className="text-slate-700 mb-6 leading-relaxed">
                  {feature.description}
                </p>

                {/* Highlights */}
                <ul className="space-y-2 mb-6">
                  {feature.highlights.map((highlight, index) => (
                    <li key={index} className="flex items-start gap-2 text-sm text-slate-600">
                      <svg
                        className={`w-5 h-5 ${feature.color.icon} flex-shrink-0 mt-0.5`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M5 13l4 4L19 7"
                        />
                      </svg>
                      <span>{highlight}</span>
                    </li>
                  ))}
                </ul>

                {/* CTA */}
                {feature.available ? (
                  <div className="flex items-center gap-2 text-slate-900 font-semibold group-hover:gap-3 transition-all duration-300">
                    <span>立即体验</span>
                    <ArrowRight className="w-5 h-5" />
                  </div>
                ) : (
                  <div className="text-sm text-slate-500 font-medium">
                    功能开发中...
                  </div>
                )}

                {/* Decorative corner */}
                <div className={`
                  absolute bottom-0 right-0 w-24 h-24 bg-gradient-to-tl ${feature.color.bg}
                  rounded-tl-full opacity-30
                `} />
              </>
            );

            const cardClassName = `
              relative group bg-gradient-to-br ${feature.color.bg} 
              rounded-2xl p-8 border-2 ${feature.color.border}
              transition-all duration-300
              ${feature.available 
                ? `${feature.color.hover} hover:scale-105 hover:shadow-xl cursor-pointer` 
                : 'opacity-75 cursor-not-allowed'
              }
            `;
            
            return feature.available ? (
              <Link
                key={feature.title}
                href={feature.href}
                className={cardClassName}
              >
                {cardContent}
              </Link>
            ) : (
              <div
                key={feature.title}
                className={cardClassName}
              >
                {cardContent}
              </div>
            );
          })}
        </div>

        {/* Bottom CTA */}
        <div className="mt-12 text-center">
          <p className="text-slate-600 mb-4">
            更多功能持续开发中，敬请期待
          </p>
          <Link
            href="/virtual-market"
            className="inline-flex items-center gap-2 px-6 py-3 bg-slate-900 text-white font-semibold rounded-lg hover:bg-slate-800 transition-colors duration-300"
          >
            <span>探索现有功能</span>
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </div>
    </section>
  );
}
