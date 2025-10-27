/**
 * API 客户端配置
 */
import axios, { AxiosInstance, AxiosError } from 'axios';
import type { ApiResponse } from '@/types/trading';

// API 基础 URL
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// 创建 axios 实例
const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 可以在这里添加 token 等认证信息
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    // 返回响应数据
    return response.data;
  },
  (error: AxiosError<ApiResponse>) => {
    // 统一错误处理
    if (error.response) {
      const { data } = error.response;

      // 如果后端返回了标准错误格式
      if (data && data.error) {
        return Promise.reject({
          message: data.error.message || '请求失败',
          code: data.error.code || 'UNKNOWN_ERROR',
        });
      }

      // HTTP 错误
      switch (error.response.status) {
        case 400:
          return Promise.reject({ message: '请求参数错误', code: 'BAD_REQUEST' });
        case 401:
          return Promise.reject({ message: '未授权，请登录', code: 'UNAUTHORIZED' });
        case 403:
          return Promise.reject({ message: '拒绝访问', code: 'FORBIDDEN' });
        case 404:
          return Promise.reject({ message: '请求的资源不存在', code: 'NOT_FOUND' });
        case 500:
          return Promise.reject({ message: '服务器内部错误', code: 'SERVER_ERROR' });
        default:
          return Promise.reject({ message: '请求失败', code: 'UNKNOWN_ERROR' });
      }
    } else if (error.request) {
      // 请求已发出，但没有收到响应
      return Promise.reject({ message: '网络错误，请检查网络连接', code: 'NETWORK_ERROR' });
    } else {
      // 其他错误
      return Promise.reject({ message: error.message || '未知错误', code: 'UNKNOWN_ERROR' });
    }
  }
);

export default apiClient;
