import { useAppI18n } from '@/i18n/useAppI18n'
import type { PredictKind } from './resultStorage'

export function resolvePredictLabel(
  kind: PredictKind,
  prediction: number | undefined,
  lookup: (key: string) => string | undefined,
  fallbackMessage?: string,
): string {
  if (prediction === undefined || Number.isNaN(prediction)) {
    return fallbackMessage ?? ''
  }
  return (
    lookup(`predict.classes.${kind}.${prediction}`) ??
    fallbackMessage ??
    String(prediction)
  )
}

export function usePredictLabel() {
  const { t, te } = useAppI18n()

  function lookup(key: string): string | undefined {
    return te(key) ? String(t(key)) : undefined
  }

  function label(
    kind: PredictKind,
    prediction: number | undefined,
    fallbackMessage?: string,
  ): string {
    return resolvePredictLabel(kind, prediction, lookup, fallbackMessage)
  }

  return { label }
}
