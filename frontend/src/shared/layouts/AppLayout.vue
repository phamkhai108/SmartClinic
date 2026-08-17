<script setup lang="ts">
import { h, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NLayout,
  NLayoutHeader,
  NLayoutSider,
  NMenu,
  NButton,
  NIcon,
  NSpace,
  type MenuOption,
} from 'naive-ui'
import {
  ChatbubbleEllipsesOutline,
  HeartOutline,
  LeafOutline,
  ScanOutline,
  HomeOutline,
  LogOutOutline,
  FemaleOutline,
  GridOutline,
} from '@vicons/ionicons5'
import { useAuthStore } from '@/stores/auth'
import LocaleSwitch from '@/shared/components/LocaleSwitch.vue'
import { useAppI18n } from '@/i18n/useAppI18n'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const { t } = useAppI18n()

function icon(comp: typeof HomeOutline) {
  return () => h(NIcon, null, { default: () => h(comp) })
}

const menuOptions = computed<MenuOption[]>(() => {
  const items: MenuOption[] = [
    { label: t('nav.home'), key: '/', icon: icon(HomeOutline) },
    { label: t('nav.chat'), key: '/app/chat', icon: icon(ChatbubbleEllipsesOutline) },
    { label: t('nav.heart'), key: '/app/predict/heart', icon: icon(HeartOutline) },
    { label: t('nav.lung'), key: '/app/predict/lung', icon: icon(LeafOutline) },
    { label: t('nav.breast'), key: '/app/predict/breast', icon: icon(FemaleOutline) },
  ]
  if (auth.hasRole('doctor', 'admin')) {
    items.push({ label: t('nav.brain'), key: '/app/predict/brain', icon: icon(ScanOutline) })
  }
  if (auth.hasRole('admin')) {
    items.push({ label: t('nav.admin'), key: '/admin', icon: icon(GridOutline) })
  }
  return items
})

const activeKey = computed(() => {
  if (route.path.includes('/result')) return route.path.replace(/\/result$/, '')
  return route.path
})

function onUpdate(key: string) {
  router.push(key)
}

function logout() {
  auth.logout()
  router.push('/')
}
</script>

<template>
  <NLayout has-sider class="min-h-dvh">
    <NLayoutSider bordered collapse-mode="width" :collapsed-width="64" :width="240" show-trigger class="!bg-white">
      <div class="brand-font px-4 py-5 text-xl font-bold text-[var(--sc-primary-deep)]">
        {{ t('common.brand') }}
      </div>
      <NMenu :value="activeKey" :options="menuOptions" @update:value="onUpdate" />
    </NLayoutSider>
    <NLayout>
      <NLayoutHeader bordered class="flex items-center justify-between bg-white/90 px-4 py-3 backdrop-blur">
        <div>
          <p class="text-sm text-slate-500">{{ t('auth.hello') }}</p>
          <p class="font-semibold">{{ auth.user?.user_name }} · {{ auth.user?.role }}</p>
        </div>
        <NSpace align="center">
          <LocaleSwitch />
          <NButton quaternary @click="logout">
            <template #icon><NIcon :component="LogOutOutline" /></template>
            {{ t('common.logout') }}
          </NButton>
        </NSpace>
      </NLayoutHeader>
      <div class="p-4 md:p-6">
        <RouterView v-slot="{ Component, route }">
          <Transition name="page" mode="out-in">
            <div :key="route.fullPath">
              <component :is="Component" />
            </div>
          </Transition>
        </RouterView>
      </div>
    </NLayout>
  </NLayout>
</template>
