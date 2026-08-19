import { describe, expect, it } from 'vitest'
import { resolvePredictLabel } from './predictLabel'

const LABELS: Record<string, string> = {
  'predict.classes.heart.0': 'No heart failure symptoms',
  'predict.classes.heart.1': 'Heart failure symptoms',
  'predict.classes.brain.2': 'No tumor',
}

function lookup(key: string): string | undefined {
  return LABELS[key]
}

describe('resolvePredictLabel', () => {
  it('maps class index to the locale string', () => {
    expect(resolvePredictLabel('heart', 1, lookup)).toBe('Heart failure symptoms')
  })

  it('falls back to API message when the key is missing', () => {
    expect(resolvePredictLabel('lung', 3, lookup, 'High cancer risk')).toBe(
      'High cancer risk',
    )
  })

  it('falls back to the class index when no translation or message exists', () => {
    expect(resolvePredictLabel('breast', 0, lookup)).toBe('0')
  })

  it('returns empty string when prediction is missing and there is no fallback', () => {
    expect(resolvePredictLabel('heart', undefined, lookup)).toBe('')
  })

  it('uses fallback message when prediction is missing', () => {
    expect(resolvePredictLabel('brain', undefined, lookup, 'glioma')).toBe('glioma')
  })

  it('resolves brain class names from the index', () => {
    expect(resolvePredictLabel('brain', 2, lookup, 'notumor')).toBe('No tumor')
  })
})
