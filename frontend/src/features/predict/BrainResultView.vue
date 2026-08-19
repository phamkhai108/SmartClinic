<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart } from 'echarts/charts'
import { TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import PredictResultShell from './PredictResultShell.vue'
import { usePredictLabel } from './predictLabel'
import { loadPredictResult, type PredictResultPayload } from './resultStorage'
import { useAppI18n } from '@/i18n/useAppI18n'

use([CanvasRenderer, PieChart, TooltipComponent])

const router = useRouter()
const { t } = useAppI18n()
const { label } = usePredictLabel()
const data = ref<PredictResultPayload | null>(null)

onMounted(() => {
  data.value = loadPredictResult()
  if (!data.value || data.value.kind !== 'brain') router.replace('/app/predict/brain')
})

onUnmounted(() => {
  if (data.value?.imagePreview?.startsWith('blob:')) URL.revokeObjectURL(data.value.imagePreview)
})

const conf = computed(() => data.value?.confidence ?? 0)
const classLabel = computed(() =>
  label('brain', data.value?.prediction, data.value?.predicted_class ?? data.value?.message),
)
const resultMessage = computed(() => `${classLabel.value} · ${conf.value}%`)
const chartOption = computed(() => ({
  tooltip: { trigger: 'item' },
  series: [
    {
      type: 'pie',
      radius: ['45%', '70%'],
      data: [
        { name: classLabel.value, value: conf.value },
        { name: 'Other', value: Math.max(0, 100 - conf.value) },
      ],
    },
  ],
}))

const recommendations = computed(() => [
  t('predict.rec.brain1'),
  t('predict.rec.brain2'),
  t('predict.rec.brain3'),
])
</script>

<template>
  <PredictResultShell
    v-if="data"
    :title="t('predict.resultBrain')"
    :message="resultMessage"
    tone="info"
    :recommendations="recommendations"
    :retry-route="data.retryRoute"
  >
    <img
      v-if="data.imagePreview"
      :src="data.imagePreview"
      alt="MRI"
      class="mx-auto mt-4 max-h-56 rounded-xl object-contain"
    />
    <VChart class="mx-auto mt-4 h-56 w-full max-w-md" :option="chartOption" autoresize />
  </PredictResultShell>
</template>
