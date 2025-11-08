'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { forgotPassword } from '@/services/emailService';

// 表单验证 schema
const forgotPasswordSchema = z.object({
  email: z.string().email('请输入有效的邮箱地址'),
});

type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>;

export default function ForgotPasswordForm() {
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
  });

  const onSubmit = async (data: ForgotPasswordFormData) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await forgotPassword(data.email);
      
      if (response.success) {
        setSuccess(true);
      } else {
        setError(response.error?.message || '请求失败，请稍后重试');
      }
    } catch (err: unknown) {
      const axiosError = err as { response?: { status?: number; data?: { error?: { details?: { retry_after?: number } } } } };
      if (axiosError.response?.status === 429) {
        const retryAfter = axiosError.response?.data?.error?.details?.retry_after;
        setError(`请求过于频繁，请 ${retryAfter || 300} 秒后重试`);
      } else {
        setError('网络错误，请稍后重试');
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <div className="text-center space-y-4">
        <div className="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center">
          <svg className="w-8 h-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h3 className="text-xl font-semibold text-gray-900">邮件已发送</h3>
        <p className="text-gray-600">
          如果该邮箱已注册，您将收到密码重置邮件。
          <br />
          请检查您的邮箱并点击邮件中的链接重置密码。
        </p>
        <p className="text-sm text-gray-500 mt-4">
          没有收到邮件？请检查垃圾邮件文件夹。
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
          注册邮箱
        </label>
        <input
          {...register('email')}
          type="email"
          id="email"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          placeholder="your@email.com"
          disabled={isLoading}
        />
        {errors.email && (
          <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
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
        {isLoading ? '发送中...' : '发送重置链接'}
      </button>

      <p className="text-sm text-center text-gray-600">
        想起密码了？{' '}
        <a href="/auth/login" className="text-purple-600 hover:text-purple-700 font-medium">
          返回登录
        </a>
      </p>
    </form>
  );
}
