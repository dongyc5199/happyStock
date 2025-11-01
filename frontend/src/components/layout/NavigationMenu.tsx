// 桌面端导航菜单组件

'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { navItems } from '@/lib/constants/navigation';

export function NavigationMenu() {
  const pathname = usePathname();

  return (
    <nav className="hidden md:flex gap-1">
      {navItems.map((item) => {
        const Icon = item.icon;
        const isActive = pathname === item.href;

        return (
          <Link
            key={item.id}
            href={item.href}
            className={`
              flex items-center gap-2 px-3 py-2 rounded transition-colors
              ${isActive 
                ? 'bg-blue-100 text-blue-700 font-medium' 
                : 'text-gray-700 hover:bg-gray-100'
              }
            `}
          >
            <Icon className="w-4 h-4" />
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
