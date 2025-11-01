// 移动端汉堡菜单组件

'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, X } from 'lucide-react';
import { navItems } from '@/lib/constants/navigation';

export function MobileMenu() {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();

  // 监听页面滚动，自动关闭菜单
  useEffect(() => {
    const handleScroll = () => {
      if (isOpen) {
        setIsOpen(false);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [isOpen]);

  // 监听屏幕旋转，自动关闭菜单
  useEffect(() => {
    const handleOrientationChange = () => {
      if (isOpen) {
        setIsOpen(false);
      }
    };

    window.addEventListener('orientationchange', handleOrientationChange);
    return () => window.removeEventListener('orientationchange', handleOrientationChange);
  }, [isOpen]);

  const handleMenuItemClick = () => {
    setIsOpen(false);
  };

  return (
    <div className="md:hidden">
      {/* 汉堡菜单按钮 */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 text-gray-700 hover:bg-gray-100 rounded"
        aria-label="打开菜单"
      >
        <Menu className="w-6 h-6" />
      </button>

      {/* 全屏菜单 */}
      {isOpen && (
        <>
          {/* 遮罩层 */}
          <div
            className="fixed inset-0 bg-black/50 z-40"
            onClick={() => setIsOpen(false)}
            aria-hidden="true"
          />

          {/* 菜单内容 */}
          <div className="fixed top-0 right-0 bottom-0 w-64 bg-white z-50 shadow-lg">
            {/* 关闭按钮 */}
            <div className="flex justify-end p-4">
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 text-gray-700 hover:bg-gray-100 rounded"
                aria-label="关闭菜单"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* 导航项 */}
            <nav className="flex flex-col p-4">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href;

                return (
                  <Link
                    key={item.id}
                    href={item.href}
                    onClick={handleMenuItemClick}
                    className={`
                      flex items-center gap-3 px-4 py-3 rounded transition-colors
                      min-h-[44px]
                      ${isActive 
                        ? 'bg-blue-100 text-blue-700 font-medium' 
                        : 'text-gray-700 hover:bg-gray-100'
                      }
                    `}
                  >
                    <Icon className="w-5 h-5" />
                    {item.label}
                  </Link>
                );
              })}
            </nav>
          </div>
        </>
      )}
    </div>
  );
}
