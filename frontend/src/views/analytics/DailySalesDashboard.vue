<template>
  <div data-testid="daily-sales-dashboard" class="p-6">
    <h1 class="text-2xl font-bold mb-6">Gunluk Satis Analizi</h1>

    <!-- Date Range Filter and Export -->
    <div data-testid="date-range-filter" class="flex gap-4 mb-6 items-end">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Baslangic</label>
        <input
          type="date"
          v-model="startDate"
          class="border rounded-md px-3 py-2"
          @change="loadAnalytics"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Bitis</label>
        <input
          type="date"
          v-model="endDate"
          class="border rounded-md px-3 py-2"
          @change="loadAnalytics"
        />
      </div>

      <!-- Export Dropdown -->
      <div class="relative ml-auto">
        <button
          data-testid="export-button"
          @click="showExportMenu = !showExportMenu"
          class="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
          :disabled="exporting"
        >
          <svg v-if="!exporting" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
          <svg v-else class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>Disa Aktar</span>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>

        <!-- Dropdown Menu -->
        <div
          v-if="showExportMenu"
          class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-10"
        >
          <button
            data-testid="export-csv"
            @click="exportData('csv')"
            class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd" />
            </svg>
            CSV olarak indir
          </button>
          <button
            data-testid="export-excel"
            @click="exportData('excel')"
            class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-green-600" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd" />
            </svg>
            Excel olarak indir
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
      <p class="text-red-600">{{ error }}</p>
      <button @click="loadAnalytics" class="mt-2 text-sm text-red-700 underline">
        Tekrar Dene
      </button>
    </div>

    <!-- Content -->
    <template v-else-if="analytics">
      <!-- Summary Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div class="bg-white rounded-lg shadow p-4">
          <h3 class="text-sm font-medium text-gray-500">Toplam Kasa</h3>
          <p data-testid="summary-total-kasa" class="text-2xl font-bold text-blue-600">
            {{ formatCurrency(analytics.summary.total_kasa) }}
          </p>
        </div>
        <div class="bg-white rounded-lg shadow p-4">
          <h3 class="text-sm font-medium text-gray-500">Toplam POS</h3>
          <p data-testid="summary-total-pos" class="text-2xl font-bold text-green-600">
            {{ formatCurrency(analytics.summary.total_pos) }}
          </p>
        </div>
        <div class="bg-white rounded-lg shadow p-4">
          <h3 class="text-sm font-medium text-gray-500">Toplam Fark</h3>
          <p
            data-testid="summary-total-diff"
            class="text-2xl font-bold"
            :class="analytics.summary.total_diff >= 0 ? 'text-green-600' : 'text-red-600'"
          >
            {{ formatCurrency(analytics.summary.total_diff) }}
          </p>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="analytics.meta.record_count === 0" data-testid="empty-state" class="text-center py-12 bg-gray-50 rounded-lg">
        <p class="text-gray-500">Bu tarih araliginda veri bulunamadi.</p>
      </div>

      <!-- Chart -->
      <div v-else data-testid="daily-sales-chart" class="bg-white rounded-lg shadow p-4 mb-6">
        <h2 class="text-lg font-semibold mb-4">Gunluk Satis Grafigi</h2>
        <apexchart
          type="bar"
          height="350"
          :options="chartOptions"
          :series="chartSeries"
        />
      </div>

      <!-- Daily Breakdown Table -->
      <div v-if="analytics.data.daily_breakdown.length > 0" class="bg-white rounded-lg shadow overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tarih</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Kasa</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">POS</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Fark</th>
              <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Durum</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="record in analytics.data.daily_breakdown" :key="record.date">
              <td class="px-4 py-3 text-sm text-gray-900">{{ formatDate(record.date) }}</td>
              <td class="px-4 py-3 text-sm text-right text-gray-900">{{ formatCurrency(record.kasa_total) }}</td>
              <td class="px-4 py-3 text-sm text-right text-gray-900">{{ formatCurrency(record.pos_total) }}</td>
              <td
                class="px-4 py-3 text-sm text-right font-medium"
                :class="record.diff_total >= 0 ? 'text-green-600' : 'text-red-600'"
              >
                {{ formatCurrency(record.diff_total) }}
              </td>
              <td class="px-4 py-3 text-center">
                <span
                  class="px-2 py-1 text-xs rounded-full"
                  :class="statusClass(record.status)"
                >
                  {{ record.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Meta Info -->
      <div class="mt-4 text-sm text-gray-500">
        <p>{{ analytics.meta.record_count }} kayit | Olusturulma: {{ formatDateTime(analytics.meta.generated_at) }}</p>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, shallowRef, computed, onMounted } from 'vue'
import type { AnalyticsEnvelope } from '@/types'
import { analyticsApi } from '@/services/api'
import type { ApexOptions } from 'apexcharts'

// Use shallowRef for chart data to avoid deep reactivity issues with ApexCharts
const analytics = shallowRef<AnalyticsEnvelope | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

// Export state
const showExportMenu = ref(false)
const exporting = ref(false)

// Date range - default to last 30 days
const today = new Date()
const thirtyDaysAgo = new Date(today)
thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)

const startDate = ref(thirtyDaysAgo.toISOString().split('T')[0])
const endDate = ref(today.toISOString().split('T')[0])

// Chart configuration - computed from analytics data
const chartOptions = computed<ApexOptions>(() => ({
  chart: {
    type: 'bar' as const,
    stacked: false,
    toolbar: {
      show: true
    }
  },
  plotOptions: {
    bar: {
      horizontal: false,
      columnWidth: '55%'
    }
  },
  dataLabels: {
    enabled: false
  },
  stroke: {
    show: true,
    width: 2,
    colors: ['transparent']
  },
  xaxis: {
    categories: analytics.value?.data.daily_breakdown.map(d => formatDate(d.date)) || [],
    labels: {
      rotate: -45
    }
  },
  yaxis: {
    title: {
      text: 'TL'
    },
    labels: {
      formatter: (val: number) => formatCurrency(val)
    }
  },
  fill: {
    opacity: 1
  },
  tooltip: {
    y: {
      formatter: (val: number) => formatCurrency(val)
    }
  },
  colors: ['#3B82F6', '#10B981', '#EF4444']
}))

const chartSeries = computed(() => {
  if (!analytics.value) return []

  const breakdown = analytics.value.data.daily_breakdown
  return [
    {
      name: 'Kasa',
      data: breakdown.map(d => d.kasa_total)
    },
    {
      name: 'POS',
      data: breakdown.map(d => d.pos_total)
    },
    {
      name: 'Fark',
      data: breakdown.map(d => d.diff_total)
    }
  ]
})

// Context Guard - verify we have branch context
const branchId = localStorage.getItem('currentBranchId')
if (!branchId) {
  console.warn('No branch context available - analytics may show unexpected data')
}

async function loadAnalytics() {
  loading.value = true
  error.value = null

  try {
    const response = await analyticsApi.getDailySalesAnalytics({
      start_date: startDate.value,
      end_date: endDate.value
    })
    // Use shallowRef assignment to avoid deep reactivity
    analytics.value = response.data
  } catch (err: unknown) {
    const axiosError = err as { response?: { data?: { detail?: string } } }
    error.value = axiosError.response?.data?.detail || 'Veri yuklenirken hata olustu'
    console.error('Analytics load error:', err)
  } finally {
    loading.value = false
  }
}

async function exportData(format: 'csv' | 'excel') {
  exporting.value = true
  showExportMenu.value = false

  try {
    const response = await analyticsApi.exportDailySalesAnalytics({
      start_date: startDate.value,
      end_date: endDate.value,
      format
    })

    // Create blob from response
    const blob = new Blob([response.data], {
      type: format === 'csv' ? 'text/csv' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })

    // Create download link
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `analytics_${startDate.value}_${endDate.value}.${format === 'csv' ? 'csv' : 'xlsx'}`

    // Trigger download
    document.body.appendChild(link)
    link.click()

    // Cleanup
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (err: unknown) {
    const axiosError = err as { response?: { data?: { detail?: string } } }
    error.value = axiosError.response?.data?.detail || 'Disa aktarma sirasinda hata olustu'
    console.error('Export error:', err)
  } finally {
    exporting.value = false
  }
}

// Formatters
function formatCurrency(value: number): string {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('tr-TR', {
    day: '2-digit',
    month: 'short'
  })
}

function formatDateTime(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleString('tr-TR')
}

function statusClass(status: string): string {
  switch (status) {
    case 'resolved':
      return 'bg-green-100 text-green-800'
    case 'reviewed':
      return 'bg-blue-100 text-blue-800'
    case 'flagged':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

onMounted(() => {
  loadAnalytics()
})
</script>

<script lang="ts">
import VueApexCharts from 'vue3-apexcharts'

export default {
  components: {
    apexchart: VueApexCharts
  }
}
</script>
