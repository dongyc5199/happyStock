'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { verifyEmail } from '@/services/emailService';
import { useToast } from '@/contexts/ToastContext';
import { getErrorMessage } from '@/lib/utils/errorMessages';

export default function VerifyEmailPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get('token');
  const { showToast } = useToast();

  const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying');
  const [errorMessage, setErrorMessage] = useState<string>('');

  useEffect(() => {
    const verify = async () => {
      if (!token) {
        setStatus('error');
        setErrorMessage('缺少验证令牌');
        return;
      }

      try {
        await verifyEmail(token);
        setStatus('success');
        showToast('邮箱验证成功！', 'success');
        
        // 3秒后跳转到首页
        setTimeout(() => {
          router.push('/');
        }, 3000);
      } catch (err: unknown) {
        setStatus('error');
        
        const errorCode = (err as { response?: { data?: { error?: { code?: string } } } }).response?.data?.error?.code;
        const friendlyMessage = getErrorMessage(errorCode, '验证失败，请稍后重试');
        setErrorMessage(friendlyMessage);
      }
    };

    verify();
  }, [token, router, showToast]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-indigo-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {status === 'verifying' && (
            <div className="text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-600 mx-auto mb-4"></div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">验证中...</h2>
              <p className="text-gray-600">请稍候，正在验证您的邮箱</p>
            </div>
          )}

          {status === 'success' && (
            <div className="text-center">
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
              <h2 className="text-2xl font-bold text-gray-900 mb-2">验证成功！</h2>
              <p className="text-gray-600 mb-4">
                您的邮箱已成功验证。
              </p>
              <p className="text-sm text-gray-500">
                正在跳转到首页...
              </p>
            </div>
          )}

          {status === 'error' && (
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center">
                <svg 
                  className="w-8 h-8 text-red-600" 
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M6 18L18 6M6 6l12 12" 
                  />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">验证失败</h2>
              <p className="text-gray-600 mb-6">{errorMessage}</p>
              
              <div className="space-y-3">
                <button
                  onClick={() => router.push('/')}
                  className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-3 rounded-lg font-medium hover:from-purple-700 hover:to-indigo-700 transition-all"
                >
                  返回首页
                </button>
                
                {errorMessage.includes('过期') && (
                  <button
                    onClick={() => router.push('/auth/resend-verification')}
                    className="w-full border-2 border-purple-600 text-purple-600 py-3 rounded-lg font-medium hover:bg-purple-50 transition-all"
                  >
                    重新发送验证邮件
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
