// 登录/注册按钮组件

'use client';

import { useState } from 'react';
import { LogIn, UserPlus } from 'lucide-react';
import { LoginModal } from '../auth/LoginModal';
import { RegisterModal } from '../auth/RegisterModal';

export function AuthButtons() {
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [isRegisterOpen, setIsRegisterOpen] = useState(false);

  return (
    <>
      <div className="flex gap-2">
        {/* 登录按钮 */}
        <button
          onClick={() => setIsLoginOpen(true)}
          className="flex items-center gap-2 px-4 py-2 text-blue-600 hover:bg-blue-50 rounded transition-colors font-medium"
        >
          <LogIn className="w-4 h-4" />
          登录
        </button>

        {/* 注册按钮 */}
        <button
          onClick={() => setIsRegisterOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded transition-colors font-medium"
        >
          <UserPlus className="w-4 h-4" />
          注册
        </button>
      </div>

      {/* 登录模态框 */}
      <LoginModal
        isOpen={isLoginOpen}
        onClose={() => setIsLoginOpen(false)}
        onSwitchToRegister={() => {
          setIsLoginOpen(false);
          setIsRegisterOpen(true);
        }}
      />

      {/* 注册模态框 */}
      <RegisterModal
        isOpen={isRegisterOpen}
        onClose={() => setIsRegisterOpen(false)}
        onSwitchToLogin={() => {
          setIsRegisterOpen(false);
          setIsLoginOpen(true);
        }}
      />
    </>
  );
}
