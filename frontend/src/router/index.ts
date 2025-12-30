import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/Login.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/onboarding',
      name: 'onboarding',
      component: () => import('@/views/Onboarding.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      component: () => import('@/views/Layout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'bilanco',
          component: () => import('@/views/Bilanco.vue')
        },
        // NEW: Giderler with nested routes (wildcard captures nested paths)
        {
          path: 'giderler',
          name: 'giderler',
          redirect: '/giderler/mal-alim'
        },
        {
          path: 'giderler/:path(.*)',  // Capture all nested paths (e.g., 'hizmet-alim/personel-iase')
          name: 'giderler-tab',
          component: () => import('@/views/Giderler.vue')
        },
        // NEW: Gelirler with nested routes
        {
          path: 'gelirler',
          name: 'gelirler',
          redirect: '/gelirler/kasa'
        },
        {
          path: 'gelirler/:path(.*)',  // Capture all nested paths
          name: 'gelirler-tab',
          component: () => import('@/views/Gelirler.vue')
        },
        // NEW: Ödemeler (Payments)
        {
          path: 'odemeler',
          name: 'odemeler',
          component: () => import('@/views/Odemeler.vue'),
          meta: {
            icon: '💳',
            title: 'Ödemeler',
            requiredPermission: null
          }
        },
        // Personnel (updated with optional tab)
        {
          path: 'personnel/:tab?',
          name: 'personnel',
          component: () => import('@/views/Personnel.vue')
        },
        // OLD: Legacy routes (redirect to new structure)
        {
          path: 'purchases',
          redirect: '/giderler/mal-alim'
        },
        {
          path: 'purchases/new',
          redirect: '/giderler/mal-alim'
        },
        {
          path: 'purchases/:id/edit',
          redirect: '/giderler/mal-alim'
        },
        {
          path: 'expenses',
          redirect: '/giderler/genel'
        },
        {
          path: 'expenses/new',
          redirect: '/giderler/genel'
        },
        {
          path: 'production',
          redirect: '/giderler/uretim'
        },
        {
          path: 'staff-meals',
          redirect: '/giderler/hizmet-alim/personel-iase'
        },
        {
          path: 'courier-expenses',
          redirect: '/giderler/hizmet-alim/kurye'
        },
        {
          path: 'sales',
          redirect: '/gelirler/kasa'
        },
        {
          path: 'kasa-farki',
          redirect: '/gelirler/kasa-farki'
        },
        // Admin routes (keep existing)
        {
          path: 'import',
          name: 'import-hub',
          component: () => import('@/views/ImportHub.vue'),
          meta: { requiresAuth: true }
        },
        {
          path: 'settings',
          name: 'settings',
          component: () => import('@/views/Settings.vue'),
          meta: { title: 'Sistem Ayarlari', requiresSuperAdmin: true }
        },
        {
          path: 'invitation-codes',
          name: 'invitation-codes',
          component: () => import('@/views/InvitationCodes.vue'),
          meta: { title: 'Davet Kodlari', requiresOwner: true }
        }
      ]
    }
  ]
})

router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth !== false && !authStore.isAuthenticated) {
    // Try to fetch user if we have a token
    if (authStore.token && !authStore.user) {
      await authStore.fetchUser()
    }

    if (!authStore.isAuthenticated) {
      return next('/login')
    }
  }

  if (to.path === '/login' && authStore.isAuthenticated) {
    return next('/')
  }

  next()
})

export default router
