import { http } from './http'

export type PredictClassResponse = {
  prediction: number
  message: string
}

export type PredictBrainResponse = {
  prediction: number
  predicted_class: string
  confidence: number
  message: string
}

export async function predictHeart(payload: Record<string, unknown>) {
  const { data } = await http.post<PredictClassResponse>('/predict/heart_failure', payload)
  return data
}

export async function predictLung(payload: Record<string, unknown>) {
  const { data } = await http.post<PredictClassResponse>('/predict/lung_cancer', payload)
  return data
}

export async function predictBrain(file: File) {
  const form = new FormData()
  form.append('file', file)
  const { data } = await http.post<PredictBrainResponse>('/brain/predict_tumor', form)
  return data
}

export async function predictBreast(payload: Record<string, number>) {
  const { data } = await http.post<PredictClassResponse>('/predict/breast_cancer', payload)
  return data
}
