<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { CashDifference, CashDifferenceSummary } from '@/types'
import { extractErrorMessage } from '@/types'
import { cashDifferenceApi } from '@/services/api'
import { useFormatters } from '@/composables'
import { Loader2, AlertCircle, CheckCircle, Clock, Flag, TrendingUp, TrendingDown, Minus } from 'lucide-vue-next'

interface Props {
  embedded?: boolean
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'action', type: 'view' | 'import', item?: CashDifference): void
}>()

const { formatCurrency } = useFormatters()

// Data
const records = ref<CashDifference[]>([])
const summary = ref<CashDifferenceSummary | null>(null)
const loading = ref(true)
const error = ref('')

// Get current month's data
const currentMonth = new Date().getMonth() + 1
const currentYear = new Date().getFullYear()

onMounted(async () => {
  await loadData()
})

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const [recordsRes, summaryRes] = await Promise.all([
      cashDifferenceApi.getAll({ month: currentMonth, year: currentYear }),
      cashDifferenceApi.getSummary({ month: currentMonth, year: currentYear })
    ])
    records.value = recordsRes.data
    summary.value = summaryRes.data
  } catch (e: unknown) {
    error.value = extractErrorMessage(e, 'Veriler yüklenemedi')
  } finally {
    loading.value = false
  }
}

// Format helpers
function formatRecordDate(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' })
}

function getStatusIcon(status: string) {
  switch (status) {
    case 'resolved': return CheckCircle
    case 'flagged': return Flag
    case 'reviewed': return Clock
    default: return AlertCircle
  }
}

function getStatusClass(status: string) {
  switch (status) {
    case 'resolved': return 'text-emerald-600'
    case 'flagged': return 'text-red-600'
    case 'reviewed': return 'text-amber-600'
    default: return 'text-gray-400'
  }
}

function getDifferenceClass(diff: number) {
  const absDiff = Math.abs(diff)
  if (absDiff <= 50) return 'text-emerald-600 bg-emerald-50'
  if (absDiff <= 200) return 'text-amber-600 bg-amber-50'
  return 'text-red-600 bg-red-50'
}
</script>

<template>
  <div class="space-y-4">
    <!-- Summary Row -->
    <div class="grid grid-cols-3 gap-2">
      <div class="bg-gray-50 rounded-lg p-3 text-center">
        <div class="text-lg font-bold text-gray-700">
          {{ summary?.total_records || 0 }}
        </div>
        <div class="text-xs text-gray-600">Gün</div>
      </div>
      <div class="rounded-lg p-3 text-center" :class="(summary?.total_diff || 0) >= 0 ? 'bg-emerald-50' : 'bg-red-50'">
        <div class="flex items-center justify-center gap-1">
          <component
            :is="(summary?.total_diff || 0) > 0 ? TrendingUp : (summary?.total_diff || 0) < 0 ? TrendingDown : Minus"
            class="w-4 h-4"
            :class="(summary?.total_diff || 0) >= 0 ? 'text-emerald-600' : 'text-red-600'"
          />
          <span class="text-lg font-bold" :class="(summary?.total_diff || 0) >= 0 ? 'text-emerald-700' : 'text-red-700'">
            {{ formatCurrency(Math.abs(summary?.total_diff || 0)) }}
          </span>
        </div>
        <div class="text-xs" :class="(summary?.total_diff || 0) >= 0 ? 'text-emerald-600' : 'text-red-600'">
          Toplam Fark
        </div>
      </div>
      <div class="bg-blue-50 rounded-lg p-3 text-center">
        <div class="text-lg font-bold text-blue-700">
          {{ summary?.pending_count || 0 }}
        </div>
        <div class="text-xs text-blue-600">Bekleyen</div>
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
    <div v-else-if="records.length === 0" class="text-center py-8 text-gray-500">
      Bu ay için kayıt bulunamadı
    </div>

    <!-- Table -->
    <div v-else class="overflow-y-auto max-h-[50vh] rounded-lg border border-gray-200">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 sticky top-0">
          <tr>
            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Tarih</th>
            <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">Kasa</th>
            <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">POS</th>
            <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">Fark</th>
            <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase">Durum</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr
            v-for="record in records"
            :key="record.id"
            class="hover:bg-gray-50 cursor-pointer"
            @click="emit('action', 'view', record)"
          >
            <td class="px-3 py-2 text-gray-900">{{ formatRecordDate(record.difference_date) }}</td>
            <td class="px-3 py-2 text-right text-gray-700">{{ formatCurrency(record.kasa_total) }}</td>
            <td class="px-3 py-2 text-right text-gray-700">{{ formatCurrency(record.pos_total) }}</td>
            <td class="px-3 py-2 text-right">
              <span
                class="inline-block px-2 py-0.5 rounded text-xs font-medium"
                :class="getDifferenceClass(record.diff_total)"
              >
                {{ record.diff_total >= 0 ? '+' : '' }}{{ formatCurrency(record.diff_total) }}
              </span>
            </td>
            <td class="px-3 py-2 text-center">
              <component
                :is="getStatusIcon(record.status)"
                class="w-4 h-4 mx-auto"
                :class="getStatusClass(record.status)"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Import Button -->
    <button
      type="button"
      class="w-full py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
      @click="emit('action', 'import')"
    >
      Excel'den İçe Aktar
    </button>
  </div>
</template>
