import axios, { type AxiosError } from 'axios'
import type { ApiErrorDetail } from '@/shared/types/api'

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

http.interceptors.response.use(
  (res) => res,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('accessToken')
      if (!window.location.pathname.startsWith('/login')) {
        const redirect = encodeURIComponent(window.location.pathname + window.location.search)
        window.location.href = `/login?redirect=${redirect}`
      }
    }
    return Promise.reject(error)
  },
)

export function extractApiError(error: unknown): string {
  const ax = error as AxiosError<{ detail?: string | ApiErrorDetail }>
  const detail = ax.response?.data?.detail
  if (!detail) return ax.message || 'Đã xảy ra lỗi.'
  if (typeof detail === 'string') return detail
  if (detail.code === 'MISSING_CONFIG') {
    const keys = detail.keys?.length ? ` Thiếu: ${detail.keys.join(', ')}` : ''
    return `${detail.message || 'Cấu hình chưa đủ.'}${keys}`
  }
  return detail.message || 'Đã xảy ra lỗi.'
}

export function getStatus(error: unknown): number | undefined {
  return (error as AxiosError).response?.status
}
