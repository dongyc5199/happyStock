// 主 Header 组件

'use client';

import { NavigationMenu } from './NavigationMenu';
import { MobileMenu } from './MobileMenu';
import { AuthButtons } from './AuthButtons';
import { UserMenu } from './UserMenu';
import { useAuth } from '@/hooks/useAuth';

export function Header() {
  const { isAuthenticated } = useAuth();

  return (
    <header className="sticky top-0 bg-white border-b z-30">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        {/* Logo */}
        <div className="text-xl font-bold bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent">
          happyStock
        </div>

        {/* 桌面导航 */}
        <div className="hidden md:flex items-center gap-6">
          <NavigationMenu />
          {!isAuthenticated ? <AuthButtons /> : <UserMenu />}
        </div>

        {/* 移动端菜单 */}
        <MobileMenu />
      </div>
    </header>
  );
}
