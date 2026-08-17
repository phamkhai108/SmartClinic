import { http } from './http'
import type { AuthUser, LoginResponse } from '@/shared/types/api'

export async function login(email: string, password: string) {
  const { data } = await http.post<LoginResponse>('/auth/login', { email, password })
  return data
}

export async function register(payload: {
  user_name: string
  email: string
  password: string
  code_verify?: string
}) {
  const { data } = await http.post<{ message: string }>('/auth/register', payload)
  return data
}

export async function fetchMe() {
  const { data } = await http.get<AuthUser>('/auth/me')
  return data
}
