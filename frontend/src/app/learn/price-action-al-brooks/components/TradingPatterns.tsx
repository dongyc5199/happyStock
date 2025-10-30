import React from 'react';
import { BarChart3, TrendingUp, TrendingDown, ArrowUp, ArrowDown } from 'lucide-react';

export default function TradingPatterns() {
  const patterns = [
    {
      id: 1,
      name: '趋势K线',
      nameEn: 'Trend Bars',
      difficulty: '入门',
      description: '实体大、影线小的K线,表明市场方向明确,买卖双方力量悬殊。连续出现趋势K线预示强劲趋势。',
      characteristics: ['实体占比超过70%', '收盘价接近最高/最低价', '影线很短或没有'],
      trading: ['顺势交易,不要逆势', '回调后继续入场', '止损放在前低/高点'],
      example: `
  上涨趋势K线示意:
     │
     ├──┐
     │  │ ← 大阳线
     │  │
     ├──┘
     │
      `,
    },
    {
      id: 2,
      name: '反转K线',
      nameEn: 'Reversal Bars',
      difficulty: '入门',
      description: '在趋势末期出现的反向大K线,通常伴随高成交量,预示趋势可能反转。包括看涨吞没和看跌吞没形态。',
      characteristics: ['与前一K线方向相反', '实体较大', '最好伴随成交量放大'],
      trading: ['等待确认后入场', '止损设在K线另一端', '目标位看前期支撑/阻力'],
      example: `
  看涨反转示意:
     ┌──┐
     │  │ ← 大阳线吞没前阴线
  ───┤  ├───
     │  │
     └──┘
      `,
    },
    {
      id: 3,
      name: '内包K线',
      nameEn: 'Inside Bars',
      difficulty: '进阶',
      description: '当前K线的高低点完全包含在前一根K线内,表示市场暂时失去方向,往往是突破的前兆。连续内包(ii, iii)信号更强。',
      characteristics: ['高点更低,低点更高', '表示市场犹豫', '通常在关键位置出现'],
      trading: ['在内包K线高低点设挂单', '向上突破做多,向下突破做空', '假突破风险较高,注意止损'],
      example: `
  内包K线(ii):
   ┌─┐
   │ ├┐    ← 第二根完全在第一根内
   └─┘│
     └┘
      `,
    },
    {
      id: 4,
      name: '双顶/双底',
      nameEn: 'Double Top/Bottom',
      difficulty: '进阶',
      description: '价格两次测试同一价格区域后反转,是最常见的反转形态。第二次测试往往伴随成交量萎缩或背离。',
      characteristics: ['两次触及相近价格', '第二次测试力度减弱', '常伴随背离'],
      trading: ['在颈线位入场', '止损放在顶/底部外', '目标位至少是双顶/底高度'],
      example: `
  双顶(M顶):
     ╱╲   ╱╲
    ╱  ╲ ╱  ╲  ← 两次触及阻力
   ╱    ╲    ╲
  ╱      ╲────╲ ← 跌破颈线确认
      `,
    },
    {
      id: 5,
      name: '突破与突破失败',
      nameEn: 'Breakouts & Failed Breakouts',
      difficulty: '进阶',
      description: '突破重要支撑/阻力位是强烈信号。但假突破也很常见,学会识别真假突破是关键。真突破伴随大K线和成交量。',
      characteristics: ['突破伴随大实体K线', '成交量显著放大', '突破后不回破位'],
      trading: ['突破后回踩入场更安全', '假突破可反向交易', '设好止损防止被骗'],
      example: `
  真突破:
        ──────  ← 阻力位
     ↑
     │  ← 大阳线突破
     │
  ───┴───
  
  假突破:
        ──────  ← 阻力位
     ↑↓ ← 短暂突破后回落
  ───┴┴───
      `,
    },
    {
      id: 6,
      name: '微趋势线突破',
      nameEn: 'Microtrend Line Breaks',
      difficulty: '高级',
      description: '在趋势中绘制连接最近几根K线低点(上涨)或高点(下跌)的趋势线,突破该线提供回调入场机会。',
      characteristics: ['连接3个以上点', '突破后快速回归趋势', '是趋势交易最佳入场点'],
      trading: ['趋势线突破时入场', '止损设在突破K线外', '目标看前期高/低点'],
      example: `
  上涨微趋势线:
        ╱
       ╱
      ╱  ← 突破趋势线后入场
     ╱___
    ╱
   ╱
      `,
    },
    {
      id: 7,
      name: '尖峰通道',
      nameEn: 'Spike & Channel',
      difficulty: '高级',
      description: '趋势通常分两个阶段:尖峰(快速突破)和通道(缓慢上涨)。识别这两个阶段有助于把握趋势节奏。',
      characteristics: ['初期快速上涨(尖峰)', '随后形成上升通道', '通道突破可能趋势结束'],
      trading: ['尖峰阶段少量参与', '通道阶段是主要交易区', '通道被跌破考虑平仓'],
      example: `
  尖峰通道结构:
      ╱──╱  ← 通道阶段
     ╱  ╱
    │  ╱
    │ ╱
    │╱  ← 尖峰阶段
      `,
    },
    {
      id: 8,
      name: '楔形',
      nameEn: 'Wedges',
      difficulty: '高级',
      description: '价格形成三次推进,但每次推进力度递减,形成楔形结构,通常预示趋势衰竭和即将反转。',
      characteristics: ['三次推进,一次比一次弱', '高点/低点逐渐收敛', '第三次推进后反转概率大'],
      trading: ['第三次推进失败时入场', '止损设在楔形外', '目标至少楔形起点'],
      example: `
  上涨楔形(看跌):
       ╱3
      ╱
     ╱2  ← 三次推进递减
    ╱
   ╱1
  ────── 突破后下跌
      `,
    },
  ];

  return (
    <section className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 md:p-12 border border-white/10">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-400 to-emerald-500 flex items-center justify-center">
          <BarChart3 className="w-6 h-6 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-white">八大经典交易模式</h2>
      </div>

      <p className="text-white/80 mb-8 leading-relaxed">
        Al Brooks 总结出了8种最常见、最有效的价格行为交易模式。
        掌握这些模式,你就拥有了在任何市场环境下寻找交易机会的能力。
      </p>

      <div className="space-y-6">
        {patterns.map((pattern) => (
          <div
            key={pattern.id}
            className="bg-gradient-to-br from-green-500/5 to-emerald-500/5 rounded-xl p-6 border border-green-400/30 hover:border-green-400/50 transition-colors"
          >
            <div className="flex flex-col md:flex-row gap-6">
              {/* Left: Info */}
              <div className="flex-1">
                <div className="flex items-start gap-4 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center flex-shrink-0 font-bold text-green-400">
                    {pattern.id}
                  </div>
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-2xl font-bold text-white">
                        {pattern.name}
                      </h3>
                      <span className="text-sm px-3 py-1 rounded-full bg-green-500/20 text-green-300 border border-green-400/30">
                        {pattern.difficulty}
                      </span>
                    </div>
                    <p className="text-sm text-green-300/80">{pattern.nameEn}</p>
                  </div>
                </div>

                <p className="text-white/80 mb-4 leading-relaxed">
                  {pattern.description}
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="text-sm font-bold text-green-300 mb-2 flex items-center gap-2">
                      <TrendingUp className="w-4 h-4" />
                      形态特征
                    </h4>
                    <ul className="space-y-1">
                      {pattern.characteristics.map((char, i) => (
                        <li key={i} className="text-sm text-white/70 flex items-start gap-2">
                          <ArrowUp className="w-3 h-3 text-green-400 flex-shrink-0 mt-1" />
                          <span>{char}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h4 className="text-sm font-bold text-green-300 mb-2 flex items-center gap-2">
                      <TrendingDown className="w-4 h-4" />
                      交易策略
                    </h4>
                    <ul className="space-y-1">
                      {pattern.trading.map((trade, i) => (
                        <li key={i} className="text-sm text-white/70 flex items-start gap-2">
                          <ArrowDown className="w-3 h-3 text-emerald-400 flex-shrink-0 mt-1" />
                          <span>{trade}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>

              {/* Right: Chart Example */}
              <div className="md:w-48 flex-shrink-0">
                <div className="bg-black/30 rounded-lg p-4 border border-green-400/20">
                  <h4 className="text-xs font-bold text-green-300 mb-3 text-center">图表示意</h4>
                  <pre className="text-green-400 text-xs leading-tight font-mono overflow-x-auto">
                    {pattern.example}
                  </pre>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Practice Tip */}
      <div className="mt-8 bg-gradient-to-r from-green-500/10 to-emerald-500/10 rounded-xl p-6 border border-green-400/30">
        <h3 className="text-lg font-bold text-green-300 mb-3 flex items-center gap-2">
          <BarChart3 className="w-5 h-5" />
          实践建议
        </h3>
        <p className="text-white/80 leading-relaxed">
          <strong className="text-green-300">不要试图一次掌握所有模式</strong>。
          建议从最基础的趋势K线和反转K线开始,在模拟盘上反复练习。
          每个模式至少观察50-100次实例,并记录交易日志。
          随着经验积累,再逐步学习更高级的模式。记住:熟练度比数量更重要!
        </p>
      </div>
    </section>
  );
}
