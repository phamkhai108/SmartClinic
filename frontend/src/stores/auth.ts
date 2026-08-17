import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import * as authApi from '@/api/auth'
import type { AuthUser, Role } from '@/shared/types/api'

function decodeJwtPayload(token: string): Partial<AuthUser> | null {
  try {
    const part = token.split('.')[1]
    if (!part) return null
    const json = atob(part.replace(/-/g, '+').replace(/_/g, '/'))
    const raw = JSON.parse(json) as Record<string, string>
    return {
      user_id: raw.user_id,
      user_name: raw.user_name,
      email: raw.email,
      role: raw.role as Role,
    }
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('accessToken'))
  const user = ref<AuthUser | null>(null)

  const isAuthenticated = computed(() => Boolean(token.value))
  const role = computed(() => user.value?.role)

  function hydrateFromToken() {
    if (!token.value) {
      user.value = null
      return
    }
    const payload = decodeJwtPayload(token.value)
    if (payload?.user_id && payload.role) {
      user.value = {
        user_id: payload.user_id,
        user_name: payload.user_name || '',
        email: payload.email || '',
        role: payload.role,
      }
    }
  }

  hydrateFromToken()

  async function login(email: string, password: string) {
    const res = await authApi.login(email, password)
    token.value = res.access_token
    localStorage.setItem('accessToken', res.access_token)
    hydrateFromToken()
    try {
      user.value = await authApi.fetchMe()
    } catch {
      /* keep JWT payload */
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('accessToken')
  }

  function hasRole(...roles: Role[]) {
    return !!user.value && roles.includes(user.value.role)
  }

  return { token, user, isAuthenticated, role, login, logout, hasRole, hydrateFromToken }
})
