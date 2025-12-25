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
        {
          path: 'sales',
          name: 'sales',
          component: () => import('@/views/UnifiedSales.vue')
        },
        {
          path: 'purchases',
          name: 'purchases',
          component: () => import('@/views/Purchases.vue')
        },
        {
          path: 'purchases/new',
          name: 'purchase-new',
          component: () => import('@/views/PurchaseForm.vue')
        },
        {
          path: 'purchases/:id/edit',
          name: 'purchase-edit',
          component: () => import('@/views/PurchaseForm.vue'),
          props: true
        },
        {
          path: 'expenses',
          name: 'expenses',
          component: () => import('@/views/Expenses.vue')
        },
        {
          path: 'expenses/new',
          name: 'expense-form',
          component: () => import('@/views/ExpenseForm.vue')
        },
        {
          path: 'production',
          name: 'production',
          component: () => import('@/views/Production.vue')
        },
        {
          path: 'staff-meals',
          name: 'staff-meals',
          component: () => import('@/views/StaffMeals.vue')
        },
        {
          path: 'personnel',
          name: 'personnel',
          component: () => import('@/views/Personnel.vue')
        },
        {
          path: 'courier-expenses',
          name: 'courier-expenses',
          component: () => import('@/views/CourierExpenses.vue')
        },
        {
          path: 'kasa-farki',
          name: 'CashDifference',
          component: () => import('@/views/CashDifference.vue')
        },
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
