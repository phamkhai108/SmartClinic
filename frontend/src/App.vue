<script setup lang="ts">
import { computed } from 'vue'
import {
  NConfigProvider,
  NDialogProvider,
  NMessageProvider,
  NNotificationProvider,
  dateEnUS,
  dateViVN,
  enUS,
  viVN,
} from 'naive-ui'
import { themeOverrides } from '@/shared/theme/naive'
import { useAppI18n } from '@/i18n/useAppI18n'

const { currentLocale } = useAppI18n()

const naiveLocale = computed(() => (currentLocale.value === 'en' ? enUS : viVN))
const naiveDateLocale = computed(() => (currentLocale.value === 'en' ? dateEnUS : dateViVN))
</script>

<template>
  <NConfigProvider
    :locale="naiveLocale"
    :date-locale="naiveDateLocale"
    :theme-overrides="themeOverrides"
  >
    <NMessageProvider>
      <NNotificationProvider>
        <NDialogProvider>
          <RouterView />
        </NDialogProvider>
      </NNotificationProvider>
    </NMessageProvider>
  </NConfigProvider>
</template>
