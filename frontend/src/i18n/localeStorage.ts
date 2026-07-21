export const LOCALE_KEY = 'smartclinic_locale'
export type AppLocale = 'vi' | 'en'

export function getStoredLocale(): AppLocale {
  const raw = localStorage.getItem(LOCALE_KEY)
  return raw === 'en' ? 'en' : 'vi'
}

export function setStoredLocale(locale: AppLocale) {
  localStorage.setItem(LOCALE_KEY, locale)
}
