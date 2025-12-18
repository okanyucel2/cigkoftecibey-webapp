<template>
  <div class="bg-gradient-to-br from-indigo-50 to-white dark:from-gray-800 dark:to-gray-900 rounded-xl shadow-sm border border-indigo-100 dark:border-gray-700 p-6">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-bold text-gray-800 dark:text-gray-100 flex items-center gap-2">
        <span class="text-2xl">✨</span>
        Yapay Zeka Asistanı
      </h3>
      <span class="text-xs px-2 py-1 bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300 rounded-full font-medium">Günlük Analiz</span>
    </div>

    <div v-if="loading" class="animate-pulse space-y-3">
      <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
      <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
      <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
    </div>

    <div v-else-if="error" class="text-red-500 text-sm p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
      {{ error }}
    </div>

    <div v-else class="space-y-4">
      <!-- AI Insight Text (Markdown supported simply) -->
      <div class="prose dark:prose-invert max-w-none text-gray-600 dark:text-gray-300 text-sm whitespace-pre-wrap leading-relaxed">
        {{ data?.insight }}
      </div>

      <!-- Quick Stats from Prediction -->
      <div class="grid grid-cols-3 gap-2 mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
        <div class="text-center p-2 bg-white dark:bg-gray-800 rounded-lg">
          <div class="text-xs text-gray-500 dark:text-gray-400">Beklenen Ciro</div>
          <div class="font-bold text-indigo-600 dark:text-indigo-400">₺{{ data?.stats?.prediction?.revenue }}</div>
        </div>
        <div class="text-center p-2 bg-white dark:bg-gray-800 rounded-lg">
          <div class="text-xs text-gray-500 dark:text-gray-400">Müşteri</div>
          <div class="font-bold text-indigo-600 dark:text-indigo-400">{{ data?.stats?.prediction?.covers }}</div>
        </div>
        <div class="text-center p-2 bg-white dark:bg-gray-800 rounded-lg">
          <div class="text-xs text-gray-500 dark:text-gray-400">Hava</div>
          <div class="font-bold text-gray-700 dark:text-gray-300">{{ data?.stats?.weather_forecast }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { aiApi } from '@/services/api'

const loading = ref(true)
const error = ref<string | null>(null)
const data = ref<any>(null)

async function fetchInsight() {
  try {
    loading.value = true
    error.value = null
    
    // Use centralized API service (handles Auth & BaseURL)
    const res = await aiApi.getDailyBrief()
    data.value = res.data
    
  } catch (err: any) {
    console.error(err)
    if (err.response?.status === 401) {
       error.value = "Oturum süresi doldu."
    } else {
       error.value = "AI analizi şu an kullanılamıyor."
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchInsight()
})
</script>
