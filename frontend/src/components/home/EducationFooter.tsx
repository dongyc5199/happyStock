'use client';

import React from 'react';
import Link from 'next/link';
import { 
  BookOpen, 
  TrendingUp, 
  BarChart3, 
  HelpCircle, 
  Sparkles,
  LineChart,
  GraduationCap,
  Lightbulb,
  ChevronRight
} from 'lucide-react';

// 新手指南内容
const beginnerGuides = [
  {
    icon: BookOpen,
    title: '交易基础',
    description: '了解股票交易基本概念、K线图表工具使用方法',
    href: '/learn/trading-basics',
  },
  {
    icon: BarChart3,
    title: 'K线图表工具',
    description: '掌握K线形态、趋势线、支撑阻力位等技术分析工具',
    href: '/learn/chart-tools',
  },
  {
    icon: GraduationCap,
    title: '账户开通指南',
    description: '快速开通虚拟交易账户,领取100万体验金',
    href: '/learn/account-guide',
  },
  {
    icon: Lightbulb,
    title: '风险管理',
    description: '学习仓位管理、止损止盈等风险控制基础知识',
    href: '/learn/risk-management',
  },
];

// 进阶学习内容
const advancedLearning = [
  {
    icon: TrendingUp,
    title: 'Al Brooks 价格行为交易',
    description: '世界顶级价格行为大师的交易方法论与实战技巧',
    href: '/learn/price-action-al-brooks',
    featured: true, // 特色标记
    badge: '🔥 热门',
    highlight: true,
  },
  {
    icon: LineChart,
    title: '技术分析进阶',
    description: '深入学习技术指标、形态学、波浪理论等高级技术',
    href: '/learn/technical-analysis',
  },
  {
    icon: Sparkles,
    title: '量化交易入门',
    description: '了解量化策略开发、回测与实盘交易技巧',
    href: '/learn/quantitative-trading',
  },
  {
    icon: TrendingUp,
    title: '趋势跟踪策略',
    description: '学习如何识别趋势、顺势而为的交易方法',
    href: '/learn/trend-following',
  },
];

// 常见问题
const faqs = [
  {
    icon: HelpCircle,
    title: '账户相关',
    description: '注册、登录、资金管理等账户问题解答',
    href: '/learn/faq/account',
  },
  {
    icon: HelpCircle,
    title: '交易相关',
    description: '下单、持仓、平仓等交易操作问题解答',
    href: '/learn/faq/trading',
  },
  {
    icon: HelpCircle,
    title: '平台功能',
    description: '图表工具、数据查询、实时行情等功能说明',
    href: '/learn/faq/platform',
  },
  {
    icon: HelpCircle,
    title: '技术支持',
    description: '遇到技术问题?查看常见问题或联系客服',
    href: '/learn/faq/support',
  },
];

export default function EducationFooter() {
  return (
    <section className="relative py-20 overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* 背景装饰 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
      </div>

      <div className="container mx-auto px-4 relative z-10">
        {/* 标题区域 */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-white mb-4">
            交易知识学习中心
          </h2>
          <p className="text-lg text-blue-200 max-w-2xl mx-auto">
            从入门到精通,系统化学习股票交易知识,提升交易技能
          </p>
        </div>

        {/* 三栏内容 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          {/* 新手指南 */}
          <div className="space-y-4">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                <BookOpen className="w-5 h-5 text-blue-400" />
              </div>
              <h3 className="text-xl font-bold text-white">新手指南</h3>
            </div>
            <div className="space-y-3">
              {beginnerGuides.map((guide, index) => {
                const Icon = guide.icon;
                return (
                  <Link
                    key={index}
                    href={guide.href}
                    className="group block p-4 rounded-lg bg-white/5 hover:bg-white/10 transition-all duration-300 border border-white/10 hover:border-blue-400/50"
                  >
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                        <Icon className="w-4 h-4 text-blue-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="font-medium text-white mb-1 group-hover:text-blue-300 transition-colors">
                          {guide.title}
                        </h4>
                        <p className="text-sm text-blue-200/70 line-clamp-2">
                          {guide.description}
                        </p>
                      </div>
                      <ChevronRight className="w-4 h-4 text-blue-400 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>

          {/* 进阶学习 */}
          <div className="space-y-4">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-purple-400" />
              </div>
              <h3 className="text-xl font-bold text-white">进阶学习</h3>
            </div>
            <div className="space-y-3">
              {advancedLearning.map((course, index) => {
                const Icon = course.icon;
                return (
                  <Link
                    key={index}
                    href={course.href}
                    className={`group block p-4 rounded-lg transition-all duration-300 border ${
                      course.highlight
                        ? 'bg-gradient-to-br from-yellow-500/10 to-orange-500/10 border-yellow-400/50 hover:border-yellow-400 shadow-lg shadow-yellow-500/20'
                        : 'bg-white/5 hover:bg-white/10 border-white/10 hover:border-purple-400/50'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform ${
                        course.highlight ? 'bg-yellow-500/20' : 'bg-purple-500/20'
                      }`}>
                        <Icon className={`w-4 h-4 ${course.highlight ? 'text-yellow-400' : 'text-purple-400'}`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className={`font-medium group-hover:transition-colors ${
                            course.highlight ? 'text-yellow-300 group-hover:text-yellow-200' : 'text-white group-hover:text-purple-300'
                          }`}>
                            {course.title}
                          </h4>
                          {course.badge && (
                            <span className="text-xs px-2 py-0.5 rounded-full bg-gradient-to-r from-yellow-500 to-orange-500 text-white font-medium">
                              {course.badge}
                            </span>
                          )}
                        </div>
                        <p className={`text-sm line-clamp-2 ${
                          course.highlight ? 'text-yellow-200/80' : 'text-purple-200/70'
                        }`}>
                          {course.description}
                        </p>
                      </div>
                      <ChevronRight className={`w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0 ${
                        course.highlight ? 'text-yellow-400' : 'text-purple-400'
                      }`} />
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>

          {/* 常见问题 */}
          <div className="space-y-4">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                <HelpCircle className="w-5 h-5 text-green-400" />
              </div>
              <h3 className="text-xl font-bold text-white">常见问题</h3>
            </div>
            <div className="space-y-3">
              {faqs.map((faq, index) => {
                const Icon = faq.icon;
                return (
                  <Link
                    key={index}
                    href={faq.href}
                    className="group block p-4 rounded-lg bg-white/5 hover:bg-white/10 transition-all duration-300 border border-white/10 hover:border-green-400/50"
                  >
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 rounded-lg bg-green-500/20 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                        <Icon className="w-4 h-4 text-green-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="font-medium text-white mb-1 group-hover:text-green-300 transition-colors">
                          {faq.title}
                        </h4>
                        <p className="text-sm text-green-200/70 line-clamp-2">
                          {faq.description}
                        </p>
                      </div>
                      <ChevronRight className="w-4 h-4 text-green-400 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>
        </div>

        {/* 大号CTA按钮 */}
        <div className="text-center">
          <Link
            href="/learn"
            className="inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-bold text-lg rounded-xl transition-all duration-300 shadow-lg shadow-blue-500/30 hover:shadow-blue-500/50 hover:scale-105"
          >
            <GraduationCap className="w-6 h-6" />
            <span>进入学习中心</span>
            <ChevronRight className="w-5 h-5" />
          </Link>
          <p className="mt-4 text-sm text-blue-200/60">
            已有 <span className="font-bold text-blue-300">10,000+</span> 用户在这里提升交易技能
          </p>
        </div>
      </div>
    </section>
  );
}
