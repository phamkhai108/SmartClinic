import type { ApiErrorDetail } from '@/shared/types/api'
import axios, { type AxiosError } from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const http = axios.create({
  baseURL,
  timeout: 60000,
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

function isAuthCredentialRequest(url?: string): boolean {
  if (!url) return false
  return url.includes('/auth/login') || url.includes('/auth/register')
}

http.interceptors.response.use(
  (res) => res,
  (error: AxiosError) => {
    const status = error.response?.status
    const url = error.config?.url
    // Login/register 401 must not wipe an existing session or look like "session expired".
    if (status === 401 && !isAuthCredentialRequest(url)) {
      localStorage.removeItem('accessToken')
      if (!window.location.pathname.startsWith('/login')) {
        const redirect = encodeURIComponent(window.location.pathname + window.location.search)
        window.location.href = `/login?redirect=${redirect}`
      }
    }
    return Promise.reject(error)
  },
)

type FastApiValidationItem = {
  loc?: Array<string | number>
  msg?: string
  message?: string
  type?: string
}

function formatValidationDetail(items: FastApiValidationItem[]): string {
  return items
    .map((item) => {
      const field = item.loc?.filter((p) => p !== 'body' && p !== 'query').join('.') || ''
      const msg = item.msg || item.message || 'Invalid value'
      return field ? `${field}: ${msg}` : msg
    })
    .join('; ')
}

export function extractApiError(error: unknown): string {
  const ax = error as AxiosError<{ detail?: string | ApiErrorDetail | FastApiValidationItem[] }>
  const status = ax.response?.status
  const detail = ax.response?.data?.detail

  if (!detail) {
    if (status === 401) return 'Email hoặc mật khẩu không đúng.'
    if (status === 400) return 'Yêu cầu không hợp lệ.'
    if (status === 422) return 'Dữ liệu gửi lên không hợp lệ.'
    return ax.message || 'Đã xảy ra lỗi.'
  }

  if (typeof detail === 'string') {
    if (detail === 'Invalid credentials.') return 'Email hoặc mật khẩu không đúng.'
    if (detail === 'Email already registered.') return 'Email đã được đăng ký.'
    return detail
  }

  if (Array.isArray(detail)) {
    const formatted = formatValidationDetail(detail)
    return formatted || 'Dữ liệu gửi lên không hợp lệ.'
  }

  if (detail.code === 'MISSING_CONFIG') {
    const keys = detail.keys?.length ? ` Thiếu: ${detail.keys.join(', ')}` : ''
    return `${detail.message || 'Cấu hình chưa đủ.'}${keys}`
  }

  return detail.message || 'Đã xảy ra lỗi.'
}

export function getStatus(error: unknown): number | undefined {
  return (error as AxiosError).response?.status
}
