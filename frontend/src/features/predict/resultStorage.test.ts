import { afterEach, describe, expect, it, vi } from 'vitest'
import { clearPredictResult, loadPredictResult, savePredictResult } from './resultStorage'

function mockSessionStorage() {
  const store = new Map<string, string>()
  vi.stubGlobal('sessionStorage', {
    getItem: (key: string) => store.get(key) ?? null,
    setItem: (key: string, value: string) => {
      store.set(key, value)
    },
    removeItem: (key: string) => {
      store.delete(key)
    },
  })
  return store
}

describe('resultStorage', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('round-trips a prediction payload including class index', () => {
    mockSessionStorage()
    savePredictResult({
      kind: 'brain',
      prediction: 2,
      message: 'notumor',
      predicted_class: 'notumor',
      confidence: 60,
      retryRoute: '/app/predict/brain',
    })
    const loaded = loadPredictResult()
    expect(loaded?.kind).toBe('brain')
    expect(loaded?.prediction).toBe(2)
    expect(loaded?.predicted_class).toBe('notumor')
  })

  it('returns null for missing or invalid JSON', () => {
    const store = mockSessionStorage()
    expect(loadPredictResult()).toBeNull()
    store.set('smartclinic_predict_result', '{not-json')
    expect(loadPredictResult()).toBeNull()
  })

  it('clears stored results', () => {
    mockSessionStorage()
    savePredictResult({ kind: 'heart', prediction: 0, retryRoute: '/x' })
    clearPredictResult()
    expect(loadPredictResult()).toBeNull()
  })
})
