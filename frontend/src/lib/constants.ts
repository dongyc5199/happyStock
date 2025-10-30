/**
 * Homepage constants - static data for feature cards, quick start steps, and education resources
 */

import { BarChart3, Brain, Users } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

// Feature Cards Data
export interface FeatureCard {
  id: string;
  title: string;
  description: string;
  icon: LucideIcon;
  primaryAction: {
    label: string;
    href: string;
  };
  secondaryAction?: {
    label: string;
    href: string;
  };
  color: string; // Tailwind color name (e.g., "blue")
}

export const FEATURES: FeatureCard[] = [
  {
    id: 'chart-tool',
    title: '专业图表工具',
    description: 'K线图、趋势线、技术指标,打造专业级交易分析平台',
    icon: BarChart3,
    primaryAction: { label: '立即体验', href: '/virtual-market' },
    secondaryAction: { label: '📖 学习K线图基础', href: '/docs/kline-basics' },
    color: 'blue',
  },
  {
    id: 'ai-trading',
    title: 'AI模拟交易',
    description: '智能选股、策略回测、风险评估,AI助力投资决策',
    icon: Brain,
    primaryAction: { label: '开始交易', href: '/virtual-market' },
    color: 'purple',
  },
  {
    id: 'social-platform',
    title: '投资社交平台',
    description: '分享策略、跟踪高手、学习交流,共同成长进步',
    icon: Users,
    primaryAction: { label: '加入社区', href: '/social' },
    color: 'green',
  },
];

// Quick Start Steps Data
export interface QuickStartStep {
  id: string;
  number: number;
  title: string;
  description: string;
  cta?: {
    label: string;
    href: string;
  };
}

export const QUICK_START_STEPS: QuickStartStep[] = [
  {
    id: 'step-1',
    number: 1,
    title: '注册账户',
    description: '快速创建模拟交易账户,获得100万虚拟资金',
    cta: { label: '立即注册', href: '/register' },
  },
  {
    id: 'step-2',
    number: 2,
    title: '选择股票',
    description: '浏览100只虚拟股票,查看实时行情和分析',
    cta: { label: '查看市场', href: '/virtual-market' },
  },
  {
    id: 'step-3',
    number: 3,
    title: '开始交易',
    description: '下单买卖,体验真实交易流程,零风险学习',
    cta: { label: '开始交易', href: '/virtual-market' },
  },
];

// Education Resources Data
export interface EducationResource {
  id: string;
  title: string;
  description: string;
  category: 'beginner' | 'intermediate' | 'advanced' | 'faq';
  readingTime: number; // minutes
  url: string; // internal route or external link
  relatedFeature?: 'chart' | 'ai' | 'social';
}

export const EDUCATION_RESOURCES: EducationResource[] = [
  // Beginner resources
  {
    id: 'kline-basics',
    title: 'K线图入门教程',
    description: '5分钟掌握阴阳线、趋势判断',
    category: 'beginner',
    readingTime: 5,
    url: '/docs/kline-basics',
    relatedFeature: 'chart',
  },
  {
    id: 'first-trade',
    title: '如何下第一单?',
    description: '新手交易流程详解',
    category: 'beginner',
    readingTime: 3,
    url: '/docs/first-trade',
    relatedFeature: 'ai',
  },
  {
    id: 'stock-codes',
    title: '股票代码含义',
    description: '理解A股代码规则',
    category: 'beginner',
    readingTime: 3,
    url: '/docs/stock-codes',
  },
  // Intermediate resources
  {
    id: 'pattern-recognition',
    title: 'K线形态识别',
    description: '掌握常见K线组合',
    category: 'intermediate',
    readingTime: 10,
    url: '/docs/pattern-recognition',
    relatedFeature: 'chart',
  },
  {
    id: 'trend-lines',
    title: '趋势线绘制技巧',
    description: '判断支撑位和阻力位',
    category: 'intermediate',
    readingTime: 8,
    url: '/docs/trend-lines',
    relatedFeature: 'chart',
  },
  {
    id: 'ai-backtesting',
    title: 'AI策略回测方法',
    description: '验证交易策略有效性',
    category: 'intermediate',
    readingTime: 12,
    url: '/docs/ai-backtesting',
    relatedFeature: 'ai',
  },
  // FAQ resources
  {
    id: 'faq-positions',
    title: '如何查看持仓?',
    description: '查询账户和持仓信息',
    category: 'faq',
    readingTime: 2,
    url: '/docs/faq-positions',
  },
  {
    id: 'faq-stop-loss',
    title: '如何设置止损?',
    description: '风险控制基础',
    category: 'faq',
    readingTime: 3,
    url: '/docs/faq-stop-loss',
  },
  {
    id: 'faq-invite',
    title: '如何邀请好友?',
    description: '社交功能使用指南',
    category: 'faq',
    readingTime: 2,
    url: '/docs/faq-invite',
    relatedFeature: 'social',
  },
];

// Group education resources by category
export const EDUCATION_BY_CATEGORY = {
  beginner: EDUCATION_RESOURCES.filter((r) => r.category === 'beginner'),
  intermediate: EDUCATION_RESOURCES.filter((r) => r.category === 'intermediate'),
  advanced: EDUCATION_RESOURCES.filter((r) => r.category === 'advanced'),
  faq: EDUCATION_RESOURCES.filter((r) => r.category === 'faq'),
};
