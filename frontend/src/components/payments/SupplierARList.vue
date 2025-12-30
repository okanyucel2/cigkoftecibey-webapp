<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { paymentsApi } from '@/services'
import type { SupplierARSummary } from '@/types'

// Expose refresh function for parent component
defineExpose({
  refresh: loadData
})

const suppliers = ref<SupplierARSummary[]>([])
const loading = ref(true)
const error = ref('')
const filter = ref<'all' | 'debtors' | 'creditors'>('all')

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

const summary = computed(() => ({
  totalBalance: suppliers.value.reduce((sum, s) => sum + Number(s.balance), 0),
  totalDebt: suppliers.value.reduce((sum, s) => sum + Number(s.total_debt), 0),
  totalCredit: suppliers.value.reduce((sum, s) => sum + Number(s.total_credit), 0),
  debtorCount: suppliers.value.filter(s => s.balance > 0).length
}))

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await paymentsApi.getSupplierAR()
    suppliers.value = data.sort((a, b) => Number(b.balance) - Number(a.balance))
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Veri yüklenemedi'
  } finally {
    loading.value = false
  }
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY'
  }).format(amount)
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('tr-TR')
}

onMounted(loadData)
</script>

<template>
  <div class="space-y-6">
    <!-- Error -->
    <div v-if="error" class="bg-red-100 text-red-700 p-4 rounded-lg">
      {{ error }}
      <button @click="error = ''" class="ml-2 font-bold">x</button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-8 text-gray-500">
      Yükleniyor...
    </div>

    <template v-else>
      <!-- Summary Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="bg-white rounded-lg shadow p-4">
          <p class="text-sm text-gray-500">Toplam Bakiye</p>
          <p class="text-2xl font-bold" :class="summary.totalBalance > 0 ? 'text-red-600' : 'text-green-600'">
            {{ formatCurrency(summary.totalBalance) }}
          </p>
        </div>
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
          v-for="f in [
            { id: 'all', label: 'Tümü' },
            { id: 'debtors', label: 'Sadece Borçlu' },
            { id: 'creditors', label: 'Sadece Alacaklı' }
          ]"
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
              <td class="px-6 py-4 text-sm font-medium" :class="{
                'text-red-600': supplier.balance > 0,
                'text-green-600': supplier.balance < 0,
                'text-gray-500': supplier.balance === 0
              }">
                {{ formatCurrency(Number(supplier.balance)) }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-500">
                {{ formatDate(supplier.last_transaction_date) }}
              </td>
              <td class="px-6 py-4 text-sm text-right text-gray-900">
                {{ formatCurrency(Number(supplier.total_debt)) }}
              </td>
              <td class="px-6 py-4 text-sm text-right text-gray-900">
                {{ formatCurrency(Number(supplier.total_credit)) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>
