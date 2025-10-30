import React from 'react';
import { Target, CheckCircle2, XCircle, AlertTriangle, Zap } from 'lucide-react';

export default function PracticalTips() {
  const dailyRoutine = [
    '开盘前浏览日线图,确定市场状态(趋势/震荡)',
    '标记关键支撑阻力位和重要均线',
    '等待高概率的交易设置出现,不要勉强交易',
    '每笔交易前明确入场点、止损点和目标位',
    '严格执行交易计划,不要临时改变规则',
    '收盘后复盘,记录交易日志和心得体会',
  ];

  const entryChecklist = [
    { item: '是否出现明确的价格行为信号?', required: true },
    { item: '市场状态是否适合当前策略?', required: true },
    { item: '风险收益比是否至少1:1.5?', required: true },
    { item: '止损位置是否合理(不会被轻易扫出)?', required: true },
    { item: '是否在关键支撑/阻力位附近?', required: false },
    { item: '是否有其他确认信号(如成交量)?', required: false },
  ];

  const positionManagement = [
    {
      title: '初始仓位',
      description: '单笔交易风险不超过账户的1-2%',
      color: 'blue',
    },
    {
      title: '加仓策略',
      description: '只在盈利的交易上加仓,不要给亏损的交易摊低成本',
      color: 'green',
    },
    {
      title: '减仓时机',
      description: '达到第一目标位时可考虑减半仓,锁定利润',
      color: 'yellow',
    },
    {
      title: '止损管理',
      description: '入场后立即设置止损,盈利后移动止损到保本位',
      color: 'red',
    },
  ];

  const commonMistakes = [
    {
      mistake: '过度交易',
      reason: '看到价格波动就想交易,忽视信号质量',
      solution: '设置每日最大交易次数,只交易最高概率的机会',
    },
    {
      mistake: '不设止损',
      reason: '害怕被止损出局,或期待价格反弹',
      solution: '每笔交易必须设置止损,并严格执行',
    },
    {
      mistake: '频繁改变策略',
      reason: '几次失败后就怀疑策略,不断更换方法',
      solution: '给策略足够的样本量(至少50-100笔),再评估',
    },
    {
      mistake: '情绪化交易',
      reason: '连续亏损后急于翻本,或盈利后过度自信',
      solution: '连续3次亏损后暂停交易,冷静分析原因',
    },
    {
      mistake: '忽视风险管理',
      reason: '重仓交易,或单笔亏损超过承受能力',
      solution: '严格控制每笔风险在1-2%,保护交易资本',
    },
  ];

  return (
    <section className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 md:p-12 border border-white/10">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-red-400 to-rose-500 flex items-center justify-center">
          <Target className="w-6 h-6 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-white">实战应用技巧</h2>
      </div>

      <p className="text-white/80 mb-8 leading-relaxed">
        理论学习固然重要,但最终还是要落实到实战中。以下是一些实用的交易技巧和注意事项,
        帮助你更好地将Al Brooks的价格行为交易方法应用到实际交易中。
      </p>

      {/* Daily Routine */}
      <div className="mb-8">
        <h3 className="text-xl font-bold text-red-300 mb-4 flex items-center gap-2">
          <Zap className="w-5 h-5" />
          每日交易流程
        </h3>
        <div className="bg-gradient-to-br from-red-500/5 to-rose-500/5 rounded-xl p-6 border border-red-400/30">
          <div className="space-y-3">
            {dailyRoutine.map((step, index) => (
              <div key={index} className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-red-500/20 flex items-center justify-center flex-shrink-0 font-bold text-red-300 border border-red-400/30">
                  {index + 1}
                </div>
                <p className="text-white/80 pt-1">{step}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Entry Checklist */}
      <div className="mb-8">
        <h3 className="text-xl font-bold text-red-300 mb-4 flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5" />
          入场前检查清单
        </h3>
        <div className="bg-gradient-to-br from-red-500/5 to-rose-500/5 rounded-xl p-6 border border-red-400/30">
          <p className="text-white/70 mb-4 text-sm">
            在点击下单按钮前,先过一遍这个清单。<strong className="text-red-300">必选项</strong>必须全部满足,
            可选项至少满足一项。
          </p>
          <div className="space-y-2">
            {entryChecklist.map((check, index) => (
              <div
                key={index}
                className={`flex items-start gap-3 p-3 rounded-lg ${
                  check.required
                    ? 'bg-red-500/10 border border-red-400/30'
                    : 'bg-white/5 border border-white/10'
                }`}
              >
                <CheckCircle2
                  className={`w-5 h-5 flex-shrink-0 mt-0.5 ${
                    check.required ? 'text-red-400' : 'text-white/40'
                  }`}
                />
                <div className="flex-1">
                  <p className="text-white/90">{check.item}</p>
                  {check.required && (
                    <span className="text-xs text-red-300 font-medium">必选项</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Position Management */}
      <div className="mb-8">
        <h3 className="text-xl font-bold text-red-300 mb-4 flex items-center gap-2">
          <Target className="w-5 h-5" />
          仓位管理原则
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {positionManagement.map((rule, index) => (
            <div
              key={index}
              className="bg-gradient-to-br from-red-500/5 to-rose-500/5 rounded-xl p-5 border border-red-400/30"
            >
              <h4 className="font-bold text-white mb-2 flex items-center gap-2">
                <div className="w-6 h-6 rounded-lg bg-red-500/20 flex items-center justify-center text-xs text-red-300 border border-red-400/30">
                  {index + 1}
                </div>
                {rule.title}
              </h4>
              <p className="text-sm text-white/70">
                {rule.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Common Mistakes */}
      <div>
        <h3 className="text-xl font-bold text-red-300 mb-4 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5" />
          常见错误与解决方案
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-red-500/20">
                <th className="px-4 py-3 text-left text-white font-bold border border-red-400/30">常见错误</th>
                <th className="px-4 py-3 text-left text-white font-bold border border-red-400/30">原因分析</th>
                <th className="px-4 py-3 text-left text-white font-bold border border-red-400/30">解决方案</th>
              </tr>
            </thead>
            <tbody>
              {commonMistakes.map((mistake, index) => (
                <tr key={index} className="bg-white/5 hover:bg-white/10 transition-colors">
                  <td className="px-4 py-3 border border-red-400/20">
                    <div className="flex items-center gap-2">
                      <XCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
                      <span className="text-white/90 font-medium">{mistake.mistake}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-white/70 text-sm border border-red-400/20">
                    {mistake.reason}
                  </td>
                  <td className="px-4 py-3 border border-red-400/20">
                    <div className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-green-400 flex-shrink-0 mt-0.5" />
                      <span className="text-white/80 text-sm">{mistake.solution}</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Final Note */}
      <div className="mt-8 bg-gradient-to-r from-red-500/10 to-rose-500/10 rounded-xl p-6 border border-red-400/30">
        <h3 className="text-lg font-bold text-red-300 mb-3 flex items-center gap-2">
          <Target className="w-5 h-5" />
          最重要的一点
        </h3>
        <p className="text-white/80 leading-relaxed">
          <strong className="text-red-300">交易是一场马拉松,而非短跑</strong>。
          不要期望在短时间内成为专家,也不要因为几次失败就放弃。
          持续学习、大量练习、严格执行、总结反思 —— 这是成功交易者的必经之路。
          记住:你的目标不是赢得每一笔交易,而是建立长期稳定盈利的交易系统。
        </p>
      </div>
    </section>
  );
}
