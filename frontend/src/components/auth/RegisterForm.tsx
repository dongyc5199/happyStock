// 注册表单组件

'use client';

import { useState, FormEvent } from 'react';
import { useAuthStore } from '@/lib/stores/authStore';
import { validateUsername, validateEmail, validatePassword } from '@/lib/validation/authValidation';

interface RegisterFormProps {
  onSwitchToLogin: () => void;
  onSuccess?: () => void;
}

export function RegisterForm({ onSwitchToLogin, onSuccess }: RegisterFormProps) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fieldErrors, setFieldErrors] = useState<{
    username?: string;
    email?: string;
    password?: string;
    confirmPassword?: string;
  }>({});

  const { register, isLoading, error, clearError } = useAuthStore();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearError();
    setFieldErrors({});

    // 表单验证
    const errors: typeof fieldErrors = {};
    
    const usernameError = validateUsername(username);
    if (usernameError) errors.username = usernameError;

    const emailError = validateEmail(email);
    if (emailError) errors.email = emailError;

    const passwordError = validatePassword(password);
    if (passwordError) errors.password = passwordError;

    if (password !== confirmPassword) {
      errors.confirmPassword = '两次输入的密码不一致';
    }

    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors);
      return;
    }

    // 调用注册 API
    await register({ username, email, password });
    
    // 检查是否注册成功
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

      {/* 用户名 */}
      <div>
        <label htmlFor="register-username" className="block text-sm font-medium text-gray-700 mb-1">
          用户名
        </label>
        <input
          id="register-username"
          type="text"
          value={username}
          onChange={(e) => {
            setUsername(e.target.value);
            if (fieldErrors.username) setFieldErrors({ ...fieldErrors, username: undefined });
          }}
          className={`w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none ${
            fieldErrors.username ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="3-20个字符，字母数字下划线"
          disabled={isLoading}
        />
        {fieldErrors.username && (
          <p className="mt-1 text-sm text-red-600">{fieldErrors.username}</p>
        )}
      </div>

      {/* 邮箱 */}
      <div>
        <label htmlFor="register-email" className="block text-sm font-medium text-gray-700 mb-1">
          邮箱
        </label>
        <input
          id="register-email"
          type="email"
          value={email}
          onChange={(e) => {
            setEmail(e.target.value);
            if (fieldErrors.email) setFieldErrors({ ...fieldErrors, email: undefined });
          }}
          className={`w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none ${
            fieldErrors.email ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="your@example.com"
          disabled={isLoading}
        />
        {fieldErrors.email && (
          <p className="mt-1 text-sm text-red-600">{fieldErrors.email}</p>
        )}
      </div>

      {/* 密码 */}
      <div>
        <label htmlFor="register-password" className="block text-sm font-medium text-gray-700 mb-1">
          密码
        </label>
        <input
          id="register-password"
          type="password"
          value={password}
          onChange={(e) => {
            setPassword(e.target.value);
            if (fieldErrors.password) setFieldErrors({ ...fieldErrors, password: undefined });
          }}
          className={`w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none ${
            fieldErrors.password ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="至少8个字符，包含字母和数字"
          disabled={isLoading}
        />
        {fieldErrors.password && (
          <p className="mt-1 text-sm text-red-600">{fieldErrors.password}</p>
        )}
      </div>

      {/* 确认密码 */}
      <div>
        <label htmlFor="register-confirm-password" className="block text-sm font-medium text-gray-700 mb-1">
          确认密码
        </label>
        <input
          id="register-confirm-password"
          type="password"
          value={confirmPassword}
          onChange={(e) => {
            setConfirmPassword(e.target.value);
            if (fieldErrors.confirmPassword) setFieldErrors({ ...fieldErrors, confirmPassword: undefined });
          }}
          className={`w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none ${
            fieldErrors.confirmPassword ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="再次输入密码"
          disabled={isLoading}
        />
        {fieldErrors.confirmPassword && (
          <p className="mt-1 text-sm text-red-600">{fieldErrors.confirmPassword}</p>
        )}
      </div>

      {/* 提交按钮 */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
      >
        {isLoading ? '注册中...' : '注册'}
      </button>

      {/* 切换到登录 */}
      <p className="text-center text-sm text-gray-600">
        已有账号？
        <button
          type="button"
          onClick={onSwitchToLogin}
          className="text-blue-600 hover:underline ml-1 font-medium"
        >
          立即登录
        </button>
      </p>
    </form>
  );
}
