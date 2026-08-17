<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { NButton, NCard, NFormItem, NSelect, NUpload, NUploadDragger, type UploadFileInfo, useMessage } from 'naive-ui'
import { listUsers, uploadFile, waitForFileTerminalStatus } from '@/api/admin'
import { extractApiError } from '@/api/http'
import { useAuthStore } from '@/stores/auth'
import type { UserDTO } from '@/shared/types/api'
import { useAppI18n } from '@/i18n/useAppI18n'
import { useValidationSchemas, validateDocFile } from '@/shared/validation/schemas'

const auth = useAuthStore()
const message = useMessage()
const { t } = useAppI18n()
const { uploadMetaSchema } = useValidationSchemas()
const users = ref<UserDTO[]>([])
const file = ref<File | null>(null)
const fileError = ref<string | null>(null)
const loading = ref(false)
const processingHint = ref<string | null>(null)

const { handleSubmit, defineField, errors, isSubmitting } = useForm({
  validationSchema: computed(() => toTypedSchema(uploadMetaSchema.value)),
  initialValues: { userId: auth.user?.user_id || '' },
})
const [userId] = defineField('userId')

const userOptions = computed(() =>
  users.value.map((u) => ({
    label: `${u.user_name} (${u.email})`,
    value: u.id,
  })),
)

async function loadUsers() {
  try {
    users.value = await listUsers()
  } catch (e) {
    message.error(extractApiError(e))
  }
}

function onChange(options: { fileList: UploadFileInfo[] }) {
  file.value = options.fileList[0]?.file ?? null
  fileError.value = validateDocFile(file.value, t)
}

const onSubmit = handleSubmit(async (values) => {
  const err = validateDocFile(file.value, t)
  fileError.value = err
  if (err || !file.value) {
    message.warning(err || t('admin.needUserFile'))
    return
  }
  loading.value = true
  processingHint.value = null
  try {
    const accepted = await uploadFile(values.userId, file.value)
    processingHint.value = t('admin.processing', { name: accepted.file_name })
    message.info(t('admin.accepted', { name: accepted.file_name }))

    const final = await waitForFileTerminalStatus(accepted.id)
    if (final.status === 'success') {
      message.success(t('admin.uploaded', { name: final.file_name }))
    } else {
      message.error(t('admin.processFailed', { name: final.file_name }))
    }
  } catch (e) {
    message.error(extractApiError(e))
  } finally {
    loading.value = false
    processingHint.value = null
  }
})

onMounted(loadUsers)
</script>

<template>
  <NCard :title="t('admin.uploadTitle')" class="max-w-xl">
    <form @submit.prevent="onSubmit">
      <NFormItem
        :label="t('admin.ownerUser')"
        :validation-status="errors.userId ? 'error' : undefined"
        :feedback="errors.userId"
      >
        <NSelect
          :value="userId"
          :options="userOptions"
          filterable
          :placeholder="t('admin.selectUser')"
          @update:value="(v: string) => (userId = v)"
        />
      </NFormItem>
      <NFormItem :validation-status="fileError ? 'error' : undefined" :feedback="fileError || undefined">
        <NUpload accept=".pdf,.docx,.xlsx,.pptx,.md,.markdown" :max="1" :default-upload="false" @change="onChange">
          <NUploadDragger>
            <div class="px-4 py-8 text-center text-sm text-slate-600">{{ t('admin.dropHint') }}</div>
          </NUploadDragger>
        </NUpload>
      </NFormItem>
      <p v-if="processingHint" class="mb-3 text-sm text-slate-600">{{ processingHint }}</p>
      <NButton type="primary" attr-type="submit" :loading="isSubmitting || loading">{{ t('admin.uploadAction') }}</NButton>
    </form>
  </NCard>
</template>
