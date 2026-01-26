<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { DailyProduction, ProductionSummary } from '@/types'
import { extractErrorMessage } from '@/types'
import { productionApi } from '@/services/api'
import { useFormatters } from '@/composables'
import { Loader2, Factory, Scale, Layers, TrendingUp } from 'lucide-vue-next'

interface Props {
  embedded?: boolean
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'action', type: 'add' | 'edit' | 'view', item?: DailyProduction): void
}>()

const { formatCurrency, formatNumber } = useFormatters()

// Data
const productions = ref<DailyProduction[]>([])
const summary = ref<ProductionSummary | null>(null)
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
    const [prodRes, summaryRes] = await Promise.all([
      productionApi.getAll({ month: currentMonth, year: currentYear }),
      productionApi.getSummary({ month: currentMonth, year: currentYear })
    ])
    productions.value = prodRes.data
    summary.value = summaryRes.data
  } catch (e: unknown) {
    error.value = extractErrorMessage(e, 'Veri yüklenemedi')
  } finally {
    loading.value = false
  }
}

// Format helpers
function formatProductionDate(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' })
}

function getTypeLabel(type: string) {
  return type === 'etli' ? 'Etli' : 'Etsiz'
}

function getTypeClass(type: string) {
  return type === 'etli' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
}
</script>

<template>
  <div class="space-y-4">
    <!-- Summary Row -->
    <div class="grid grid-cols-4 gap-2">
      <div class="bg-purple-50 rounded-lg p-3 text-center">
        <Scale class="w-4 h-4 mx-auto text-purple-600 mb-1" />
        <div class="text-lg font-bold text-purple-700">
          {{ formatNumber(summary?.total_kneaded_kg || 0) }} kg
        </div>
        <div class="text-xs text-purple-600">Toplam</div>
      </div>
      <div class="bg-blue-50 rounded-lg p-3 text-center">
        <Layers class="w-4 h-4 mx-auto text-blue-600 mb-1" />
        <div class="text-lg font-bold text-blue-700">
          {{ formatNumber(summary?.total_legen_count || 0) }}
        </div>
        <div class="text-xs text-blue-600">Legen</div>
      </div>
      <div class="bg-emerald-50 rounded-lg p-3 text-center">
        <TrendingUp class="w-4 h-4 mx-auto text-emerald-600 mb-1" />
        <div class="text-lg font-bold text-emerald-700">
          {{ formatNumber(summary?.avg_daily_kg || 0) }} kg
        </div>
        <div class="text-xs text-emerald-600">Ort/Gün</div>
      </div>
      <div class="bg-amber-50 rounded-lg p-3 text-center">
        <Factory class="w-4 h-4 mx-auto text-amber-600 mb-1" />
        <div class="text-lg font-bold text-amber-700">
          {{ formatCurrency(summary?.total_cost || 0) }}
        </div>
        <div class="text-xs text-amber-600">Maliyet</div>
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
    <div v-else-if="productions.length === 0" class="text-center py-8 text-gray-500">
      Bu ay için üretim kaydı bulunamadı
    </div>

    <!-- Table -->
    <div v-else class="overflow-y-auto max-h-[50vh] rounded-lg border border-gray-200">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 sticky top-0">
          <tr>
            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Tarih</th>
            <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase">Tip</th>
            <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">Yoğrulan</th>
            <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">Legen</th>
            <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">Maliyet</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr
            v-for="prod in productions"
            :key="prod.id"
            class="hover:bg-gray-50 cursor-pointer"
            @click="emit('action', 'edit', prod)"
          >
            <td class="px-3 py-2 text-gray-900">{{ formatProductionDate(prod.production_date) }}</td>
            <td class="px-3 py-2 text-center">
              <span
                class="px-2 py-0.5 rounded text-xs font-medium"
                :class="getTypeClass(prod.production_type || 'etli')"
              >
                {{ getTypeLabel(prod.production_type || 'etli') }}
              </span>
            </td>
            <td class="px-3 py-2 text-right text-gray-700">{{ formatNumber(prod.kneaded_kg) }} kg</td>
            <td class="px-3 py-2 text-right text-gray-700">{{ formatNumber(prod.legen_count || 0) }}</td>
            <td class="px-3 py-2 text-right font-medium text-gray-900">
              {{ formatCurrency(prod.total_cost || 0) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add Button -->
    <button
      type="button"
      class="w-full py-2 text-sm font-medium text-purple-600 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors"
      @click="emit('action', 'add')"
    >
      + Yeni Üretim Ekle
    </button>
  </div>
</template>
