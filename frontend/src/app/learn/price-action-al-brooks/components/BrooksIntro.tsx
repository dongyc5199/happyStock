import React from 'react';
import { User, Award, BookOpen, TrendingUp } from 'lucide-react';

export default function BrooksIntro() {
  return (
    <section className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 md:p-12 border border-white/10">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center">
          <User className="w-6 h-6 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-white">Al Brooks 大师简介</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Left Column - Biography */}
        <div className="space-y-4">
          <h3 className="text-xl font-bold text-yellow-300 flex items-center gap-2">
            <Award className="w-5 h-5" />
            个人背景
          </h3>
          <div className="text-white/80 space-y-3 leading-relaxed">
            <p>
              <strong className="text-yellow-300">Al Brooks</strong> 拥有医学博士(MD)学位,
              曾是一名执业医生。在取得了成功的医学生涯后,他决定全职投身于金融市场交易,
              这一转变展现了他对交易事业的极大热情和决心。
            </p>
            <p>
              Brooks 从事专业交易已超过<strong className="text-yellow-300">30年</strong>,
              积累了丰富的实战经验。他不仅是一位成功的交易者,
              更致力于教育工作,帮助全球数以万计的交易者理解和应用价格行为交易方法。
            </p>
            <p>
              他被业界誉为<strong className="text-yellow-300">&ldquo;世界最佳价格行为权威&rdquo;</strong>(The Best Price Action Authority in the World),
              这一称号体现了他在价格行为分析领域的卓越地位和广泛影响力。
            </p>
          </div>
        </div>

        {/* Right Column - Achievements */}
        <div className="space-y-4">
          <h3 className="text-xl font-bold text-yellow-300 flex items-center gap-2">
            <BookOpen className="w-5 h-5" />
            主要成就
          </h3>
          <div className="space-y-3">
            <div className="bg-white/5 rounded-lg p-4 border border-yellow-400/20">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-yellow-500/20 flex items-center justify-center flex-shrink-0">
                  <BookOpen className="w-4 h-4 text-yellow-400" />
                </div>
                <div>
                  <h4 className="font-bold text-white mb-1">4本畅销书</h4>
                  <p className="text-sm text-white/70">
                    由 Wiley 出版社出版,全球发行,被誉为价格行为交易的&ldquo;圣经&rdquo;
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white/5 rounded-lg p-4 border border-yellow-400/20">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-yellow-500/20 flex items-center justify-center flex-shrink-0">
                  <TrendingUp className="w-4 h-4 text-yellow-400" />
                </div>
                <div>
                  <h4 className="font-bold text-white mb-1">在线课程与交易室</h4>
                  <p className="text-sm text-white/70">
                    提供100+小时的完整视频课程和实时交易室服务
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white/5 rounded-lg p-4 border border-yellow-400/20">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-yellow-500/20 flex items-center justify-center flex-shrink-0">
                  <Award className="w-4 h-4 text-yellow-400" />
                </div>
                <div>
                  <h4 className="font-bold text-white mb-1">行业认可</h4>
                  <p className="text-sm text-white/70">
                    CME、MoneyShow、Investing.com 等知名机构的特邀讲师
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Key Contributions */}
      <div className="mt-8 pt-8 border-t border-white/10">
        <h3 className="text-xl font-bold text-yellow-300 mb-4">核心贡献</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gradient-to-br from-yellow-500/10 to-orange-500/10 rounded-lg p-4 border border-yellow-400/20">
            <h4 className="font-bold text-white mb-2">系统化方法论</h4>
            <p className="text-sm text-white/70">
              将价格行为交易从经验主义提升为可学习、可复制的系统化交易方法
            </p>
          </div>
          <div className="bg-gradient-to-br from-yellow-500/10 to-orange-500/10 rounded-lg p-4 border border-yellow-400/20">
            <h4 className="font-bold text-white mb-2">概率思维</h4>
            <p className="text-sm text-white/70">
              强调以概率和数学期望为基础的交易决策,而非追求完美的市场预测
            </p>
          </div>
          <div className="bg-gradient-to-br from-yellow-500/10 to-orange-500/10 rounded-lg p-4 border border-yellow-400/20">
            <h4 className="font-bold text-white mb-2">实战导向</h4>
            <p className="text-sm text-white/70">
              所有理论均来自30+年实战经验,适用于任何市场和时间周期
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
