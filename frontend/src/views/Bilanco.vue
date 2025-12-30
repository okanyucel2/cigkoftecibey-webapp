<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ComparisonModeSelector from '@/components/ui/ComparisonModeSelector.vue'
import ComparisonCard from '@/components/ui/ComparisonCard.vue'
import DeltaBand from '@/components/ui/DeltaBand.vue'
import SmartInsightCard from '@/components/dashboard/SmartInsightCard.vue'
import { reportsApi } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import type { ComparisonConfig, BilancoPeriodData } from '@/types/comparison'

const router = useRouter()
const authStore = useAuthStore()

// Comparison state
const comparisonConfig = ref<ComparisonConfig>({
  mode: 'today_vs_yesterday',
  leftPeriod: { label: 'Bugün', start: '', end: '' },
  rightPeriod: { label: 'Dün', start: '', end: '' }
})

const leftData = ref<BilancoPeriodData | null>(null)
const rightData = ref<BilancoPeriodData | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const requestId = ref(0)

// Retry countdown
const retryCountdown = ref(0)
const retryTimer = ref<NodeJS.Timeout | null>(null)

// Fetch comparison data
const fetchComparisonData = async () => {
  // Increment request ID for this fetch
  const currentRequestId = ++requestId.value
  loading.value = true
  error.value = null

  // Clear existing retry timer
  if (retryTimer.value) {
    clearInterval(retryTimer.value)
    retryTimer.value = null
  }
  retryCountdown.value = 0

  try {
    const response = await reportsApi.bilancoCompare({
      left_start: comparisonConfig.value.leftPeriod.start,
      left_end: comparisonConfig.value.leftPeriod.end,
      right_start: comparisonConfig.value.rightPeriod.start,
      right_end: comparisonConfig.value.rightPeriod.end
    })

    // Validate empty state - check if data exists
    if (!response.data.left || !response.data.right) {
      throw new Error('Karşılaştırma verileri bulunamadı. Lütfen tarih aralığını kontrol edin.')
    }

    // Only update state if this is still the latest request
    if (currentRequestId === requestId.value) {
      leftData.value = response.data.left
      rightData.value = response.data.right
    }
  } catch (err) {
    // Only update state if this is still the latest request
    if (currentRequestId === requestId.value) {
      error.value = err instanceof Error ? err.message : 'Veriler yüklenemedi. Lütfen sayfayı yenileyen.'
      // Start retry countdown
      retryCountdown.value = 5
      retryTimer.value = setInterval(() => {
        retryCountdown.value--
        if (retryCountdown.value <= 0) {
          if (retryTimer.value) {
            clearInterval(retryTimer.value)
            retryTimer.value = null
          }
        }
      }, 1000)
    }
  } finally {
    // Only update loading state if this is still the latest request
    if (currentRequestId === requestId.value) {
      loading.value = false
    }
  }
}

// Watch for config changes
watch(comparisonConfig, fetchComparisonData, { deep: true })

// Refresh when branch changes
watch(() => authStore.currentBranchId, () => {
  fetchComparisonData()
})

// Load initial data on mount
onMounted(fetchComparisonData)
</script>

<template>
  <div class="space-y-6">
    <!-- Hızlı İşlemler -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <span class="text-xl">🚀</span>
        Hızlı İşlemler
      </h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <button @click="router.push('/sales')" class="btn btn-primary flex items-center justify-center gap-2">
          <span>💳</span>
          <span>Kasa Girişi</span>
        </button>
        <button @click="router.push('/purchases/new')" class="btn btn-secondary flex items-center justify-center gap-2">
          <span>📦</span>
          <span>Mal Alımı</span>
        </button>
        <button @click="router.push('/expenses/new')" class="btn btn-secondary flex items-center justify-center gap-2">
          <span>💸</span>
          <span>Gider Ekle</span>
        </button>
        <button @click="router.push('/production')" class="btn btn-secondary flex items-center justify-center gap-2">
          <span>🥙</span>
          <span>Üretim Gir</span>
        </button>
      </div>
    </div>

    <!-- Comparison Mode Selector -->
    <div class="flex justify-center">
      <ComparisonModeSelector v-model="comparisonConfig" />
    </div>

    <!-- Loading State with Skeleton -->
    <transition
      enter-active-class="transition-opacity duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="loading" class="comparison-container" role="status" aria-live="polite">
        <div class="comparison-grid">
          <!-- Left Skeleton -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 space-y-4">
            <div class="animate-pulse">
              <div class="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
              <div class="h-4 bg-gray-200 rounded w-1/2 mb-3"></div>
              <div class="grid grid-cols-3 gap-2 mb-4">
                <div class="h-16 bg-gray-200 rounded"></div>
                <div class="h-16 bg-gray-200 rounded"></div>
                <div class="h-16 bg-gray-200 rounded"></div>
              </div>
              <div class="h-20 bg-gray-200 rounded mb-4"></div>
              <div class="h-4 bg-gray-200 rounded w-1/3 mb-3"></div>
              <div class="space-y-2">
                <div class="h-4 bg-gray-200 rounded"></div>
                <div class="h-4 bg-gray-200 rounded"></div>
                <div class="h-4 bg-gray-200 rounded"></div>
              </div>
              <div class="h-20 bg-gray-200 rounded mb-4"></div>
              <div class="h-20 bg-gray-200 rounded"></div>
            </div>
          </div>

          <!-- Delta Skeleton -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 space-y-4">
            <div class="animate-pulse">
              <div class="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
              <div class="grid grid-cols-2 gap-3">
                <div class="h-24 bg-gray-200 rounded"></div>
                <div class="h-24 bg-gray-200 rounded"></div>
                <div class="h-24 bg-gray-200 rounded"></div>
                <div class="h-24 bg-gray-200 rounded"></div>
              </div>
              <div class="h-8 bg-gray-200 rounded mt-4"></div>
            </div>
          </div>

          <!-- Right Skeleton -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 space-y-4">
            <div class="animate-pulse">
              <div class="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
              <div class="h-4 bg-gray-200 rounded w-1/2 mb-3"></div>
              <div class="grid grid-cols-3 gap-2 mb-4">
                <div class="h-16 bg-gray-200 rounded"></div>
                <div class="h-16 bg-gray-200 rounded"></div>
                <div class="h-16 bg-gray-200 rounded"></div>
              </div>
              <div class="h-20 bg-gray-200 rounded mb-4"></div>
              <div class="h-4 bg-gray-200 rounded w-1/3 mb-3"></div>
              <div class="space-y-2">
                <div class="h-4 bg-gray-200 rounded"></div>
                <div class="h-4 bg-gray-200 rounded"></div>
                <div class="h-4 bg-gray-200 rounded"></div>
              </div>
              <div class="h-20 bg-gray-200 rounded mb-4"></div>
              <div class="h-20 bg-gray-200 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- Error State with Retry -->
    <transition
      enter-active-class="transition-opacity duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="!loading && error" class="flex items-center justify-center min-h-[400px] px-4" role="alert" aria-live="assertive">
        <div class="text-center max-w-md">
          <div class="text-6xl mb-4">⚠️</div>
          <h3 class="text-xl font-semibold text-gray-800 mb-2">Veriler Yüklenemedi</h3>
          <p class="text-gray-600 mb-6">{{ error }}</p>
          <button
            @click="fetchComparisonData"
            :disabled="retryCountdown > 0"
            class="btn btn-primary mb-4"
            :class="{ 'opacity-50 cursor-not-allowed': retryCountdown > 0 }"
          >
            {{ retryCountdown > 0 ? `Tekrar Dene (${retryCountdown}s)` : 'Tekrar Dene' }}
          </button>
          <div class="text-sm text-gray-500">
            Sorun devam ediyorsa, farklı bir tarih aralığı deneyin veya sayfayı yenileyin.
          </div>
        </div>
      </div>
    </transition>

    <!-- Comparison Content -->
    <transition
      enter-active-class="transition-opacity duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
    >
      <div v-if="!loading && !error && leftData && rightData" class="comparison-container">
        <!-- Left Card | Delta Band | Right Card -->
        <div class="comparison-grid">
          <ComparisonCard :data="leftData" position="left" />
          <DeltaBand :left-data="leftData" :right-data="rightData" />
          <ComparisonCard :data="rightData" position="right" />
        </div>
      </div>
    </transition>

    <!-- AI Asistan -->
    <SmartInsightCard />
  </div>
</template>

<style scoped>
.comparison-container {
  margin-top: 1rem;
}

.comparison-grid {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 1rem;
  align-items: start;
}

@media (max-width: 1024px) {
  .comparison-grid {
    grid-template-columns: 1fr;
  }
}
</style>
