import React from 'react';
import { BookOpen, Star, ExternalLink } from 'lucide-react';

export default function BooksList() {
  const books = [
    {
      title: 'Reading Price Charts Bar by Bar',
      titleCn: '逐根K线解读价格行为',
      year: 2009,
      pages: 400,
      difficulty: 3,
      rating: 4.8,
      description: 'Al Brooks价格行为交易系列的第一本,也是最基础的一本。详细讲解了价格行为交易的基本概念、K线解读方法、市场结构分析等核心内容。',
      coreContent: [
        '价格行为交易的基本原理',
        '单根K线和K线组合的解读',
        '趋势、震荡和过渡的识别',
        '支撑阻力位的判断',
        '入场、止损和目标位的设置',
      ],
      targetAudience: '零基础学员,适合作为入门教材',
      keyChapters: '第3章(趋势)、第5章(K线形态)、第11章(交易管理)',
    },
    {
      title: 'Trading Price Action Trends',
      titleCn: '趋势交易中的价格行为',
      year: 2011,
      pages: 350,
      difficulty: 4,
      rating: 4.7,
      description: '专注于趋势市场的交易策略。深入讲解如何识别趋势、如何在趋势中寻找入场点、如何管理趋势交易等。',
      coreContent: [
        '趋势的定义和分类(强趋势/弱趋势)',
        '趋势通道的绘制和使用',
        '回调入场的最佳时机',
        '趋势反转的早期信号',
        '尖峰通道(Spike & Channel)交易',
      ],
      targetAudience: '有一定基础,想专注趋势交易的学员',
      keyChapters: '第2章(趋势线)、第5章(通道)、第12章(尖峰通道)',
    },
    {
      title: 'Trading Price Action Trading Ranges',
      titleCn: '震荡区间中的价格行为',
      year: 2012,
      pages: 350,
      difficulty: 4,
      rating: 4.6,
      description: '专门讲解震荡市场(Trading Range)的交易方法。震荡市场占据市场时间的60-70%,掌握震荡交易至关重要。',
      coreContent: [
        '震荡区间的识别和定义',
        '震荡区间内的高抛低吸策略',
        '突破交易与假突破识别',
        '从震荡到趋势的过渡',
        '楔形(Wedge)形态交易',
      ],
      targetAudience: '想提高震荡市场交易能力的中级学员',
      keyChapters: '第3章(震荡特征)、第7章(突破)、第10章(楔形)',
    },
    {
      title: 'Trading Price Action Reversals',
      titleCn: '反转中的价格行为',
      year: 2012,
      pages: 350,
      difficulty: 5,
      rating: 4.7,
      description: '最高级的一本,讲解各种反转形态和反转交易策略。反转交易风险高但收益也高,需要丰富的经验。',
      coreContent: [
        '主要反转形态(双顶/双底、头肩顶/底等)',
        '反转K线的识别',
        '趋势衰竭的信号',
        '反转确认的方法',
        '反转交易的风险管理',
      ],
      targetAudience: '有丰富经验,想掌握反转交易的高级学员',
      keyChapters: '第4章(反转形态)、第8章(失败的反转)、第11章(楔形反转)',
    },
  ];

  return (
    <section className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 md:p-12 border border-white/10">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-yellow-400 to-amber-500 flex items-center justify-center">
          <BookOpen className="w-6 h-6 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-white">四本必读书籍</h2>
      </div>

      <p className="text-white/80 mb-8 leading-relaxed">
        Al Brooks 的4本价格行为交易系列书籍,由 <strong className="text-yellow-300">Wiley 出版社</strong> 出版,
        是价格行为交易领域的权威教材。建议<strong className="text-yellow-300">按顺序阅读</strong>,
        每本书至少读2-3遍,每次都会有新的收获。
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {books.map((book, index) => (
          <div
            key={index}
            className="bg-gradient-to-br from-yellow-500/5 to-amber-500/5 rounded-xl p-6 border border-yellow-400/30 hover:border-yellow-400/50 transition-all duration-300"
          >
            {/* Book Header */}
            <div className="flex items-start gap-4 mb-4">
              <div className="w-16 h-20 bg-gradient-to-br from-yellow-400 to-amber-500 rounded-lg flex items-center justify-center flex-shrink-0 shadow-lg">
                <span className="text-2xl font-bold text-white">{index + 1}</span>
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-xl font-bold text-white mb-1 leading-tight">
                  {book.titleCn}
                </h3>
                <p className="text-sm text-yellow-300/80 mb-2 leading-tight">
                  {book.title}
                </p>
                <div className="flex items-center gap-3 text-xs text-white/60">
                  <span>{book.year}年</span>
                  <span>•</span>
                  <span>{book.pages}页</span>
                  <span>•</span>
                  <div className="flex items-center gap-1">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <Star
                        key={i}
                        className={`w-3 h-3 ${
                          i < Math.floor(book.rating)
                            ? 'text-yellow-400 fill-current'
                            : 'text-white/30'
                        }`}
                      />
                    ))}
                    <span className="ml-1 text-yellow-400">{book.rating}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Difficulty */}
            <div className="flex items-center gap-2 mb-4">
              <span className="text-xs text-white/70">难度:</span>
              <div className="flex gap-1">
                {Array.from({ length: 5 }).map((_, i) => (
                  <div
                    key={i}
                    className={`w-6 h-2 rounded-full ${
                      i < book.difficulty ? 'bg-yellow-400' : 'bg-white/20'
                    }`}
                  />
                ))}
              </div>
            </div>

            {/* Description */}
            <p className="text-white/80 mb-4 leading-relaxed text-sm">
              {book.description}
            </p>

            {/* Core Content */}
            <div className="mb-4">
              <h4 className="text-sm font-bold text-yellow-300 mb-2">核心内容:</h4>
              <ul className="space-y-1">
                {book.coreContent.map((content, i) => (
                  <li key={i} className="text-xs text-white/70 flex items-start gap-2">
                    <div className="w-1 h-1 rounded-full bg-yellow-400 flex-shrink-0 mt-1.5" />
                    <span>{content}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Target Audience & Key Chapters */}
            <div className="space-y-2 mb-4 text-xs">
              <div className="bg-white/5 rounded-lg p-3 border border-yellow-400/20">
                <span className="font-bold text-yellow-300">适合人群: </span>
                <span className="text-white/70">{book.targetAudience}</span>
              </div>
              <div className="bg-white/5 rounded-lg p-3 border border-yellow-400/20">
                <span className="font-bold text-yellow-300">重点章节: </span>
                <span className="text-white/70">{book.keyChapters}</span>
              </div>
            </div>

            {/* Purchase Links */}
            <div className="flex gap-2">
              <a
                href={`https://www.amazon.com/s?k=${encodeURIComponent(book.title)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 px-4 py-2 bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-300 text-sm font-medium rounded-lg transition-colors border border-yellow-400/30 flex items-center justify-center gap-2"
              >
                <ExternalLink className="w-4 h-4" />
                <span>Amazon</span>
              </a>
              <a
                href={`https://book.douban.com/subject_search?search_text=${encodeURIComponent(book.title)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 px-4 py-2 bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-300 text-sm font-medium rounded-lg transition-colors border border-yellow-400/30 flex items-center justify-center gap-2"
              >
                <ExternalLink className="w-4 h-4" />
                <span>豆瓣</span>
              </a>
            </div>
          </div>
        ))}
      </div>

      {/* Reading Tips */}
      <div className="mt-8 bg-gradient-to-r from-yellow-500/10 to-amber-500/10 rounded-xl p-6 border border-yellow-400/30">
        <h3 className="text-lg font-bold text-yellow-300 mb-3 flex items-center gap-2">
          <BookOpen className="w-5 h-5" />
          阅读建议
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-white/80">
          <div>
            <p className="mb-2">
              <strong className="text-yellow-300">• 循序渐进:</strong> 先读第一本打基础,再根据自己的交易风格选择后续书籍
            </p>
            <p className="mb-2">
              <strong className="text-yellow-300">• 边读边练:</strong> 每学完一章,立即在图表上寻找相应的实例
            </p>
          </div>
          <div>
            <p className="mb-2">
              <strong className="text-yellow-300">• 重复阅读:</strong> 这些书需要反复读,每次都会有新的理解
            </p>
            <p className="mb-2">
              <strong className="text-yellow-300">• 做好笔记:</strong> 记录关键概念和自己的思考,建立知识体系
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
