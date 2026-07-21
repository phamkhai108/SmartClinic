<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'
import {
  NButton,
  NCard,
  NFormItem,
  NInput,
  NList,
  NListItem,
  NSpin,
  NTag,
  NThing,
  useMessage,
} from 'naive-ui'
import { fetchSessionMessages, fetchSessions, sendChatStream } from '@/api/chat'
import { extractApiError, getStatus } from '@/api/http'
import { useAuthStore } from '@/stores/auth'
import type { ChatMessage, SessionInfo } from '@/shared/types/api'
import { useAppI18n } from '@/i18n/useAppI18n'
import { useValidationSchemas } from '@/shared/validation/schemas'

interface UiMessage extends ChatMessage {
  references?: string[]
  streaming?: boolean
}

const auth = useAuthStore()
const messageApi = useMessage()
const { t } = useAppI18n()
const { chatSchema } = useValidationSchemas()
function escapeHtml(text: string): string {
  return text
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
}

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
  highlight(str: string, lang: string): string {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return `<pre class="hljs"><code>${hljs.highlight(str, { language: lang, ignoreIllegals: true }).value}</code></pre>`
      } catch {
        /* fall through */
      }
    }
    return `<pre class="hljs"><code>${escapeHtml(str)}</code></pre>`
  },
})

const sessions = ref<SessionInfo[]>([])
const sessionId = ref<string>(crypto.randomUUID())
const messages = ref<UiMessage[]>([])
const loading = ref(false)
const listRef = ref<HTMLElement | null>(null)
let abortController: AbortController | null = null

const { handleSubmit, defineField, errors, isSubmitting, resetForm } = useForm({
  validationSchema: computed(() => toTypedSchema(chatSchema.value)),
  initialValues: { message: '' },
})
const [input] = defineField('message')

const rendered = computed(() =>
  messages.value.map((m) => ({
    ...m,
    html: m.role === 'assistant' ? md.render(m.content || '…') : '',
  })),
)

async function scrollToBottom() {
  await nextTick()
  listRef.value?.scrollTo({ top: listRef.value.scrollHeight, behavior: 'smooth' })
}

async function loadSessions() {
  if (!auth.user) return
  try {
    sessions.value = await fetchSessions(auth.user.user_id)
  } catch (e) {
    if (getStatus(e) !== 404) messageApi.warning(extractApiError(e))
  }
}

async function openSession(id: string) {
  if (loading.value) {
    abortController?.abort()
    loading.value = false
  }
  sessionId.value = id
  try {
    const rows = await fetchSessionMessages(id)
    messages.value = rows.map((r: { sender: string; message: string }) => ({
      role: r.sender === 'assistant' ? 'assistant' : 'user',
      content: r.message,
    }))
  } catch (e) {
    messageApi.error(extractApiError(e))
  }
}

function newChat() {
  if (loading.value) {
    abortController?.abort()
    loading.value = false
  }
  sessionId.value = crypto.randomUUID()
  messages.value = []
  resetForm()
}

const onSubmit = handleSubmit(async (values) => {
  if (!auth.user || loading.value) return
  const content = values.message.trim()
  messages.value.push({ role: 'user', content })
  resetForm()

  const assistantIndex = messages.value.length
  messages.value.push({
    role: 'assistant',
    content: '',
    references: [],
    streaming: true,
  })

  loading.value = true
  abortController = new AbortController()
  await scrollToBottom()

  let gotDone = false
  try {
    await sendChatStream(
      {
        user_id: auth.user.user_id,
        session_id: sessionId.value,
        messages: [{ role: 'user', content }],
      },
      {
        onToken(token) {
          const msg = messages.value[assistantIndex]
          if (!msg) return
          msg.content += token
          void scrollToBottom()
        },
        onReferences(refs) {
          const msg = messages.value[assistantIndex]
          if (!msg) return
          msg.references = refs
        },
        onDone(info) {
          gotDone = true
          const msg = messages.value[assistantIndex]
          if (!msg) return
          if (info.content) msg.content = info.content
          msg.streaming = false
          void loadSessions()
        },
        onError(err) {
          const msg = messages.value[assistantIndex]
          if (msg && !msg.content) {
            messages.value.splice(assistantIndex, 1)
          } else if (msg) {
            msg.streaming = false
          }
          messageApi.error(err.message)
        },
      },
      abortController.signal,
    )
    if (!gotDone) {
      const msg = messages.value[assistantIndex]
      if (msg?.streaming) {
        msg.streaming = false
        if (!msg.content) {
          messages.value.splice(assistantIndex, 1)
          messageApi.error(t('chat.noReply'))
        }
      }
    }
  } catch (e) {
    if ((e as Error).name === 'AbortError') return
    const msg = messages.value[assistantIndex]
    if (msg && !msg.content) messages.value.splice(assistantIndex, 1)
    else if (msg) msg.streaming = false
    messageApi.error(extractApiError(e))
  } finally {
    loading.value = false
    abortController = null
  }
})

onMounted(loadSessions)
onBeforeUnmount(() => abortController?.abort())
</script>

<template>
  <div class="grid gap-4 lg:grid-cols-[260px_1fr]">
    <NCard :title="t('chat.sessions')" size="small" class="h-[calc(100dvh-140px)] overflow-auto">
      <NButton block class="mb-3" secondary @click="newChat">{{ t('chat.newChat') }}</NButton>
      <NList hoverable clickable>
        <NListItem v-for="s in sessions" :key="s.session_id" @click="openSession(s.session_id)">
          <NThing :title="s.conversation_name" :description="new Date(s.latest_timestamp).toLocaleString()" />
        </NListItem>
      </NList>
      <p v-if="!sessions.length" class="text-sm text-slate-500">{{ t('chat.emptyHistory') }}</p>
    </NCard>

    <NCard class="flex h-[calc(100dvh-140px)] flex-col">
      <template #header>
        <span class="font-semibold">{{ t('chat.assistant') }}</span>
      </template>
      <div ref="listRef" class="flex-1 space-y-4 overflow-y-auto pr-1">
        <div
          v-for="(m, i) in rendered"
          :key="i"
          class="max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed"
          :class="m.role === 'user' ? 'ml-auto bg-[var(--sc-primary)] text-white' : 'bg-slate-100 text-slate-800'"
        >
          <div
            v-if="m.role === 'assistant'"
            class="chat-md prose prose-sm max-w-none prose-pre:bg-slate-800 prose-pre:text-slate-100 prose-code:before:content-none prose-code:after:content-none"
            v-html="m.html"
          />
          <div v-else class="whitespace-pre-wrap break-words">{{ m.content }}</div>
          <div v-if="m.references?.length" class="mt-3 flex flex-wrap gap-1 border-t border-slate-200/80 pt-2">
            <span class="mr-1 text-xs text-slate-500">{{ t('chat.sources') }}</span>
            <NTag v-for="ref in m.references" :key="ref" size="small" :bordered="false">{{ ref }}</NTag>
          </div>
        </div>
        <div v-if="loading" class="py-2"><NSpin size="small" /></div>
      </div>
      <form class="mt-4 flex items-end gap-2" @submit.prevent="onSubmit">
        <NFormItem
          class="mb-0 min-w-0 flex-1"
          :show-label="false"
          :show-feedback="Boolean(errors.message)"
          :validation-status="errors.message ? 'error' : undefined"
          :feedback="errors.message"
        >
          <NInput
            :value="input"
            type="textarea"
            :autosize="{ minRows: 1, maxRows: 4 }"
            :placeholder="t('chat.placeholder')"
            :disabled="loading"
            @update:value="(v: string) => (input = v)"
            @keydown.enter.exact.prevent="onSubmit"
          />
        </NFormItem>
        <NButton
          class="shrink-0"
          type="primary"
          attr-type="submit"
          :loading="isSubmitting || loading"
          :disabled="loading"
        >
          {{ t('chat.send') }}
        </NButton>
      </form>
    </NCard>
  </div>
</template>
