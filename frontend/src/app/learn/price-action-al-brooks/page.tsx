'use client';

import React from 'react';
import Link from 'next/link';
import { ChevronLeft, GraduationCap } from 'lucide-react';
import HeroSection from './components/HeroSection';
import BrooksIntro from './components/BrooksIntro';
import WhatIsPriceAction from './components/WhatIsPriceAction';
import CoreConcepts from './components/CoreConcepts';
import TradingPatterns from './components/TradingPatterns';
import LearningPath from './components/LearningPath';
import BooksList from './components/BooksList';
import ResourcesSection from './components/ResourcesSection';
import PracticalTips from './components/PracticalTips';
import FAQ from './components/FAQ';

export default function AlBrooksPriceActionPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-md border-b border-white/10 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link href="/learn" className="flex items-center gap-3 text-white hover:text-blue-300 transition-colors">
              <ChevronLeft className="w-5 h-5" />
              <span className="font-medium">返回学习中心</span>
            </Link>
            <Link href="/" className="flex items-center gap-2 text-white/80 hover:text-white transition-colors">
              <GraduationCap className="w-5 h-5" />
              <span className="text-sm">happyStock</span>
            </Link>
          </div>
        </div>
      </header>

      {/* Page Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-16">
        {/* Hero Section */}
        <HeroSection />

        {/* Al Brooks Introduction */}
        <BrooksIntro />

        {/* What is Price Action Trading */}
        <WhatIsPriceAction />

        {/* Core Concepts */}
        <CoreConcepts />

        {/* Trading Patterns */}
        <TradingPatterns />

        {/* Learning Path */}
        <LearningPath />

        {/* Books List */}
        <BooksList />

        {/* Resources Section */}
        <ResourcesSection />

        {/* Practical Tips */}
        <PracticalTips />

        {/* FAQ */}
        <FAQ />

        {/* CTA Section */}
        <div className="text-center bg-gradient-to-r from-yellow-500/20 via-orange-500/20 to-red-500/20 rounded-2xl p-12 border border-yellow-400/30">
          <h3 className="text-3xl font-bold text-yellow-300 mb-4">
            开始你的价格行为交易学习之旅
          </h3>
          <p className="text-lg text-yellow-100/80 mb-8 max-w-2xl mx-auto">
            系统学习 Al Brooks 的价格行为交易方法,掌握专业交易技能
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link
              href="/virtual-market"
              className="px-8 py-4 bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 text-white font-bold text-lg rounded-xl transition-all duration-300 shadow-lg shadow-yellow-500/30 hover:shadow-yellow-500/50 hover:scale-105"
            >
              开始实战练习
            </Link>
            <Link
              href="/learn"
              className="px-8 py-4 bg-white/10 hover:bg-white/20 text-white font-bold text-lg rounded-xl transition-all duration-300 border border-white/20"
            >
              浏览更多课程
            </Link>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-white/10 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-white/60 text-sm">
            <p>happyStock 学习中心 - Al Brooks 价格行为交易专题</p>
            <p className="mt-2">© 2025 happyStock. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
