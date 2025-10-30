import React from 'react';
import { Route, Clock, CheckCircle2, BookOpen } from 'lucide-react';

export default function LearningPath() {
  const stages = [
    {
      stage: 1,
      title: '基础认知阶段',
      duration: '1-2周',
      description: '了解价格行为交易的基本概念,熟悉Al Brooks的核心理念和术语。',
      goals: [
        '理解三种市场状态(趋势/震荡/过渡)',
        '认识基本K线形态(趋势K线、反转K线、内包K线)',
        '掌握支撑阻力位的识别',
        '了解概率思维和风险管理基础',
      ],
      resources: [
        '阅读《Reading Price Charts Bar by Bar》第1-5章',
        '观看入门视频课程(前20小时)',
        '每天复盘分析10根K线',
      ],
      color: 'blue',
    },
    {
      stage: 2,
      title: '模式识别阶段',
      duration: '1-3个月',
      description: '系统学习8大经典交易模式,训练在实时图表中快速识别这些模式的能力。',
      goals: [
        '熟练识别8种经典交易模式',
        '理解每种模式的概率和风险收益比',
        '能在5分钟内扫描图表并找到交易机会',
        '开始在模拟账户中实践',
      ],
      resources: [
        '阅读《Trading Price Action Trends》全书',
        '观看模式识别专题视频',
        '每天标注至少5个交易设置',
        '模拟交易至少50笔',
      ],
      color: 'purple',
    },
    {
      stage: 3,
      title: '实战练习阶段',
      duration: '3-6个月',
      description: '在模拟账户中大量练习,建立交易系统,培养盘感和交易纪律。',
      goals: [
        '完成至少200笔模拟交易',
        '交易胜率达到40%以上',
        '盈亏比达到1:1.5以上',
        '建立完整的交易计划和日志系统',
      ],
      resources: [
        '阅读《Trading Price Action Trading Ranges》',
        '阅读《Trading Price Action Reversals》',
        '参加在线交易室观摩',
        '每周复盘总结交易得失',
      ],
      color: 'green',
    },
    {
      stage: 4,
      title: '精进提升阶段',
      duration: '持续进行',
      description: '不断优化交易系统,提升交易技能,培养专业交易者的心态和习惯。',
      goals: [
        '稳定盈利3个月以上',
        '形成自己的交易风格和优势模式',
        '情绪管理和心理素质达到专业水准',
        '持续学习和适应市场变化',
      ],
      resources: [
        '重读4本书,每次都有新收获',
        '参与交易社区讨论和分享',
        '研究其他成功交易者的方法',
        '考虑小额实盘交易(风险可控)',
      ],
      color: 'orange',
    },
  ];

  const colorClasses: Record<string, { bg: string; border: string; text: string }> = {
    blue: { bg: 'bg-blue-500/10', border: 'border-blue-400/30', text: 'text-blue-300' },
    purple: { bg: 'bg-purple-500/10', border: 'border-purple-400/30', text: 'text-purple-300' },
    green: { bg: 'bg-green-500/10', border: 'border-green-400/30', text: 'text-green-300' },
    orange: { bg: 'bg-orange-500/10', border: 'border-orange-400/30', text: 'text-orange-300' },
  };

  return (
    <section className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 md:p-12 border border-white/10">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center">
          <Route className="w-6 h-6 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-white">学习路线图</h2>
      </div>

      <p className="text-white/80 mb-8 leading-relaxed">
        学习价格行为交易是一个循序渐进的过程。以下是我们为你规划的4个阶段学习路线,
        从零基础到专业交易者,每个阶段都有明确的目标和学习资源。
      </p>

      {/* Timeline */}
      <div className="relative space-y-8">
        {/* Vertical line */}
        <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-blue-400 via-purple-400 via-green-400 to-orange-400 hidden md:block" />

        {stages.map((stage) => {
          const colors = colorClasses[stage.color];
          
          return (
            <div key={stage.stage} className="relative">
              {/* Stage marker */}
              <div className="hidden md:flex absolute left-0 w-16 h-16 items-center justify-center">
                <div className={`w-14 h-14 rounded-full ${colors.bg} border-4 ${colors.border} flex items-center justify-center bg-slate-900 z-10`}>
                  <span className={`text-xl font-bold ${colors.text}`}>{stage.stage}</span>
                </div>
              </div>

              {/* Content */}
              <div className="md:ml-24">
                <div className={`${colors.bg} rounded-xl p-6 border ${colors.border}`}>
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <span className="md:hidden text-2xl font-bold text-white">阶段 {stage.stage}</span>
                        <h3 className="text-2xl font-bold text-white">{stage.title}</h3>
                      </div>
                      <div className="flex items-center gap-2 text-white/70">
                        <Clock className="w-4 h-4" />
                        <span className="text-sm">{stage.duration}</span>
                      </div>
                    </div>
                  </div>

                  <p className="text-white/80 mb-6 leading-relaxed">
                    {stage.description}
                  </p>

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Learning Goals */}
                    <div>
                      <h4 className={`font-bold ${colors.text} mb-3 flex items-center gap-2`}>
                        <CheckCircle2 className="w-5 h-5" />
                        学习目标
                      </h4>
                      <ul className="space-y-2">
                        {stage.goals.map((goal, i) => (
                          <li key={i} className="text-sm text-white/70 flex items-start gap-2">
                            <div className={`w-1.5 h-1.5 rounded-full ${colors.text.replace('text-', 'bg-')} flex-shrink-0 mt-2`} />
                            <span>{goal}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Learning Resources */}
                    <div>
                      <h4 className={`font-bold ${colors.text} mb-3 flex items-center gap-2`}>
                        <BookOpen className="w-5 h-5" />
                        学习资源
                      </h4>
                      <ul className="space-y-2">
                        {stage.resources.map((resource, i) => (
                          <li key={i} className="text-sm text-white/70 flex items-start gap-2">
                            <div className={`w-1.5 h-1.5 rounded-full ${colors.text.replace('text-', 'bg-')} flex-shrink-0 mt-2`} />
                            <span>{resource}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Important Notes */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-blue-500/10 rounded-lg p-5 border border-blue-400/30">
          <h4 className="font-bold text-blue-300 mb-2 flex items-center gap-2">
            <Clock className="w-5 h-5" />
            关于时间安排
          </h4>
          <p className="text-sm text-white/70 leading-relaxed">
            以上时间仅供参考,实际进度因人而异。重要的不是速度,而是扎实掌握每个阶段的知识。
            不要急于进入下一阶段,宁可在当前阶段多花时间打好基础。
          </p>
        </div>

        <div className="bg-orange-500/10 rounded-lg p-5 border border-orange-400/30">
          <h4 className="font-bold text-orange-300 mb-2 flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5" />
            关于实盘交易
          </h4>
          <p className="text-sm text-white/70 leading-relaxed">
            <strong className="text-orange-300">不建议过早开始实盘交易</strong>。
            在模拟盘上稳定盈利至少3个月后,再考虑小额实盘。
            即使开始实盘,也要严格控制风险,单笔损失不超过账户的1-2%。
          </p>
        </div>
      </div>
    </section>
  );
}
