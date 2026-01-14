<script setup lang="ts">
import { ref, watch, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import VerticalNav, { type NavItem } from '@/components/ui/VerticalNav.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// Mobile breakpoint (lg = 1024px in Tailwind)
const MOBILE_BREAKPOINT = 1024

// Start closed on mobile, open on desktop
const sidebarOpen = ref(window.innerWidth >= MOBILE_BREAKPOINT)
const branchSelectorOpen = ref(false)

// Close sidebar on mobile when route changes
watch(() => route.path, () => {
  if (window.innerWidth < MOBILE_BREAKPOINT) {
    sidebarOpen.value = false
  }
})

// Handle window resize - close sidebar if resizing to mobile
function handleResize() {
  if (window.innerWidth < MOBILE_BREAKPOINT) {
    sidebarOpen.value = false
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

/**
 * Phase 1 Navigation Structure (Platform Evolution Roadmap)
 * Target: 6 main navigation groups with submenu support
 *
 * Structure uses VerticalNav component with collapsible subItems
 */
const navItems = computed<NavItem[]>(() => [
  { id: '/', label: 'Bilanço', icon: '📊' },
  { id: '/dashboard-v2', label: 'Bilanço V2 (Beta)', icon: '🚀' },
  { id: '/import', label: 'İçe Aktar', icon: '📥' },
  {
    id: '/sales',
    label: 'Ciro',
    icon: '💰',
    subItems: [
      { id: '/sales', label: 'Kasa' },
      { id: '/sales/verify', label: 'Kasa Farkı' }
    ]
  },
  {
    id: '/operations',
    label: 'Operasyon',
    icon: '🏭',
    subItems: [
      { id: '/operations/production', label: 'Üretim' },
      { id: '/operations/purchases', label: 'Mal Alım' }
    ]
  },
  {
    id: '/personnel',
    label: 'Personel',
    icon: '👥',
    subItems: [
      { id: '/personnel', label: 'Personel Listesi' },
      { id: '/personnel/meals', label: 'Personel İaşe' },
      { id: '/personnel/payroll', label: 'Bordro' }
    ]
  },
  {
    id: '/expenses',
    label: 'Giderler',
    icon: '💸',
    subItems: [
      { id: '/expenses', label: 'Genel Giderler' },
      { id: '/expenses/courier', label: 'Kurye' }
    ]
  }
])

// Current active nav item based on route
const activeNavId = computed(() => route.path)

// Handle navigation from VerticalNav
function handleNavSelect(id: string) {
  router.push(id)
}

// Versiyon bilgileri (build sirasinda enjekte edilir)
const appVersion = __APP_VERSION__
const gitCommit = __GIT_COMMIT__
const gitDate = __GIT_DATE__

const adminMenuItems = [
  { path: '/settings', name: 'Sistem Ayarlari', icon: '⚙️' },
]

// Owner-level menu items
const ownerMenuItems = [
  { path: '/invitation-codes', name: 'Davet Kodlari', icon: '🔑' },
]

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

async function handleBranchSwitch(branchId: number) {
  branchSelectorOpen.value = false
  if (branchId === authStore.currentBranchId) return

  await authStore.switchBranch(branchId)
  // Vue will re-mount route components via router-view key change
}
</script>

<template>
  <div class="min-h-screen bg-gray-100 flex">
    <!-- Sidebar - always fixed -->
    <aside
      :class="[
        'fixed inset-y-0 left-0 z-50 w-64 bg-brand-dark transform transition-transform duration-200 lg:translate-x-0 flex flex-col',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      ]"
    >
      <!-- Logo -->
      <div class="h-16 flex items-center px-6 border-b border-gray-700 flex-shrink-0">
        <span class="text-2xl mr-3">🥙</span>
        <span class="font-display font-bold text-white">Cig Kofte</span>
      </div>

      <!-- Branch Selector (only show if user has multiple branches) -->
      <div v-if="authStore.hasMultipleBranches" class="px-3 py-3 border-b border-gray-700 flex-shrink-0">
        <div class="relative">
          <button
            @click="branchSelectorOpen = !branchSelectorOpen"
            class="w-full flex items-center justify-between px-4 py-2 bg-gray-700 rounded-lg text-white hover:bg-gray-600 transition-colors"
          >
            <div class="flex items-center">
              <span class="text-sm mr-2">🏪</span>
              <span class="text-sm font-medium truncate">{{ authStore.currentBranch?.name || 'Sube Sec' }}</span>
            </div>
            <svg
              :class="['w-4 h-4 transition-transform', branchSelectorOpen ? 'rotate-180' : '']"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          <!-- Dropdown -->
          <div
            v-if="branchSelectorOpen"
            class="absolute top-full left-0 right-0 mt-1 bg-gray-800 rounded-lg shadow-lg z-10 overflow-hidden"
          >
            <button
              v-for="branch in authStore.accessibleBranches"
              :key="branch.id"
              @click="handleBranchSwitch(branch.id)"
              :class="[
                'w-full text-left px-4 py-2 text-sm transition-colors',
                branch.id === authStore.currentBranchId
                  ? 'bg-brand-red text-white'
                  : 'text-gray-300 hover:bg-gray-700'
              ]"
            >
              {{ branch.name }}
            </button>
          </div>
        </div>
      </div>

      <!-- Single branch display (when user has only one branch) -->
      <div v-else class="px-3 py-3 border-b border-gray-700 flex-shrink-0">
        <div class="flex items-center px-4 py-2 text-gray-400">
          <span class="text-sm mr-2">🏪</span>
          <span class="text-sm">{{ authStore.currentBranch?.name }}</span>
        </div>
      </div>

      <!-- Menu - scrollable if needed -->
      <nav class="flex-1 overflow-y-auto py-4 px-3 sidebar-nav">
        <VerticalNav
          :items="navItems"
          :model-value="activeNavId"
          @update:model-value="handleNavSelect"
        />

        <!-- Owner Menu (Owner or Super Admin) -->
        <template v-if="authStore.user?.role === 'owner' || authStore.isSuperAdmin">
          <div class="my-3 border-t border-gray-700"></div>
          <p class="px-4 py-2 text-xs text-gray-500 uppercase tracking-wider">Sahip Menusu</p>
          <router-link
            v-for="item in ownerMenuItems"
            :key="item.path"
            :to="item.path"
            :class="[
              'flex items-center px-4 py-3 mb-1 rounded-lg transition-colors',
              route.path === item.path
                ? 'bg-brand-red text-white'
                : 'text-gray-300 hover:bg-gray-700'
            ]"
          >
            <span class="text-xl mr-3">{{ item.icon }}</span>
            <span class="font-medium">{{ item.name }}</span>
          </router-link>
        </template>

        <!-- Admin Menu (Super Admin only) -->
        <template v-if="authStore.isSuperAdmin">
          <div class="my-3 border-t border-gray-700"></div>
          <p class="px-4 py-2 text-xs text-gray-500 uppercase tracking-wider">Yonetim</p>
          <router-link
            v-for="item in adminMenuItems"
            :key="item.path"
            :to="item.path"
            :class="[
              'flex items-center px-4 py-3 mb-1 rounded-lg transition-colors',
              route.path === item.path
                ? 'bg-brand-red text-white'
                : 'text-gray-300 hover:bg-gray-700'
            ]"
          >
            <span class="text-xl mr-3">{{ item.icon }}</span>
            <span class="font-medium">{{ item.name }}</span>
          </router-link>
        </template>
      </nav>

      <!-- User - always at bottom -->
      <div class="flex-shrink-0 p-4 border-t border-gray-700">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <div class="w-8 h-8 bg-brand-red rounded-full flex items-center justify-center text-white font-medium">
              {{ authStore.user?.name?.charAt(0) || 'U' }}
            </div>
            <div class="ml-3">
              <p class="text-sm font-medium text-white">{{ authStore.user?.name }}</p>
              <p class="text-xs text-gray-400">{{ authStore.user?.role }}</p>
            </div>
          </div>
          <button
            @click="handleLogout"
            class="p-2 text-gray-400 hover:text-white transition-colors"
            title="Cikis Yap"
          >
            🚪
          </button>
        </div>
        <!-- Versiyon Bilgisi -->
        <div class="mt-3 pt-3 border-t border-gray-700 text-center">
          <p class="text-xs text-gray-500">
            v{{ appVersion }} ({{ gitCommit }})
          </p>
          <p class="text-xs text-gray-600">
            {{ gitDate }}
          </p>
        </div>
      </div>
    </aside>

    <!-- Main Content - with left margin for fixed sidebar on large screens -->
    <div class="flex-1 flex flex-col min-w-0 lg:ml-64">
      <!-- Header -->
      <header class="h-16 bg-white border-b border-gray-200 flex items-center px-6 sticky top-0 z-40">
        <button
          @click="sidebarOpen = !sidebarOpen"
          class="lg:hidden p-2 mr-4 text-gray-600 hover:bg-gray-100 rounded-lg"
        >
          ☰
        </button>
        <h1 class="text-xl font-display font-semibold text-gray-800">
          {{ route.meta.title || route.name }}
        </h1>
      </header>

      <!-- Page Content -->
      <main class="flex-1 p-6 overflow-auto">
        <router-view :key="authStore.currentBranchId ?? 'default'" />
      </main>
    </div>

    <!-- Mobile Overlay -->
    <div
      v-if="sidebarOpen"
      @click="sidebarOpen = false"
      class="fixed inset-0 bg-black/50 z-40 lg:hidden"
    />
  </div>
</template>

<style scoped>
/* Override VerticalNav styles for dark sidebar */
.sidebar-nav :deep(.vertical-nav) {
  gap: 4px;
}

.sidebar-nav :deep(.nav-button) {
  color: #d1d5db; /* gray-300 */
  background: transparent;
}

.sidebar-nav :deep(.nav-button:hover) {
  background: #374151; /* gray-700 */
  color: white;
}

.sidebar-nav :deep(.nav-button.active) {
  background: #dc2626; /* brand-red */
  color: white;
}

.sidebar-nav :deep(.nav-button.subitem.active) {
  background: #b91c1c; /* darker red for subitem */
}

.sidebar-nav :deep(.expand-icon) {
  color: #9ca3af; /* gray-400 */
}

.sidebar-nav :deep(.nav-button.active .expand-icon) {
  color: rgba(255, 255, 255, 0.8);
}

.sidebar-nav :deep(.nav-subitems) {
  border-left: 2px solid #374151;
  margin-left: 12px;
  padding-left: 8px;
}

/* Mobile dropdown styles override */
@media (max-width: 640px) {
  .sidebar-nav :deep(.nav-subitems) {
    background: #1f2937; /* gray-800 */
    border: 1px solid #374151;
    border-left: none;
    margin-left: 0;
    padding-left: 0;
  }
}
</style>
