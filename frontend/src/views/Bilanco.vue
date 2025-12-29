<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import type { BilancoStats } from '@/types'
import { reportsApi } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import SmartInsightCard from '@/components/dashboard/SmartInsightCard.vue'

const router = useRouter()
const authStore = useAuthStore()
const stats = ref<BilancoStats | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

async function fetchData() {
  try {
    loading.value = true
    error.value = null
    const res = await reportsApi.getBilanco()
    stats.value = res.data
  } catch (err: any) {
    console.error('Failed to load bilanco:', err)
    error.value = 'Veriler yüklenemedi. Lütfen sayfayı yenileyin.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})

// Refresh when branch changes
watch(() => authStore.currentBranchId, () => {
  fetchData()
})

function formatCurrency(value: number | string | null | undefined) {
  const num = Number(value) || 0
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(num)
}

function formatCompact(value: number | string | null | undefined) {
  const num = Number(value) || 0
  if (num >= 1000) {
    return `${(num / 1000).toFixed(0)}K`
  }
  return formatCurrency(num)
}

function formatPercent(value: number | null | undefined) {
  const num = Number(value) || 0
  const sign = num >= 0 ? '▲' : '▼'
  return `${sign} %${Math.abs(num).toFixed(0)}`
}

function formatDate(dateStr: string) {
  const d = new Date(dateStr)
  return d.toLocaleDateString('tr-TR', { day: 'numeric', month: 'long', year: 'numeric' })
}

function formatDateRange(start: string, end: string) {
  const s = new Date(start)
  const e = new Date(end)
  return `${s.getDate()}-${e.getDate()} ${s.toLocaleDateString('tr-TR', { month: 'long' })}`
}

// Haftalık grafik için max değer
const weeklyMax = computed(() => {
  if (!stats.value) return 1
  const thisWeek = stats.value.this_week_daily.map(d => d.amount)
  const lastWeek = stats.value.last_week_daily.map(d => d.amount)
  return Math.max(...thisWeek, ...lastWeek, 1)
})

// Geçen hafta toplam gider
const lastWeekExpenses = computed(() => {
  if (!stats.value) return 0
  const b = stats.value.last_week_breakdown
  return (b.mal_alimi || 0) + (b.gider || 0) + (b.staff || 0) +
         (b.kurye || 0) + (b.parttime || 0) + (b.uretim || 0)
})

// Geçen hafta kar
const lastWeekProfit = computed(() => {
  if (!stats.value) return 0
  return stats.value.last_week_total - lastWeekExpenses.value
})

// Aylık grafik için max değer
const monthlyMax = computed(() => {
  if (!stats.value) return 1
  return Math.max(...stats.value.this_month_chart.map(d => d.amount), 1)
})

// Aylık toplam gider
const thisMonthExpenses = computed(() => {
  if (!stats.value) return 0
  const b = stats.value.this_month_breakdown
  return (b.mal_alimi || 0) + (b.gider || 0) + (b.staff || 0) +
         (b.kurye || 0) + (b.parttime || 0) + (b.uretim || 0)
})

const lastMonthExpenses = computed(() => {
  if (!stats.value) return 0
  const b = stats.value.last_month_breakdown
  return (b.mal_alimi || 0) + (b.gider || 0) + (b.staff || 0) +
         (b.kurye || 0) + (b.parttime || 0) + (b.uretim || 0)
})

const thisMonthProfit = computed(() => {
  if (!stats.value) return 0
  return stats.value.this_month_revenue - thisMonthExpenses.value
})

const lastMonthProfit = computed(() => {
  if (!stats.value) return 0
  return stats.value.last_month_revenue - lastMonthExpenses.value
})
</script>

<template>
  <div v-if="loading" class="flex items-center justify-center h-64">
    <div class="text-center">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-2"></div>
      <div class="text-gray-500">Yükleniyor...</div>
    </div>
  </div>

  <div v-else-if="error" class="flex items-center justify-center h-64">
    <div class="text-center">
      <div class="text-red-500 mb-4">{{ error }}</div>
      <button @click="fetchData" class="btn btn-primary">Tekrar Dene</button>
    </div>
  </div>

  <div v-else-if="stats" class="space-y-6">
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

    <!-- Bölüm 0: Bugün (Şu Ana Kadar) -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-gray-800 flex items-center gap-2">
          <span class="text-xl">⏰</span>
          Bugün ({{ formatDate(stats.today_date) }}, {{ stats.today_day_name }})
        </h2>
        <span class="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded-full">Anlık</span>
      </div>

      <!-- Kasa Detayları -->
      <div class="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4">
        <!-- Visa -->
        <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-3 border border-blue-200">
          <p class="text-xs text-blue-600 font-medium flex items-center gap-1">
            <span>💳</span> Visa
          </p>
          <p class="text-xl font-bold text-blue-700">{{ formatCurrency(stats.today_breakdown.visa) }}</p>
        </div>

        <!-- Nakit -->
        <div class="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-lg p-3 border border-emerald-200">
          <p class="text-xs text-emerald-600 font-medium flex items-center gap-1">
            <span>💵</span> Nakit
          </p>
          <p class="text-xl font-bold text-emerald-700">{{ formatCurrency(stats.today_breakdown.nakit) }}</p>
        </div>

        <!-- Online -->
        <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-3 border border-purple-200">
          <p class="text-xs text-purple-600 font-medium flex items-center gap-1">
            <span>📱</span> Online
          </p>
          <p class="text-xl font-bold text-purple-700">{{ formatCurrency(stats.today_breakdown.online) }}</p>
        </div>
      </div>

      <!-- Özet Kartları -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <!-- Toplam Ciro -->
        <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4 border border-green-200">
          <p class="text-sm text-green-600 font-medium flex items-center gap-1">
            <span>💰</span> Toplam Ciro
          </p>
          <p class="text-2xl font-bold text-green-700">{{ formatCurrency(stats.today_revenue) }}</p>
        </div>

        <!-- Toplam Gider -->
        <div class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-4 border border-orange-200">
          <p class="text-sm text-orange-600 font-medium flex items-center gap-1">
            <span>📦</span> Toplam Gider
          </p>
          <p class="text-2xl font-bold text-orange-700">{{ formatCurrency(stats.today_expenses) }}</p>
        </div>

        <!-- Net Kar -->
        <div :class="[
          'rounded-xl p-4 border',
          stats.today_profit >= 0
            ? 'bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200'
            : 'bg-gradient-to-br from-red-50 to-red-100 border-red-200'
        ]">
          <p :class="['text-sm font-medium flex items-center gap-1', stats.today_profit >= 0 ? 'text-blue-600' : 'text-red-600']">
            <span>📈</span> Net Kâr
          </p>
          <p :class="['text-2xl font-bold', stats.today_profit >= 0 ? 'text-blue-700' : 'text-red-700']">
            {{ formatCurrency(stats.today_profit) }}
          </p>
        </div>
      </div>

      <!-- Gider Detayları -->
      <div class="grid grid-cols-2 gap-x-4 gap-y-1 text-sm text-gray-500 pt-3 border-t border-gray-100">
        <span>Mal Alımı {{ formatCurrency(stats.today_breakdown.mal_alimi) }}</span>
        <span>İşletme Giderleri {{ formatCurrency(stats.today_breakdown.gider) }}</span>
        <span>Personel Yemekleri {{ formatCurrency(stats.today_breakdown.staff) }}</span>
        <span>Kurye {{ formatCurrency(stats.today_breakdown.kurye) }}</span>
        <span>Part-Time {{ formatCurrency(stats.today_breakdown.parttime) }}</span>
        <span>Üretim {{ formatCurrency(stats.today_breakdown.uretim) }}</span>
      </div>
    </div>

    <!-- Bölüm 1: Dün Özeti -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-gray-800 flex items-center gap-2">
          <span class="text-xl">📅</span>
          Dün ({{ formatDate(stats.yesterday_date) }}, {{ stats.yesterday_day_name }})
        </h2>
        <span :class="['text-sm px-3 py-1 rounded-full', stats.yesterday_vs_previous_pct >= 0 ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600']">
          {{ formatPercent(stats.yesterday_vs_previous_pct) }} önceki gün
        </span>
      </div>

      <!-- Kasa Detayları -->
      <div class="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4">
        <!-- Visa -->
        <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-3 border border-blue-200">
          <p class="text-xs text-blue-600 font-medium flex items-center gap-1">
            <span>💳</span> Visa
          </p>
          <p class="text-xl font-bold text-blue-700">{{ formatCurrency(stats.yesterday_breakdown.visa) }}</p>
        </div>

        <!-- Nakit -->
        <div class="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-lg p-3 border border-emerald-200">
          <p class="text-xs text-emerald-600 font-medium flex items-center gap-1">
            <span>💵</span> Nakit
          </p>
          <p class="text-xl font-bold text-emerald-700">{{ formatCurrency(stats.yesterday_breakdown.nakit) }}</p>
        </div>

        <!-- Online -->
        <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-3 border border-purple-200">
          <p class="text-xs text-purple-600 font-medium flex items-center gap-1">
            <span>📱</span> Online
          </p>
          <p class="text-xl font-bold text-purple-700">{{ formatCurrency(stats.yesterday_breakdown.online) }}</p>
        </div>
      </div>

      <!-- Özet Kartları -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <!-- Toplam Ciro -->
        <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4 border border-green-200">
          <p class="text-sm text-green-600 font-medium flex items-center gap-1">
            <span>💰</span> Toplam Ciro
          </p>
          <p class="text-2xl font-bold text-green-700">{{ formatCurrency(stats.yesterday_revenue) }}</p>
        </div>

        <!-- Toplam Gider -->
        <div class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-4 border border-orange-200">
          <p class="text-sm text-orange-600 font-medium flex items-center gap-1">
            <span>📦</span> Toplam Gider
          </p>
          <p class="text-2xl font-bold text-orange-700">{{ formatCurrency(stats.yesterday_expenses) }}</p>
        </div>

        <!-- Net Kar -->
        <div :class="[
          'rounded-xl p-4 border',
          stats.yesterday_profit >= 0
            ? 'bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200'
            : 'bg-gradient-to-br from-red-50 to-red-100 border-red-200'
        ]">
          <p :class="['text-sm font-medium flex items-center gap-1', stats.yesterday_profit >= 0 ? 'text-blue-600' : 'text-red-600']">
            <span>📈</span> Net Kâr
          </p>
          <p :class="['text-2xl font-bold', stats.yesterday_profit >= 0 ? 'text-blue-700' : 'text-red-700']">
            {{ formatCurrency(stats.yesterday_profit) }}
          </p>
        </div>
      </div>

      <!-- Gider Detayları -->
      <div class="grid grid-cols-2 gap-x-4 gap-y-1 text-sm text-gray-500 pt-3 border-t border-gray-100">
        <span>Mal Alımı {{ formatCurrency(stats.yesterday_breakdown.mal_alimi) }}</span>
        <span>İşletme Giderleri {{ formatCurrency(stats.yesterday_breakdown.gider) }}</span>
        <span>Personel Yemekleri {{ formatCurrency(stats.yesterday_breakdown.staff) }}</span>
        <span>Kurye {{ formatCurrency(stats.yesterday_breakdown.kurye) }}</span>
        <span>Part-Time {{ formatCurrency(stats.yesterday_breakdown.parttime) }}</span>
        <span>Üretim {{ formatCurrency(stats.yesterday_breakdown.uretim) }}</span>
      </div>
    </div>

    <!-- Bölüm 2: Haftalık Karşılaştırma -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-gray-800 flex items-center gap-2">
          <span class="text-xl">📊</span>
          Geçen Hafta ({{ formatDateRange(stats.last_week_start, stats.last_week_end) }})
        </h2>
        <span :class="['text-sm px-3 py-1 rounded-full', stats.week_vs_week_pct >= 0 ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600']">
          {{ formatPercent(stats.week_vs_week_pct) }} bu haftaya göre
        </span>
      </div>

      <!-- Kasa Detayları -->
      <div class="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4">
        <!-- Visa -->
        <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-3 border border-blue-200">
          <p class="text-xs text-blue-600 font-medium flex items-center gap-1">
            <span>💳</span> Visa
          </p>
          <p class="text-xl font-bold text-blue-700">{{ formatCurrency(stats.last_week_breakdown.visa) }}</p>
        </div>

        <!-- Nakit -->
        <div class="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-lg p-3 border border-emerald-200">
          <p class="text-xs text-emerald-600 font-medium flex items-center gap-1">
            <span>💵</span> Nakit
          </p>
          <p class="text-xl font-bold text-emerald-700">{{ formatCurrency(stats.last_week_breakdown.nakit) }}</p>
        </div>

        <!-- Online -->
        <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-3 border border-purple-200">
          <p class="text-xs text-purple-600 font-medium flex items-center gap-1">
            <span>📱</span> Online
          </p>
          <p class="text-xl font-bold text-purple-700">{{ formatCurrency(stats.last_week_breakdown.online) }}</p>
        </div>
      </div>

      <!-- Özet Kartları -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <!-- Toplam Ciro -->
        <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4 border border-green-200">
          <p class="text-sm text-green-600 font-medium flex items-center gap-1">
            <span>💰</span> Toplam Ciro
          </p>
          <p class="text-2xl font-bold text-green-700">{{ formatCurrency(stats.last_week_total) }}</p>
          <p class="text-xs text-gray-500 mt-1">Bu hafta: {{ formatCurrency(stats.this_week_total) }}</p>
        </div>

        <!-- Toplam Gider -->
        <div class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-4 border border-orange-200">
          <p class="text-sm text-orange-600 font-medium flex items-center gap-1">
            <span>📦</span> Toplam Gider
          </p>
          <p class="text-2xl font-bold text-orange-700">{{ formatCurrency(lastWeekExpenses) }}</p>
        </div>

        <!-- Net Kar -->
        <div :class="[
          'rounded-xl p-4 border',
          lastWeekProfit >= 0
            ? 'bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200'
            : 'bg-gradient-to-br from-red-50 to-red-100 border-red-200'
        ]">
          <p :class="['text-sm font-medium flex items-center gap-1', lastWeekProfit >= 0 ? 'text-blue-600' : 'text-red-600']">
            <span>📈</span> Net Kâr
          </p>
          <p :class="['text-2xl font-bold', lastWeekProfit >= 0 ? 'text-blue-700' : 'text-red-700']">
            {{ formatCurrency(lastWeekProfit) }}
          </p>
        </div>
      </div>

      <!-- Gider Detayları -->
      <div class="grid grid-cols-2 gap-x-4 gap-y-1 text-sm text-gray-500 pt-3 border-t border-gray-100 mb-6">
        <span>Mal Alımı {{ formatCurrency(stats.last_week_breakdown.mal_alimi) }}</span>
        <span>İşletme Giderleri {{ formatCurrency(stats.last_week_breakdown.gider) }}</span>
        <span>Personel Yemekleri {{ formatCurrency(stats.last_week_breakdown.staff) }}</span>
        <span>Kurye {{ formatCurrency(stats.last_week_breakdown.kurye) }}</span>
        <span>Part-Time {{ formatCurrency(stats.last_week_breakdown.parttime) }}</span>
        <span>Üretim {{ formatCurrency(stats.last_week_breakdown.uretim) }}</span>
      </div>

      <!-- Gün Bazlı Karşılaştırma -->
      <p class="text-sm text-gray-600 font-medium mb-3">Günlük Dağılım</p>
      <div class="flex items-end gap-2 h-32 mb-4">
        <div v-for="(day, idx) in stats.this_week_daily" :key="day.date" class="flex-1 flex flex-col items-center">
          <div class="w-full flex flex-col items-center gap-1">
            <div
              class="w-3/4 bg-indigo-500 rounded-t transition-all"
              :style="{ height: `${Math.max(4, (day.amount / weeklyMax) * 100)}px` }"
              :title="`Bu hafta: ${formatCurrency(day.amount)}`"
            />
            <div
              v-if="stats.last_week_daily[idx]"
              class="w-3/4 bg-gray-300 rounded-t transition-all"
              :style="{ height: `${Math.max(4, (stats.last_week_daily[idx].amount / weeklyMax) * 100)}px` }"
              :title="`Geçen hafta: ${formatCurrency(stats.last_week_daily[idx].amount)}`"
            />
          </div>
          <p class="text-xs text-gray-500 mt-2">{{ day.day_name }}</p>
          <p class="text-xs font-medium">{{ formatCompact(day.amount) }}</p>
        </div>
      </div>

      <!-- Grafik açıklaması -->
      <div class="flex justify-center gap-6 text-xs text-gray-500 mb-4">
        <span class="flex items-center gap-1">
          <span class="w-3 h-3 bg-indigo-500 rounded"></span> Bu Hafta
        </span>
        <span class="flex items-center gap-1">
          <span class="w-3 h-3 bg-gray-300 rounded"></span> Geçen Hafta
        </span>
      </div>

      <!-- En iyi / En kötü -->
      <div class="flex gap-4 text-sm pt-3 border-t border-gray-100">
        <span v-if="stats.this_week_best_day" class="text-green-600 flex items-center gap-1">
          🏆 En iyi: {{ stats.this_week_best_day.day_name }} ({{ formatCurrency(stats.this_week_best_day.amount) }})
        </span>
        <span v-if="stats.this_week_worst_day" class="text-orange-600 flex items-center gap-1">
          📉 En düşük: {{ stats.this_week_worst_day.day_name }} ({{ formatCurrency(stats.this_week_worst_day.amount) }})
        </span>
      </div>
    </div>

    <!-- Bölüm 3: Aylık Özet -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-gray-800 flex items-center gap-2">
          <span class="text-xl">📆</span>
          {{ stats.this_month_name }} Özeti
        </h2>
        <span class="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
          {{ stats.this_month_days_passed }}/{{ stats.this_month_days_total }} gün
        </span>
      </div>

      <!-- Kasa Detayları -->
      <div class="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4">
        <!-- Visa -->
        <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-3 border border-blue-200">
          <p class="text-xs text-blue-600 font-medium flex items-center gap-1">
            <span>💳</span> Visa
          </p>
          <p class="text-xl font-bold text-blue-700">{{ formatCurrency(stats.this_month_breakdown.visa) }}</p>
        </div>

        <!-- Nakit -->
        <div class="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-lg p-3 border border-emerald-200">
          <p class="text-xs text-emerald-600 font-medium flex items-center gap-1">
            <span>💵</span> Nakit
          </p>
          <p class="text-xl font-bold text-emerald-700">{{ formatCurrency(stats.this_month_breakdown.nakit) }}</p>
        </div>

        <!-- Online -->
        <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-3 border border-purple-200">
          <p class="text-xs text-purple-600 font-medium flex items-center gap-1">
            <span>📱</span> Online
          </p>
          <p class="text-xl font-bold text-purple-700">{{ formatCurrency(stats.this_month_breakdown.online) }}</p>
        </div>
      </div>

      <!-- Özet Kartları -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <!-- Toplam Ciro -->
        <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4 border border-green-200">
          <p class="text-sm text-green-600 font-medium flex items-center gap-1">
            <span>💰</span> Toplam Ciro
          </p>
          <p class="text-2xl font-bold text-green-700">{{ formatCurrency(stats.this_month_revenue) }}</p>
          <p class="text-xs text-gray-500 mt-1">Geçen ay: {{ formatCurrency(stats.last_month_revenue) }}</p>
        </div>

        <!-- Toplam Gider -->
        <div class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-4 border border-orange-200">
          <p class="text-sm text-orange-600 font-medium flex items-center gap-1">
            <span>📦</span> Toplam Gider
          </p>
          <p class="text-2xl font-bold text-orange-700">{{ formatCurrency(thisMonthExpenses) }}</p>
          <p class="text-xs text-gray-500 mt-1">Geçen ay: {{ formatCurrency(lastMonthExpenses) }}</p>
        </div>

        <!-- Net Kar -->
        <div :class="[
          'rounded-xl p-4 border',
          thisMonthProfit >= 0
            ? 'bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200'
            : 'bg-gradient-to-br from-red-50 to-red-100 border-red-200'
        ]">
          <p :class="['text-sm font-medium flex items-center gap-1', thisMonthProfit >= 0 ? 'text-blue-600' : 'text-red-600']">
            <span>📈</span> Net Kâr
          </p>
          <p :class="['text-2xl font-bold', thisMonthProfit >= 0 ? 'text-blue-700' : 'text-red-700']">
            {{ formatCurrency(thisMonthProfit) }}
          </p>
          <p class="text-xs text-gray-500 mt-1">Geçen ay: {{ formatCurrency(lastMonthProfit) }}</p>
        </div>
      </div>

      <!-- Gider Detayları -->
      <div class="grid grid-cols-2 gap-x-4 gap-y-1 text-sm text-gray-500 pt-3 border-t border-gray-100 mb-6">
        <span>Mal Alımı {{ formatCurrency(stats.this_month_breakdown.mal_alimi) }}</span>
        <span>İşletme Giderleri {{ formatCurrency(stats.this_month_breakdown.gider) }}</span>
        <span>Personel Yemekleri {{ formatCurrency(stats.this_month_breakdown.staff) }}</span>
        <span>Kurye {{ formatCurrency(stats.this_month_breakdown.kurye) }}</span>
        <span>Part-Time {{ formatCurrency(stats.this_month_breakdown.parttime) }}</span>
        <span>Üretim {{ formatCurrency(stats.this_month_breakdown.uretim) }}</span>
      </div>

      <!-- Aylık Grafik -->
      <p class="text-sm text-gray-600 font-medium mb-3">Günlük Dağılım</p>
      <div class="h-24 flex items-end gap-px mb-4 bg-gray-50 rounded-lg p-2">
        <div
          v-for="day in stats.this_month_chart"
          :key="day.date"
          class="flex-1 bg-emerald-400 rounded-t transition-all hover:bg-emerald-500 cursor-pointer"
          :style="{ height: `${Math.max(2, (day.amount / monthlyMax) * 100)}%` }"
          :title="`${day.day_name}. gün: ${formatCurrency(day.amount)}`"
        />
      </div>

      <!-- Alt bilgiler -->
      <div class="flex flex-wrap gap-4 text-sm text-gray-600 pt-3 border-t border-gray-100">
        <span>Günlük Ortalama: <strong class="text-gray-800">{{ formatCurrency(stats.this_month_daily_avg) }}</strong></span>
        <span class="text-gray-300">•</span>
        <span>Kalan Gün: <strong class="text-gray-800">{{ stats.this_month_days_total - stats.this_month_days_passed }}</strong></span>
        <span class="text-gray-300">•</span>
        <span>Tahmini Ay Sonu: <strong class="text-emerald-600">{{ formatCurrency(stats.this_month_forecast) }}</strong></span>
      </div>
    </div>

    <!-- AI Asistan -->
    <SmartInsightCard />
  </div>
</template>
