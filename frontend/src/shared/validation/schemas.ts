import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { z } from 'zod'
import type { MessageSchema } from '@/i18n/locales/vi'

export function useValidationSchemas() {
  const { t, locale } = useI18n<{ message: MessageSchema }>()

  const loginSchema = computed(() => {
    void locale.value
    return z.object({
      email: z.string().trim().min(1, t('validation.required')).email(t('validation.email')),
      password: z.string().min(1, t('validation.required')).min(4, t('validation.minPassword', { min: 4 })),
    })
  })

  const registerSchema = computed(() => {
    void locale.value
    return z.object({
      user_name: z.string().trim().min(1, t('validation.required')).min(2, t('validation.minUserName', { min: 2 })),
      email: z.string().trim().min(1, t('validation.required')).email(t('validation.email')),
      password: z.string().min(1, t('validation.required')).min(4, t('validation.minPassword', { min: 4 })),
    })
  })

  const otpSchema = computed(() => {
    void locale.value
    return z.object({
      code_verify: z
        .string()
        .trim()
        .min(1, t('validation.required'))
        .length(6, t('validation.otpLength'))
        .regex(/^\d+$/, t('validation.otpDigits')),
    })
  })

  const heartSchema = computed(() => {
    void locale.value
    const num = z.number({ invalid_type_error: t('validation.number') })
    return z.object({
      Age: num.min(1, t('validation.min', { min: 1 })).max(120, t('validation.max', { max: 120 })),
      Sex: z.enum(['M', 'F']),
      ChestPainType: z.enum(['TA', 'ATA', 'NAP', 'ASY']),
      RestingBP: num.min(50).max(250),
      Cholesterol: num.min(0).max(800),
      FastingBS: num.min(0).max(1),
      RestingECG: z.enum(['Normal', 'ST', 'LVH']),
      MaxHR: num.min(50).max(250),
      ExerciseAngina: z.enum(['Y', 'N']),
      Oldpeak: num.min(0).max(10),
      ST_Slope: z.enum(['Up', 'Flat', 'Down']),
    })
  })

  const lungSchema = computed(() => {
    void locale.value
    const scale = z
      .number({ invalid_type_error: t('validation.number') })
      .min(0, t('validation.min', { min: 0 }))
      .max(10, t('validation.max', { max: 10 }))
    return z.object({
      Age: z.number({ invalid_type_error: t('validation.number') }).min(0).max(120),
      Gender: z.number().min(0).max(1),
      Air_Pollution: scale,
      Alcohol_use: scale,
      OccuPational_Hazards: scale,
      Genetic_Risk: scale,
      chronic_Lung_Disease: scale,
      Smoking: scale,
      Passive_Smoker: scale,
      Chest_Pain: scale,
      Coughing_of_Blood: scale,
      Clubbing_of_Finger_Nails: scale,
    })
  })

  const breastSchema = computed(() => {
    void locale.value
    const n = z.number({ invalid_type_error: t('validation.number') })
    return z.object({
      radius_mean: n,
      texture_mean: n,
      perimeter_mean: n,
      area_mean: n,
      smoothness_mean: n,
      compactness_mean: n,
      concavity_mean: n,
      'concave points_mean': n,
      radius_se: n,
      perimeter_se: n,
      area_se: n,
      concavity_se: n,
      radius_worst: n,
      texture_worst: n,
      perimeter_worst: n,
      area_worst: n,
      smoothness_worst: n,
      compactness_worst: n,
      concavity_worst: n,
      'concave points_worst': n,
      symmetry_worst: n,
    })
  })

  const chatSchema = computed(() => {
    void locale.value
    return z.object({
      message: z.string().trim().min(1, t('validation.messageRequired')),
    })
  })

  const uploadMetaSchema = computed(() => {
    void locale.value
    return z.object({
      userId: z.string().min(1, t('validation.required')),
    })
  })

  return {
    loginSchema,
    registerSchema,
    otpSchema,
    heartSchema,
    lungSchema,
    breastSchema,
    chatSchema,
    uploadMetaSchema,
  }
}

export function validateImageFile(
  file: File | null,
  t: (key: string, params?: Record<string, unknown>) => string,
) {
  if (!file) return t('validation.fileRequired')
  const ok = /\.(jpe?g|png)$/i.test(file.name)
  if (!ok) return t('validation.fileTypeImage')
  if (file.size > 10 * 1024 * 1024) return t('validation.fileTooLarge', { mb: 10 })
  return null
}

export function validateDocFile(
  file: File | null,
  t: (key: string, params?: Record<string, unknown>) => string,
) {
  if (!file) return t('validation.fileRequired')
  const ok = /\.(pdf|docx|xlsx|pptx|md|markdown)$/i.test(file.name)
  if (!ok) return t('validation.fileTypeDoc')
  if (file.size > 20 * 1024 * 1024) return t('validation.fileTooLarge', { mb: 20 })
  return null
}
