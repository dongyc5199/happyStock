import React from 'react';
import { TrendingUp, Target, Eye, CheckCircle2, XCircle } from 'lucide-react';

export default function WhatIsPriceAction() {
  return (
    <section className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 md:p-12 border border-white/10">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center">
          <TrendingUp className="w-6 h-6 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-white">什么是价格行为交易</h2>
      </div>

      {/* Definition */}
      <div className="mb-8">
        <h3 className="text-xl font-bold text-blue-300 mb-4 flex items-center gap-2">
          <Target className="w-5 h-5" />
          核心定义
        </h3>
        <div className="bg-gradient-to-br from-blue-500/10 to-purple-500/10 rounded-xl p-6 border border-blue-400/30">
          <p className="text-white/90 text-lg leading-relaxed">
            <strong className="text-blue-300">价格行为交易(Price Action Trading)</strong>是一种纯粹基于价格走势的交易方法,
            交易者通过观察和分析K线图上的价格变化、形态和结构来做出交易决策,
            <strong className="text-blue-300">而不依赖传统的技术指标</strong>(如MACD、RSI、KDJ等)。
          </p>
          <p className="text-white/80 mt-4 leading-relaxed">
            这种方法认为,价格本身已经反映了所有市场信息,
            包括供需关系、市场情绪、主力行为等。通过研究价格的&ldquo;语言&rdquo;,
            交易者可以更直接、更清晰地理解市场动态。
          </p>
        </div>
      </div>

      {/* Core Principles */}
      <div className="mb-8">
        <h3 className="text-xl font-bold text-blue-300 mb-4 flex items-center gap-2">
          <Eye className="w-5 h-5" />
          核心原则
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white/5 rounded-lg p-5 border border-blue-400/20">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                <CheckCircle2 className="w-5 h-5 text-blue-400" />
              </div>
              <div>
                <h4 className="font-bold text-white mb-2">价格至上</h4>
                <p className="text-sm text-white/70">
                  价格是市场的最终裁判,所有的信息最终都会体现在价格走势上
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white/5 rounded-lg p-5 border border-blue-400/20">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                <CheckCircle2 className="w-5 h-5 text-blue-400" />
              </div>
              <div>
                <h4 className="font-bold text-white mb-2">简洁直观</h4>
                <p className="text-sm text-white/70">
                  不使用复杂的指标公式,只需观察K线图就能做出交易决策
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white/5 rounded-lg p-5 border border-blue-400/20">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                <CheckCircle2 className="w-5 h-5 text-blue-400" />
              </div>
              <div>
                <h4 className="font-bold text-white mb-2">概率思维</h4>
                <p className="text-sm text-white/70">
                  不追求100%准确预测,而是寻找高概率的交易机会
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white/5 rounded-lg p-5 border border-blue-400/20">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                <CheckCircle2 className="w-5 h-5 text-blue-400" />
              </div>
              <div>
                <h4 className="font-bold text-white mb-2">通用适用</h4>
                <p className="text-sm text-white/70">
                  适用于任何市场(股票、期货、外汇)和任何时间周期
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Comparison Table */}
      <div>
        <h3 className="text-xl font-bold text-blue-300 mb-4">价格行为交易 vs 传统技术分析</h3>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-blue-500/20">
                <th className="px-4 py-3 text-left text-white font-bold border border-blue-400/30">对比维度</th>
                <th className="px-4 py-3 text-left text-white font-bold border border-blue-400/30">价格行为交易</th>
                <th className="px-4 py-3 text-left text-white font-bold border border-blue-400/30">传统技术分析</th>
              </tr>
            </thead>
            <tbody>
              <tr className="bg-white/5">
                <td className="px-4 py-3 text-white/90 border border-blue-400/20">分析基础</td>
                <td className="px-4 py-3 text-white/80 border border-blue-400/20">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-400 flex-shrink-0" />
                    <span>纯K线价格走势</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-white/80 border border-blue-400/20">
                  <div className="flex items-center gap-2">
                    <XCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
                    <span>各类技术指标</span>
                  </div>
                </td>
              </tr>
              <tr className="bg-white/5">
                <td className="px-4 py-3 text-white/90 border border-blue-400/20">信号延迟</td>
                <td className="px-4 py-3 text-white/80 border border-blue-400/20">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-400 flex-shrink-0" />
                    <span>实时,无延迟</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-white/80 border border-blue-400/20">
                  <div className="flex items-center gap-2">
                    <XCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
                    <span>滞后,有延迟</span>
                  </div>
                </td>
              </tr>
              <tr className="bg-white/5">
                <td className="px-4 py-3 text-white/90 border border-blue-400/20">图表简洁度</td>
                <td className="px-4 py-3 text-white/80 border border-blue-400/20">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-400 flex-shrink-0" />
                    <span>简洁清晰</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-white/80 border border-blue-400/20">
                  <div className="flex items-center gap-2">
                    <XCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
                    <span>复杂凌乱</span>
                  </div>
                </td>
              </tr>
              <tr className="bg-white/5">
                <td className="px-4 py-3 text-white/90 border border-blue-400/20">学习难度</td>
                <td className="px-4 py-3 text-white/80 border border-blue-400/20">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-400 flex-shrink-0" />
                    <span>需要大量看盘经验</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-white/80 border border-blue-400/20">
                  <div className="flex items-center gap-2">
                    <XCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
                    <span>公式复杂,易混淆</span>
                  </div>
                </td>
              </tr>
              <tr className="bg-white/5">
                <td className="px-4 py-3 text-white/90 border border-blue-400/20">适用性</td>
                <td className="px-4 py-3 text-white/80 border border-blue-400/20">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-400 flex-shrink-0" />
                    <span>所有市场和周期</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-white/80 border border-blue-400/20">
                  <div className="flex items-center gap-2">
                    <XCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
                    <span>特定市场可能失效</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Note */}
      <div className="mt-6 bg-blue-500/10 rounded-lg p-4 border border-blue-400/30">
        <p className="text-sm text-blue-200/90">
          <strong className="text-blue-300">💡 重要提示:</strong> 价格行为交易并不排斥所有指标,
          Al Brooks 也会使用移动平均线(MA)来辅助判断趋势。关键在于,价格是主要决策依据,指标只是辅助工具。
        </p>
      </div>
    </section>
  );
}
