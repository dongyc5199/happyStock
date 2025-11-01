// Zustand 认证状态管理

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, LoginCredentials, RegisterData } from '@/types/auth';
import { authApi } from '@/lib/api/auth';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  fetchCurrentUser: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (credentials) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.login(credentials);
          if (response.success && response.data) {
            set({
              user: response.data.user,
              token: response.data.token,
              isAuthenticated: true,
              isLoading: false,
            });
          } else {
            throw new Error(response.error?.message || '登录失败');
          }
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : '网络错误',
            isLoading: false,
          });
        }
      },

      register: async (data) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.register(data);
          if (response.success && response.data) {
            set({
              user: response.data.user,
              token: response.data.token,
              isAuthenticated: true,
              isLoading: false,
            });
          } else {
            throw new Error(response.error?.message || '注册失败');
          }
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : '网络错误',
            isLoading: false,
          });
        }
      },

      logout: async () => {
        const token = get().token;
        if (token) {
          try {
            await authApi.logout(token);
          } catch (error) {
            console.error('Logout API error:', error);
          }
        }
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null,
        });
      },

      fetchCurrentUser: async () => {
        const token = get().token;
        if (!token) return;

        try {
          const response = await authApi.getCurrentUser(token);
          if (response.success && response.data) {
            set({ user: response.data.user, isAuthenticated: true });
          } else {
            // Token 无效，清除状态
            set({ user: null, token: null, isAuthenticated: false });
          }
        } catch {
          set({ user: null, token: null, isAuthenticated: false });
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
