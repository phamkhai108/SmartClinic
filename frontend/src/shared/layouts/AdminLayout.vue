<script setup lang="ts">
import { h, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NLayout, NLayoutHeader, NLayoutSider, NMenu, NButton, NIcon, NSpace, type MenuOption } from 'naive-ui'
import {
  PeopleOutline,
  DocumentsOutline,
  CloudUploadOutline,
  GridOutline,
  ArrowBackOutline,
} from '@vicons/ionicons5'
import { useAuthStore } from '@/stores/auth'
import LocaleSwitch from '@/shared/components/LocaleSwitch.vue'
import { useAppI18n } from '@/i18n/useAppI18n'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const { t } = useAppI18n()

function icon(comp: typeof GridOutline) {
  return () => h(NIcon, null, { default: () => h(comp) })
}

const options = computed<MenuOption[]>(() => [
  { label: t('admin.title'), key: '/admin', icon: icon(GridOutline) },
  { label: t('nav.users'), key: '/admin/users', icon: icon(PeopleOutline) },
  { label: t('nav.files'), key: '/admin/files', icon: icon(DocumentsOutline) },
  { label: t('nav.upload'), key: '/admin/upload', icon: icon(CloudUploadOutline) },
])

const activeKey = computed(() => route.path)
</script>

<template>
  <NLayout has-sider class="min-h-dvh">
    <NLayoutSider bordered :width="240" class="!bg-slate-900">
      <div class="brand-font px-4 py-5 text-xl font-bold text-teal-300">{{ t('nav.admin') }}</div>
      <NMenu :value="activeKey" :options="options" inverted @update:value="(k: string) => router.push(k)" />
    </NLayoutSider>
    <NLayout>
      <NLayoutHeader bordered class="flex items-center justify-between bg-white px-4 py-3">
        <p class="font-semibold">{{ auth.user?.email }}</p>
        <NSpace align="center">
          <LocaleSwitch />
          <NButton quaternary @click="router.push('/')">
            <template #icon><NIcon :component="ArrowBackOutline" /></template>
            {{ t('nav.backHome') }}
          </NButton>
        </NSpace>
      </NLayoutHeader>
      <div class="p-4 md:p-6">
        <RouterView />
      </div>
    </NLayout>
  </NLayout>
</template>
