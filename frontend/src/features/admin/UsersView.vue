<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { NButton, NCard, NDataTable, NSelect, useMessage, type DataTableColumns } from 'naive-ui'
import { listUsers, updateUserRole } from '@/api/admin'
import { extractApiError } from '@/api/http'
import type { Role, UserDTO } from '@/shared/types/api'
import { useAppI18n } from '@/i18n/useAppI18n'

const message = useMessage()
const { t } = useAppI18n()
const loading = ref(false)
const rows = ref<UserDTO[]>([])

const columns = computed<DataTableColumns<UserDTO>>(() => [
  { title: t('admin.colName'), key: 'user_name' },
  { title: t('admin.colEmail'), key: 'email' },
  { title: t('admin.colRole'), key: 'role' },
  {
    title: t('admin.colChangeRole'),
    key: 'actions',
    render(row) {
      if (row.role === 'admin') return '—'
      return h(NSelect, {
        value: row.role,
        options: [
          { label: 'user', value: 'user' },
          { label: 'doctor', value: 'doctor' },
        ],
        style: { width: '120px' },
        onUpdateValue: async (v: Role) => {
          try {
            await updateUserRole(row.id, v as 'user' | 'doctor')
            message.success(t('admin.roleUpdated'))
            await load()
          } catch (e) {
            message.error(extractApiError(e))
          }
        },
      })
    },
  },
])

async function load() {
  loading.value = true
  try {
    rows.value = await listUsers()
  } catch (e) {
    message.error(extractApiError(e))
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <NCard :title="t('admin.usersTitle')">
    <template #header-extra>
      <NButton secondary :loading="loading" @click="load">{{ t('common.refresh') }}</NButton>
    </template>
    <NDataTable :columns="columns" :data="rows" :loading="loading" />
  </NCard>
</template>
