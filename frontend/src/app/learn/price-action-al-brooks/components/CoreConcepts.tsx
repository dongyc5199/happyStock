import React from 'react';
import { Lightbulb, TrendingUp, Target, Zap, Brain, Scale, Clock } from 'lucide-react';

export default function CoreConcepts() {
  const concepts = [
    {
      icon: TrendingUp,
      title: '三种市场状态',
      description: '市场只有三种状态:趋势(Trend)、震荡(Trading Range)、过渡(Transition)。理解当前市场处于哪种状态是交易的首要任务。',
      details: [
        '趋势市场:价格持续向一个方向运动,回调幅度小',
        '震荡市场:价格在固定区间内上下波动',
        '过渡阶段:从趋势转为震荡,或从震荡转为趋势的临界状态',
      ],
      color: 'blue',
    },
    {
      icon: Zap,
      title: '两次尝试原则',
      description: '市场通常会给出两次机会。如果第一次突破失败,往往会有第二次尝试;如果错过了第一次入场机会,通常还会有第二次。',
      details: [
        '双顶/双底形态是两次尝试的典型表现',
        '突破后的回踩提供第二次入场机会',
        '不要因为错过第一次就冲动追涨杀跌',
      ],
      color: 'purple',
    },
    {
      icon: Target,
      title: '被困交易者',
      description: '价格反转往往源于大量交易者被&ldquo;困住&rdquo;。理解被困交易者的心理和行为,可以预判价格反转点。',
      details: [
        '假突破会困住激进的突破交易者',
        '趋势末期会困住追涨杀跌的散户',
        '被困者被迫平仓会加速价格反转',
      ],
      color: 'orange',
    },
    {
      icon: Brain,
      title: '磁铁效应',
      description: '某些价格水平(如整数关口、前高/前低、均线等)对价格有&ldquo;磁铁&rdquo;般的吸引力,价格往往会向这些位置靠拢。',
      details: [
        '整数关口(如100、1000)有强大吸引力',
        '前期高点/低点是重要的磁铁位',
        '重要移动平均线(如20EMA)也有磁铁效应',
      ],
      color: 'green',
    },
    {
      icon: Scale,
      title: '趋势强度判断',
      description: '通过观察K线的大小、连续性、回调幅度等,可以判断趋势的强弱,从而决定是顺势交易还是等待反转。',
      details: [
        '强趋势:K线实体大,连续性强,回调小',
        '弱趋势:K线实体小,经常有反向K线,回调大',
        '趋势减弱时考虑减仓或平仓',
      ],
      color: 'red',
    },
    {
      icon: Lightbulb,
      title: '概率与数学期望',
      description: 'Al Brooks强调交易是概率游戏,不要追求100%的成功率。关键是找到高概率机会,并通过合理的风险收益比获得正期望。',
      details: [
        '即使只有40%成功率,1:2的风险收益比也能盈利',
        '不要因为一次失败就否定整个策略',
        '关注长期统计结果,而非单次交易',
      ],
      color: 'indigo',
    },
    {
      icon: Clock,
      title: '时间周期理解',
      description: '不同时间周期的价格行为是相互影响的。日线图的趋势可能在5分钟图上表现为震荡,理解多周期关系至关重要。',
      details: [
        '大周期趋势方向是小周期的主导力量',
        '小周期的震荡可能只是大周期的回调',
        '在大周期趋势方向上交易,成功率更高',
      ],
      color: 'pink',
    },
  ];

  const colorClasses: Record<string, { bg: string; icon: string; border: string }> = {
    blue: { bg: 'bg-blue-500/10', icon: 'text-blue-400', border: 'border-blue-400/30' },
    purple: { bg: 'bg-purple-500/10', icon: 'text-purple-400', border: 'border-purple-400/30' },
    orange: { bg: 'bg-orange-500/10', icon: 'text-orange-400', border: 'border-orange-400/30' },
    green: { bg: 'bg-green-500/10', icon: 'text-green-400', border: 'border-green-400/30' },
    red: { bg: 'bg-red-500/10', icon: 'text-red-400', border: 'border-red-400/30' },
    indigo: { bg: 'bg-indigo-500/10', icon: 'text-indigo-400', border: 'border-indigo-400/30' },
    pink: { bg: 'bg-pink-500/10', icon: 'text-pink-400', border: 'border-pink-400/30' },
  };

  return (
    <section className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 md:p-12 border border-white/10">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-400 to-pink-500 flex items-center justify-center">
          <Lightbulb className="w-6 h-6 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-white">Al Brooks 核心交易理念</h2>
      </div>

      <p className="text-white/80 mb-8 leading-relaxed">
        Al Brooks 的价格行为交易体系建立在以下7大核心理念之上。
        深入理解这些理念,是掌握其交易方法的关键。
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {concepts.map((concept, index) => {
          const Icon = concept.icon;
          const colors = colorClasses[concept.color];
          
          return (
            <div
              key={index}
              className={`${colors.bg} rounded-xl p-6 border ${colors.border} hover:scale-[1.02] transition-transform duration-300`}
            >
              <div className="flex items-start gap-4 mb-4">
                <div className={`w-12 h-12 rounded-xl ${colors.bg} border ${colors.border} flex items-center justify-center flex-shrink-0`}>
                  <Icon className={`w-6 h-6 ${colors.icon}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`text-xs px-2 py-1 rounded-full ${colors.bg} ${colors.icon} font-medium border ${colors.border}`}>
                      理念 {index + 1}
                    </span>
                  </div>
                  <h3 className={`text-xl font-bold text-white mb-2`}>
                    {concept.title}
                  </h3>
                </div>
              </div>

              <p className="text-white/80 mb-4 leading-relaxed">
                {concept.description}
              </p>

              <div className="space-y-2">
                <h4 className="text-sm font-bold text-white/90 mb-2">关键要点:</h4>
                {concept.details.map((detail, i) => (
                  <div key={i} className="flex items-start gap-2">
                    <div className={`w-1.5 h-1.5 rounded-full ${colors.icon.replace('text-', 'bg-')} flex-shrink-0 mt-2`} />
                    <p className="text-sm text-white/70 flex-1">{detail}</p>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary */}
      <div className="mt-8 bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-xl p-6 border border-purple-400/30">
        <h3 className="text-lg font-bold text-purple-300 mb-3 flex items-center gap-2">
          <Brain className="w-5 h-5" />
          核心思想总结
        </h3>
        <p className="text-white/80 leading-relaxed">
          Al Brooks 的交易哲学强调<strong className="text-purple-300">理性分析、概率思维和风险管理</strong>。
          他认为交易不是艺术而是科学,通过系统化的方法论和大量实践,
          任何人都可以掌握价格行为交易。关键在于保持客观、遵守纪律、持续学习。
        </p>
      </div>
    </section>
  );
}
