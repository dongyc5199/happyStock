/**
 * QuickActionsSection - 快速操作和教育资源
 * 
 * 整合了快速导航、功能特性和投资教育内容
 */

import Link from 'next/link';
import {
  TrendingUp,
  BarChart3,
  PieChart,
  BookOpen,
  GraduationCap,
  Lightbulb,
  ArrowRight,
} from 'lucide-react';

export function QuickActionsSection() {
  const mainActions = [
    {
      icon: TrendingUp,
      title: '开始交易',
      description: '进入虚拟交易平台,实时买卖股票',
      href: '/virtual-market',
      color: 'blue',
      highlight: true,
    },
    {
      icon: BarChart3,
      title: '指数看板',
      description: '查看主要指数走势和行业板块表现',
      href: '/virtual-market/indices',
      color: 'indigo',
    },
    {
      icon: PieChart,
      title: '板块分析',
      description: '深入了解各行业板块的投资机会',
      href: '/virtual-market/sectors',
      color: 'purple',
    },
  ];

const educationResources = [
  {
    icon: BookOpen,
    title: '新手入门',
    description: '从零开始学习股票交易基础知识',
    topics: ['什么是股票', '如何开户', '基本术语', '交易规则'],
    href: '/learn?tab=beginner',
  },
  {
    icon: GraduationCap,
    title: '进阶学习',
    description: '掌握技术分析和基本面分析方法',
    topics: ['K线图解读', '技术指标', '财务分析', '估值方法'],
    href: '/learn?tab=advanced',
  },
  {
    icon: Lightbulb,
    title: '投资策略',
    description: '学习成功投资者的交易策略和风险管理',
    topics: ['价值投资', '趋势跟踪', '止损止盈', '仓位管理'],
    href: '/learn?tab=advanced',
  },
];  return (
    <div className="space-y-16">
      {/* 快速操作 */}
      <div className="space-y-8">
        <div className="text-center space-y-3">
          <h2 className="text-3xl lg:text-4xl font-bold text-gray-900">
            开始您的投资之旅
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            选择下面的功能,立即开始探索虚拟交易平台
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {mainActions.map((action) => {
            const Icon = action.icon;
            const colorClasses = {
              blue: 'from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700',
              indigo: 'from-indigo-500 to-indigo-600 hover:from-indigo-600 hover:to-indigo-700',
              purple: 'from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700',
            };

            return (
              <Link
                key={action.title}
                href={action.href}
                className={`group relative overflow-hidden rounded-xl p-6 text-white transition-all ${
                  action.highlight
                    ? `bg-gradient-to-br ${colorClasses[action.color as keyof typeof colorClasses]} shadow-xl hover:shadow-2xl scale-105`
                    : `bg-gradient-to-br ${colorClasses[action.color as keyof typeof colorClasses]} shadow-lg hover:shadow-xl`
                }`}
              >
                <div className="relative z-10">
                  <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <Icon className="w-6 h-6" />
                  </div>
                  
                  <h3 className="text-xl font-bold mb-2">{action.title}</h3>
                  <p className="text-sm text-white/90 mb-4">{action.description}</p>
                  
                  <div className="flex items-center gap-2 text-sm font-medium group-hover:gap-3 transition-all">
                    立即前往
                    <ArrowRight className="w-4 h-4" />
                  </div>
                </div>

                {/* 装饰圆圈 */}
                <div className="absolute -right-8 -bottom-8 w-32 h-32 bg-white/10 rounded-full group-hover:scale-150 transition-transform duration-500"></div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* 投资教育资源 */}
      <div className="space-y-8">
        <div className="text-center space-y-3">
          <h2 className="text-3xl lg:text-4xl font-bold text-gray-900">
            投资学习资源
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            从基础到进阶,系统学习投资知识
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {educationResources.map((resource) => {
            const Icon = resource.icon;
            return (
              <Link
                key={resource.title}
                href={resource.href}
                className="group bg-white rounded-xl p-6 shadow-sm hover:shadow-lg transition-all border border-gray-100 hover:border-indigo-200 cursor-pointer"
              >
                <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-indigo-200 transition-colors">
                  <Icon className="w-6 h-6 text-indigo-600" />
                </div>
                
                <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-indigo-600 transition-colors">{resource.title}</h3>
                <p className="text-gray-600 mb-4">{resource.description}</p>
                
                <ul className="space-y-2">
                  {resource.topics.map((topic) => (
                    <li key={topic} className="flex items-center gap-2 text-sm text-gray-600">
                      <div className="w-1.5 h-1.5 bg-indigo-600 rounded-full"></div>
                      {topic}
                    </li>
                  ))}
                </ul>

                {/* 悬停时显示箭头 */}
                <div className="mt-4 flex items-center gap-2 text-sm font-medium text-indigo-600 opacity-0 group-hover:opacity-100 transition-opacity">
                  了解更多
                  <ArrowRight className="w-4 h-4" />
                </div>
              </Link>
            );
          })}
        </div>
      </div>

    </div>
  );
}
