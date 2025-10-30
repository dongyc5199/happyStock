'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export function MainNav() {
  const pathname = usePathname();

  const isActive = (path: string) => {
    if (path === '/virtual-market') {
      return pathname === path || pathname.startsWith('/virtual-market/stocks');
    }
    return pathname.startsWith(path);
  };

  const navItems = [
    { href: '/virtual-market', label: '市场首页' },
    { href: '/virtual-market/indices', label: '指数看板' },
    { href: '/virtual-market/sectors', label: '板块分析' },
  ];

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center group">
            <h1 className="text-2xl font-bold text-gray-900 group-hover:text-blue-600 transition-colors">
              happyStock
            </h1>
            <span className="ml-3 px-3 py-1 text-xs font-medium text-blue-600 bg-blue-100 rounded-full">
              虚拟市场
            </span>
          </Link>

          {/* Navigation */}
          <nav className="flex gap-8">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`relative font-medium transition-colors ${
                  isActive(item.href)
                    ? 'text-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {item.label}
                {isActive(item.href) && (
                  <span className="absolute -bottom-[17px] left-0 right-0 h-0.5 bg-blue-600"></span>
                )}
              </Link>
            ))}
          </nav>
        </div>
      </div>
    </header>
  );
}
