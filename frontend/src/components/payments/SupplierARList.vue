<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { paymentsApi } from '@/services'
import type { SupplierARSummary } from '@/types'
import { extractErrorMessage } from '@/types'

// Expose refresh function for parent component
defineExpose({
  refresh: loadData
})

const suppliers = ref<SupplierARSummary[]>([])
const loading = ref(true)
const error = ref('')
const filter = ref<'all' | 'debtors' | 'creditors'>('all')

// Filter options with proper typing
const filterOptions = [
  { id: 'all' as const, label: 'Tümü' },
  { id: 'debtors' as const, label: 'Sadece Borçlu' },
  { id: 'creditors' as const, label: 'Sadece Alacaklı' }
]

const filteredSuppliers = computed(() => {
  switch (filter.value) {
    case 'debtors':
      return suppliers.value.filter(s => s.balance > 0)
    case 'creditors':
      return suppliers.value.filter(s => s.balance < 0)
    default:
      return suppliers.value
  }
})

const summary = computed(() => {
  return suppliers.value.reduce((acc, s) => ({
    totalDebt: acc.totalDebt + Math.max(0, s.balance),
    totalCredit: acc.totalCredit + Math.abs(Math.min(0, s.balance)),
    debtorCount: acc.debtorCount + (s.balance > 0 ? 1 : 0)
  }), {
    totalDebt: 0,
    totalCredit: 0,
    debtorCount: 0
  })
})

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const response = await paymentsApi.getSupplierAR()
    suppliers.value = response.data
  } catch (e: unknown) {
    error.value = extractErrorMessage(e, 'Veri yüklenirken hata oluştu')
  } finally {
    loading.value = false
  }
}

function formatCurrency(amount: number) {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY'
  }).format(Math.abs(amount))
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">Tedarikçi Cari Hesap</h2>
        <p class="text-gray-600 mt-1">Borç ve alacak takibi</p>
      </div>
      <button
        @click="loadData"
        class="px-4 py-2 bg-brand-red text-white rounded-lg hover:bg-red-700 transition-colors"
        :disabled="loading"
      >
        {{ loading ? 'Yükleniyor...' : 'Yenile' }}
      </button>
    </div>

    <!-- Error -->
    <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
      {{ error }}
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow p-4">
        <p class="text-sm text-gray-500">Toplam Borç</p>
        <p class="text-2xl font-bold text-red-600">
          {{ formatCurrency(summary.totalDebt) }}
        </p>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <p class="text-sm text-gray-500">Toplam Alacak</p>
        <p class="text-2xl font-bold text-green-600">
          {{ formatCurrency(summary.totalCredit) }}
        </p>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <p class="text-sm text-gray-500">Borçlu Tedarikçi</p>
        <p class="text-2xl font-bold text-gray-900">
          {{ summary.debtorCount }}
        </p>
      </div>
    </div>

    <!-- Filters -->
    <div class="flex items-center gap-3">
      <span class="text-sm text-gray-600">Filtre:</span>
      <button
        v-for="f in filterOptions"
        :key="f.id"
        @click="filter = f.id"
        :class="[
          'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
          filter === f.id
            ? 'bg-brand-red text-white'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        ]"
      >
        {{ f.label }}
      </button>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div v-if="filteredSuppliers.length === 0" class="p-8 text-center text-gray-500">
        Kayıt bulunamadı
      </div>

      <table v-else class="w-full">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tedarikçi</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Bakiye</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Son Hareket</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Borç</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Alacak</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr
            v-for="supplier in filteredSuppliers"
            :key="supplier.id"
            class="hover:bg-gray-50"
          >
            <td class="px-6 py-4 text-sm font-medium text-gray-900">
              🏪 {{ supplier.name }}
            </td>
            <td class="px-6 py-4 text-sm">
              <span
                :class="supplier.balance > 0 ? 'text-red-600' : 'text-green-600'"
                class="font-medium"
              >
                {{ formatCurrency(supplier.balance) }}
              </span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-500">
              {{ supplier.last_transaction_date || '-' }}
            </td>
            <td class="px-6 py-4 text-right text-sm text-red-600 font-medium">
              {{ supplier.balance > 0 ? formatCurrency(supplier.balance) : '-' }}
            </td>
            <td class="px-6 py-4 text-right text-sm text-green-600 font-medium">
              {{ supplier.balance < 0 ? formatCurrency(Math.abs(supplier.balance)) : '-' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
