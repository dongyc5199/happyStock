import React, { useState } from 'react';
import { HelpCircle, ChevronDown, ChevronUp } from 'lucide-react';

interface FAQItem {
  question: string;
  answer: string;
  category: string;
}

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  const faqs: FAQItem[] = [
    {
      question: '学习Al Brooks的价格行为交易需要多长时间?',
      answer: '这取决于你的学习投入和市场经验。零基础学员通常需要6-12个月才能基本掌握,其中包括理论学习(2-3个月)和大量模拟交易练习(3-9个月)。但要达到稳定盈利的水平,可能需要1-2年甚至更长时间。记住:学习交易是一个持续的过程,即使是Al Brooks本人也强调要不断学习和适应市场变化。',
      category: '学习相关',
    },
    {
      question: '零基础可以学习价格行为交易吗?',
      answer: '完全可以!Al Brooks的价格行为交易方法实际上对零基础学员更友好,因为你不需要先学习各种复杂的技术指标。从一张干净的K线图开始,循序渐进地学习价格行为的语言,反而比那些已经形成固定思维模式的交易者更容易接受这套方法。建议从第一本书《Reading Price Charts Bar by Bar》开始,配合大量看盘练习。',
      category: '学习相关',
    },
    {
      question: '价格行为交易完全不使用指标吗?',
      answer: 'Al Brooks的价格行为交易主要依赖纯K线分析,但并不绝对排斥所有指标。他本人也使用移动平均线(MA)来辅助判断趋势方向。关键在于:价格行为是主要决策依据,指标只是辅助工具。不要让指标主导你的交易决策,更不要在图表上堆砌一堆指标。一条20EMA或50EMA足矣。',
      category: '方法论',
    },
    {
      question: '如何判断当前市场是趋势还是震荡?',
      answer: '这是价格行为交易的核心问题之一。Al Brooks提供了几个判断标准:1) 趋势市场有明显的更高高点和更高低点(上涨)或更低高点和更低低点(下跌);2) 趋势K线连续出现,实体大,方向一致;3) 回调幅度小于推进幅度;4) 价格明显偏离移动平均线。震荡市场则相反:价格在一个区间内来回波动,没有明确方向,K线大小不一,方向混乱。刚开始可能不好判断,需要大量看盘练习培养盘感。',
      category: '方法论',
    },
    {
      question: '价格行为交易的胜率和盈亏比大概是多少?',
      answer: 'Al Brooks强调不要追求高胜率。在价格行为交易中,40-50%的胜率是正常且可接受的。关键是要有足够的盈亏比(Risk:Reward Ratio)。如果你的盈亏比能达到1:2,那么即使胜率只有40%,长期下来也是盈利的。实际上,追求过高的胜率往往会导致过早止盈,错失大行情。更好的策略是:接受一定的失败率,让盈利的交易充分发展,把亏损的交易及时截断。',
      category: '交易表现',
    },
    {
      question: '价格行为交易适用于哪些市场和时间周期?',
      answer: 'Al Brooks的价格行为交易方法具有普适性,适用于任何市场(股票、期货、外汇、加密货币)和任何时间周期(从1分钟到日线甚至周线)。这是因为价格行为反映的是市场参与者的心理和行为,这些基本规律在不同市场和周期是相通的。不过,Al Brooks本人主要交易E-mini S&P 500期货,使用5分钟图。对于初学者,建议从15分钟或1小时图开始练习,这样信号更清晰,节奏也更从容。',
      category: '适用性',
    },
    {
      question: 'Al Brooks的方法能直接用于A股市场吗?',
      answer: '可以,但需要注意A股的特殊性。Al Brooks的价格行为原理是普适的,但A股有一些独特之处:1) T+1交易制度;2) 10%涨跌停限制;3) 较强的政策影响;4) 散户占比大,市场情绪波动大。这些因素会影响价格行为的表现。建议在应用时:更注重大周期图表(日线、周线),减少日内交易;适当调整止损和目标位设置;关注政策面和资金流向;在模拟盘上充分验证后再实盘。总体而言,核心理念是通用的,但具体应用需要根据A股特点做调整。',
      category: '适用性',
    },
    {
      question: '如何克服交易中的心理障碍?',
      answer: 'Al Brooks认为,交易心理问题的根源往往是缺乏明确的交易计划和风险管理。要克服心理障碍:1) 制定详细的交易计划,包括入场、止损、止盈规则;2) 严格控制每笔交易的风险(不超过账户的1-2%);3) 接受亏损是交易的一部分,不要因为一次失败就否定整个策略;4) 记录交易日志,客观分析得失;5) 设置每日最大亏损额,达到后立即停止交易。当你知道最坏的结果是什么,并且这个结果在你的承受范围内时,心理压力会大大减轻。记住:你的目标不是每笔都赢,而是长期稳定盈利。',
      category: '心理管理',
    },
  ];

  return (
    <section className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 md:p-12 border border-white/10">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center">
          <HelpCircle className="w-6 h-6 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-white">常见问题解答</h2>
      </div>

      <p className="text-white/80 mb-8 leading-relaxed">
        以下是学习Al Brooks价格行为交易过程中最常遇到的问题及其详细解答。
        点击问题可展开查看完整答案。
      </p>

      <div className="space-y-4">
        {faqs.map((faq, index) => (
          <div
            key={index}
            className="bg-gradient-to-br from-indigo-500/5 to-purple-500/5 rounded-xl border border-indigo-400/30 overflow-hidden transition-all duration-300"
          >
            <button
              onClick={() => setOpenIndex(openIndex === index ? null : index)}
              className="w-full px-6 py-4 flex items-start justify-between gap-4 hover:bg-white/5 transition-colors"
            >
              <div className="flex-1 text-left">
                <div className="flex items-center gap-3 mb-1">
                  <span className="text-xs px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-400/30 font-medium">
                    {faq.category}
                  </span>
                </div>
                <h3 className="text-lg font-bold text-white">
                  {faq.question}
                </h3>
              </div>
              <div className="flex-shrink-0">
                {openIndex === index ? (
                  <ChevronUp className="w-6 h-6 text-indigo-400" />
                ) : (
                  <ChevronDown className="w-6 h-6 text-indigo-400" />
                )}
              </div>
            </button>
            
            {openIndex === index && (
              <div className="px-6 pb-4 pt-2 border-t border-indigo-400/20">
                <p className="text-white/80 leading-relaxed whitespace-pre-line">
                  {faq.answer}
                </p>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Additional Help */}
      <div className="mt-8 bg-gradient-to-r from-indigo-500/10 to-purple-500/10 rounded-xl p-6 border border-indigo-400/30">
        <h3 className="text-lg font-bold text-indigo-300 mb-3 flex items-center gap-2">
          <HelpCircle className="w-5 h-5" />
          还有其他问题?
        </h3>
        <p className="text-white/80 mb-4 leading-relaxed">
          如果以上解答没有覆盖你的疑问,可以通过以下方式寻求帮助:
        </p>
        <ul className="space-y-2 text-sm text-white/70">
          <li className="flex items-start gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-indigo-400 flex-shrink-0 mt-2" />
            <span>在happyStock虚拟市场中实践,通过大量练习找到答案</span>
          </li>
          <li className="flex items-start gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-indigo-400 flex-shrink-0 mt-2" />
            <span>加入价格行为交易相关的学习社群,与其他学员交流</span>
          </li>
          <li className="flex items-start gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-indigo-400 flex-shrink-0 mt-2" />
            <span>重读Al Brooks的书籍,每次阅读都会有新的理解</span>
          </li>
          <li className="flex items-start gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-indigo-400 flex-shrink-0 mt-2" />
            <span>订阅Al Brooks的官方课程和交易室,获得第一手指导</span>
          </li>
        </ul>
      </div>
    </section>
  );
}
