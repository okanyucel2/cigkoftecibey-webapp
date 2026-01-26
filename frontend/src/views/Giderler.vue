<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import VerticalNav from '@/components/ui/VerticalNav.vue'
import type { NavItem } from '@/components/ui/VerticalNav.vue'

// Import existing views
import Purchases from './Purchases.vue'
import StaffMeals from './StaffMeals.vue'
import CourierExpenses from './CourierExpenses.vue'
import Production from './Production.vue'
import Expenses from './Expenses.vue'

const router = useRouter()
const route = useRoute()

// Navigation items
const navItems: NavItem[] = [
  {
    id: 'mal-alim',
    label: 'Mal Alımları',
    icon: '📦'
  },
  {
    id: 'hizmet-alim',
    label: 'Hizmet Alımları',
    icon: '🍽️',
    subItems: [
      { id: 'hizmet-alim/personel-iase', label: 'Personel İaşe' },
      { id: 'hizmet-alim/kurye', label: 'Kurye Hizmetleri' }
    ]
  },
  {
    id: 'uretim',
    label: 'Üretim',
    icon: '🥙'
  },
  {
    id: 'genel',
    label: 'Genel Giderler',
    icon: '📋'
  }
]

// Active tab with computed get/set
// Supports both:
// 1. New routes with meta.defaultPath (e.g., /expenses/courier → meta.defaultPath: 'hizmet-alim/kurye')
// 2. Legacy /giderler/xxx routes (backwards compatibility)
const activeTab = computed({
  get: () => {
    // First check for meta.defaultPath (new route structure)
    if (route.meta?.defaultPath) {
      return route.meta.defaultPath as string
    }
    // Fall back to legacy path parsing
    const path = route.path.replace('/giderler/', '')
    return path || 'mal-alim'
  },
  set: (value) => {
    // Map internal tab IDs to new routes
    const routeMap: Record<string, string> = {
      'mal-alim': '/operations/purchases',
      'uretim': '/operations/production',
      'genel': '/expenses',
      'hizmet-alim/kurye': '/expenses/courier',
      'hizmet-alim/personel-iase': '/personnel/meals'
    }
    router.push(routeMap[value] || `/giderler/${value}`)
  }
})

// Current view component
const currentView = computed(() => {
  switch (activeTab.value) {
    case 'mal-alim':
      return Purchases
    case 'hizmet-alim':  // Parent item - default to first sub-item
      return StaffMeals
    case 'hizmet-alim/personel-iase':
      return StaffMeals
    case 'hizmet-alim/kurye':
      return CourierExpenses
    case 'uretim':
      return Production
    case 'genel':
      return Expenses
    default:
      return Purchases
  }
})
</script>

<template>
  <div class="giderler-view">
    <div class="giderler-header">
      <h1 class="page-title">💸 Giderler</h1>
      <p class="page-description">Mal alımları, hizmet giderleri, üretim ve işletme giderleri</p>
    </div>

    <div class="giderler-content">
      <!-- Vertical Navigation -->
      <aside class="giderler-nav">
        <VerticalNav v-model="activeTab" :items="navItems" />
      </aside>

      <!-- Content Area -->
      <main class="giderler-main">
        <component :is="currentView" :key="activeTab" />
      </main>
    </div>
  </div>
</template>

<style scoped>
.giderler-view {
  min-height: 100%;
}

.giderler-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  font-family: 'font-display', sans-serif;
  color: #111827;
  margin: 0 0 8px 0;
}

.page-description {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.giderler-content {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 24px;
  align-items: start;
}

.giderler-nav {
  position: sticky;
  top: 0;
}

.giderler-main {
  min-width: 0;
}

@media (max-width: 1024px) {
  .giderler-content {
    grid-template-columns: 1fr;
  }

  .giderler-nav {
    position: static;
  }
}
</style>
