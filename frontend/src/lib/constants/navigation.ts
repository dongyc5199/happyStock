// 导航配置

import { Home, TrendingUp, LayoutGrid, GraduationCap, Info, type LucideIcon } from 'lucide-react';

export interface NavigationItem {
  id: string;
  label: string;
  href: string;
  icon: LucideIcon;
  order: number;
}

export const navItems: NavigationItem[] = [
  { id: 'home', label: '首页', href: '/', icon: Home, order: 1 },
  { id: 'market', label: '市场行情', href: '/virtual-market', icon: TrendingUp, order: 2 },
  { id: 'sectors', label: '板块', href: '/sectors', icon: LayoutGrid, order: 3 },
  { id: 'learn', label: '学习中心', href: '/learn', icon: GraduationCap, order: 4 },
  { id: 'about', label: '关于', href: '/about', icon: Info, order: 5 },
];
