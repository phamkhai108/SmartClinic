import { http } from './http'
import type { ApiErrorDetail, ChatMessage, SessionInfo } from '@/shared/types/api'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export interface ChatStreamDone {
  message_id: string
  session_id: string
  content?: string
}

export interface ChatStreamHandlers {
  onToken: (content: string) => void
  onReferences: (references: string[]) => void
  onDone: (info: ChatStreamDone) => void
  onError: (error: { code?: string; message: string }) => void
}

function parseErrorDetail(data: unknown): string {
  if (!data || typeof data !== 'object') return 'Đã xảy ra lỗi.'
  const detail = (data as { detail?: string | ApiErrorDetail }).detail
  if (!detail) return 'Đã xảy ra lỗi.'
  if (typeof detail === 'string') return detail
  if (detail.code === 'MISSING_CONFIG') {
    const keys = detail.keys?.length ? ` Thiếu: ${detail.keys.join(', ')}` : ''
    return `${detail.message || 'Cấu hình chưa đủ.'}${keys}`
  }
  return detail.message || 'Đã xảy ra lỗi.'
}

export async function sendChatStream(
  payload: {
    user_id: string
    session_id: string
    messages: ChatMessage[]
  },
  handlers: ChatStreamHandlers,
  signal?: AbortSignal,
): Promise<void> {
  const token = localStorage.getItem('accessToken')
  const res = await fetch(`${baseURL}/chat_all/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(payload),
    signal,
  })

  if (!res.ok) {
    let message = `HTTP ${res.status}`
    try {
      const data = await res.json()
      message = parseErrorDetail(data)
    } catch {
      /* keep status message */
    }
    if (res.status === 401) {
      localStorage.removeItem('accessToken')
      if (!window.location.pathname.startsWith('/login')) {
        const redirect = encodeURIComponent(window.location.pathname + window.location.search)
        window.location.href = `/login?redirect=${redirect}`
      }
    }
    handlers.onError({ code: String(res.status), message })
    return
  }

  if (!res.body) {
    handlers.onError({ message: 'Không nhận được luồng phản hồi.' })
    return
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const parts = buffer.split('\n\n')
    buffer = parts.pop() ?? ''

    for (const part of parts) {
      const dataLine = part
        .split('\n')
        .map((l) => l.trimEnd())
        .find((l) => l.startsWith('data:'))
      if (!dataLine) continue
      const raw = dataLine.replace(/^data:\s?/, '')
      if (!raw || raw === '[DONE]') continue

      let event: {
        type: string
        content?: string
        references?: string[]
        message_id?: string
        session_id?: string
        code?: string
        message?: string
      }
      try {
        event = JSON.parse(raw)
      } catch {
        continue
      }

      if (event.type === 'token' && event.content) {
        handlers.onToken(event.content)
      } else if (event.type === 'references' && event.references) {
        handlers.onReferences(event.references)
      } else if (event.type === 'done') {
        handlers.onDone({
          message_id: event.message_id || '',
          session_id: event.session_id || payload.session_id,
          content: event.content,
        })
      } else if (event.type === 'error') {
        handlers.onError({
          code: event.code,
          message: event.message || 'Agent error',
        })
        return
      }
    }
  }
}

export async function fetchSessions(userId: string) {
  const { data } = await http.get<SessionInfo[]>(`/chat_history/chat_sessions/${userId}`)
  return data
}

export async function fetchSessionMessages(sessionId: string) {
  const { data } = await http.get(`/chat_history/chat_history/${sessionId}`)
  return data
}
