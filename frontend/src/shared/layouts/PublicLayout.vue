<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NDrawer, NDrawerContent, NSpace } from 'naive-ui'
import { useAuthStore } from '@/stores/auth'
import FloatingChatWidget from '@/shared/components/FloatingChatWidget.vue'
import LocaleSwitch from '@/shared/components/LocaleSwitch.vue'
import { useAppI18n } from '@/i18n/useAppI18n'

const auth = useAuthStore()
const router = useRouter()
const { t } = useAppI18n()
const mobileOpen = ref(false)
const isAuthed = computed(() => auth.isAuthenticated)

function logout() {
  auth.logout()
  router.push({ name: 'home' })
}

function go(path: string) {
  mobileOpen.value = false
  router.push(path)
}
</script>

<template>
  <div class="min-h-dvh flex flex-col">
    <header class="sticky top-0 z-40 border-b border-slate-200/70 bg-white/80 backdrop-blur-md">
      <div class="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3 md:px-6">
        <RouterLink to="/" class="brand-font text-2xl font-bold tracking-tight text-[var(--sc-primary-deep)]">
          {{ t('common.brand') }}
        </RouterLink>
        <nav class="hidden items-center gap-6 text-sm font-medium text-slate-600 md:flex">
          <RouterLink to="/" class="hover:text-[var(--sc-primary)]">{{ t('nav.home') }}</RouterLink>
          <RouterLink to="/about" class="hover:text-[var(--sc-primary)]">{{ t('nav.about') }}</RouterLink>
          <RouterLink v-if="isAuthed" to="/app/chat" class="hover:text-[var(--sc-primary)]">{{ t('nav.chat') }}</RouterLink>
          <RouterLink v-if="auth.hasRole('admin')" to="/admin" class="hover:text-[var(--sc-primary)]">{{ t('nav.admin') }}</RouterLink>
        </nav>
        <NSpace align="center">
          <LocaleSwitch />
          <NButton class="md:!hidden" quaternary @click="mobileOpen = true">{{ t('nav.menu') }}</NButton>
          <template v-if="!isAuthed">
            <NButton quaternary @click="router.push('/login')">{{ t('nav.login') }}</NButton>
            <NButton type="primary" @click="router.push('/register')">{{ t('nav.register') }}</NButton>
          </template>
          <template v-else>
            <span class="hidden text-sm text-slate-500 sm:inline">{{ auth.user?.user_name }}</span>
            <NButton quaternary @click="logout">{{ t('common.logout') }}</NButton>
          </template>
        </NSpace>
      </div>
    </header>

    <NDrawer v-model:show="mobileOpen" placement="right" :width="280">
      <NDrawerContent :title="t('nav.menu')" closable>
        <div class="flex flex-col gap-3 text-sm font-medium">
          <button class="cursor-pointer text-left" type="button" @click="go('/')">{{ t('nav.home') }}</button>
          <button class="cursor-pointer text-left" type="button" @click="go('/about')">{{ t('nav.about') }}</button>
          <button v-if="isAuthed" class="cursor-pointer text-left" type="button" @click="go('/app/chat')">{{ t('nav.chat') }}</button>
          <button v-if="auth.hasRole('admin')" class="cursor-pointer text-left" type="button" @click="go('/admin')">{{ t('nav.admin') }}</button>
        </div>
      </NDrawerContent>
    </NDrawer>

    <main class="flex-1">
      <RouterView v-slot="{ Component }">
        <Transition name="page" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </main>
    <footer class="border-t border-slate-200/80 bg-white/60 py-8 text-center text-sm text-slate-500">
      © {{ new Date().getFullYear() }} {{ t('common.brand') }} — {{ t('footer.note') }}
    </footer>
    <FloatingChatWidget />
  </div>
</template>
