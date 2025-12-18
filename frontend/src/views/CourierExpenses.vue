<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import type { CourierExpense, CourierExpenseSummary } from '@/types'
import { courierExpensesApi } from '@/services/api'
import ConfirmModal from '@/components/ui/ConfirmModal.vue'

// Data
const expenses = ref<CourierExpense[]>([])
const summary = ref<CourierExpenseSummary | null>(null)
const loading = ref(true)
const error = ref('')

// Filters
const currentDate = new Date()
const selectedMonth = ref(currentDate.getMonth() + 1)
const selectedYear = ref(currentDate.getFullYear())

// Modal State
const showModal = ref(false)
const showBulkModal = ref(false)
const editingId = ref<number | null>(null)

const submitting = ref(false)

// Confirm Modal State
const showConfirm = ref(false)
const confirmMessage = ref('')
const confirmAction = ref<(() => Promise<void>) | null>(null)

function openConfirm(message: string, action: () => Promise<void>) {
  confirmMessage.value = message
  confirmAction.value = action
  showConfirm.value = true
}

async function handleConfirm() {
  if (confirmAction.value) {
    await confirmAction.value()
  }
  showConfirm.value = false
}

// Form
const form = ref({
  expense_date: new Date().toISOString().split('T')[0],
  package_count: 0,
  amount: 0,
  vat_rate: 20,
  notes: ''
})

// Bulk Form
const bulkForm = ref({
  start_date: '',
  end_date: '',
  entries: [] as Array<{
    date: string,
    package_count: number,
    amount: number,
    vat_rate: number
  }>
})

const months = [
  { value: 1, label: 'Ocak' },
  { value: 2, label: 'Subat' },
  { value: 3, label: 'Mart' },
  { value: 4, label: 'Nisan' },
  { value: 5, label: 'Mayis' },
  { value: 6, label: 'Haziran' },
  { value: 7, label: 'Temmuz' },
  { value: 8, label: 'Agustos' },
  { value: 9, label: 'Eylul' },
  { value: 10, label: 'Ekim' },
  { value: 11, label: 'Kasim' },
  { value: 12, label: 'Aralik' },
]

const years = computed(() => {
  const currentYear = new Date().getFullYear()
  return [currentYear, currentYear - 1, currentYear - 2]
})

onMounted(async () => {
  await loadData()
})

watch([selectedMonth, selectedYear], () => {
  loadData()
})

async function loadData() {
  loading.value = true
  try {
    const [expensesRes, summaryRes] = await Promise.all([
      courierExpensesApi.getAll({
        year: selectedYear.value,
        month: selectedMonth.value
      }),
      courierExpensesApi.getSummary({
        year: selectedYear.value,
        month: selectedMonth.value
      })
    ])

    expenses.value = expensesRes.data
    summary.value = summaryRes.data
  } catch (e) {
    console.error('Failed to load data:', e)
  } finally {
    loading.value = false
  }
}

// Computed KDV for form
const formVatAmount = computed(() => form.value.amount * (form.value.vat_rate / 100))
const formTotalWithVat = computed(() => form.value.amount + formVatAmount.value)

function openAddModal() {
  editingId.value = null
  form.value = {
    expense_date: new Date().toISOString().split('T')[0],
    package_count: 0,
    amount: 0,
    vat_rate: 20,
    notes: ''
  }
  showModal.value = true
}

function openEditModal(expense: CourierExpense) {
  editingId.value = expense.id
  form.value = {
    expense_date: expense.expense_date,
    package_count: expense.package_count,
    amount: expense.amount,
    vat_rate: expense.vat_rate,
    notes: expense.notes || ''
  }
  showModal.value = true
}

async function submitForm() {
  if (form.value.package_count <= 0 || form.value.amount <= 0) {
    error.value = 'Paket sayisi ve tutar sifirdan buyuk olmalidir'
    return
  }

  submitting.value = true
  error.value = ''

  try {
    if (editingId.value) {
      await courierExpensesApi.update(editingId.value, form.value)
    } else {
      await courierExpensesApi.create(form.value)
    }

    showModal.value = false
    await loadData()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Kayit basarisiz'
  } finally {
    submitting.value = false
  }
}

async function deleteExpense(id: number) {
  openConfirm('Bu kurye giderini silmek istediginize emin misiniz?', async () => {
    try {
      await courierExpensesApi.delete(id)
      expenses.value = expenses.value.filter(e => e.id !== id)
      await loadData()
    } catch (e) {
      console.error('Failed to delete:', e)
      alert('Silme basarisiz!')
    }
  })
}

// Bulk Entry Functions
function openBulkModal() {
  const startDate = new Date(selectedYear.value, selectedMonth.value - 1, 1)
  const endDate = new Date(selectedYear.value, selectedMonth.value, 0)

  bulkForm.value = {
    start_date: startDate.toISOString().split('T')[0],
    end_date: endDate.toISOString().split('T')[0],
    entries: []
  }
  generateBulkEntries()
  showBulkModal.value = true
}

function generateBulkEntries() {
  const start = new Date(bulkForm.value.start_date)
  const end = new Date(bulkForm.value.end_date)
  const entries = []

  const current = new Date(start)
  while (current <= end) {
    const dateStr = current.toISOString().split('T')[0]

    // Check if data exists for this date
    const existing = expenses.value.find(e => e.expense_date === dateStr)

    entries.push({
      date: dateStr,
      package_count: existing?.package_count || 0,
      amount: existing?.amount || 0,
      vat_rate: existing?.vat_rate || 20
    })

    current.setDate(current.getDate() + 1)
  }

  bulkForm.value.entries = entries
}

function getBulkEntryVat(entry: { amount: number, vat_rate: number }): number {
  return entry.amount * (entry.vat_rate / 100)
}

function getBulkEntryTotal(entry: { amount: number, vat_rate: number }): number {
  return entry.amount + getBulkEntryVat(entry)
}

const bulkTotalPackages = computed(() =>
  bulkForm.value.entries.reduce((sum, e) => sum + (e.package_count || 0), 0)
)

const bulkTotalAmount = computed(() =>
  bulkForm.value.entries.reduce((sum, e) => sum + (e.amount || 0), 0)
)

const bulkTotalWithVat = computed(() =>
  bulkForm.value.entries.reduce((sum, e) => sum + getBulkEntryTotal(e), 0)
)

async function submitBulkForm() {
  submitting.value = true
  error.value = ''

  try {
    const filteredEntries = bulkForm.value.entries
      .filter(e => e.package_count > 0 && e.amount > 0)
      .map(e => ({
        expense_date: e.date,
        package_count: e.package_count,
        amount: e.amount,
        vat_rate: e.vat_rate
      }))

    if (filteredEntries.length > 0) {
      await courierExpensesApi.createBulk({ entries: filteredEntries })
    }

    showBulkModal.value = false
    await loadData()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Toplu kayit basarisiz'
  } finally {
    submitting.value = false
  }
}

// Format helpers
function formatCurrency(value: number) {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 2
  }).format(value)
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('tr-TR', {
    day: '2-digit',
    month: 'long',
    weekday: 'short'
  })
}

function formatNumber(value: number) {
  return new Intl.NumberFormat('tr-TR').format(value)
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between flex-wrap gap-4">
      <h1 class="text-2xl font-display font-bold text-gray-900">Kurye Giderleri</h1>
    </div>

    <!-- Error -->
    <div v-if="error" class="bg-red-100 text-red-700 p-4 rounded-lg">
      {{ error }}
      <button @click="error = ''" class="ml-2 text-red-800 font-bold">x</button>
    </div>

    <!-- Filters -->
    <div class="flex items-center justify-between flex-wrap gap-4">
      <div class="flex gap-2 items-center bg-gray-100 rounded-lg px-3 py-1.5">
        <select v-model="selectedMonth" class="bg-transparent border-none text-sm font-medium focus:ring-0">
          <option v-for="month in months" :key="month.value" :value="month.value">{{ month.label }}</option>
        </select>
        <select v-model="selectedYear" class="bg-transparent border-none text-sm font-medium focus:ring-0">
          <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
        </select>
      </div>
      <div class="flex gap-2">
        <button @click="openBulkModal" class="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700">
          Toplu Giris
        </button>
        <button @click="openAddModal" class="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700">
          + Kayit Ekle
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow p-4">
        <p class="text-sm text-gray-500">Toplam Paket</p>
        <p class="text-xl font-bold text-blue-600">{{ formatNumber(summary?.total_packages || 0) }}</p>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <p class="text-sm text-gray-500">KDV Haric Tutar</p>
        <p class="text-xl font-bold text-gray-700">{{ formatCurrency(summary?.total_amount || 0) }}</p>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <p class="text-sm text-gray-500">KDV Tutari</p>
        <p class="text-xl font-bold text-orange-600">{{ formatCurrency(summary?.total_vat || 0) }}</p>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <p class="text-sm text-gray-500">KDV Dahil Toplam</p>
        <p class="text-xl font-bold text-green-600">{{ formatCurrency(summary?.total_with_vat || 0) }}</p>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg shadow p-4 text-white">
        <p class="text-blue-100 text-sm">Gun Sayisi</p>
        <p class="text-2xl font-bold">{{ summary?.days_count || 0 }}</p>
      </div>
      <div class="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg shadow p-4 text-white">
        <p class="text-purple-100 text-sm">Gunluk Ort. Paket</p>
        <p class="text-2xl font-bold">{{ formatNumber(Math.round(summary?.avg_daily_packages || 0)) }}</p>
      </div>
      <div class="bg-gradient-to-r from-green-500 to-green-600 rounded-lg shadow p-4 text-white">
        <p class="text-green-100 text-sm">Paket Basi Maliyet</p>
        <p class="text-2xl font-bold">{{ formatCurrency(summary?.avg_package_cost || 0) }}</p>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-gray-500">
        Yukleniyor...
      </div>

      <div v-else-if="expenses.length === 0" class="p-8 text-center text-gray-500">
        Bu donemde kayit bulunamadi
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tarih</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Paket Sayisi</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Tutar (KDV Haric)</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">KDV (%)</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Toplam</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase w-24">Islem</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="expense in expenses" :key="expense.id" class="hover:bg-gray-50">
              <td class="px-4 py-3 text-sm font-medium text-gray-900 whitespace-nowrap">
                {{ formatDate(expense.expense_date) }}
              </td>
              <td class="px-4 py-3 text-right text-sm font-medium text-blue-600">
                {{ formatNumber(expense.package_count) }}
              </td>
              <td class="px-4 py-3 text-right text-sm text-gray-700">
                {{ formatCurrency(expense.amount) }}
              </td>
              <td class="px-4 py-3 text-right text-sm text-gray-500">
                %{{ expense.vat_rate }}
              </td>
              <td class="px-4 py-3 text-right font-bold text-green-600">
                {{ formatCurrency(expense.total_with_vat) }}
              </td>
              <td class="px-4 py-3 text-right">
                <div class="flex justify-end gap-2">
                  <button
                    @click="openEditModal(expense)"
                    class="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    Duzenle
                  </button>
                  <button
                    @click="deleteExpense(expense.id)"
                    class="text-red-500 hover:text-red-700 text-sm"
                  >
                    Sil
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
          <!-- Footer Totals -->
          <tfoot class="bg-gray-100 font-bold">
            <tr>
              <td class="px-4 py-3 text-sm text-gray-700">TOPLAM</td>
              <td class="px-4 py-3 text-right text-sm text-blue-600">
                {{ formatNumber(summary?.total_packages || 0) }}
              </td>
              <td class="px-4 py-3 text-right text-sm text-gray-700">
                {{ formatCurrency(summary?.total_amount || 0) }}
              </td>
              <td class="px-4 py-3 text-right text-sm text-gray-500">-</td>
              <td class="px-4 py-3 text-right text-green-600">
                {{ formatCurrency(summary?.total_with_vat || 0) }}
              </td>
              <td></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>

    <!-- ==================== ADD/EDIT MODAL ==================== -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        <div class="p-4 border-b flex justify-between items-center">
          <h2 class="text-lg font-semibold">{{ editingId ? 'Kurye Gideri Duzenle' : 'Yeni Kurye Gideri' }}</h2>
          <button @click="showModal = false" class="text-gray-500 hover:text-gray-700 text-2xl">&times;</button>
        </div>

        <form @submit.prevent="submitForm" class="p-4 space-y-4">
          <!-- Tarih -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Tarih *</label>
            <input
              v-model="form.expense_date"
              type="date"
              class="w-full border rounded-lg px-3 py-2"
              required
            />
          </div>

          <!-- Paket Sayisi -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Paket Sayisi *</label>
            <input
              v-model.number="form.package_count"
              type="number"
              min="0"
              class="w-full border rounded-lg px-3 py-2"
              required
            />
          </div>

          <!-- Tutar (KDV Haric) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Tutar (KDV Haric) *</label>
            <div class="relative">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">TL</span>
              <input
                v-model.number="form.amount"
                type="number"
                step="0.01"
                min="0"
                class="w-full border rounded-lg pl-10 pr-3 py-2"
                required
              />
            </div>
          </div>

          <!-- KDV Orani -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">KDV Orani (%)</label>
            <input
              v-model.number="form.vat_rate"
              type="number"
              step="0.01"
              min="0"
              max="100"
              class="w-full border rounded-lg px-3 py-2"
            />
          </div>

          <!-- Hesaplanan Degerler -->
          <div class="bg-gray-50 rounded-lg p-3 space-y-2">
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">KDV Tutari</span>
              <span class="font-medium text-orange-600">{{ formatCurrency(formVatAmount) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-700 font-medium">KDV Dahil Toplam</span>
              <span class="font-bold text-green-600">{{ formatCurrency(formTotalWithVat) }}</span>
            </div>
          </div>

          <!-- Not -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Not (opsiyonel)</label>
            <input
              v-model="form.notes"
              type="text"
              class="w-full border rounded-lg px-3 py-2"
              placeholder="Aciklama..."
            />
          </div>

          <!-- Butonlar -->
          <div class="flex gap-3 pt-2">
            <button
              type="button"
              @click="showModal = false"
              class="flex-1 py-2 border rounded-lg text-gray-700 hover:bg-gray-100"
            >
              Iptal
            </button>
            <button
              type="submit"
              :disabled="submitting"
              class="flex-1 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
            >
              {{ submitting ? 'Kaydediliyor...' : 'Kaydet' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ==================== BULK ENTRY MODAL ==================== -->
    <div v-if="showBulkModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-5xl mx-4 max-h-[90vh] overflow-hidden flex flex-col">
        <div class="p-4 border-b flex justify-between items-center sticky top-0 bg-white">
          <div>
            <h2 class="text-lg font-semibold">Toplu Kurye Gideri Girisi</h2>
            <p class="text-sm text-gray-500">Birden fazla gun icin kurye gideri girebilirsiniz</p>
          </div>
          <button @click="showBulkModal = false" class="text-gray-500 hover:text-gray-700 text-2xl">&times;</button>
        </div>

        <form @submit.prevent="submitBulkForm" class="flex-1 overflow-hidden flex flex-col">
          <!-- Tarih Araligi -->
          <div class="p-4 border-b bg-gray-50">
            <div class="flex gap-4 items-center flex-wrap">
              <div class="flex items-center gap-2">
                <label class="text-sm font-medium text-gray-700">Baslangic:</label>
                <input
                  v-model="bulkForm.start_date"
                  @change="generateBulkEntries"
                  type="date"
                  class="border rounded-lg px-3 py-1.5 text-sm"
                />
              </div>
              <div class="flex items-center gap-2">
                <label class="text-sm font-medium text-gray-700">Bitis:</label>
                <input
                  v-model="bulkForm.end_date"
                  @change="generateBulkEntries"
                  type="date"
                  class="border rounded-lg px-3 py-1.5 text-sm"
                />
              </div>
              <div class="flex-1 text-right space-x-4">
                <span class="text-sm text-gray-500">{{ bulkForm.entries.length }} gun</span>
                <span class="text-sm">Paket: <strong class="text-blue-600">{{ formatNumber(bulkTotalPackages) }}</strong></span>
                <span class="font-bold text-green-600">Toplam: {{ formatCurrency(bulkTotalWithVat) }}</span>
              </div>
            </div>
          </div>

          <!-- Tablo -->
          <div class="flex-1 overflow-auto">
            <table class="w-full text-sm">
              <thead class="bg-gray-100 sticky top-0">
                <tr>
                  <th class="px-3 py-2 text-left font-medium text-gray-600 whitespace-nowrap">Tarih</th>
                  <th class="px-2 py-2 text-center font-medium text-gray-600 whitespace-nowrap w-28">Paket Sayisi</th>
                  <th class="px-2 py-2 text-center font-medium text-gray-600 whitespace-nowrap w-36">Tutar (KDV Haric)</th>
                  <th class="px-2 py-2 text-center font-medium text-gray-600 whitespace-nowrap w-20">KDV %</th>
                  <th class="px-3 py-2 text-right font-medium text-gray-600 whitespace-nowrap w-32">Toplam</th>
                </tr>
              </thead>
              <tbody class="divide-y">
                <tr v-for="(entry, idx) in bulkForm.entries" :key="entry.date" :class="idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'">
                  <td class="px-3 py-2 font-medium text-gray-700 whitespace-nowrap">
                    {{ formatDate(entry.date) }}
                  </td>
                  <td class="px-1 py-1">
                    <input
                      v-model.number="entry.package_count"
                      type="number"
                      min="0"
                      class="w-full border rounded px-2 py-1 text-right text-sm"
                      placeholder="0"
                    />
                  </td>
                  <td class="px-1 py-1">
                    <input
                      v-model.number="entry.amount"
                      type="number"
                      step="0.01"
                      min="0"
                      class="w-full border rounded px-2 py-1 text-right text-sm"
                      placeholder="0.00"
                    />
                  </td>
                  <td class="px-1 py-1">
                    <input
                      v-model.number="entry.vat_rate"
                      type="number"
                      min="0"
                      max="100"
                      class="w-full border rounded px-2 py-1 text-right text-sm"
                      placeholder="20"
                    />
                  </td>
                  <td class="px-3 py-2 text-right font-bold text-gray-900 whitespace-nowrap">
                    {{ formatCurrency(getBulkEntryTotal(entry)) }}
                  </td>
                </tr>
              </tbody>
              <!-- Footer -->
              <tfoot class="bg-gray-100 font-bold sticky bottom-0">
                <tr>
                  <td class="px-3 py-2 text-gray-700">TOPLAM</td>
                  <td class="px-2 py-2 text-center text-blue-600">{{ formatNumber(bulkTotalPackages) }}</td>
                  <td class="px-2 py-2 text-center text-gray-700">{{ formatCurrency(bulkTotalAmount) }}</td>
                  <td class="px-2 py-2 text-center text-gray-500">-</td>
                  <td class="px-3 py-2 text-right text-green-600">{{ formatCurrency(bulkTotalWithVat) }}</td>
                </tr>
              </tfoot>
            </table>
          </div>

          <!-- Butonlar -->
          <div class="p-4 border-t bg-gray-50 flex gap-3 justify-end">
            <button
              type="button"
              @click="showBulkModal = false"
              class="px-6 py-2 border rounded-lg text-gray-700 hover:bg-gray-100"
            >
              Iptal
            </button>
            <button
              type="submit"
              :disabled="submitting"
              class="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
            >
              {{ submitting ? 'Kaydediliyor...' : 'Tumu Kaydet' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <ConfirmModal 
      :show="showConfirm"
      :message="confirmMessage"
      @confirm="handleConfirm"
      @cancel="showConfirm = false"
    />
  </div>
</template>
