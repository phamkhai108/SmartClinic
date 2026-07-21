import { http } from './http'
import type { FileInfo, Role, UserDTO } from '@/shared/types/api'

export async function listUsers() {
  const { data } = await http.get<UserDTO[]>('/users/')
  return data
}

export async function updateUserRole(userId: string, role: Exclude<Role, 'admin'>) {
  const { data } = await http.put<UserDTO>(`/users/${userId}/role`, { role })
  return data
}

export async function listFiles(userId = 'all') {
  const { data } = await http.get<FileInfo[]>('/files/get_info_files', {
    params: { user_id: userId },
  })
  return data
}

export async function uploadFile(userId: string, file: File) {
  const form = new FormData()
  form.append('file', file)
  const { data } = await http.post<FileInfo>('/files/upload_flow', form, {
    params: { user_id: userId },
    timeout: 600_000,
  })
  return data
}

export async function deleteFile(fileName: string) {
  const { data } = await http.delete(`/files/delete_file/${encodeURIComponent(fileName)}`)
  return data
}
