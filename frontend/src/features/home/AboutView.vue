<script setup lang="ts">
import { useAppI18n } from '@/i18n/useAppI18n'

const { t } = useAppI18n()
</script>

<template>
  <section class="mx-auto max-w-3xl px-4 py-16 md:px-6">
    <h1 class="brand-font mb-4 text-4xl font-bold text-[var(--sc-primary-deep)]">{{ t('about.title') }}</h1>
    <div class="space-y-8 text-base leading-relaxed text-slate-700">
      <p>{{ t('about.p1') }}</p>
      <div>
        <h2 class="mb-2 text-xl font-semibold text-slate-800">{{ t('about.missionTitle') }}</h2>
        <p>{{ t('about.mission') }}</p>
      </div>
      <div>
        <h2 class="mb-2 text-xl font-semibold text-slate-800">{{ t('about.techTitle') }}</h2>
        <ul class="list-disc space-y-1 pl-5">
          <li>{{ t('about.tech1') }}</li>
          <li>{{ t('about.tech2') }}</li>
          <li>{{ t('about.tech3') }}</li>
          <li>{{ t('about.tech4') }}</li>
        </ul>
      </div>
      <p class="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
        {{ t('about.disclaimer') }}
      </p>
    </div>
  </section>
</template>
