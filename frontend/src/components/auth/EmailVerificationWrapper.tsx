'use client';

import { useAuth } from '@/hooks/useAuth';
import EmailVerificationBanner from './EmailVerificationBanner';

/**
 * 邮箱验证横幅包装器
 * 仅在用户已登录且邮箱未验证时显示
 */
export function EmailVerificationWrapper() {
  const { user, isAuthenticated } = useAuth();

  // 只有在已登录且邮箱未验证时才显示
  if (!isAuthenticated || !user || user.email_verified) {
    return null;
  }

  return <EmailVerificationBanner email={user.email} />;
}
