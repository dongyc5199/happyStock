'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { 
  BookOpen, 
  TrendingUp, 
  BarChart3, 
  HelpCircle, 
  Sparkles,
  LineChart,
  GraduationCap,
  Lightbulb,
  ChevronRight,
  Star,
  Clock,
  Users
} from 'lucide-react';

type TabType = 'beginner' | 'advanced' | 'faq';

export default function LearnPage() {
  const searchParams = useSearchParams();
  const tabParam = searchParams.get('tab') as TabType | null;
  const [activeTab, setActiveTab] = useState<TabType>(tabParam || 'beginner');

  // 监听 URL 参数变化
  useEffect(() => {
    if (tabParam && (tabParam === 'beginner' || tabParam === 'advanced' || tabParam === 'faq')) {
      setActiveTab(tabParam);
    }
  }, [tabParam]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-md border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-3">
              <GraduationCap className="w-8 h-8 text-blue-400" />
              <div>
                <h1 className="text-xl font-bold text-white">happyStock 学习中心</h1>
                <p className="text-xs text-blue-300">Trading Knowledge Center</p>
              </div>
            </Link>
            <Link
              href="/"
              className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors border border-white/20"
            >
              返回首页
            </Link>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-5xl font-bold text-white mb-4">
            开启你的交易学习之旅
          </h2>
          <p className="text-xl text-blue-200 max-w-3xl mx-auto mb-8">
            从零基础到专业交易者,系统化、专业化的交易知识学习平台
          </p>
          <div className="flex items-center justify-center gap-8 text-white/80">
            <div className="flex items-center gap-2">
              <Users className="w-5 h-5 text-blue-400" />
              <span>10,000+ 学员</span>
            </div>
            <div className="flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-blue-400" />
              <span>100+ 课程</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-blue-400" />
              <span>24/7 学习</span>
            </div>
          </div>
        </div>

        {/* Featured Content - Al Brooks */}
        <div className="mb-12">
          <Link
            href="/learn/price-action-al-brooks"
            className="group relative block overflow-hidden rounded-2xl bg-gradient-to-br from-yellow-500/20 via-orange-500/20 to-red-500/20 border-2 border-yellow-400/50 p-8 hover:border-yellow-400 transition-all duration-300 hover:scale-[1.02] shadow-2xl shadow-yellow-500/20"
          >
            <div className="absolute top-4 right-4">
              <div className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-full text-white font-bold text-sm">
                <Star className="w-4 h-4 fill-current" />
                <span>特色推荐</span>
              </div>
            </div>
            <div className="flex items-start gap-6">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center flex-shrink-0">
                <TrendingUp className="w-10 h-10 text-white" />
              </div>
              <div className="flex-1">
                <h3 className="text-3xl font-bold text-yellow-300 mb-3 group-hover:text-yellow-200 transition-colors">
                  Al Brooks 价格行为交易
                </h3>
                <p className="text-lg text-yellow-100/90 mb-4">
                  世界顶级价格行为交易大师的完整交易体系 • 4本经典著作详解 • 8大核心交易模式 • 完整学习路线图
                </p>
                <div className="flex items-center gap-4 text-yellow-200/80">
                  <div className="flex items-center gap-2">
                    <BookOpen className="w-4 h-4" />
                    <span className="text-sm">30+ 年经验</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Star className="w-4 h-4 fill-current" />
                    <span className="text-sm">殿堂级大师</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-4 h-4" />
                    <span className="text-sm">实战导向</span>
                  </div>
                </div>
              </div>
              <ChevronRight className="w-8 h-8 text-yellow-300 group-hover:translate-x-2 transition-transform flex-shrink-0" />
            </div>
          </Link>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center justify-center gap-4 mb-8">
          <button
            onClick={() => setActiveTab('beginner')}
            className={`px-6 py-3 rounded-xl font-medium transition-all duration-300 ${
              activeTab === 'beginner'
                ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/50'
                : 'bg-white/10 text-white/70 hover:bg-white/20'
            }`}
          >
            <div className="flex items-center gap-2">
              <BookOpen className="w-5 h-5" />
              <span>新手指南</span>
            </div>
          </button>
          <button
            onClick={() => setActiveTab('advanced')}
            className={`px-6 py-3 rounded-xl font-medium transition-all duration-300 ${
              activeTab === 'advanced'
                ? 'bg-purple-500 text-white shadow-lg shadow-purple-500/50'
                : 'bg-white/10 text-white/70 hover:bg-white/20'
            }`}
          >
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              <span>进阶学习</span>
            </div>
          </button>
          <button
            onClick={() => setActiveTab('faq')}
            className={`px-6 py-3 rounded-xl font-medium transition-all duration-300 ${
              activeTab === 'faq'
                ? 'bg-green-500 text-white shadow-lg shadow-green-500/50'
                : 'bg-white/10 text-white/70 hover:bg-white/20'
            }`}
          >
            <div className="flex items-center gap-2">
              <HelpCircle className="w-5 h-5" />
              <span>常见问题</span>
            </div>
          </button>
        </div>

        {/* Tab Content */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Beginner Tab */}
          {activeTab === 'beginner' && (
            <>
              <CourseCard
                icon={BookOpen}
                title="交易基础知识"
                description="股票交易的基本概念、术语、交易规则等入门知识"
                duration="2-4 小时"
                level="入门"
                href="/learn/trading-basics"
                color="blue"
              />
              <CourseCard
                icon={BarChart3}
                title="K线图表工具"
                description="学习K线形态、趋势线、支撑阻力位等技术分析基础"
                duration="3-5 小时"
                level="入门"
                href="/learn/chart-tools"
                color="blue"
              />
              <CourseCard
                icon={GraduationCap}
                title="账户开通指南"
                description="快速开通虚拟交易账户,领取100万体验金开始交易"
                duration="10 分钟"
                level="入门"
                href="/learn/account-guide"
                color="blue"
              />
              <CourseCard
                icon={Lightbulb}
                title="风险管理基础"
                description="学习仓位管理、止损止盈等风险控制的基本方法"
                duration="2-3 小时"
                level="入门"
                href="/learn/risk-management"
                color="blue"
              />
              <CourseCard
                icon={LineChart}
                title="技术指标入门"
                description="了解常用技术指标(MA、MACD、RSI等)的使用方法"
                duration="3-4 小时"
                level="入门"
                href="/learn/technical-indicators"
                color="blue"
              />
              <CourseCard
                icon={BookOpen}
                title="交易心理学"
                description="了解交易心理、情绪管理、建立正确的交易思维"
                duration="2-3 小时"
                level="入门"
                href="/learn/trading-psychology"
                color="blue"
              />
            </>
          )}

          {/* Advanced Tab */}
          {activeTab === 'advanced' && (
            <>
              <CourseCard
                icon={TrendingUp}
                title="Al Brooks 价格行为交易"
                description="世界顶级价格行为大师的交易方法论与实战技巧"
                duration="30+ 小时"
                level="进阶"
                href="/learn/price-action-al-brooks"
                color="purple"
                featured={true}
              />
              <CourseCard
                icon={LineChart}
                title="技术分析进阶"
                description="深入学习技术指标、形态学、波浪理论等高级技术"
                duration="20+ 小时"
                level="进阶"
                href="/learn/technical-analysis"
                color="purple"
              />
              <CourseCard
                icon={Sparkles}
                title="量化交易入门"
                description="了解量化策略开发、回测与实盘交易技巧"
                duration="15+ 小时"
                level="进阶"
                href="/learn/quantitative-trading"
                color="purple"
              />
              <CourseCard
                icon={TrendingUp}
                title="趋势跟踪策略"
                description="学习如何识别趋势、顺势而为的交易方法"
                duration="10+ 小时"
                level="进阶"
                href="/learn/trend-following"
                color="purple"
              />
              <CourseCard
                icon={BarChart3}
                title="盘口语言解读"
                description="学习通过盘口数据分析主力行为和市场情绪"
                duration="12+ 小时"
                level="进阶"
                href="/learn/order-flow"
                color="purple"
              />
              <CourseCard
                icon={Lightbulb}
                title="高级风险管理"
                description="资金管理、仓位配置、风险收益比等高级技巧"
                duration="8+ 小时"
                level="进阶"
                href="/learn/advanced-risk"
                color="purple"
              />
            </>
          )}

          {/* FAQ Tab */}
          {activeTab === 'faq' && (
            <>
              <FAQCard
                icon={HelpCircle}
                title="账户相关问题"
                questions={[
                  '如何注册账户?',
                  '忘记密码怎么办?',
                  '如何充值虚拟资金?',
                  '账户安全如何保障?',
                ]}
                href="/learn/faq/account"
              />
              <FAQCard
                icon={HelpCircle}
                title="交易相关问题"
                questions={[
                  '如何下单买入股票?',
                  '什么是市价单和限价单?',
                  '如何设置止损止盈?',
                  '交易手续费如何计算?',
                ]}
                href="/learn/faq/trading"
              />
              <FAQCard
                icon={HelpCircle}
                title="平台功能问题"
                questions={[
                  '如何查看实时行情?',
                  '图表工具如何使用?',
                  '如何查看历史数据?',
                  '手机端如何使用?',
                ]}
                href="/learn/faq/platform"
              />
              <FAQCard
                icon={HelpCircle}
                title="技术支持"
                questions={[
                  '遇到bug如何反馈?',
                  '如何联系客服?',
                  '浏览器兼容性问题?',
                  '数据延迟怎么办?',
                ]}
                href="/learn/faq/support"
              />
              <FAQCard
                icon={HelpCircle}
                title="学习相关问题"
                questions={[
                  '零基础如何开始学习?',
                  '学习路线如何规划?',
                  '需要多长时间入门?',
                  '有没有学习社群?',
                ]}
                href="/learn/faq/learning"
              />
              <FAQCard
                icon={HelpCircle}
                title="其他问题"
                questions={[
                  '虚拟市场和真实市场的区别?',
                  '可以直接用于实盘吗?',
                  '平台是否收费?',
                  '数据来源是什么?',
                ]}
                href="/learn/faq/other"
              />
            </>
          )}
        </div>

        {/* CTA Section */}
        <div className="mt-16 text-center bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-2xl p-12 border border-white/10">
          <h3 className="text-3xl font-bold text-white mb-4">
            准备好开始学习了吗?
          </h3>
          <p className="text-lg text-blue-200 mb-8 max-w-2xl mx-auto">
            加入 10,000+ 交易者,系统化学习交易知识,提升实战能力
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link
              href="/virtual-market"
              className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-bold text-lg rounded-xl transition-all duration-300 shadow-lg shadow-blue-500/30 hover:shadow-blue-500/50 hover:scale-105"
            >
              开始体验交易
            </Link>
            <Link
              href="/learn/price-action-al-brooks"
              className="px-8 py-4 bg-white/10 hover:bg-white/20 text-white font-bold text-lg rounded-xl transition-all duration-300 border border-white/20"
            >
              查看特色课程
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

// Course Card Component
interface CourseCardProps {
  icon: React.ElementType;
  title: string;
  description: string;
  duration: string;
  level: string;
  href: string;
  color: 'blue' | 'purple';
  featured?: boolean;
}

function CourseCard({ icon: Icon, title, description, duration, level, href, color, featured }: CourseCardProps) {
  const colorClasses = {
    blue: {
      bg: 'bg-blue-500/20',
      icon: 'text-blue-400',
      hover: 'hover:border-blue-400/50',
      badge: 'bg-blue-500/20 text-blue-300',
    },
    purple: {
      bg: 'bg-purple-500/20',
      icon: 'text-purple-400',
      hover: 'hover:border-purple-400/50',
      badge: 'bg-purple-500/20 text-purple-300',
    },
  };

  const classes = colorClasses[color];

  return (
    <Link
      href={href}
      className={`group relative block p-6 rounded-xl bg-white/5 border border-white/10 ${classes.hover} transition-all duration-300 hover:bg-white/10`}
    >
      {featured && (
        <div className="absolute -top-3 -right-3">
          <div className="px-3 py-1 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-full text-white text-xs font-bold">
            🔥 热门
          </div>
        </div>
      )}
      <div className={`w-12 h-12 rounded-lg ${classes.bg} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
        <Icon className={`w-6 h-6 ${classes.icon}`} />
      </div>
      <h4 className="text-lg font-bold text-white mb-2 group-hover:text-blue-300 transition-colors">
        {title}
      </h4>
      <p className="text-sm text-white/70 mb-4 line-clamp-2">
        {description}
      </p>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className={`text-xs px-2 py-1 rounded ${classes.badge}`}>
            {level}
          </span>
          <span className="text-xs text-white/60 flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {duration}
          </span>
        </div>
        <ChevronRight className={`w-5 h-5 ${classes.icon} group-hover:translate-x-1 transition-transform`} />
      </div>
    </Link>
  );
}

// FAQ Card Component
interface FAQCardProps {
  icon: React.ElementType;
  title: string;
  questions: string[];
  href: string;
}

function FAQCard({ icon: Icon, title, questions, href }: FAQCardProps) {
  return (
    <Link
      href={href}
      className="group block p-6 rounded-xl bg-white/5 border border-white/10 hover:border-green-400/50 transition-all duration-300 hover:bg-white/10"
    >
      <div className="w-12 h-12 rounded-lg bg-green-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
        <Icon className="w-6 h-6 text-green-400" />
      </div>
      <h4 className="text-lg font-bold text-white mb-4 group-hover:text-green-300 transition-colors">
        {title}
      </h4>
      <ul className="space-y-2 mb-4">
        {questions.map((q, i) => (
          <li key={i} className="text-sm text-white/70 flex items-start gap-2">
            <ChevronRight className="w-4 h-4 text-green-400 flex-shrink-0 mt-0.5" />
            <span>{q}</span>
          </li>
        ))}
      </ul>
      <div className="flex items-center justify-between pt-4 border-t border-white/10">
        <span className="text-sm text-green-400 font-medium">查看全部答案</span>
        <ChevronRight className="w-5 h-5 text-green-400 group-hover:translate-x-1 transition-transform" />
      </div>
    </Link>
  );
}
