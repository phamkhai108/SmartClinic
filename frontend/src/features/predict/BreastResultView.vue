<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import PredictResultShell from './PredictResultShell.vue'
import { loadPredictResult, type PredictResultPayload } from './resultStorage'
import { useAppI18n } from '@/i18n/useAppI18n'

const router = useRouter()
const { t } = useAppI18n()
const data = ref<PredictResultPayload | null>(null)

onMounted(() => {
  data.value = loadPredictResult()
  if (!data.value || data.value.kind !== 'breast') router.replace('/app/predict/breast')
})

const tone = computed(() => (data.value?.prediction === 1 ? 'danger' : 'success'))
const recommendations = computed(() =>
  data.value?.prediction === 1
    ? [t('predict.rec.breastHigh1'), t('predict.rec.breastHigh2'), t('predict.rec.breastHigh3')]
    : [t('predict.rec.breastLow1'), t('predict.rec.breastLow2'), t('predict.rec.breastLow3')],
)
</script>

<template>
  <PredictResultShell
    v-if="data"
    :title="t('predict.resultBreast')"
    :message="data.message"
    :tone="tone"
    :recommendations="recommendations"
    :retry-route="data.retryRoute"
  />
</template>
