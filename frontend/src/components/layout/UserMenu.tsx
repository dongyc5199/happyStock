// 用户下拉菜单组件

'use client';

import { useState, useRef, useEffect } from 'react';
import { User, Settings, LogOut, ChevronDown } from 'lucide-react';
import { UserAvatar } from './UserAvatar';
import { useAuth } from '@/hooks/useAuth';

export function UserMenu() {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const { user, logout } = useAuth();

  // 点击外部关闭菜单
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  const handleLogout = async () => {
    await logout();
    setIsOpen(false);
  };

  if (!user) return null;

  // 截断用户名 (最多12字符)
  const displayName = user.username.length > 12 
    ? user.username.substring(0, 12) + '...' 
    : user.username;

  return (
    <div className="relative" ref={menuRef}>
      {/* 用户信息按钮 */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded hover:bg-gray-100 transition-colors"
        title={user.username} // 悬停显示完整用户名
      >
        <UserAvatar 
          avatarUrl={user.avatar_url} 
          username={user.username} 
          size="sm" 
        />
        <span className="text-sm font-medium text-gray-700">
          {displayName}
        </span>
        <ChevronDown 
          className={`w-4 h-4 text-gray-500 transition-transform ${
            isOpen ? 'rotate-180' : ''
          }`} 
        />
      </button>

      {/* 下拉菜单 */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
          <button
            onClick={() => {
              // TODO: 跳转到个人中心
              setIsOpen(false);
            }}
            className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
          >
            <User className="w-4 h-4" />
            个人中心
          </button>

          <button
            onClick={() => {
              // TODO: 跳转到账户设置
              setIsOpen(false);
            }}
            className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
          >
            <Settings className="w-4 h-4" />
            账户设置
          </button>

          <div className="border-t border-gray-200 my-1" />

          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
          >
            <LogOut className="w-4 h-4" />
            退出登录
          </button>
        </div>
      )}
    </div>
  );
}
