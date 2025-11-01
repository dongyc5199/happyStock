// 注册模态框组件

'use client';

import * as Dialog from '@radix-ui/react-dialog';
import { X } from 'lucide-react';
import { RegisterForm } from './RegisterForm';
import { useAuthStore } from '@/lib/stores/authStore';

interface RegisterModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSwitchToLogin: () => void;
}

export function RegisterModal({ isOpen, onClose, onSwitchToLogin }: RegisterModalProps) {
  const { clearError } = useAuthStore();

  const handleClose = () => {
    clearError();
    onClose();
  };

  return (
    <Dialog.Root open={isOpen} onOpenChange={handleClose}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-40" />
        <Dialog.Content className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-lg p-6 w-full max-w-md z-50 max-h-[90vh] overflow-y-auto">
          <div className="flex justify-between items-center mb-4">
            <Dialog.Title className="text-2xl font-bold text-gray-900">
              注册
            </Dialog.Title>
            <Dialog.Close asChild>
              <button 
                className="text-gray-500 hover:text-gray-700 transition-colors p-1 rounded hover:bg-gray-100"
                aria-label="关闭"
              >
                <X className="w-5 h-5" />
              </button>
            </Dialog.Close>
          </div>

          <RegisterForm 
            onSwitchToLogin={() => {
              handleClose();
              onSwitchToLogin();
            }}
            onSuccess={handleClose}
          />
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
