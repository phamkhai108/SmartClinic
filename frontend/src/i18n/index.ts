import { createI18n } from 'vue-i18n'
import en from './locales/en'
import vi, { type MessageSchema } from './locales/vi'
import { getStoredLocale } from './localeStorage'

export type { MessageSchema }

const i18n = createI18n<[MessageSchema], 'vi' | 'en'>({
  legacy: false,
  locale: getStoredLocale(),
  fallbackLocale: 'en',
  messages: { vi, en },
})

export default i18n
