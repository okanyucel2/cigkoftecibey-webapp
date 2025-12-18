<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { DashboardStats } from '@/types'
import { reportsApi } from '@/services/api'
import SmartInsightCard from '@/components/dashboard/SmartInsightCard.vue'

const router = useRouter()

const stats = ref<DashboardStats | null>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const dashboardRes = await reportsApi.getDashboard()
    stats.value = dashboardRes.data
  } catch (error) {
    console.error('Failed to load dashboard:', error)
  } finally {
    loading.value = false
  }
})

function formatCurrency(value: number | string | null | undefined) {
  const num = Number(value) || 0
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 0
  }).format(num)
}

// String değerleri number'a çevir
function toNum(value: number | string | null | undefined): number {
  return Number(value) || 0
}

</script>

<template>
  <div v-if="loading" class="flex items-center justify-center h-64">
    <div class="text-gray-500">Yukleniyor...</div>
  </div>

  <div v-else class="space-y-6">
    <!-- KPI Cards - 6 kart (2 satir x 3 kolon) -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <!-- AI Insight Card (Spans full width on mobile, 2 cols on desktop if desired, but here we keep it simple) -->
      <div class="col-span-1 md:col-span-2 lg:col-span-3">
        <SmartInsightCard />
      </div>

      <!-- Row 1 -->
      <!-- Salon Satis -->
      <div class="kpi-card border-l-4 border-blue-500">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500">Salon Satisi</p>
            <p class="text-2xl font-display font-bold text-blue-600">
              {{ formatCurrency(stats?.today_salon || 0) }}
            </p>
          </div>
          <div class="text-3xl">🏠</div>
        </div>
      </div>

      <!-- Telefon Paket -->
      <div class="kpi-card border-l-4 border-orange-500">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500">Telefon Paket</p>
            <p class="text-2xl font-display font-bold text-orange-600">
              {{ formatCurrency(stats?.today_telefon || 0) }}
            </p>
          </div>
          <div class="text-3xl">📞</div>
        </div>
      </div>

      <!-- Online Satis -->
      <div class="kpi-card border-l-4 border-purple-500">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500">Online Satis</p>
            <p class="text-2xl font-display font-bold text-purple-600">
              {{ formatCurrency(stats?.today_online_sales || 0) }}
            </p>
            <p v-if="toNum(stats?.online_platform_count) > 0" class="text-xs text-gray-400 mt-1">
              {{ stats?.online_platform_count }} platform
            </p>
          </div>
          <div class="text-3xl">📱</div>
        </div>
      </div>

      <!-- Row 2 -->
      <!-- Toplam Ciro -->
      <div class="kpi-card border-l-4 border-brand-red">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500">Toplam Ciro</p>
            <p class="text-2xl font-display font-bold text-gray-900">
              {{ formatCurrency(stats?.today_total_sales || 0) }}
            </p>
            <p class="text-xs text-gray-400 mt-1">
              Salon + Telefon + Online
            </p>
          </div>
          <div class="text-3xl">💰</div>
        </div>
      </div>

      <!-- Toplam Gider -->
      <div class="kpi-card border-l-4 border-yellow-500">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500">Toplam Gider</p>
            <p class="text-2xl font-display font-bold text-gray-900">
              {{ formatCurrency(toNum(stats?.today_purchases) + toNum(stats?.today_expenses) + toNum(stats?.today_staff_meals)) }}
            </p>
            <p class="text-xs text-gray-400 mt-1">
              📦 {{ formatCurrency(toNum(stats?.today_purchases)) }} · 💸 {{ formatCurrency(toNum(stats?.today_expenses)) }} · 🍽️ {{ formatCurrency(toNum(stats?.today_staff_meals)) }}
            </p>
          </div>
          <div class="text-3xl">📉</div>
        </div>
      </div>

      <!-- Net Kar -->
      <div class="kpi-card border-l-4 border-green-500">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500">Net Kar</p>
            <p :class="[
              'text-2xl font-display font-bold',
              toNum(stats?.today_profit) >= 0 ? 'text-green-600' : 'text-red-600'
            ]">
              {{ formatCurrency(stats?.today_profit || 0) }}
            </p>
          </div>
          <div class="text-3xl">📈</div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="card">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">Hizli Islemler</h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <button
          @click="router.push('/sales')"
          class="btn btn-primary flex items-center justify-center gap-2"
        >
          <span>💰</span>
          <span>Satis Gir</span>
        </button>
        <button
          @click="router.push('/purchases/new')"
          class="btn btn-secondary flex items-center justify-center gap-2"
        >
          <span>📦</span>
          <span>Mal Alimi</span>
        </button>
        <button
          @click="router.push('/expenses/new')"
          class="btn btn-secondary flex items-center justify-center gap-2"
        >
          <span>💸</span>
          <span>Gider Ekle</span>
        </button>
        <button
          @click="router.push('/production')"
          class="btn btn-secondary flex items-center justify-center gap-2"
        >
          <span>🥙</span>
          <span>Uretim Gir</span>
        </button>
      </div>
    </div>

    <!-- Weekly Chart (Simple) -->
    <div class="card">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">Haftalik Satis Trendi</h2>
      <div class="flex items-end gap-2 h-48">
        <div
          v-for="day in stats?.week_sales || []"
          :key="day.date"
          class="flex-1 flex flex-col items-center"
        >
          <div
            class="w-full bg-brand-red rounded-t transition-all"
            :style="{
              height: `${Math.max(10, (day.sales / Math.max(...(stats?.week_sales || []).map(d => d.sales), 1)) * 150)}px`
            }"
          />
          <p class="text-xs text-gray-500 mt-2">{{ day.day }}</p>
          <p class="text-xs font-medium">{{ formatCurrency(day.sales) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
