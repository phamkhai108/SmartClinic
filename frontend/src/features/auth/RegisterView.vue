<script setup lang="ts">
import { computed, ref } from 'vue'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'
import { useRouter } from 'vue-router'
import { NButton, NCard, NFormItem, NInput, useMessage } from 'naive-ui'
import { register } from '@/api/auth'
import { extractApiError } from '@/api/http'
import { useAppI18n } from '@/i18n/useAppI18n'

const router = useRouter()
const message = useMessage()
const { t, currentLocale } = useAppI18n()
const step = ref<'request' | 'verify'>('request')

const schema = computed(() => {
  void currentLocale.value
  return z.object({
    user_name: z
      .string()
      .trim()
      .min(1, t('validation.required'))
      .min(2, t('validation.minUserName', { min: 2 })),
    email: z
      .string()
      .trim()
      .min(1, t('validation.required'))
      .pipe(z.email({ error: t('validation.email') })),
    password: z
      .string()
      .min(1, t('validation.required'))
      .min(4, t('validation.minPassword', { min: 4 })),
    code_verify:
      step.value === 'verify'
        ? z
            .string()
            .trim()
            .min(1, t('validation.required'))
            .length(6, t('validation.otpLength'))
            .regex(/^\d+$/, t('validation.otpDigits'))
        : z.string().optional(),
  })
})

const { handleSubmit, defineField, errors, isSubmitting } = useForm({
  validationSchema: computed(() => toTypedSchema(schema.value)),
  initialValues: { user_name: '', email: '', password: '', code_verify: '' },
})

const [userName] = defineField('user_name')
const [email] = defineField('email')
const [password] = defineField('password')
const [code] = defineField('code_verify')

const onSubmit = handleSubmit(async (formValues) => {
  try {
    if (step.value === 'request') {
      const res = await register({
        user_name: formValues.user_name.trim(),
        email: formValues.email.trim(),
        password: formValues.password,
      })
      message.success(res.message)
      step.value = 'verify'
      return
    }
    const res = await register({
      user_name: formValues.user_name.trim(),
      email: formValues.email.trim(),
      password: formValues.password,
      code_verify: formValues.code_verify?.trim(),
    })
    message.success(res.message)
    await router.push('/login')
  } catch (e) {
    message.error(extractApiError(e))
  }
})
</script>

<template>
  <div class="mx-auto flex max-w-md px-4 py-16">
    <NCard class="w-full shadow-lg shadow-teal-900/5">
      <h1 class="brand-font mb-1 text-3xl font-bold text-[var(--sc-primary-deep)]">{{ t('auth.registerTitle') }}</h1>
      <p class="mb-6 text-sm text-slate-500">
        {{ step === 'request' ? t('auth.registerStep1') : t('auth.registerStep2') }}
      </p>
      <form @submit.prevent="onSubmit">
        <NFormItem
          :label="t('auth.userName')"
          required
          :validation-status="errors.user_name ? 'error' : undefined"
          :feedback="errors.user_name"
        >
          <NInput :value="userName" :disabled="step === 'verify'" @update:value="(v: string) => (userName = v)" />
        </NFormItem>
        <NFormItem
          :label="t('auth.email')"
          required
          :validation-status="errors.email ? 'error' : undefined"
          :feedback="errors.email"
        >
          <NInput
            :value="email"
            type="text"
            autocomplete="email"
            :disabled="step === 'verify'"
            @update:value="(v: string) => (email = v)"
          />
        </NFormItem>
        <NFormItem
          :label="t('auth.password')"
          required
          :validation-status="errors.password ? 'error' : undefined"
          :feedback="errors.password"
        >
          <NInput
            :value="password"
            type="password"
            show-password-on="click"
            :disabled="step === 'verify'"
            @update:value="(v: string) => (password = v)"
          />
        </NFormItem>
        <NFormItem
          v-if="step === 'verify'"
          :label="t('auth.codeVerify')"
          required
          :validation-status="errors.code_verify ? 'error' : undefined"
          :feedback="errors.code_verify"
        >
          <NInput
            :value="code"
            :placeholder="t('auth.codePlaceholder')"
            @update:value="(v: string) => (code = v)"
          />
        </NFormItem>
        <NButton type="primary" attr-type="submit" block :loading="isSubmitting">
          {{ step === 'request' ? t('auth.sendCode') : t('auth.completeRegister') }}
        </NButton>
      </form>
    </NCard>
  </div>
</template>
