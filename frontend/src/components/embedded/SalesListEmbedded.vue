<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { OnlineSale, OnlineSalesSummary, ChannelsGrouped } from '@/types'
import { unifiedSalesApi, onlineSalesApi } from '@/services/api'
import { useFormatters } from '@/composables'
import { Loader2, Wallet, Store, Smartphone } from 'lucide-vue-next'

interface Props {
  embedded?: boolean
}

defineProps<Props>()

const { formatCurrency } = useFormatters()

// Data
const channels = ref<ChannelsGrouped>({ pos: [], online: [] })
const sales = ref<OnlineSale[]>([])
const summary = ref<OnlineSalesSummary | null>(null)
const loading = ref(true)
const error = ref('')

// Get current month's data
const currentMonth = new Date().getMonth() + 1
const currentYear = new Date().getFullYear()

onMounted(async () => {
  await Promise.all([loadChannels(), loadData()])
})

async function loadChannels() {
  try {
    const { data } = await unifiedSalesApi.getChannels()
    channels.value = data
  } catch (e) {
    console.error('Failed to load channels:', e)
  }
}

async function loadData() {
  loading.value = true
  try {
    const startDate = new Date(currentYear, currentMonth - 1, 1)
    const endDate = new Date(currentYear, currentMonth, 0)

    const [salesRes, summaryRes] = await Promise.all([
      onlineSalesApi.getSales({
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0]
      }),
      onlineSalesApi.getSummary({
        year: currentYear,
        month: currentMonth
      })
    ])

    sales.value = salesRes.data
    summary.value = summaryRes.data
  } catch (e) {
    error.value = 'Veriler yüklenemedi'
  } finally {
    loading.value = false
  }
}

// Group sales by date
const salesByDate = computed(() => {
  const grouped: Record<string, Record<number, OnlineSale>> = {}

  for (const sale of sales.value) {
    if (!grouped[sale.sale_date]) {
      grouped[sale.sale_date] = {}
    }
    grouped[sale.sale_date][sale.platform_id] = sale
  }

  return Object.entries(grouped)
    .sort((a, b) => b[0].localeCompare(a[0]))
    .slice(0, 10) // Show last 10 days
    .map(([date, channelSales]) => ({
      date,
      sales: channelSales,
      total: Object.values(channelSales).reduce((sum, s) => sum + Number(s.amount), 0)
    }))
})

// Format helpers
function formatSaleDate(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' })
}

// All channels combined
const allChannels = computed(() => [...channels.value.pos, ...channels.value.online])

// Get total for a channel
function getChannelTotal(channelName: string): number {
  if (!summary.value?.platform_totals) return 0
  return summary.value.platform_totals[channelName] || 0
}
</script>

<template>
  <div class="space-y-4">
    <!-- Summary Row -->
    <div class="grid grid-cols-3 gap-2">
      <div class="bg-emerald-50 rounded-lg p-3 text-center">
        <Wallet class="w-4 h-4 mx-auto text-emerald-600 mb-1" />
        <div class="text-lg font-bold text-emerald-700">
          {{ formatCurrency(summary?.total_amount || 0) }}
        </div>
        <div class="text-xs text-emerald-600">Toplam</div>
      </div>
      <div class="bg-blue-50 rounded-lg p-3 text-center">
        <Store class="w-4 h-4 mx-auto text-blue-600 mb-1" />
        <div class="text-lg font-bold text-blue-700">
          {{ formatCurrency(getChannelTotal('Salon') + getChannelTotal('Nakit') + getChannelTotal('Kart')) }}
        </div>
        <div class="text-xs text-blue-600">Kasa</div>
      </div>
      <div class="bg-purple-50 rounded-lg p-3 text-center">
        <Smartphone class="w-4 h-4 mx-auto text-purple-600 mb-1" />
        <div class="text-lg font-bold text-purple-700">
          {{ formatCurrency(getChannelTotal('Getir') + getChannelTotal('Yemeksepeti') + getChannelTotal('Trendyol')) }}
        </div>
        <div class="text-xs text-purple-600">Online</div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-8">
      <Loader2 class="w-6 h-6 animate-spin text-gray-400" />
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">
      {{ error }}
    </div>

    <!-- Empty State -->
    <div v-else-if="salesByDate.length === 0" class="text-center py-8 text-gray-500">
      Bu ay için satış kaydı bulunamadı
    </div>

    <!-- Table -->
    <div v-else class="overflow-y-auto max-h-[50vh] rounded-lg border border-gray-200">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 sticky top-0">
          <tr>
            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Tarih</th>
            <th
              v-for="channel in allChannels.slice(0, 4)"
              :key="channel.id"
              class="px-2 py-2 text-right text-xs font-medium text-gray-500 uppercase truncate max-w-[80px]"
            >
              {{ channel.name }}
            </th>
            <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">Toplam</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr
            v-for="day in salesByDate"
            :key="day.date"
            class="hover:bg-gray-50"
          >
            <td class="px-3 py-2 text-gray-900 font-medium">{{ formatSaleDate(day.date) }}</td>
            <td
              v-for="channel in allChannels.slice(0, 4)"
              :key="channel.id"
              class="px-2 py-2 text-right text-gray-600 text-xs"
            >
              {{ day.sales[channel.id] ? formatCurrency(Number(day.sales[channel.id].amount)) : '-' }}
            </td>
            <td class="px-3 py-2 text-right font-medium text-gray-900">
              {{ formatCurrency(day.total) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>
