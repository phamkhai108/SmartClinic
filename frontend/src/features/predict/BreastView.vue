<script setup lang="ts">
import { computed } from 'vue'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { useRouter } from 'vue-router'
import { NButton, NCard, NFormItem, NInputNumber, useMessage } from 'naive-ui'
import { predictBreast } from '@/api/predict'
import { extractApiError } from '@/api/http'
import { useAppI18n } from '@/i18n/useAppI18n'
import { useValidationSchemas } from '@/shared/validation/schemas'
import { savePredictResult } from './resultStorage'

const router = useRouter()
const message = useMessage()
const { t } = useAppI18n()
const { breastSchema } = useValidationSchemas()

const initialValues = {
  radius_mean: 14.0,
  texture_mean: 19.0,
  perimeter_mean: 90.0,
  area_mean: 600.0,
  smoothness_mean: 0.1,
  compactness_mean: 0.1,
  concavity_mean: 0.08,
  'concave points_mean': 0.05,
  radius_se: 0.4,
  perimeter_se: 2.5,
  area_se: 40.0,
  concavity_se: 0.03,
  radius_worst: 16.0,
  texture_worst: 25.0,
  perimeter_worst: 110.0,
  area_worst: 800.0,
  smoothness_worst: 0.13,
  compactness_worst: 0.25,
  concavity_worst: 0.25,
  'concave points_worst': 0.12,
  symmetry_worst: 0.3,
}

const { handleSubmit, values, errors, isSubmitting, setFieldValue } = useForm({
  validationSchema: computed(() => toTypedSchema(breastSchema.value)),
  initialValues,
})

const groups = [
  {
    titleKey: 'predict.groupMean',
    keys: [
      ['radius_mean', 'predict.fields.radius'],
      ['texture_mean', 'predict.fields.texture'],
      ['perimeter_mean', 'predict.fields.perimeter'],
      ['area_mean', 'predict.fields.area'],
      ['smoothness_mean', 'predict.fields.smoothness'],
      ['compactness_mean', 'predict.fields.compactness'],
      ['concavity_mean', 'predict.fields.concavity'],
      ['concave points_mean', 'predict.fields.concavePoints'],
    ] as const,
  },
  {
    titleKey: 'predict.groupSe',
    keys: [
      ['radius_se', 'predict.fields.radiusSe'],
      ['perimeter_se', 'predict.fields.perimeterSe'],
      ['area_se', 'predict.fields.areaSe'],
      ['concavity_se', 'predict.fields.concavitySe'],
    ] as const,
  },
  {
    titleKey: 'predict.groupWorst',
    keys: [
      ['radius_worst', 'predict.fields.radius'],
      ['texture_worst', 'predict.fields.texture'],
      ['perimeter_worst', 'predict.fields.perimeter'],
      ['area_worst', 'predict.fields.area'],
      ['smoothness_worst', 'predict.fields.smoothness'],
      ['compactness_worst', 'predict.fields.compactness'],
      ['concavity_worst', 'predict.fields.concavity'],
      ['concave points_worst', 'predict.fields.concavePoints'],
      ['symmetry_worst', 'predict.fields.symmetry'],
    ] as const,
  },
]

const onSubmit = handleSubmit(async (formValues) => {
  try {
    const res = await predictBreast({ ...formValues })
    savePredictResult({
      kind: 'breast',
      prediction: res.prediction,
      message: res.message,
      retryRoute: '/app/predict/breast',
    })
    await router.push('/app/predict/breast/result')
  } catch (e) {
    message.error(extractApiError(e))
  }
})
</script>

<template>
  <div class="mx-auto max-w-4xl space-y-4">
    <NCard :title="t('predict.breastTitle')">
      <p class="mb-4 text-sm text-slate-500">{{ t('predict.breastHint') }}</p>
      <form @submit.prevent="onSubmit">
        <div v-for="group in groups" :key="group.titleKey" class="mb-6">
          <h3 class="mb-2 text-sm font-semibold text-[var(--sc-primary-deep)]">{{ t(group.titleKey) }}</h3>
          <div class="grid gap-2 md:grid-cols-2">
            <NFormItem
              v-for="[key, labelKey] in group.keys"
              :key="key"
              :label="t(labelKey)"
              :validation-status="errors[key] ? 'error' : undefined"
              :feedback="errors[key]"
            >
              <NInputNumber
                :value="values[key]"
                :step="0.01"
                class="w-full"
                @update:value="(v) => setFieldValue(key, v ?? 0)"
              />
            </NFormItem>
          </div>
        </div>
        <NButton type="primary" attr-type="submit" :loading="isSubmitting">{{ t('predict.predictAction') }}</NButton>
      </form>
    </NCard>
  </div>
</template>
