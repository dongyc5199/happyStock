/**
 * 邮件相关 API 服务
 * 处理密码重置、邮箱验证等功能
 */
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  new_password: string;
  confirm_password: string;
}

export interface VerifyEmailRequest {
  token: string;
}

export interface ChangeEmailRequest {
  new_email: string;
  password: string;
}

export interface ApiResponse<T = unknown> {
  success: boolean;
  message?: string;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

/**
 * 请求密码重置
 */
export async function forgotPassword(email: string): Promise<ApiResponse> {
  const response = await axios.post<ApiResponse>(
    `${API_BASE_URL}/api/auth/forgot-password`,
    { email }
  );
  return response.data;
}

/**
 * 验证重置令牌
 */
export async function verifyResetToken(token: string): Promise<{ valid: boolean; expires_at: string }> {
  const response = await axios.get<{ valid: boolean; expires_at: string }>(
    `${API_BASE_URL}/api/auth/reset-password/verify`,
    { params: { token } }
  );
  return response.data;
}

/**
 * 重置密码
 */
export async function resetPassword(data: ResetPasswordRequest): Promise<ApiResponse> {
  const response = await axios.post<ApiResponse>(
    `${API_BASE_URL}/api/auth/reset-password`,
    data
  );
  return response.data;
}

/**
 * 验证邮箱
 */
export async function verifyEmail(token: string): Promise<ApiResponse<{ email: string; verified_at: string }>> {
  const response = await axios.post<ApiResponse<{ email: string; verified_at: string }>>(
    `${API_BASE_URL}/api/auth/verify-email`,
    { token }
  );
  return response.data;
}

/**
 * 重新发送验证邮件
 */
export async function resendVerification(): Promise<ApiResponse> {
  const response = await axios.post<ApiResponse>(
    `${API_BASE_URL}/api/auth/resend-verification`,
    {},
    {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    }
  );
  return response.data;
}

/**
 * 重新发送验证邮件（带邮箱参数）
 */
export async function resendVerificationEmail(email: string): Promise<ApiResponse> {
  const response = await axios.post<ApiResponse>(
    `${API_BASE_URL}/api/auth/resend-verification`,
    { email }
  );
  return response.data;
}

/**
 * 获取邮箱验证状态
 */
export async function getEmailStatus(): Promise<ApiResponse<{
  email: string;
  email_verified: boolean;
  email_verified_at: string | null;
  can_resend: boolean;
}>> {
  const response = await axios.get<ApiResponse<{
    email: string;
    email_verified: boolean;
    email_verified_at: string | null;
    can_resend: boolean;
  }>>(
    `${API_BASE_URL}/api/auth/email-status`,
    {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    }
  );
  return response.data;
}

/**
 * 请求更改邮箱
 */
export async function changeEmail(data: ChangeEmailRequest): Promise<ApiResponse> {
  const response = await axios.post<ApiResponse>(
    `${API_BASE_URL}/api/auth/change-email`,
    data,
    {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    }
  );
  return response.data;
}

/**
 * 确认邮箱更改
 */
export async function confirmEmailChange(token: string): Promise<ApiResponse<{ new_email: string }>> {
  const response = await axios.post<ApiResponse<{ new_email: string }>>(
    `${API_BASE_URL}/api/auth/confirm-email-change`,
    { token }
  );
  return response.data;
}
