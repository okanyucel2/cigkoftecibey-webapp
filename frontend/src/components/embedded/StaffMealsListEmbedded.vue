<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { StaffMeal, StaffMealSummary } from '@/types'
import { extractErrorMessage } from '@/types'
import { staffMealsApi } from '@/services/api'
import { useFormatters } from '@/composables'
import { Loader2, Coffee, Users, Calendar, TrendingUp } from 'lucide-vue-next'

interface Props {
  embedded?: boolean
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'action', type: 'add' | 'edit' | 'delete', item?: StaffMeal): void
}>()

const { formatCurrency } = useFormatters()

// Data
const meals = ref<StaffMeal[]>([])
const summary = ref<StaffMealSummary | null>(null)
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
    const [mealsRes, summaryRes] = await Promise.all([
      staffMealsApi.getAll({ month: currentMonth, year: currentYear }),
      staffMealsApi.getSummary({ month: currentMonth, year: currentYear })
    ])
    meals.value = mealsRes.data
    summary.value = summaryRes.data
  } catch (e: unknown) {
    error.value = extractErrorMessage(e, 'Veri yüklenemedi')
  } finally {
    loading.value = false
  }
}

// Format helpers
function formatMealDate(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' })
}
</script>

<template>
  <div class="space-y-4">
    <!-- Summary Row -->
    <div class="grid grid-cols-4 gap-2">
      <div class="bg-emerald-50 rounded-lg p-3 text-center">
        <Coffee class="w-4 h-4 mx-auto text-emerald-600 mb-1" />
        <div class="text-lg font-bold text-emerald-700">
          {{ formatCurrency(summary?.total_cost || 0) }}
        </div>
        <div class="text-xs text-emerald-600">Toplam</div>
      </div>
      <div class="bg-blue-50 rounded-lg p-3 text-center">
        <Users class="w-4 h-4 mx-auto text-blue-600 mb-1" />
        <div class="text-lg font-bold text-blue-700">
          {{ summary?.total_staff_count || 0 }}
        </div>
        <div class="text-xs text-blue-600">Kişi</div>
      </div>
      <div class="bg-purple-50 rounded-lg p-3 text-center">
        <TrendingUp class="w-4 h-4 mx-auto text-purple-600 mb-1" />
        <div class="text-lg font-bold text-purple-700">
          {{ Number(summary?.avg_daily_staff || 0).toFixed(1) }}
        </div>
        <div class="text-xs text-purple-600">Ort/Gün</div>
      </div>
      <div class="bg-gray-50 rounded-lg p-3 text-center">
        <Calendar class="w-4 h-4 mx-auto text-gray-600 mb-1" />
        <div class="text-lg font-bold text-gray-700">
          {{ summary?.days_count || 0 }}
        </div>
        <div class="text-xs text-gray-600">Gün</div>
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
    <div v-else-if="meals.length === 0" class="text-center py-8 text-gray-500">
      Bu ay için kayıt bulunamadı
    </div>

    <!-- Table -->
    <div v-else class="overflow-y-auto max-h-[50vh] rounded-lg border border-gray-200">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 sticky top-0">
          <tr>
            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Tarih</th>
            <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase">Kişi</th>
            <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">Birim</th>
            <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">Toplam</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr
            v-for="meal in meals"
            :key="meal.id"
            class="hover:bg-gray-50 cursor-pointer"
            @click="emit('action', 'edit', meal)"
          >
            <td class="px-3 py-2 text-gray-900">{{ formatMealDate(meal.meal_date) }}</td>
            <td class="px-3 py-2 text-center text-gray-700">{{ meal.staff_count }}</td>
            <td class="px-3 py-2 text-right text-gray-500">{{ formatCurrency(Number(meal.unit_price)) }}</td>
            <td class="px-3 py-2 text-right font-medium text-gray-900">
              {{ formatCurrency(Number(meal.total)) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>
