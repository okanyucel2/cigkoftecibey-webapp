<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { MonthlyPayroll } from '@/types'
import { personnelApi } from '@/services/api'
import { useFormatters } from '@/composables'
import { Loader2, Wallet, Calendar, CreditCard } from 'lucide-vue-next'

interface Props {
  embedded?: boolean
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'action', type: 'add' | 'view', item?: MonthlyPayroll): void
}>()

const { formatCurrency } = useFormatters()

// Data
const payrolls = ref<MonthlyPayroll[]>([])
const loading = ref(true)
const error = ref('')

// Get current month's data
const currentMonth = new Date().getMonth() + 1
const currentYear = new Date().getFullYear()

onMounted(async () => {
  await loadPayrolls()
})

async function loadPayrolls() {
  loading.value = true
  try {
    const { data } = await personnelApi.getPayrolls({ month: currentMonth, year: currentYear })
    payrolls.value = data
  } catch (e) {
    error.value = 'Ödemeler yüklenemedi'
  } finally {
    loading.value = false
  }
}

// Computed summaries
const totalPayments = computed(() => payrolls.value.reduce((sum, p) => sum + Number(p.total), 0))
const salaryPayments = computed(() => payrolls.value.filter(p => p.record_type === 'salary').reduce((sum, p) => sum + Number(p.total), 0))
const advancePayments = computed(() => payrolls.value.filter(p => p.record_type === 'advance').reduce((sum, p) => sum + Number(p.total), 0))
const paymentCount = computed(() => payrolls.value.length)

// Format helpers
function formatPaymentDate(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' })
}

function getRecordTypeLabel(type: string) {
  const labels: Record<string, string> = {
    salary: 'Maaş',
    advance: 'Avans',
    weekly: 'Haftalık',
    sgk: 'SGK',
    prim: 'Prim'
  }
  return labels[type] || type
}

function getRecordTypeClass(type: string) {
  const classes: Record<string, string> = {
    salary: 'bg-emerald-100 text-emerald-700',
    advance: 'bg-amber-100 text-amber-700',
    weekly: 'bg-blue-100 text-blue-700',
    sgk: 'bg-gray-100 text-gray-700',
    prim: 'bg-purple-100 text-purple-700'
  }
  return classes[type] || 'bg-gray-100 text-gray-700'
}
</script>

<template>
  <div class="space-y-4">
    <!-- Summary Row -->
    <div class="grid grid-cols-4 gap-2">
      <div class="bg-emerald-50 rounded-lg p-3 text-center">
        <Wallet class="w-4 h-4 mx-auto text-emerald-600 mb-1" />
        <div class="text-lg font-bold text-emerald-700">
          {{ formatCurrency(totalPayments) }}
        </div>
        <div class="text-xs text-emerald-600">Toplam</div>
      </div>
      <div class="bg-blue-50 rounded-lg p-3 text-center">
        <CreditCard class="w-4 h-4 mx-auto text-blue-600 mb-1" />
        <div class="text-lg font-bold text-blue-700">
          {{ formatCurrency(salaryPayments) }}
        </div>
        <div class="text-xs text-blue-600">Maaş</div>
      </div>
      <div class="bg-amber-50 rounded-lg p-3 text-center">
        <Wallet class="w-4 h-4 mx-auto text-amber-600 mb-1" />
        <div class="text-lg font-bold text-amber-700">
          {{ formatCurrency(advancePayments) }}
        </div>
        <div class="text-xs text-amber-600">Avans</div>
      </div>
      <div class="bg-gray-50 rounded-lg p-3 text-center">
        <Calendar class="w-4 h-4 mx-auto text-gray-600 mb-1" />
        <div class="text-lg font-bold text-gray-700">
          {{ paymentCount }}
        </div>
        <div class="text-xs text-gray-600">Ödeme</div>
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
    <div v-else-if="payrolls.length === 0" class="text-center py-8 text-gray-500">
      Bu ay için ödeme kaydı bulunamadı
    </div>

    <!-- Table -->
    <div v-else class="overflow-y-auto max-h-[50vh] rounded-lg border border-gray-200">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 sticky top-0">
          <tr>
            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Tarih</th>
            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Personel</th>
            <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase">Tip</th>
            <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">Tutar</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr
            v-for="payroll in payrolls"
            :key="payroll.id"
            class="hover:bg-gray-50 cursor-pointer"
            @click="emit('action', 'view', payroll)"
          >
            <td class="px-3 py-2 text-gray-900">{{ formatPaymentDate(payroll.payment_date) }}</td>
            <td class="px-3 py-2 text-gray-700">{{ payroll.employee?.name || '-' }}</td>
            <td class="px-3 py-2 text-center">
              <span
                class="px-2 py-0.5 rounded text-xs font-medium"
                :class="getRecordTypeClass(payroll.record_type)"
              >
                {{ getRecordTypeLabel(payroll.record_type) }}
              </span>
            </td>
            <td class="px-3 py-2 text-right font-medium text-gray-900">
              {{ formatCurrency(Number(payroll.total)) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>
