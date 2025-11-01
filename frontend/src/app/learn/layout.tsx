import { ReactNode } from 'react';
import '@/styles/learn-layout.css';

export default function LearnLayout({
  children,
}: {
  children: ReactNode;
}) {
  // 学习中心使用自己的独立布局,不显示全局 Header
  return <div className="learn-page-wrapper">{children}</div>;
}
