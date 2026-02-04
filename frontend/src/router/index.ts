import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAuth } from '@/composables/useAuth'

/**
 * Phase 1 Router Structure (Platform Evolution Roadmap)
 * =====================================================
 *
 * Target: 6 main navigation groups
 * - / (Bilanço) - Dashboard
 * - /import - Central Import Hub
 * - /sales - Ciro (Sales)
 * - /operations - Operasyon (Production & Purchases)
 * - /personnel - Personel
 * - /expenses - Giderler
 * - /settings - Admin settings
 */

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
        // ==========================================
        // MAIN ROUTES (Phase 1 Target Structure)
        // ==========================================

        // 📊 Bilanço (Dashboard)
        {
          path: '',
          name: 'bilanco',
          component: () => import('@/views/Bilanco.vue')
        },

        // 📊 Dashboard V2 (Command Center)
        {
          path: 'dashboard-v2',
          name: 'dashboard-v2',
          component: () => import('@/views/DashboardV2.vue'),
          meta: { title: 'Dashboard V2' }
        },

        // 📥 İçe Aktar (Import Hub)
        {
          path: 'import',
          name: 'import-hub',
          component: () => import('@/views/ImportHub.vue'),
          meta: { requiresAuth: true }
        },

        // 💰 Ciro (Sales)
        {
          path: 'sales',
          name: 'sales',
          component: () => import('@/views/Gelirler.vue'),
          meta: { defaultPath: 'kasa' }
        },
        {
          path: 'sales/verify',
          name: 'sales-verify',
          component: () => import('@/views/Gelirler.vue'),
          meta: { defaultPath: 'kasa-farki' }
        },

        // 🏭 Operasyon (Operations)
        {
          path: 'operations',
          name: 'operations',
          redirect: '/operations/production'
        },
        {
          path: 'operations/production',
          name: 'operations-production',
          component: () => import('@/views/Giderler.vue'),
          meta: { defaultPath: 'uretim' }
        },
        {
          path: 'operations/purchases',
          name: 'operations-purchases',
          component: () => import('@/views/Giderler.vue'),
          meta: { defaultPath: 'mal-alim' }
        },

        // 👥 Personel (Personnel)
        {
          path: 'personnel',
          name: 'personnel',
          component: () => import('@/views/Personnel.vue')
        },
        {
          path: 'personnel/meals',
          name: 'personnel-meals',
          component: () => import('@/views/Giderler.vue'),
          meta: { defaultPath: 'hizmet-alim/personel-iase' }
        },
        {
          path: 'personnel/payroll',
          name: 'personnel-payroll',
          component: () => import('@/views/Personnel.vue'),
          meta: { defaultTab: 'payroll' }
        },

        // 💸 Giderler (Expenses)
        {
          path: 'expenses',
          name: 'expenses',
          component: () => import('@/views/Giderler.vue'),
          meta: { defaultPath: 'genel' }
        },
        {
          path: 'expenses/courier',
          name: 'expenses-courier',
          component: () => import('@/views/Giderler.vue'),
          meta: { defaultPath: 'hizmet-alim/kurye' }
        },

        // 📈 Analitik (Analytics)
        {
          path: 'analytics/daily-sales',
          name: 'analytics-daily-sales',
          component: () => import('@/views/analytics/DailySalesDashboard.vue'),
          meta: { title: 'Gunluk Satis Analizi' }
        },

        // 🍽️ Menu Yonetimi
        {
          path: 'menu',
          name: 'menu-management',
          component: () => import('@/views/MenuManagement.vue'),
          meta: { title: 'Menu Yonetimi' }
        },

        // ⚙️ Ayarlar (Settings) - Admin only
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
        },

        // ==========================================
        // LEGACY ROUTES (Redirects to new structure)
        // ==========================================

        // Gelirler → Sales
        {
          path: 'gelirler',
          redirect: '/sales'
        },
        {
          path: 'gelirler/kasa',
          redirect: '/sales'
        },
        {
          path: 'gelirler/kasa-farki',
          redirect: '/sales/verify'
        },
        {
          path: 'gelirler/:path(.*)',
          redirect: '/sales'
        },

        // Giderler → Operations/Expenses
        {
          path: 'giderler',
          redirect: '/operations/purchases'
        },
        {
          path: 'giderler/mal-alim',
          redirect: '/operations/purchases'
        },
        {
          path: 'giderler/uretim',
          redirect: '/operations/production'
        },
        {
          path: 'giderler/genel',
          redirect: '/expenses'
        },
        {
          path: 'giderler/hizmet-alim/kurye',
          redirect: '/expenses/courier'
        },
        {
          path: 'giderler/hizmet-alim/personel-iase',
          redirect: '/personnel/meals'
        },

        // Other legacy routes
        {
          path: 'purchases',
          redirect: '/operations/purchases'
        },
        {
          path: 'purchases/new',
          redirect: '/operations/purchases'
        },
        {
          path: 'purchases/:id/edit',
          redirect: '/operations/purchases'
        },
        {
          path: 'production',
          redirect: '/operations/production'
        },
        {
          path: 'expenses-old',
          redirect: '/expenses'
        },
        {
          path: 'staff-meals',
          redirect: '/personnel/meals'
        },
        {
          path: 'courier-expenses',
          redirect: '/expenses/courier'
        },
        {
          path: 'kasa-farki',
          redirect: '/sales/verify'
        },

        // Ödemeler (keeping for backward compatibility)
        {
          path: 'odemeler',
          name: 'odemeler',
          component: () => import('@/views/Odemeler.vue'),
          meta: {
            icon: '💳',
            title: 'Ödemeler',
            requiredPermission: null
          }
        }
      ]
    }
  ]
})

/**
 * Global navigation guard for authentication and authorization
 */
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()
  const auth = useAuth()

  // Skip auth check for public routes
  if (to.meta.requiresAuth === false) {
    // If already authenticated, redirect to home
    if (authStore.isAuthenticated) {
      return next('/')
    }
    return next()
  }

  // Protected route - check authentication
  if (!authStore.isAuthenticated) {
    // Try to restore session from storage
    if (authStore.token && !authStore.user) {
      try {
        await authStore.fetchUser()
      } catch (err) {
        // Session is invalid
        authStore.logout()
        return next('/login')
      }
    }

    // Still not authenticated
    if (!authStore.isAuthenticated) {
      return next('/login')
    }
  }

  // Check permission requirements
  if (to.meta.requiresSuperAdmin && !authStore.isSuperAdmin) {
    return next('/')
  }

  if (to.meta.requiresOwner && authStore.user?.role !== 'owner') {
    return next('/')
  }

  // Validate token with server (periodic check)
  if (authStore.isAuthenticated) {
    try {
      // Check if token is still valid
      if (!auth.isTokenValid()) {
        // Token expired
        await authStore.logout()
        return next('/login')
      }

      // Refresh user info if needed
      if (!authStore.user) {
        await authStore.fetchUser()
      }
    } catch (err) {
      console.error('Auth validation error:', err)
      authStore.logout()
      return next('/login')
    }
  }

  next()
})

/**
 * Navigation guard for handling token expiry warnings
 */
router.afterEach((to, _from) => {
  // Don't warn on login/onboarding pages
  if (to.path === '/login' || to.path === '/onboarding') {
    return
  }

  const auth = useAuth()

  // Show warning if token expiring soon
  if (auth.isTokenExpiringSoon.value && !auth.error.value) {
    // Warning is already shown via composable
  }
})

export default router
