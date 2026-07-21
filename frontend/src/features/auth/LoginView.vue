<script setup lang="ts">
import { computed } from 'vue'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NCard, NFormItem, NInput, useMessage } from 'naive-ui'
import { useAuthStore } from '@/stores/auth'
import { extractApiError } from '@/api/http'
import { useAppI18n } from '@/i18n/useAppI18n'
import { useValidationSchemas } from '@/shared/validation/schemas'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const message = useMessage()
const { t } = useAppI18n()
const { loginSchema } = useValidationSchemas()

const { handleSubmit, defineField, errors, isSubmitting } = useForm({
  validationSchema: computed(() => toTypedSchema(loginSchema.value)),
  initialValues: { email: '', password: '' },
})

const [email] = defineField('email')
const [password] = defineField('password')

const onSubmit = handleSubmit(async (values) => {
  try {
    await auth.login(values.email.trim(), values.password)
    message.success(t('auth.loginSuccess'))
    const redirect = (route.query.redirect as string) || '/app/chat'
    await router.push(redirect)
  } catch (e) {
    message.error(extractApiError(e))
  }
})
</script>

<template>
  <div class="mx-auto flex max-w-md px-4 py-16">
    <NCard class="w-full shadow-lg shadow-teal-900/5">
      <h1 class="brand-font mb-1 text-3xl font-bold text-[var(--sc-primary-deep)]">{{ t('auth.loginTitle') }}</h1>
      <p class="mb-6 text-sm text-slate-500">{{ t('auth.loginSubtitle') }}</p>
      <form @submit.prevent="onSubmit">
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
            placeholder="you@example.com"
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
            autocomplete="current-password"
            placeholder="••••••••"
            @update:value="(v: string) => (password = v)"
          />
        </NFormItem>
        <NButton type="primary" attr-type="submit" block :loading="isSubmitting" class="mt-2">
          {{ t('auth.loginAction') }}
        </NButton>
      </form>
      <p class="mt-4 text-center text-sm text-slate-500">
        {{ t('auth.noAccount') }}
        <RouterLink to="/register" class="font-semibold text-[var(--sc-primary)]">{{ t('nav.register') }}</RouterLink>
      </p>
    </NCard>
  </div>
</template>
