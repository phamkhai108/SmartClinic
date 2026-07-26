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

export async function getFile(fileId: string) {
  const { data } = await http.get<FileInfo>(`/files/${encodeURIComponent(fileId)}`)
  return data
}

export async function uploadFile(userId: string, file: File) {
  const form = new FormData()
  form.append('file', file)
  const { data } = await http.post<FileInfo>('/files/upload_flow', form, {
    params: { user_id: userId },
    timeout: 120_000,
  })
  return data
}

/** Poll until status leaves pending (or timeout). */
export async function waitForFileTerminalStatus(
  fileId: string,
  options: { intervalMs?: number; timeoutMs?: number } = {},
): Promise<FileInfo> {
  const intervalMs = options.intervalMs ?? 2000
  const timeoutMs = options.timeoutMs ?? 600_000
  const started = Date.now()

  while (Date.now() - started < timeoutMs) {
    const info = await getFile(fileId)
    if (info.status !== 'pending') {
      return info
    }
    await new Promise((r) => setTimeout(r, intervalMs))
  }
  throw new Error('File processing timed out')
}

export async function deleteFile(fileId: string) {
  const { data } = await http.delete(`/files/delete_file/${encodeURIComponent(fileId)}`)
  return data
}
