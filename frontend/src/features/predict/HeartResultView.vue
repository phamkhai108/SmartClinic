<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { GaugeChart } from 'echarts/charts'
import VChart from 'vue-echarts'
import PredictResultShell from './PredictResultShell.vue'
import { loadPredictResult, type PredictResultPayload } from './resultStorage'
import { useAppI18n } from '@/i18n/useAppI18n'

use([CanvasRenderer, GaugeChart])

const router = useRouter()
const { t } = useAppI18n()
const data = ref<PredictResultPayload | null>(null)

onMounted(() => {
  data.value = loadPredictResult()
  if (!data.value || data.value.kind !== 'heart') router.replace('/app/predict/heart')
})

const tone = computed(() => (data.value?.prediction === 1 ? 'danger' : 'success'))
const chartOption = computed(() => ({
  series: [
    {
      type: 'gauge',
      min: 0,
      max: 1,
      data: [{ value: data.value?.prediction ?? 0, name: 'Risk' }],
      detail: { formatter: '{value}' },
      axisLine: {
        lineStyle: {
          width: 14,
          color: [
            [0.5, '#0f766e'],
            [1, '#dc2626'],
          ],
        },
      },
    },
  ],
}))

const recommendations = computed(() =>
  data.value?.prediction === 1
    ? [t('predict.rec.heartHigh1'), t('predict.rec.heartHigh2'), t('predict.rec.heartHigh3')]
    : [t('predict.rec.heartLow1'), t('predict.rec.heartLow2'), t('predict.rec.heartLow3')],
)
</script>

<template>
  <PredictResultShell
    v-if="data"
    :title="t('predict.resultHeart')"
    :message="data.message"
    :tone="tone"
    :recommendations="recommendations"
    :retry-route="data.retryRoute"
  >
    <VChart class="mx-auto mt-4 h-56 w-full max-w-md" :option="chartOption" autoresize />
  </PredictResultShell>
</template>
