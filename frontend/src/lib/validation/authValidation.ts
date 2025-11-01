// 表单验证规则

export const authValidation = {
  username: {
    minLength: 3,
    maxLength: 20,
    pattern: /^[a-zA-Z0-9_]{3,20}$/,
    message: '用户名必须为3-20个字符，只能包含字母、数字和下划线',
  },
  email: {
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    message: '请输入有效的邮箱地址',
  },
  password: {
    minLength: 8,
    maxLength: 128,
    pattern: /^(?=.*[A-Za-z])(?=.*\d).{8,128}$/,
    message: '密码必须至少8个字符，包含字母和数字',
  },
};

export function validateUsername(username: string): string | null {
  if (!username) return '用户名不能为空';
  if (!authValidation.username.pattern.test(username)) {
    return authValidation.username.message;
  }
  return null;
}

export function validateEmail(email: string): string | null {
  if (!email) return '邮箱不能为空';
  if (!authValidation.email.pattern.test(email)) {
    return authValidation.email.message;
  }
  return null;
}

export function validatePassword(password: string): string | null {
  if (!password) return '密码不能为空';
  if (password.length < authValidation.password.minLength) {
    return `密码至少需要${authValidation.password.minLength}个字符`;
  }
  if (!authValidation.password.pattern.test(password)) {
    return authValidation.password.message;
  }
  return null;
}
