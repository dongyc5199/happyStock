import ForgotPasswordForm from '@/components/auth/ForgotPasswordForm';

export default function ForgotPasswordPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl max-w-md w-full p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">忘记密码</h1>
          <p className="text-gray-600">输入您的注册邮箱，我们将发送密码重置链接</p>
        </div>

        <ForgotPasswordForm />
      </div>
    </div>
  );
}
