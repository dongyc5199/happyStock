/**
 * 错误消息映射
 * 将后端错误代码转换为用户友好的中文消息
 */

export const errorMessages: Record<string, string> = {
  // 通用错误
  'INTERNAL_ERROR': '服务器内部错误，请稍后重试',
  'INVALID_REQUEST': '请求参数无效',
  'UNAUTHORIZED': '未授权，请先登录',
  'FORBIDDEN': '没有权限执行此操作',
  'NOT_FOUND': '请求的资源不存在',

  // 认证错误
  'INVALID_CREDENTIALS': '用户名或密码错误',
  'USER_NOT_FOUND': '用户不存在',
  'USER_ALREADY_EXISTS': '用户名或邮箱已被注册',
  'USERNAME_TAKEN': '用户名已被占用',
  'EMAIL_TAKEN': '邮箱已被注册',
  'INVALID_TOKEN': '令牌无效或已过期',
  'TOKEN_EXPIRED': '令牌已过期，请重新发送',
  'TOKEN_USED': '此令牌已被使用',

  // 密码重置
  'INVALID_RESET_TOKEN': '密码重置链接无效',
  'RESET_TOKEN_EXPIRED': '密码重置链接已过期',
  'RESET_TOKEN_USED': '此重置链接已被使用',
  'PASSWORD_MISMATCH': '两次输入的密码不一致',
  'WEAK_PASSWORD': '密码强度不足，请使用更复杂的密码',

  // 邮箱验证
  'EMAIL_NOT_VERIFIED': '邮箱未验证',
  'ALREADY_VERIFIED': '该邮箱已经验证过了',
  'VERIFICATION_FAILED': '邮箱验证失败',
  'INVALID_VERIFICATION_TOKEN': '验证链接无效',
  'VERIFICATION_TOKEN_EXPIRED': '验证链接已过期，请重新发送验证邮件',
  'VERIFICATION_TOKEN_USED': '此验证链接已被使用',

  // 速率限制
  'RATE_LIMIT_EXCEEDED': '请求过于频繁，请稍后重试',
  'TOO_MANY_REQUESTS': '请求次数过多，请稍后重试',

  // 邮件发送
  'EMAIL_SEND_FAILED': '邮件发送失败，请稍后重试',
  'EMAIL_SERVICE_ERROR': '邮件服务暂时不可用',

  // 验证错误
  'VALIDATION_ERROR': '输入数据验证失败',
  'INVALID_EMAIL': '邮箱格式不正确',
  'INVALID_USERNAME': '用户名格式不正确',
  'INVALID_PASSWORD': '密码格式不正确',
};

/**
 * 获取友好的错误消息
 * @param errorCode - 后端返回的错误代码
 * @param defaultMessage - 默认消息（如果找不到映射）
 * @returns 用户友好的错误消息
 */
export function getErrorMessage(errorCode?: string, defaultMessage = '操作失败，请稍后重试'): string {
  if (!errorCode) {
    return defaultMessage;
  }
  
  return errorMessages[errorCode] || defaultMessage;
}

/**
 * 从错误对象中提取错误消息
 * @param error - 捕获的错误对象
 * @returns 用户友好的错误消息
 */
export function extractErrorMessage(error: unknown): string {
  // 尝试从 Axios 错误响应中提取
  const axiosError = error as {
    response?: {
      data?: {
        error?: {
          code?: string;
          message?: string;
        };
        message?: string;
        code?: string;
      };
    };
    message?: string;
  };

  // 优先使用后端返回的错误码
  const errorCode = axiosError.response?.data?.error?.code || axiosError.response?.data?.code;
  if (errorCode) {
    return getErrorMessage(errorCode);
  }

  // 其次使用后端返回的错误消息
  const backendMessage = axiosError.response?.data?.error?.message || axiosError.response?.data?.message;
  if (backendMessage) {
    return backendMessage;
  }

  // 最后使用错误对象的消息
  if (axiosError.message) {
    return axiosError.message;
  }

  return '操作失败，请稍后重试';
}

/**
 * 从速率限制错误中提取重试时间
 * @param error - 捕获的错误对象
 * @returns 重试等待时间（秒）
 */
export function extractRetryAfter(error: unknown): number {
  const axiosError = error as {
    response?: {
      data?: {
        error?: {
          details?: {
            retry_after?: number;
          };
        };
        retry_after?: number;
      };
    };
  };

  return (
    axiosError.response?.data?.error?.details?.retry_after ||
    axiosError.response?.data?.retry_after ||
    300 // 默认5分钟
  );
}
