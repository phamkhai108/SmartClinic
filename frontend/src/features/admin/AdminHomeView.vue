<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { NCard, NGrid, NGi, NButton, NStatistic, useMessage } from 'naive-ui'
import { useRouter } from 'vue-router'
import { listFiles } from '@/api/admin'
import { extractApiError } from '@/api/http'
import type { FileInfo } from '@/shared/types/api'
import { useAppI18n } from '@/i18n/useAppI18n'

const router = useRouter()
const message = useMessage()
const { t } = useAppI18n()
const files = ref<FileInfo[]>([])
const loading = ref(false)

const total = computed(() => files.value.length)
const success = computed(() => files.value.filter((f) => f.status === 'success').length)
const other = computed(() => total.value - success.value)

const cards = computed(() => [
  { title: t('admin.usersCard'), desc: t('admin.usersDesc'), to: '/admin/users' },
  { title: t('admin.filesCard'), desc: t('admin.filesDesc'), to: '/admin/files' },
  { title: t('admin.uploadCard'), desc: t('admin.uploadDesc'), to: '/admin/upload' },
])

async function load() {
  loading.value = true
  try {
    files.value = await listFiles('all')
  } catch (e) {
    message.error(extractApiError(e))
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="brand-font mb-2 text-3xl font-bold text-[var(--sc-primary-deep)]">{{ t('admin.title') }}</h1>
      <p class="text-slate-600">{{ t('admin.lead') }}</p>
    </div>

    <NGrid cols="1 m:3" :x-gap="16" :y-gap="16" responsive="screen">
      <NGi><NCard><NStatistic :label="t('admin.totalFiles')" :value="total" /></NCard></NGi>
      <NGi><NCard><NStatistic :label="t('admin.successFiles')" :value="success" /></NCard></NGi>
      <NGi><NCard><NStatistic :label="t('admin.otherFiles')" :value="other" /></NCard></NGi>
    </NGrid>

    <NGrid cols="1 m:3" :x-gap="16" :y-gap="16" responsive="screen">
      <NGi v-for="c in cards" :key="c.title">
        <NCard>
          <h3 class="mb-2 text-lg font-semibold">{{ c.title }}</h3>
          <p class="mb-4 text-sm text-slate-600">{{ c.desc }}</p>
          <NButton type="primary" secondary :loading="loading" @click="router.push(c.to)">{{ t('common.open') }}</NButton>
        </NCard>
      </NGi>
    </NGrid>
  </div>
</template>
