<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { paymentsApi } from '@/services'
import type { SupplierPayment, PaymentFilters, PaymentType } from '@/types'

const payments = ref<SupplierPayment[]>([])
const loading = ref(true)
const error = ref('')

const filters = ref<PaymentFilters>({
  start_date: new Date().toISOString().split('T')[0],
  end_date: new Date().toISOString().split('T')[0]
})

const paymentTypeLabels: Record<PaymentType, string> = {
  cash: 'Nakit',
  eft: 'EFT',
  check: 'Çek',
  promissory: 'Senet',
  partial: 'Kısmi'
}

const summary = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  return {
    today: payments.value
      .filter(p => p.payment_date.startsWith(today))
      .reduce((sum, p) => sum + Number(p.amount), 0),
    total: payments.value.reduce((sum, p) => sum + Number(p.amount), 0)
  }
})

async function loadPayments() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await paymentsApi.getPayments(filters.value)
    payments.value = data
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

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('tr-TR')
}

onMounted(loadPayments)
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
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-white rounded-lg shadow p-4">
          <p class="text-sm text-gray-500">Bugün</p>
          <p class="text-2xl font-bold text-brand-red">
            {{ formatCurrency(summary.today) }}
          </p>
        </div>
        <div class="bg-white rounded-lg shadow p-4">
          <p class="text-sm text-gray-500">Toplam</p>
          <p class="text-2xl font-bold text-gray-900">
            {{ formatCurrency(summary.total) }}
          </p>
        </div>
      </div>

      <!-- Table -->
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <div v-if="payments.length === 0" class="p-8 text-center text-gray-500">
          Ödeme kaydı bulunamadı
        </div>

        <table v-else class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tarih</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tedarikçi</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tür</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Tutar</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Açıklama</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="payment in payments" :key="payment.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 text-sm text-gray-900">
                {{ formatDate(payment.payment_date) }}
              </td>
              <td class="px-6 py-4 text-sm font-medium text-gray-900">
                🏪 {{ payment.supplier_name }}
              </td>
              <td class="px-6 py-4">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  {{ paymentTypeLabels[payment.payment_type] }}
                </span>
              </td>
              <td class="px-6 py-4 text-sm text-right font-semibold text-gray-900">
                {{ formatCurrency(Number(payment.amount)) }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                {{ payment.description || '-' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>
