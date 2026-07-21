<script setup lang="ts">
import { computed } from 'vue'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { useRouter } from 'vue-router'
import { NButton, NCard, NFormItem, NInputNumber, NSelect, useMessage } from 'naive-ui'
import { predictHeart } from '@/api/predict'
import { extractApiError } from '@/api/http'
import { useAppI18n } from '@/i18n/useAppI18n'
import { useValidationSchemas } from '@/shared/validation/schemas'
import { savePredictResult } from './resultStorage'

const router = useRouter()
const message = useMessage()
const { t } = useAppI18n()
const { heartSchema } = useValidationSchemas()

const { handleSubmit, defineField, errors, isSubmitting } = useForm({
  validationSchema: computed(() => toTypedSchema(heartSchema.value)),
  initialValues: {
    Age: 45,
    Sex: 'M' as const,
    ChestPainType: 'ATA' as const,
    RestingBP: 130,
    Cholesterol: 250,
    FastingBS: 0,
    RestingECG: 'Normal' as const,
    MaxHR: 160,
    ExerciseAngina: 'N' as const,
    Oldpeak: 1.5,
    ST_Slope: 'Up' as const,
  },
})

const [Age] = defineField('Age')
const [Sex] = defineField('Sex')
const [ChestPainType] = defineField('ChestPainType')
const [RestingBP] = defineField('RestingBP')
const [Cholesterol] = defineField('Cholesterol')
const [FastingBS] = defineField('FastingBS')
const [RestingECG] = defineField('RestingECG')
const [MaxHR] = defineField('MaxHR')
const [ExerciseAngina] = defineField('ExerciseAngina')
const [Oldpeak] = defineField('Oldpeak')
const [ST_Slope] = defineField('ST_Slope')

const onSubmit = handleSubmit(async (values) => {
  try {
    const res = await predictHeart({ ...values })
    savePredictResult({
      kind: 'heart',
      prediction: res.prediction,
      message: res.message,
      retryRoute: '/app/predict/heart',
    })
    await router.push('/app/predict/heart/result')
  } catch (e) {
    message.error(extractApiError(e))
  }
})
</script>

<template>
  <div class="mx-auto max-w-4xl">
    <NCard :title="t('predict.heartTitle')">
      <form class="grid gap-2 md:grid-cols-2" @submit.prevent="onSubmit">
        <NFormItem :label="t('predict.fields.age')" :validation-status="errors.Age ? 'error' : undefined" :feedback="errors.Age">
          <NInputNumber :value="Age" class="w-full" @update:value="(v) => (Age = v ?? 0)" />
        </NFormItem>
        <NFormItem :label="t('predict.fields.sex')" :validation-status="errors.Sex ? 'error' : undefined" :feedback="errors.Sex">
          <NSelect
            :value="Sex"
            :options="[
              { label: t('predict.fields.male'), value: 'M' },
              { label: t('predict.fields.female'), value: 'F' },
            ]"
            @update:value="(v: string) => (Sex = v as 'M' | 'F')"
          />
        </NFormItem>
        <NFormItem :label="t('predict.fields.chestPain')" :validation-status="errors.ChestPainType ? 'error' : undefined" :feedback="errors.ChestPainType">
          <NSelect
            :value="ChestPainType"
            :options="['TA', 'ATA', 'NAP', 'ASY'].map((v) => ({ label: v, value: v }))"
            @update:value="(v: string) => (ChestPainType = v as typeof ChestPainType)"
          />
        </NFormItem>
        <NFormItem :label="t('predict.fields.restingBp')" :validation-status="errors.RestingBP ? 'error' : undefined" :feedback="errors.RestingBP">
          <NInputNumber :value="RestingBP" class="w-full" @update:value="(v) => (RestingBP = v ?? 0)" />
        </NFormItem>
        <NFormItem :label="t('predict.fields.cholesterol')" :validation-status="errors.Cholesterol ? 'error' : undefined" :feedback="errors.Cholesterol">
          <NInputNumber :value="Cholesterol" class="w-full" @update:value="(v) => (Cholesterol = v ?? 0)" />
        </NFormItem>
        <NFormItem :label="t('predict.fields.fastingBs')" :validation-status="errors.FastingBS ? 'error' : undefined" :feedback="errors.FastingBS">
          <NInputNumber :value="FastingBS" :min="0" :max="1" class="w-full" @update:value="(v) => (FastingBS = v ?? 0)" />
        </NFormItem>
        <NFormItem :label="t('predict.fields.restingEcg')" :validation-status="errors.RestingECG ? 'error' : undefined" :feedback="errors.RestingECG">
          <NSelect
            :value="RestingECG"
            :options="['Normal', 'ST', 'LVH'].map((v) => ({ label: v, value: v }))"
            @update:value="(v: string) => (RestingECG = v as typeof RestingECG)"
          />
        </NFormItem>
        <NFormItem :label="t('predict.fields.maxHr')" :validation-status="errors.MaxHR ? 'error' : undefined" :feedback="errors.MaxHR">
          <NInputNumber :value="MaxHR" class="w-full" @update:value="(v) => (MaxHR = v ?? 0)" />
        </NFormItem>
        <NFormItem :label="t('predict.fields.exerciseAngina')" :validation-status="errors.ExerciseAngina ? 'error' : undefined" :feedback="errors.ExerciseAngina">
          <NSelect
            :value="ExerciseAngina"
            :options="[
              { label: t('predict.fields.yes'), value: 'Y' },
              { label: t('predict.fields.no'), value: 'N' },
            ]"
            @update:value="(v: string) => (ExerciseAngina = v as 'Y' | 'N')"
          />
        </NFormItem>
        <NFormItem :label="t('predict.fields.oldpeak')" :validation-status="errors.Oldpeak ? 'error' : undefined" :feedback="errors.Oldpeak">
          <NInputNumber :value="Oldpeak" :step="0.1" class="w-full" @update:value="(v) => (Oldpeak = v ?? 0)" />
        </NFormItem>
        <NFormItem :label="t('predict.fields.stSlope')" :validation-status="errors.ST_Slope ? 'error' : undefined" :feedback="errors.ST_Slope">
          <NSelect
            :value="ST_Slope"
            :options="['Up', 'Flat', 'Down'].map((v) => ({ label: v, value: v }))"
            @update:value="(v: string) => (ST_Slope = v as typeof ST_Slope)"
          />
        </NFormItem>
        <div class="md:col-span-2">
          <NButton type="primary" attr-type="submit" :loading="isSubmitting">{{ t('predict.predictAction') }}</NButton>
        </div>
      </form>
    </NCard>
  </div>
</template>
