<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import VerticalNav from '@/components/ui/VerticalNav.vue'
import type { NavItem } from '@/components/ui/VerticalNav.vue'

// Import existing views
import UnifiedSales from './UnifiedSales.vue'
import CashDifference from './CashDifference.vue'

const router = useRouter()
const route = useRoute()

// Navigation items
const navItems: NavItem[] = [
  {
    id: 'kasa',
    label: 'Kasa Hareketleri',
    icon: '💰'
  },
  {
    id: 'kasa-farki',
    label: 'Kasa Farkı',
    icon: '💵'
  }
]

// Active tab with bidirectional binding to route
const activeTab = computed({
  get: () => {
    const path = route.path.replace('/gelirler/', '')
    return path || 'kasa'
  },
  set: (value) => {
    router.push(`/gelirler/${value}`)
  }
})

// Current view component based on active tab
const currentView = computed(() => {
  switch (activeTab.value) {
    case 'kasa':
      return UnifiedSales
    case 'kasa-farki':
      return CashDifference
    default:
      return UnifiedSales
  }
})
</script>

<template>
  <div class="gelirler-view">
    <div class="gelirler-header">
      <h1 class="page-title">💰 Gelirler</h1>
      <p class="page-description">Kasa hareketleri ve kasa farkı analizi</p>
    </div>

    <div class="gelirler-content">
      <!-- Vertical Navigation -->
      <aside class="gelirler-nav">
        <VerticalNav v-model="activeTab" :items="navItems" />
      </aside>

      <!-- Content Area -->
      <main class="gelirler-main">
        <component :is="currentView" :key="activeTab" />
      </main>
    </div>
  </div>
</template>

<style scoped>
.gelirler-view {
  min-height: 100%;
}

.gelirler-header {
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

.gelirler-content {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 24px;
  align-items: start;
}

.gelirler-nav {
  position: sticky;
  top: 0;
}

.gelirler-main {
  min-width: 0;
}

@media (max-width: 1024px) {
  .gelirler-content {
    grid-template-columns: 1fr;
  }

  .gelirler-nav {
    position: static;
  }
}
</style>
