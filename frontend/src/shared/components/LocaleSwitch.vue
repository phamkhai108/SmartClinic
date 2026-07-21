<script setup lang="ts">
import { NSelect } from 'naive-ui'
import { useAppI18n } from '@/i18n/useAppI18n'
import type { AppLocale } from '@/i18n/localeStorage'

const { t, currentLocale } = useAppI18n()

const options = [
  { label: 'VI', value: 'vi' },
  { label: 'EN', value: 'en' },
]

function onUpdate(value: string) {
  currentLocale.value = value as AppLocale
}
</script>

<template>
  <NSelect
    :value="currentLocale"
    :options="options"
    size="small"
    style="width: 72px"
    :aria-label="t('common.language')"
    @update:value="onUpdate"
  />
</template>
