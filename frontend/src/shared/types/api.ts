export type Role = 'user' | 'doctor' | 'admin'

export interface AuthUser {
  user_id: string
  user_name: string
  email: string
  role: Role
}

export interface ApiErrorDetail {
  code?: string
  message?: string
  keys?: string[]
}

export interface FastApiValidationError {
  loc?: Array<string | number>
  msg?: string
  type?: string
}


export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ChoiceMessage {
  messages: ChatMessage[]
  message_id: string
  time_at: string
  finish_reason: string
}

export interface ChatResponse {
  user_id: string
  choice: ChoiceMessage
  history: ChoiceMessage[]
  reference: string[]
  time_at: string
}

export interface SessionInfo {
  session_id: string
  conversation_name: string
  latest_timestamp: string
}

export interface FileInfo {
  id: string
  user_id: string
  status: string
  file_name: string
  created_at: string
}

export interface UserDTO {
  id: string
  user_name: string
  email: string
  role: Role
}
