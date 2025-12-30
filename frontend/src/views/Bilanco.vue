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

// Fetch comparison data
const fetchComparisonData = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await reportsApi.bilancoCompare({
      left_start: comparisonConfig.value.leftPeriod.start,
      left_end: comparisonConfig.value.leftPeriod.end,
      right_start: comparisonConfig.value.rightPeriod.start,
      right_end: comparisonConfig.value.rightPeriod.end
    })

    leftData.value = response.data.left
    rightData.value = response.data.right
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Veriler yüklenemedi. Lütfen sayfayı yenileyin.'
  } finally {
    loading.value = false
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

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center h-64">
      <div class="text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-2"></div>
        <div class="text-gray-500">Yükleniyor...</div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex items-center justify-center h-64">
      <div class="text-center">
        <div class="text-red-500 mb-4">{{ error }}</div>
        <button @click="fetchComparisonData" class="btn btn-primary">Tekrar Dene</button>
      </div>
    </div>

    <!-- Comparison Content -->
    <div v-else-if="leftData && rightData" class="comparison-container">
      <!-- Left Card | Delta Band | Right Card -->
      <div class="comparison-grid">
        <ComparisonCard :data="leftData" position="left" />
        <DeltaBand :left-data="leftData" :right-data="rightData" />
        <ComparisonCard :data="rightData" position="right" />
      </div>
    </div>

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
