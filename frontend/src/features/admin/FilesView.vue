<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { NButton, NCard, NDataTable, useDialog, useMessage, type DataTableColumns } from 'naive-ui'
import { deleteFile, listFiles } from '@/api/admin'
import { extractApiError } from '@/api/http'
import type { FileInfo } from '@/shared/types/api'
import { useAppI18n } from '@/i18n/useAppI18n'

const message = useMessage()
const dialog = useDialog()
const { t } = useAppI18n()
const loading = ref(false)
const rows = ref<FileInfo[]>([])

const columns = computed<DataTableColumns<FileInfo>>(() => [
  { title: t('admin.colFileName'), key: 'file_name' },
  { title: t('admin.colUser'), key: 'user_id' },
  { title: t('admin.colStatus'), key: 'status' },
  {
    title: t('admin.colCreated'),
    key: 'created_at',
    render: (r) => new Date(r.created_at).toLocaleString(),
  },
  {
    title: '',
    key: 'actions',
    render(row) {
      return h(
        NButton,
        {
          size: 'small',
          type: 'error',
          tertiary: true,
          onClick: () => {
            dialog.warning({
              title: t('admin.deleteConfirm'),
              content: row.file_name,
              positiveText: t('common.delete'),
              negativeText: t('common.cancel'),
              onPositiveClick: async () => {
                try {
                  await deleteFile(row.id)
                  message.success(t('admin.deleted'))
                  await load()
                } catch (e) {
                  message.error(extractApiError(e))
                }
              },
            })
          },
        },
        { default: () => t('common.delete') },
      )
    },
  },
])

async function load() {
  loading.value = true
  try {
    rows.value = await listFiles('all')
  } catch (e) {
    message.error(extractApiError(e))
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <NCard :title="t('admin.filesTitle')">
    <template #header-extra>
      <NButton secondary :loading="loading" @click="load">{{ t('common.refresh') }}</NButton>
    </template>
    <NDataTable :columns="columns" :data="rows" :loading="loading" />
  </NCard>
</template>
