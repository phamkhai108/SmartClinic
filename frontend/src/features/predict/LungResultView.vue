<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import PredictResultShell from './PredictResultShell.vue'
import { usePredictLabel } from './predictLabel'
import { loadPredictResult, type PredictResultPayload } from './resultStorage'
import { useAppI18n } from '@/i18n/useAppI18n'

const router = useRouter()
const { t } = useAppI18n()
const { label } = usePredictLabel()
const data = ref<PredictResultPayload | null>(null)

onMounted(() => {
  data.value = loadPredictResult()
  if (!data.value || data.value.kind !== 'lung') router.replace('/app/predict/lung')
})

const tone = computed(() => {
  const p = data.value?.prediction
  if (p === 3) return 'danger'
  if (p === 2) return 'warning'
  return 'success'
})

const recommendations = computed(() => {
  const p = data.value?.prediction
  if (p === 3) return [t('predict.rec.lungHigh1'), t('predict.rec.lungHigh2'), t('predict.rec.lungHigh3')]
  if (p === 2) return [t('predict.rec.lungMid1'), t('predict.rec.lungMid2'), t('predict.rec.lungMid3')]
  return [t('predict.rec.lungLow1'), t('predict.rec.lungLow2'), t('predict.rec.lungLow3')]
})

const resultMessage = computed(() =>
  label('lung', data.value?.prediction, data.value?.message),
)
</script>

<template>
  <PredictResultShell
    v-if="data"
    :title="t('predict.resultLung')"
    :message="resultMessage"
    :tone="tone"
    :recommendations="recommendations"
    :retry-route="data.retryRoute"
  >
    <p class="mt-4 text-center text-sm text-slate-500">{{ t('predict.level') }}: {{ data.prediction }}</p>
  </PredictResultShell>
</template>
