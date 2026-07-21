<script setup lang="ts">
import { computed } from 'vue'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { useRouter } from 'vue-router'
import { NButton, NCard, NFormItem, NInputNumber, NSelect, useMessage } from 'naive-ui'
import { predictLung } from '@/api/predict'
import { extractApiError } from '@/api/http'
import { useAppI18n } from '@/i18n/useAppI18n'
import { useValidationSchemas } from '@/shared/validation/schemas'
import { savePredictResult } from './resultStorage'

const router = useRouter()
const message = useMessage()
const { t } = useAppI18n()
const { lungSchema } = useValidationSchemas()

const { handleSubmit, defineField, errors, isSubmitting, values, setFieldValue } = useForm({
  validationSchema: computed(() => toTypedSchema(lungSchema.value)),
  initialValues: {
    Age: 60,
    Gender: 1,
    Air_Pollution: 3,
    Alcohol_use: 2,
    OccuPational_Hazards: 1,
    Genetic_Risk: 2,
    chronic_Lung_Disease: 1,
    Smoking: 2,
    Passive_Smoker: 1,
    Chest_Pain: 2,
    Coughing_of_Blood: 1,
    Clubbing_of_Finger_Nails: 1,
  },
})

const [Age] = defineField('Age')
const [Gender] = defineField('Gender')

const scaleFields = [
  { key: 'Air_Pollution' as const, label: 'predict.fields.airPollution' },
  { key: 'Alcohol_use' as const, label: 'predict.fields.alcoholUse' },
  { key: 'OccuPational_Hazards' as const, label: 'predict.fields.occupationalHazards' },
  { key: 'Genetic_Risk' as const, label: 'predict.fields.geneticRisk' },
  { key: 'chronic_Lung_Disease' as const, label: 'predict.fields.chronicLung' },
  { key: 'Smoking' as const, label: 'predict.fields.smoking' },
  { key: 'Passive_Smoker' as const, label: 'predict.fields.passiveSmoker' },
  { key: 'Chest_Pain' as const, label: 'predict.fields.chestPainLung' },
  { key: 'Coughing_of_Blood' as const, label: 'predict.fields.coughingBlood' },
  { key: 'Clubbing_of_Finger_Nails' as const, label: 'predict.fields.clubbing' },
]

const onSubmit = handleSubmit(async (formValues) => {
  try {
    const res = await predictLung({ ...formValues })
    savePredictResult({
      kind: 'lung',
      prediction: res.prediction,
      message: res.message,
      retryRoute: '/app/predict/lung',
    })
    await router.push('/app/predict/lung/result')
  } catch (e) {
    message.error(extractApiError(e))
  }
})
</script>

<template>
  <div class="mx-auto max-w-4xl">
    <NCard :title="t('predict.lungTitle')">
      <p class="mb-4 text-sm text-slate-500">{{ t('predict.lungHint') }}</p>
      <form class="grid gap-2 md:grid-cols-2" @submit.prevent="onSubmit">
        <NFormItem :label="t('predict.fields.age')" :validation-status="errors.Age ? 'error' : undefined" :feedback="errors.Age">
          <NInputNumber :value="Age" class="w-full" @update:value="(v) => (Age = v ?? 0)" />
        </NFormItem>
        <NFormItem :label="t('predict.fields.gender')" :validation-status="errors.Gender ? 'error' : undefined" :feedback="errors.Gender">
          <NSelect
            :value="Gender"
            :options="[
              { label: t('predict.fields.maleShort'), value: 1 },
              { label: t('predict.fields.femaleShort'), value: 0 },
            ]"
            @update:value="(v: number) => (Gender = v)"
          />
        </NFormItem>
        <NFormItem
          v-for="f in scaleFields"
          :key="f.key"
          :label="t(f.label)"
          :feedback="errors[f.key] || t('predict.fields.scaleHint')"
          :validation-status="errors[f.key] ? 'error' : undefined"
        >
          <NInputNumber
            :value="values[f.key]"
            :min="0"
            :max="10"
            class="w-full"
            @update:value="(v) => setFieldValue(f.key, v ?? 0)"
          />
        </NFormItem>
        <div class="md:col-span-2">
          <NButton type="primary" attr-type="submit" :loading="isSubmitting">{{ t('predict.predictAction') }}</NButton>
        </div>
      </form>
    </NCard>
  </div>
</template>
