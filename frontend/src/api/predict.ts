import { http } from './http'

export async function predictHeart(payload: Record<string, unknown>) {
  const { data } = await http.post<{ prediction: number; message: string }>(
    '/predict/heart_failure',
    payload,
  )
  return data
}

export async function predictLung(payload: Record<string, unknown>) {
  const { data } = await http.post<{ prediction: number; message: string }>(
    '/predict/lung_cancer',
    payload,
  )
  return data
}

export async function predictBrain(file: File) {
  const form = new FormData()
  form.append('file', file)
  const { data } = await http.post<{ predicted_class: string; confidence: number }>(
    '/brain/predict_tumor',
    form,
  )
  return data
}

export async function predictBreast(payload: Record<string, number>) {
  const { data } = await http.post<{ prediction: number; message: string }>(
    '/predict/breast_cancer',
    payload,
  )
  return data
}
