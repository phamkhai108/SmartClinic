import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { AppLocale } from './localeStorage'
import { setStoredLocale } from './localeStorage'
import type { MessageSchema } from './locales/vi'

export function useAppI18n() {
  const { t, locale, te } = useI18n<{ message: MessageSchema }, AppLocale>()

  const currentLocale = computed({
    get: () => locale.value as AppLocale,
    set: (value: AppLocale) => {
      locale.value = value
      setStoredLocale(value)
    },
  })

  function setLocale(value: AppLocale) {
    currentLocale.value = value
  }

  return { t, te, locale, currentLocale, setLocale }
}
