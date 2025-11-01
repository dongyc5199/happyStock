// 自定义认证 Hook

'use client';

import { useAuthStore } from '@/lib/stores/authStore';

export function useAuth() {
  const {
    user,
    token,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    fetchCurrentUser,
    clearError,
  } = useAuthStore();

  return {
    user,
    token,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    fetchCurrentUser,
    clearError,
  };
}
