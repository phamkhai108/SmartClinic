export type PredictKind = 'heart' | 'lung' | 'brain' | 'breast'

export interface PredictResultPayload {
  kind: PredictKind
  prediction?: number
  message?: string
  predicted_class?: string
  confidence?: number
  imagePreview?: string
  retryRoute: string
}

const KEY = 'smartclinic_predict_result'

export function savePredictResult(payload: PredictResultPayload) {
  sessionStorage.setItem(KEY, JSON.stringify(payload))
}

export function loadPredictResult(): PredictResultPayload | null {
  const raw = sessionStorage.getItem(KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as PredictResultPayload
  } catch {
    return null
  }
}

export function clearPredictResult() {
  sessionStorage.removeItem(KEY)
}
