<script setup lang="ts">
import { useRouter } from 'vue-router'
import { NButton, NCard, NSpace } from 'naive-ui'
import { useAppI18n } from '@/i18n/useAppI18n'

defineProps<{
  title: string
  message: string
  tone: 'success' | 'warning' | 'danger' | 'info'
  recommendations: string[]
  retryRoute: string
}>()

const router = useRouter()
const { t } = useAppI18n()

const toneClass = {
  success: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  warning: 'bg-amber-50 text-amber-800 border-amber-200',
  danger: 'bg-rose-50 text-rose-700 border-rose-200',
  info: 'bg-sky-50 text-sky-800 border-sky-200',
}
</script>

<template>
  <div class="mx-auto max-w-3xl space-y-4">
    <div class="flex items-center justify-between text-sm text-slate-500">
      <span class="font-medium text-[var(--sc-primary)]">{{ t('predict.stepInfo') }}</span>
      <span class="font-medium text-[var(--sc-primary)]">{{ t('predict.stepAnalyze') }}</span>
      <span class="font-semibold text-[var(--sc-primary-deep)]">{{ t('predict.stepResult') }}</span>
    </div>

    <NCard>
      <div class="rounded-2xl border p-6 text-center" :class="toneClass[tone]">
        <h1 class="brand-font mb-2 text-3xl font-bold">{{ title }}</h1>
        <p class="text-lg font-medium">{{ message }}</p>
      </div>

      <slot />

      <div class="mt-6">
        <h2 class="mb-2 text-base font-semibold text-slate-800">{{ t('predict.recommendations') }}</h2>
        <ul class="list-disc space-y-1 pl-5 text-sm text-slate-600">
          <li v-for="(item, i) in recommendations" :key="i">{{ item }}</li>
        </ul>
      </div>

      <NSpace class="mt-6">
        <NButton type="primary" @click="router.push(retryRoute)">{{ t('predict.retry') }}</NButton>
        <NButton secondary @click="router.push('/app/chat')">{{ t('nav.chat') }}</NButton>
      </NSpace>
    </NCard>
  </div>
</template>
