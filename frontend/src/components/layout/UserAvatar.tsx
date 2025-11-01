// 用户头像组件

'use client';

import Image from 'next/image';

interface UserAvatarProps {
  avatarUrl: string | null;
  username: string;
  size?: 'sm' | 'md' | 'lg';
}

const sizeClasses = {
  sm: 'w-8 h-8 text-sm',
  md: 'w-10 h-10 text-base',
  lg: 'w-12 h-12 text-lg',
};

export function UserAvatar({ avatarUrl, username, size = 'md' }: UserAvatarProps) {
  // 获取用户名首字母
  const initial = username.charAt(0).toUpperCase();

  if (avatarUrl) {
    return (
      <Image
        src={avatarUrl}
        alt={username}
        width={48}
        height={48}
        className={`${sizeClasses[size]} rounded-full object-cover`}
      />
    );
  }

  // 默认头像：显示首字母
  return (
    <div
      className={`${sizeClasses[size]} rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center text-white font-semibold`}
    >
      {initial}
    </div>
  );
}
