/**
 * HeroSection Component - Homepage hero section
 * 
 * Displays value proposition, CTAs, and visual appeal
 * User Story 1: 快速理解平台价值主张
 */

import React from 'react';
import Link from 'next/link';
import { ArrowRight, TrendingUp } from 'lucide-react';
import { HeroChartAnimation } from './HeroChartAnimation';

export interface HeroSectionProps {
  /** Number of registered users (social proof) */
  userCount?: number;
  /** Primary CTA href */
  primaryCtaHref?: string;
  /** Secondary CTA href */
  secondaryCtaHref?: string;
}

/**
 * Hero section component for homepage
 * 
 * @example
 * ```tsx
 * <HeroSection userCount={15234} />
 * ```
 */
export function HeroSection({
  userCount = 15000,
  primaryCtaHref = '/virtual-market',
  secondaryCtaHref = '/docs',
}: HeroSectionProps) {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800">
      {/* Background decorative elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-1/2 -right-1/2 w-96 h-96 bg-blue-200/20 dark:bg-blue-500/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-1/2 -left-1/2 w-96 h-96 bg-purple-200/20 dark:bg-purple-500/10 rounded-full blur-3xl" />
      </div>

      {/* Content */}
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left: Text content (60% on large screens) */}
          <div className="lg:pr-8">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-sm font-medium mb-6">
              <TrendingUp className="w-4 h-4" />
              <span>零风险学习投资</span>
            </div>

            {/* Main heading */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 dark:text-white mb-6 leading-tight">
              在虚拟市场学投资
              <br />
              <span className="text-blue-600 dark:text-blue-400">零风险实战</span>
            </h1>

            {/* Subtitle */}
            <p className="text-lg sm:text-xl text-gray-600 dark:text-gray-300 mb-8 leading-relaxed">
              A股真实数据模拟，100万虚拟资金，专业图表工具
              <br />
              无需投入真金白银，轻松掌握投资技能
            </p>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row gap-4 mb-8">
              <Link
                href={primaryCtaHref}
                className="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold text-lg transition-colors shadow-lg shadow-blue-500/30"
              >
                开始体验
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                href={secondaryCtaHref}
                className="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-lg border-2 border-gray-300 dark:border-gray-600 hover:border-blue-500 dark:hover:border-blue-400 text-gray-700 dark:text-gray-300 font-semibold text-lg transition-colors"
              >
                了解更多
              </Link>
            </div>

            {/* Social proof */}
            <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
              <div className="flex -space-x-2">
                {[1, 2, 3, 4].map((i) => (
                  <div
                    key={i}
                    className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 border-2 border-white dark:border-gray-900"
                  />
                ))}
              </div>
              <span>
                已有 <span className="font-semibold text-gray-900 dark:text-white">{userCount.toLocaleString()}</span> 位投资者加入
              </span>
            </div>
          </div>

          {/* Right: Animated Chart Carousel (40% on large screens) */}
          <div className="relative lg:pl-8">
            <HeroChartAnimation />
          </div>
        </div>
      </div>
    </section>
  );
}
