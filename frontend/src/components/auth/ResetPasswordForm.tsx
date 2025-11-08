'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useRouter, useSearchParams } from 'next/navigation';
import { verifyResetToken, resetPassword } from '@/services/emailService';

// 表单验证 schema
const resetPasswordSchema = z.object({
  new_password: z
    .string()
    .min(8, '密码必须至少8个字符')
    .regex(/[a-zA-Z]/, '密码必须包含字母')
    .regex(/[0-9]/, '密码必须包含数字'),
  confirm_password: z.string(),
}).refine((data) => data.new_password === data.confirm_password, {
  message: '两次输入的密码不一致',
  path: ['confirm_password'],
});

type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>;

export default function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get('token');

  const [isLoading, setIsLoading] = useState(false);
  const [isVerifying, setIsVerifying] = useState(true);
  const [tokenError, setTokenError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
  });

  useEffect(() => {
    const verifyToken = async () => {
      if (!token) {
        setTokenError('缺少重置令牌');
        setIsVerifying(false);
        return;
      }

      try {
        const response = await verifyResetToken(token);
        if (!response.valid) {
          setTokenError('令牌无效');
        }
      } catch (err: any) {
        const errorCode = err.response?.data?.code || err.response?.data?.detail?.code;
        if (errorCode === 'TOKEN_EXPIRED') {
          setTokenError('重置链接已过期，请重新申请');
        } else if (errorCode === 'TOKEN_USED') {
          setTokenError('重置链接已使用，请重新申请');
        } else {
          setTokenError('令牌验证失败');
        }
      } finally {
        setIsVerifying(false);
      }
    };

    verifyToken();
  }, [token]);

  const onSubmit = async (data: ResetPasswordFormData) => {
    if (!token) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await resetPassword({
        token,
        new_password: data.new_password,
        confirm_password: data.confirm_password,
      });

      if (response.success) {
        setSuccess(true);
        // 3秒后跳转到首页
        setTimeout(() => {
          router.push('/');
        }, 3000);
      } else {
        setError(response.error?.message || '重置失败，请稍后重试');
      }
    } catch (err: any) {
      const errorCode = err.response?.data?.error?.code;
      if (errorCode === 'TOKEN_EXPIRED') {
        setError('重置链接已过期，请重新申请');
      } else if (errorCode === 'TOKEN_USED') {
        setError('重置链接已使用');
      } else {
        setError('网络错误，请稍后重试');
      }
    } finally {
      setIsLoading(false);
    }
  };

  // 验证令牌中
  if (isVerifying) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">验证重置链接...</p>
      </div>
    );
  }

  // 令牌无效
  if (tokenError) {
    return (
      <div className="text-center space-y-4">
        <div className="w-16 h-16 mx-auto bg-red-100 rounded-full flex items-center justify-center">
          <svg className="w-8 h-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>
        <h3 className="text-xl font-semibold text-gray-900">链接无效</h3>
        <p className="text-gray-600">{tokenError}</p>
        <a
          href="/auth/forgot-password"
          className="inline-block mt-4 text-purple-600 hover:text-purple-700 font-medium"
        >
          重新申请密码重置
        </a>
      </div>
    );
  }

  // 重置成功
  if (success) {
    return (
      <div className="text-center space-y-4">
        <div className="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center">
          <svg className="w-8 h-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h3 className="text-xl font-semibold text-gray-900">密码重置成功！</h3>
        <p className="text-gray-600">
          您的密码已成功重置。
          <br />
          正在跳转到首页，请使用新密码登录...
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div>
        <label htmlFor="new_password" className="block text-sm font-medium text-gray-700 mb-2">
          新密码
        </label>
        <div className="relative">
          <input
            {...register('new_password')}
            type={showPassword ? 'text' : 'password'}
            id="new_password"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent pr-10"
            placeholder="至少8个字符，包含字母和数字"
            disabled={isLoading}
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
          >
            {showPassword ? '隐藏' : '显示'}
          </button>
        </div>
        {errors.new_password && (
          <p className="mt-1 text-sm text-red-600">{errors.new_password.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="confirm_password" className="block text-sm font-medium text-gray-700 mb-2">
          确认新密码
        </label>
        <input
          {...register('confirm_password')}
          type={showPassword ? 'text' : 'password'}
          id="confirm_password"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          placeholder="再次输入新密码"
          disabled={isLoading}
        />
        {errors.confirm_password && (
          <p className="mt-1 text-sm text-red-600">{errors.confirm_password.message}</p>
        )}
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-3 rounded-lg font-medium hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
      >
        {isLoading ? '重置中...' : '重置密码'}
      </button>
    </form>
  );
}
