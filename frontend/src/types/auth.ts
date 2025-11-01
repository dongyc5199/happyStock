// 认证相关类型定义

export interface User {
  id: string;
  username: string;
  email: string;
  avatar_url: string | null;
  created_at: string;
}

export interface AuthSession {
  user: User;
  token: string;
  expires_at: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
}

// API 响应类型
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: { field: string };
  };
}
