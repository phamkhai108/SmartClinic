import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { Role } from '@/shared/types/api'
import i18n from '@/i18n'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    roles?: Role[]
    titleKey?: string
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/shared/layouts/PublicLayout.vue'),
    children: [
      { path: '', name: 'home', component: () => import('@/features/home/HomeView.vue'), meta: { titleKey: 'titles.home' } },
      { path: 'about', name: 'about', component: () => import('@/features/home/AboutView.vue'), meta: { titleKey: 'titles.about' } },
      { path: 'login', name: 'login', component: () => import('@/features/auth/LoginView.vue'), meta: { titleKey: 'titles.login' } },
      { path: 'register', name: 'register', component: () => import('@/features/auth/RegisterView.vue'), meta: { titleKey: 'titles.register' } },
    ],
  },
  {
    path: '/app',
    component: () => import('@/shared/layouts/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: 'chat', name: 'chat', component: () => import('@/features/chat/ChatView.vue'), meta: { requiresAuth: true, titleKey: 'titles.chat' } },
      { path: 'predict/heart', name: 'predict-heart', component: () => import('@/features/predict/HeartView.vue'), meta: { requiresAuth: true, titleKey: 'titles.predictHeart' } },
      { path: 'predict/heart/result', name: 'predict-heart-result', component: () => import('@/features/predict/HeartResultView.vue'), meta: { requiresAuth: true, titleKey: 'titles.resultHeart' } },
      { path: 'predict/lung', name: 'predict-lung', component: () => import('@/features/predict/LungView.vue'), meta: { requiresAuth: true, titleKey: 'titles.predictLung' } },
      { path: 'predict/lung/result', name: 'predict-lung-result', component: () => import('@/features/predict/LungResultView.vue'), meta: { requiresAuth: true, titleKey: 'titles.resultLung' } },
      { path: 'predict/breast', name: 'predict-breast', component: () => import('@/features/predict/BreastView.vue'), meta: { requiresAuth: true, titleKey: 'titles.predictBreast' } },
      { path: 'predict/breast/result', name: 'predict-breast-result', component: () => import('@/features/predict/BreastResultView.vue'), meta: { requiresAuth: true, titleKey: 'titles.resultBreast' } },
      { path: 'predict/brain', name: 'predict-brain', component: () => import('@/features/predict/BrainView.vue'), meta: { requiresAuth: true, roles: ['doctor', 'admin'], titleKey: 'titles.predictBrain' } },
      { path: 'predict/brain/result', name: 'predict-brain-result', component: () => import('@/features/predict/BrainResultView.vue'), meta: { requiresAuth: true, roles: ['doctor', 'admin'], titleKey: 'titles.resultBrain' } },
    ],
  },
  {
    path: '/admin',
    component: () => import('@/shared/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
    children: [
      { path: '', name: 'admin', component: () => import('@/features/admin/AdminHomeView.vue'), meta: { titleKey: 'titles.admin' } },
      { path: 'users', name: 'admin-users', component: () => import('@/features/admin/UsersView.vue'), meta: { titleKey: 'titles.adminUsers' } },
      { path: 'files', name: 'admin-files', component: () => import('@/features/admin/FilesView.vue'), meta: { titleKey: 'titles.adminFiles' } },
      { path: 'upload', name: 'admin-upload', component: () => import('@/features/admin/UploadView.vue'), meta: { titleKey: 'titles.adminUpload' } },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  const titleKey = to.meta.titleKey || to.matched.map((r) => r.meta.titleKey).find(Boolean)
  if (titleKey) {
    document.title = `${i18n.global.t(titleKey)} · SmartClinic`
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  const roles = to.matched.flatMap((r) => r.meta.roles || [])
  if (roles.length && (!auth.user || !roles.includes(auth.user.role))) {
    return { name: 'home' }
  }

  if ((to.name === 'login' || to.name === 'register') && auth.isAuthenticated) {
    return { name: 'home' }
  }

  return true
})

export default router
