import React from 'react';
import { Star, Award, BookOpen, TrendingUp } from 'lucide-react';

export default function HeroSection() {
  return (
    <section className="relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-yellow-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-orange-500/10 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 text-center py-12">
        {/* Featured Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-full text-white font-bold text-sm mb-6">
          <Star className="w-4 h-4 fill-current" />
          <span>特色推荐课程</span>
          <Star className="w-4 h-4 fill-current" />
        </div>

        {/* Title */}
        <h1 className="text-5xl md:text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 via-orange-300 to-red-300 mb-6">
          Al Brooks 价格行为交易
        </h1>

        {/* Subtitle */}
        <p className="text-xl md:text-2xl text-yellow-100/90 mb-8 max-w-3xl mx-auto">
          世界顶级价格行为交易大师的完整交易体系
        </p>

        {/* Highlights */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto mb-8">
          <div className="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-yellow-400/30">
            <BookOpen className="w-8 h-8 text-yellow-400 mx-auto mb-2" />
            <div className="text-2xl font-bold text-white mb-1">4本</div>
            <div className="text-sm text-yellow-200/80">经典著作</div>
          </div>
          <div className="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-yellow-400/30">
            <TrendingUp className="w-8 h-8 text-yellow-400 mx-auto mb-2" />
            <div className="text-2xl font-bold text-white mb-1">100+</div>
            <div className="text-sm text-yellow-200/80">小时视频</div>
          </div>
          <div className="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-yellow-400/30">
            <Award className="w-8 h-8 text-yellow-400 mx-auto mb-2" />
            <div className="text-2xl font-bold text-white mb-1">30+</div>
            <div className="text-sm text-yellow-200/80">年经验</div>
          </div>
          <div className="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-yellow-400/30">
            <Star className="w-8 h-8 text-yellow-400 mx-auto mb-2 fill-current" />
            <div className="text-2xl font-bold text-white mb-1">殿堂级</div>
            <div className="text-sm text-yellow-200/80">交易大师</div>
          </div>
        </div>

        {/* Description */}
        <p className="text-lg text-yellow-100/70 max-w-2xl mx-auto">
          Al Brooks 是全球公认的价格行为交易权威专家,他的交易方法论经过30多年实战检验,
          适用于任何市场、任何时间周期。本课程将系统讲解其核心交易理念、经典交易模式以及实战应用技巧。
        </p>
      </div>
    </section>
  );
}
