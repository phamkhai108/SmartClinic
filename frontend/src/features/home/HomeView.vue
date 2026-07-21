<script setup lang="ts">
import { computed } from 'vue'
import { NButton, NGrid, NGi } from 'naive-ui'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAppI18n } from '@/i18n/useAppI18n'

const router = useRouter()
const auth = useAuthStore()
const { t } = useAppI18n()

const services = computed(() => [
  { title: t('home.services.chat.title'), desc: t('home.services.chat.desc'), to: '/app/chat' },
  { title: t('home.services.heart.title'), desc: t('home.services.heart.desc'), to: '/app/predict/heart' },
  { title: t('home.services.lung.title'), desc: t('home.services.lung.desc'), to: '/app/predict/lung' },
  { title: t('home.services.breast.title'), desc: t('home.services.breast.desc'), to: '/app/predict/breast' },
  { title: t('home.services.brain.title'), desc: t('home.services.brain.desc'), to: '/app/predict/brain' },
])

const gallery = [
  { src: '/images/UngThuPhoi.jpg', alt: 'lung' },
  { src: '/images/ungthuvu.jpg', alt: 'breast' },
  { src: '/images/XuongKhop.jpg', alt: 'ortho' },
  { src: '/images/fullwidth.jpg', alt: 'clinic' },
]

const testimonials = computed(() => [
  { quote: t('home.testimonials.t1.quote'), name: t('home.testimonials.t1.name'), role: t('home.testimonials.t1.role') },
  { quote: t('home.testimonials.t2.quote'), name: t('home.testimonials.t2.name'), role: t('home.testimonials.t2.role') },
  { quote: t('home.testimonials.t3.quote'), name: t('home.testimonials.t3.name'), role: t('home.testimonials.t3.role') },
])

const panelItems = computed(() => [
  t('home.panelItems.jwt'),
  t('home.panelItems.rag'),
  t('home.panelItems.predict'),
  t('home.panelItems.admin'),
])
</script>

<template>
  <section class="relative overflow-hidden">
    <div class="mx-auto grid max-w-6xl gap-10 px-4 py-16 md:grid-cols-2 md:items-center md:px-6 md:py-24">
      <div class="space-y-6">
        <p class="brand-font text-5xl font-bold leading-tight text-[var(--sc-primary-deep)] md:text-6xl">
          {{ t('common.brand') }}
        </p>
        <h1 class="text-2xl font-semibold tracking-tight text-slate-800 md:text-3xl">{{ t('home.headline') }}</h1>
        <p class="max-w-xl text-base leading-relaxed text-slate-600">{{ t('home.lead') }}</p>
        <div class="flex flex-wrap gap-3">
          <NButton type="primary" size="large" @click="router.push(auth.isAuthenticated ? '/app/chat' : '/login')">
            {{ t('home.ctaStart') }}
          </NButton>
          <NButton size="large" secondary @click="router.push('/about')">{{ t('home.ctaAbout') }}</NButton>
        </div>
      </div>
      <div
        class="relative min-h-[280px] overflow-hidden rounded-[28px] bg-[linear-gradient(145deg,#0f766e_0%,#0369a1_55%,#0f172a_100%)] p-8 text-white shadow-xl shadow-teal-900/20"
      >
        <div class="absolute inset-0 opacity-30 [background:radial-gradient(circle_at_20%_20%,white,transparent_40%)]" />
        <div class="relative space-y-4">
          <p class="brand-font text-3xl font-semibold">{{ t('home.panelTitle') }}</p>
          <ul class="space-y-3 text-sm text-teal-50/95">
            <li v-for="item in panelItems" :key="item">{{ item }}</li>
          </ul>
        </div>
      </div>
    </div>
  </section>

  <section class="mx-auto max-w-6xl px-4 pb-16 md:px-6">
    <h2 class="mb-2 text-2xl font-semibold text-slate-800">{{ t('home.servicesTitle') }}</h2>
    <p class="mb-8 max-w-2xl text-slate-600">{{ t('home.servicesLead') }}</p>
    <NGrid cols="1 s:2 l:3" :x-gap="16" :y-gap="16" responsive="screen">
      <NGi v-for="item in services" :key="item.title">
        <button
          class="h-full w-full cursor-pointer rounded-2xl border border-slate-200/80 bg-white/80 p-5 text-left shadow-sm transition duration-200 hover:-translate-y-1 hover:border-teal-300 hover:shadow-md"
          @click="router.push(item.to)"
        >
          <h3 class="mb-2 text-lg font-semibold text-[var(--sc-primary-deep)]">{{ item.title }}</h3>
          <p class="text-sm leading-relaxed text-slate-600">{{ item.desc }}</p>
        </button>
      </NGi>
    </NGrid>
  </section>

  <section class="mx-auto max-w-6xl px-4 pb-16 md:px-6">
    <h2 class="mb-6 text-2xl font-semibold text-slate-800">{{ t('home.galleryTitle') }}</h2>
    <div class="grid grid-cols-2 gap-3 md:grid-cols-4">
      <img
        v-for="img in gallery"
        :key="img.src"
        :src="img.src"
        :alt="img.alt"
        width="400"
        height="280"
        class="h-36 w-full rounded-xl object-cover md:h-44"
        loading="lazy"
      />
    </div>
  </section>

  <section class="mx-auto max-w-6xl px-4 pb-20 md:px-6">
    <h2 class="mb-6 text-2xl font-semibold text-slate-800">{{ t('home.testimonialsTitle') }}</h2>
    <div class="grid gap-4 md:grid-cols-3">
      <blockquote
        v-for="item in testimonials"
        :key="item.name"
        class="rounded-2xl border border-slate-200/80 bg-white/70 p-5"
      >
        <p class="mb-4 text-sm leading-relaxed text-slate-700">“{{ item.quote }}”</p>
        <footer class="text-sm font-semibold text-[var(--sc-primary-deep)]">
          {{ item.name }} <span class="font-normal text-slate-500">· {{ item.role }}</span>
        </footer>
      </blockquote>
    </div>
  </section>
</template>
