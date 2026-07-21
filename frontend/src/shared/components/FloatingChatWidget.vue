<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NIcon } from 'naive-ui'
import { ChatbubbleEllipsesOutline, CloseOutline } from '@vicons/ionicons5'
import { useAuthStore } from '@/stores/auth'
import { useAppI18n } from '@/i18n/useAppI18n'

const open = ref(false)
const router = useRouter()
const auth = useAuthStore()
const { t } = useAppI18n()

function toggle() {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login', query: { redirect: '/app/chat' } })
    return
  }
  open.value = !open.value
}

function goFull() {
  open.value = false
  router.push('/app/chat')
}
</script>

<template>
  <div class="fixed bottom-5 right-5 z-50 flex flex-col items-end gap-3">
    <div
      v-if="open"
      class="w-[min(380px,calc(100vw-2rem))] overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl shadow-teal-900/15"
    >
      <div class="flex items-center justify-between bg-[var(--sc-primary)] px-4 py-3 text-white">
        <span class="font-semibold">{{ t('chat.floatTitle') }}</span>
        <button type="button" class="cursor-pointer" :aria-label="t('chat.closeAria')" @click="open = false">
          <NIcon :component="CloseOutline" :size="20" />
        </button>
      </div>
      <div class="space-y-3 p-4 text-sm text-slate-600">
        <p>{{ t('chat.floatHint') }}</p>
        <NButton type="primary" block @click="goFull">{{ t('chat.floatOpen') }}</NButton>
      </div>
    </div>
    <NButton
      type="primary"
      circle
      size="large"
      class="!h-14 !w-14 shadow-lg"
      :aria-label="t('chat.openChatAria')"
      @click="toggle"
    >
      <template #icon>
        <NIcon :component="open ? CloseOutline : ChatbubbleEllipsesOutline" :size="24" />
      </template>
    </NButton>
  </div>
</template>
