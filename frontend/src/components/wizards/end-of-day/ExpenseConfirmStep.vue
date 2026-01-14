<template>
  <div class="space-y-4">
    <!-- Instruction -->
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <p class="text-sm text-blue-700">
        Bugunku giderleri kontrol edin ve onaylayin.
        Eksik veya hatali kayit varsa duzenleme icin ilgili sayfaya gidin.
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="space-y-3">
      <div v-for="i in 4" :key="i" class="animate-pulse">
        <div class="bg-gray-100 rounded-lg h-16" />
      </div>
    </div>

    <!-- Expense List -->
    <div v-else class="space-y-3">
      <div
        v-for="expense in expenses"
        :key="expense.id"
        :class="[
          'rounded-lg border p-4 transition-colors',
          expense.confirmed
            ? 'bg-emerald-50 border-emerald-200'
            : 'bg-white border-gray-200 hover:border-gray-300'
        ]"
      >
        <label class="flex items-start gap-3 cursor-pointer">
          <input
            type="checkbox"
            :checked="expense.confirmed"
            @change="toggleExpense(expense.id)"
            class="mt-1 h-5 w-5 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500"
          />
          <div class="flex-1 min-w-0">
            <div class="flex justify-between items-start gap-2">
              <span class="font-medium text-gray-900 text-sm">{{ expense.description }}</span>
              <span class="font-semibold text-gray-900 whitespace-nowrap">
                {{ formatCurrency(expense.amount) }}
              </span>
            </div>
          </div>
        </label>
      </div>

      <!-- Empty State -->
      <div
        v-if="expenses.length === 0"
        class="text-center py-8 text-gray-500"
      >
        <Package class="w-12 h-12 mx-auto mb-3 text-gray-300" />
        <p>Bugune ait gider kaydedilmemis</p>
      </div>
    </div>

    <!-- Summary -->
    <div v-if="expenses.length > 0" class="bg-gray-50 rounded-lg p-4 mt-4">
      <div class="flex justify-between items-center">
        <span class="text-sm text-gray-600">Toplam Gider</span>
        <span class="text-lg font-bold text-gray-900">{{ formatCurrency(totalExpenses) }}</span>
      </div>
      <div class="flex justify-between items-center mt-2 text-sm">
        <span class="text-gray-500">Onaylanan</span>
        <span :class="allConfirmed ? 'text-emerald-600' : 'text-amber-600'">
          {{ confirmedCount }}/{{ expenses.length }}
        </span>
      </div>
    </div>

    <!-- Add Missing Expense Button -->
    <button
      type="button"
      class="w-full mt-4 flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors border border-dashed border-blue-200"
      @click="emit('add-expense')"
    >
      <Plus class="w-4 h-4" />
      Eksik Gider Ekle
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Package, Plus } from 'lucide-vue-next'

interface ExpenseItem {
  id: number
  description: string
  amount: number
  confirmed: boolean
}

interface Props {
  expenses: ExpenseItem[]
  loading?: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:expenses': [value: ExpenseItem[]]
  'add-expense': []
}>()

function toggleExpense(id: number) {
  const updated = props.expenses.map(e =>
    e.id === id ? { ...e, confirmed: !e.confirmed } : e
  )
  emit('update:expenses', updated)
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 2
  }).format(value)
}

const totalExpenses = computed(() =>
  props.expenses.reduce((sum, e) => sum + e.amount, 0)
)

const confirmedCount = computed(() =>
  props.expenses.filter(e => e.confirmed).length
)

const allConfirmed = computed(() =>
  props.expenses.length > 0 && props.expenses.every(e => e.confirmed)
)
</script>
