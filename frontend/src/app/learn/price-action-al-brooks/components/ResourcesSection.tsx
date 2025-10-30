import React from 'react';
import { Globe, Video, MessageCircle, Users, ExternalLink } from 'lucide-react';

export default function ResourcesSection() {
  const officialResources = [
    {
      icon: Globe,
      title: 'Al Brooks官方网站',
      description: '获取最新课程信息、博客文章和交易室服务',
      url: 'https://www.brookstradingcourse.com',
      color: 'blue',
    },
    {
      icon: Video,
      title: '100+小时视频课程',
      description: '完整的价格行为交易视频教程,涵盖所有核心概念',
      url: 'https://www.brookstradingcourse.com/video-course',
      color: 'purple',
    },
    {
      icon: Users,
      title: 'Al Brooks交易室',
      description: '每日实时市场分析和交易机会讲解',
      url: 'https://www.brookstradingcourse.com/trading-room',
      color: 'green',
    },
  ];

  const chineseResources = [
    {
      icon: MessageCircle,
      title: '知乎专栏',
      description: '搜索"Al Brooks"或"价格行为交易",有很多高质量的学习笔记和实战分享',
      keywords: ['Al Brooks', '价格行为', 'Price Action'],
      color: 'blue',
    },
    {
      icon: Video,
      title: 'B站视频教程',
      description: 'B站上有Al Brooks书籍的导读视频和实战案例分析',
      keywords: ['Al Brooks', '价格行为交易', 'K线形态'],
      color: 'pink',
    },
    {
      icon: MessageCircle,
      title: '微信公众号',
      description: '关注"价格行为交易"、"裸K交易"等主题的公众号',
      keywords: ['价格行为', '裸K交易', '盘感训练'],
      color: 'green',
    },
    {
      icon: Users,
      title: '交易论坛与社群',
      description: '加入价格行为交易相关的QQ群、微信群,与同行交流',
      keywords: ['价格行为交易群', 'Al Brooks学习群'],
      color: 'orange',
    },
  ];

  const colorClasses: Record<string, { bg: string; icon: string; border: string }> = {
    blue: { bg: 'bg-blue-500/10', icon: 'text-blue-400', border: 'border-blue-400/30' },
    purple: { bg: 'bg-purple-500/10', icon: 'text-purple-400', border: 'border-purple-400/30' },
    green: { bg: 'bg-green-500/10', icon: 'text-green-400', border: 'border-green-400/30' },
    orange: { bg: 'bg-orange-500/10', icon: 'text-orange-400', border: 'border-orange-400/30' },
    pink: { bg: 'bg-pink-500/10', icon: 'text-pink-400', border: 'border-pink-400/30' },
  };

  return (
    <section className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 md:p-12 border border-white/10">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center">
          <Globe className="w-6 h-6 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-white">学习资源推荐</h2>
      </div>

      {/* Official Resources */}
      <div className="mb-12">
        <h3 className="text-xl font-bold text-emerald-300 mb-4 flex items-center gap-2">
          <Globe className="w-5 h-5" />
          官方资源(英文)
        </h3>
        <p className="text-white/70 mb-6 text-sm">
          Al Brooks的官方资源是学习价格行为交易的最佳来源,内容最权威、最系统。
          虽然是英文,但配合图表讲解,理解难度不大。
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {officialResources.map((resource, index) => {
            const Icon = resource.icon;
            const colors = colorClasses[resource.color];
            
            return (
              <a
                key={index}
                href={resource.url}
                target="_blank"
                rel="noopener noreferrer"
                className={`block ${colors.bg} rounded-xl p-6 border ${colors.border} hover:border-emerald-400/50 transition-all duration-300 group`}
              >
                <div className={`w-12 h-12 rounded-lg ${colors.bg} border ${colors.border} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <Icon className={`w-6 h-6 ${colors.icon}`} />
                </div>
                <h4 className="font-bold text-white mb-2 flex items-center gap-2">
                  {resource.title}
                  <ExternalLink className="w-4 h-4 text-emerald-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                </h4>
                <p className="text-sm text-white/70">
                  {resource.description}
                </p>
              </a>
            );
          })}
        </div>
      </div>

      {/* Chinese Resources */}
      <div>
        <h3 className="text-xl font-bold text-emerald-300 mb-4 flex items-center gap-2">
          <MessageCircle className="w-5 h-5" />
          中文学习资源
        </h3>
        <p className="text-white/70 mb-6 text-sm">
          国内也有不少优质的价格行为交易学习资源,可以帮助你更好地理解和应用这些理论。
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {chineseResources.map((resource, index) => {
            const Icon = resource.icon;
            const colors = colorClasses[resource.color];
            
            return (
              <div
                key={index}
                className={`${colors.bg} rounded-xl p-6 border ${colors.border}`}
              >
                <div className="flex items-start gap-4 mb-4">
                  <div className={`w-12 h-12 rounded-lg ${colors.bg} border ${colors.border} flex items-center justify-center flex-shrink-0`}>
                    <Icon className={`w-6 h-6 ${colors.icon}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-bold text-white mb-2">
                      {resource.title}
                    </h4>
                    <p className="text-sm text-white/70 mb-3">
                      {resource.description}
                    </p>
                  </div>
                </div>
                <div className="flex flex-wrap gap-2">
                  {resource.keywords.map((keyword, i) => (
                    <span
                      key={i}
                      className={`text-xs px-3 py-1 rounded-full ${colors.bg} ${colors.icon} border ${colors.border}`}
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Important Notes */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-emerald-500/10 rounded-lg p-5 border border-emerald-400/30">
          <h4 className="font-bold text-emerald-300 mb-2 flex items-center gap-2">
            <ExternalLink className="w-5 h-5" />
            官方课程说明
          </h4>
          <p className="text-sm text-white/70 leading-relaxed">
            Al Brooks的视频课程价格约<strong className="text-emerald-300">$399</strong>(一次性付费),
            交易室服务约<strong className="text-emerald-300">$99/月</strong>。
            虽然价格不低,但内容非常系统和深入。对于认真学习的人来说,是物有所值的投资。
          </p>
        </div>

        <div className="bg-orange-500/10 rounded-lg p-5 border border-orange-400/30">
          <h4 className="font-bold text-orange-300 mb-2 flex items-center gap-2">
            <MessageCircle className="w-5 h-5" />
            甄别信息质量
          </h4>
          <p className="text-sm text-white/70 leading-relaxed">
            网络上关于价格行为交易的资源质量参差不齐。建议<strong className="text-orange-300">以官方书籍和课程为准</strong>,
            其他资源仅作为补充参考。避免盲目相信各种&ldquo;必胜法&rdquo;、&ldquo;秘籍&rdquo;等夸张宣传。
          </p>
        </div>
      </div>
    </section>
  );
}
