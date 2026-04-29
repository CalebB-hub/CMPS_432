import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const routes = [
  {
    path: '/home',
    redirect: '/',
  },
  {
    path: '/',
    name: 'home',
    component: () => import('../views/Home.vue'),
    meta: { requiresAuth: false, requiresGuest: true },
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('../views/Home.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/cloud',
    name: 'cloud',
    component: () => import('../views/cloud.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/cloud/add',
    name: 'cloud-add',
    component: () => import('../views/AddItemView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/cloud/edit/:id',
    name: 'cloud-edit',
    component: () => import('../views/EditItemView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('../views/SettingsView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/RegisterView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!auth.user && auth.token) {
    await auth.fetchMe()
  }
  if (to.meta.requiresGuest && auth.user) {
    return { name: 'cloud' }
  }
  if (to.meta.requiresAuth && !auth.user) {
    return { name: 'login' }
  }
})

export default router
