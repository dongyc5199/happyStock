// 认证 API 客户端

import type { 
  LoginCredentials, 
  RegisterData, 
  AuthSession, 
  User,
  ApiResponse 
} from '@/types/auth';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export const authApi = {
  async login(credentials: LoginCredentials): Promise<ApiResponse<AuthSession>> {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });
    return response.json();
  },

  async register(data: RegisterData): Promise<ApiResponse<AuthSession>> {
    const response = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  },

  async getCurrentUser(token: string): Promise<ApiResponse<{ user: User }>> {
    const response = await fetch(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.json();
  },

  async logout(token: string): Promise<ApiResponse<{ message: string }>> {
    const response = await fetch(`${API_BASE}/auth/logout`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.json();
  },
};
