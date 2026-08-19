<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NCard, NFormItem, NUpload, type UploadFileInfo, useMessage } from 'naive-ui'
import { predictBrain } from '@/api/predict'
import { extractApiError } from '@/api/http'
import { useAppI18n } from '@/i18n/useAppI18n'
import { validateImageFile } from '@/shared/validation/schemas'
import { savePredictResult } from './resultStorage'

const router = useRouter()
const message = useMessage()
const { t } = useAppI18n()
const loading = ref(false)
const file = ref<File | null>(null)
const preview = ref<string | null>(null)
const fileError = ref<string | null>(null)

function onChange(options: { fileList: UploadFileInfo[] }) {
  if (preview.value?.startsWith('blob:')) URL.revokeObjectURL(preview.value)
  const raw = options.fileList[0]?.file ?? null
  file.value = raw
  preview.value = raw ? URL.createObjectURL(raw) : null
  fileError.value = validateImageFile(raw, t)
}

async function submit() {
  const err = validateImageFile(file.value, t)
  fileError.value = err
  if (err || !file.value) {
    message.warning(err || t('predict.chooseImageWarn'))
    return
  }
  loading.value = true
  try {
    const res = await predictBrain(file.value)
    savePredictResult({
      kind: 'brain',
      prediction: res.prediction,
      message: res.message,
      predicted_class: res.predicted_class,
      confidence: res.confidence,
      imagePreview: preview.value || undefined,
      retryRoute: '/app/predict/brain',
    })
    await router.push('/app/predict/brain/result')
  } catch (e) {
    message.error(extractApiError(e))
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-3xl">
    <NCard :title="t('predict.brainTitle')">
      <NFormItem :validation-status="fileError ? 'error' : undefined" :feedback="fileError || undefined">
        <NUpload accept=".jpg,.jpeg,.png" :max="1" :default-upload="false" @change="onChange">
          <NButton>{{ t('predict.chooseImage') }}</NButton>
        </NUpload>
      </NFormItem>
      <img v-if="preview" :src="preview" alt="MRI preview" class="mt-4 max-h-72 rounded-xl object-contain" />
      <NButton class="mt-4" type="primary" :loading="loading" @click="submit">{{ t('predict.classifyAction') }}</NButton>
    </NCard>
  </div>
</template>
