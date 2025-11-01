// 登录表单组件

'use client';

import { useState, FormEvent } from 'react';
import { useAuthStore } from '@/lib/stores/authStore';

interface LoginFormProps {
  onSwitchToRegister: () => void;
  onSuccess?: () => void;
}

export function LoginForm({ onSwitchToRegister, onSuccess }: LoginFormProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [fieldErrors, setFieldErrors] = useState<{ username?: string; password?: string }>({});

  const { login, isLoading, error, clearError } = useAuthStore();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearError();
    setFieldErrors({});

    // 基础验证
    const errors: { username?: string; password?: string } = {};
    if (!username) errors.username = '用户名/邮箱不能为空';
    if (!password) errors.password = '密码不能为空';

    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors);
      return;
    }

    // 调用登录 API
    await login({ username, password });
    
    // 检查是否登录成功
    if (useAuthStore.getState().isAuthenticated) {
      onSuccess?.();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* 全局错误信息 */}
      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded text-sm">
          {error}
        </div>
      )}

      {/* 用户名/邮箱 */}
      <div>
        <label htmlFor="login-username" className="block text-sm font-medium text-gray-700 mb-1">
          用户名/邮箱
        </label>
        <input
          id="login-username"
          type="text"
          value={username}
          onChange={(e) => {
            setUsername(e.target.value);
            if (fieldErrors.username) setFieldErrors({ ...fieldErrors, username: undefined });
          }}
          className={`w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none ${
            fieldErrors.username ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="请输入用户名或邮箱"
          disabled={isLoading}
        />
        {fieldErrors.username && (
          <p className="mt-1 text-sm text-red-600">{fieldErrors.username}</p>
        )}
      </div>

      {/* 密码 */}
      <div>
        <label htmlFor="login-password" className="block text-sm font-medium text-gray-700 mb-1">
          密码
        </label>
        <input
          id="login-password"
          type="password"
          value={password}
          onChange={(e) => {
            setPassword(e.target.value);
            if (fieldErrors.password) setFieldErrors({ ...fieldErrors, password: undefined });
          }}
          className={`w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none ${
            fieldErrors.password ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="请输入密码"
          disabled={isLoading}
        />
        {fieldErrors.password && (
          <p className="mt-1 text-sm text-red-600">{fieldErrors.password}</p>
        )}
      </div>

      {/* 提交按钮 */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
      >
        {isLoading ? '登录中...' : '登录'}
      </button>

      {/* 切换到注册 */}
      <p className="text-center text-sm text-gray-600">
        还没有账号？
        <button
          type="button"
          onClick={onSwitchToRegister}
          className="text-blue-600 hover:underline ml-1 font-medium"
        >
          立即注册
        </button>
      </p>
    </form>
  );
}
