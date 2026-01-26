<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { Expense, ExpenseCategory } from '@/types'
import { expensesApi, expenseCategoriesApi } from '@/services/api'
import { useFormatters } from '@/composables'
import { Loader2, Receipt, Tag, Calendar, TrendingDown } from 'lucide-vue-next'

interface Props {
  embedded?: boolean
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'action', type: 'add' | 'edit' | 'delete', item?: Expense): void
}>()

const { formatCurrency } = useFormatters()

// Data
const expenses = ref<Expense[]>([])
const categories = ref<ExpenseCategory[]>([])
const loading = ref(true)
const error = ref('')

// Get current month's data
const currentMonth = new Date().getMonth() + 1
const currentYear = new Date().getFullYear()
const startDate = new Date(currentYear, currentMonth - 1, 1).toISOString().split('T')[0]
const endDate = new Date(currentYear, currentMonth, 0).toISOString().split('T')[0]

onMounted(async () => {
  await Promise.all([loadExpenses(), loadCategories()])
})

async function loadCategories() {
  try {
    const { data } = await expenseCategoriesApi.getAll()
    categories.value = data
  } catch (e) {
    console.error('Failed to load categories:', e)
  }
}

async function loadExpenses() {
  loading.value = true
  try {
    const { data } = await expensesApi.getAll({
      start_date: startDate,
      end_date: endDate
    })
    expenses.value = data
  } catch (e) {
    error.value = 'Giderler yüklenemedi'
  } finally {
    loading.value = false
  }
}

// Computed summaries
const totalExpenses = computed(() => expenses.value.reduce((sum, e) => sum + Number(e.amount), 0))
const fixedExpenses = computed(() => expenses.value.filter(e => e.category?.is_fixed).reduce((sum, e) => sum + Number(e.amount), 0))
const variableExpenses = computed(() => totalExpenses.value - fixedExpenses.value)
const expenseCount = computed(() => expenses.value.length)

// Group by category for summary
const byCategory = computed(() => {
  const grouped: Record<string, number> = {}
  for (const exp of expenses.value) {
    const catName = exp.category?.name || 'Diğer'
    grouped[catName] = (grouped[catName] || 0) + Number(exp.amount)
  }
  return Object.entries(grouped)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
})

// Format helpers
function formatExpenseDate(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' })
}

function getCategoryColor(categoryName: string) {
  const colors: Record<string, string> = {
    'Kira': 'bg-red-100 text-red-700',
    'Personel': 'bg-blue-100 text-blue-700',
    'Elektrik': 'bg-yellow-100 text-yellow-700',
    'Su': 'bg-cyan-100 text-cyan-700',
    'Malzeme': 'bg-green-100 text-green-700'
  }
  return colors[categoryName] || 'bg-gray-100 text-gray-700'
}
</script>

<template>
  <div class="space-y-4">
    <!-- Summary Row -->
    <div class="grid grid-cols-4 gap-2">
      <div class="bg-red-50 rounded-lg p-3 text-center">
        <Receipt class="w-4 h-4 mx-auto text-red-600 mb-1" />
        <div class="text-lg font-bold text-red-700">
          {{ formatCurrency(totalExpenses) }}
        </div>
        <div class="text-xs text-red-600">Toplam</div>
      </div>
      <div class="bg-amber-50 rounded-lg p-3 text-center">
        <TrendingDown class="w-4 h-4 mx-auto text-amber-600 mb-1" />
        <div class="text-lg font-bold text-amber-700">
          {{ formatCurrency(fixedExpenses) }}
        </div>
        <div class="text-xs text-amber-600">Sabit</div>
      </div>
      <div class="bg-purple-50 rounded-lg p-3 text-center">
        <Tag class="w-4 h-4 mx-auto text-purple-600 mb-1" />
        <div class="text-lg font-bold text-purple-700">
          {{ formatCurrency(variableExpenses) }}
        </div>
        <div class="text-xs text-purple-600">Değişken</div>
      </div>
      <div class="bg-gray-50 rounded-lg p-3 text-center">
        <Calendar class="w-4 h-4 mx-auto text-gray-600 mb-1" />
        <div class="text-lg font-bold text-gray-700">
          {{ expenseCount }}
        </div>
        <div class="text-xs text-gray-600">Kayıt</div>
      </div>
    </div>

    <!-- Top Categories -->
    <div v-if="byCategory.length > 0" class="flex flex-wrap gap-2">
      <div
        v-for="[name, amount] in byCategory"
        :key="name"
        class="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium"
        :class="getCategoryColor(name)"
      >
        <span>{{ name }}</span>
        <span class="opacity-75">{{ formatCurrency(amount) }}</span>
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
    <div v-else-if="expenses.length === 0" class="text-center py-8 text-gray-500">
      Bu ay için gider kaydı bulunamadı
    </div>

    <!-- Table -->
    <div v-else class="overflow-y-auto max-h-[45vh] rounded-lg border border-gray-200">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 sticky top-0">
          <tr>
            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Tarih</th>
            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Kategori</th>
            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Açıklama</th>
            <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">Tutar</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr
            v-for="expense in expenses.slice(0, 20)"
            :key="expense.id"
            class="hover:bg-gray-50 cursor-pointer"
            @click="emit('action', 'edit', expense)"
          >
            <td class="px-3 py-2 text-gray-900">{{ formatExpenseDate(expense.expense_date) }}</td>
            <td class="px-3 py-2">
              <span
                class="px-2 py-0.5 rounded text-xs font-medium"
                :class="getCategoryColor(expense.category?.name || 'Diğer')"
              >
                {{ expense.category?.name || 'Diğer' }}
              </span>
            </td>
            <td class="px-3 py-2 text-gray-600 truncate max-w-[150px]">{{ expense.description || '-' }}</td>
            <td class="px-3 py-2 text-right font-medium text-gray-900">
              {{ formatCurrency(Number(expense.amount)) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add Button -->
    <button
      type="button"
      class="w-full py-2 text-sm font-medium text-amber-600 bg-amber-50 rounded-lg hover:bg-amber-100 transition-colors"
      @click="emit('action', 'add')"
    >
      + Yeni Gider Ekle
    </button>
  </div>
</template>
