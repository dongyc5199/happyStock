// 注册表单组件

'use client';

import { useState, FormEvent } from 'react';
import { useAuthStore } from '@/lib/stores/authStore';
import { validateUsername, validateEmail, validatePassword } from '@/lib/validation/authValidation';
import { useToast } from '@/contexts/ToastContext';

interface RegisterFormProps {
  onSwitchToLogin: () => void;
  onSuccess?: () => void;
}

export function RegisterForm({ onSwitchToLogin, onSuccess }: RegisterFormProps) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isSuccess, setIsSuccess] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<{
    username?: string;
    email?: string;
    password?: string;
    confirmPassword?: string;
  }>({});

  const { register, isLoading, error, clearError } = useAuthStore();
  const { showToast } = useToast();

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
      setIsSuccess(true);
      showToast('注册成功，欢迎加入 happyStock！', 'success');
      // 3秒后关闭模态框
      setTimeout(() => {
        onSuccess?.();
      }, 3000);
    }
  };

  // 如果注册成功，显示成功消息
  if (isSuccess) {
    return (
      <div className="text-center py-8">
        <div className="w-16 h-16 mx-auto mb-4 bg-green-100 rounded-full flex items-center justify-center">
          <svg 
            className="w-8 h-8 text-green-600" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M5 13l4 4L19 7" 
            />
          </svg>
        </div>
        <h3 className="text-xl font-bold text-gray-900 mb-2">注册成功！</h3>
        <p className="text-gray-600 mb-4">
          欢迎加入 happyStock！
        </p>
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 text-left">
          <div className="flex items-start">
            <svg 
              className="h-5 w-5 text-yellow-400 mt-0.5 mr-2 flex-shrink-0" 
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path 
                fillRule="evenodd" 
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" 
                clipRule="evenodd" 
              />
            </svg>
            <div className="flex-1">
              <p className="text-sm font-medium text-yellow-800">
                请验证您的邮箱
              </p>
              <p className="text-sm text-yellow-700 mt-1">
                我们已向 <strong>{email}</strong> 发送了验证邮件，请查收并点击链接完成验证。
              </p>
            </div>
          </div>
        </div>
        <p className="text-sm text-gray-500 mt-4">
          正在跳转...
        </p>
      </div>
    );
  }

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
