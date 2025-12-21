<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import type { CourierExpense, CourierExpenseSummary } from '@/types'
import { courierExpensesApi } from '@/services/api'

// Composables
import { useFormatters, useMonthYearFilter, useConfirmModal } from '@/composables'

// UI Components
import { ConfirmModal, ErrorAlert, LoadingState, MonthYearFilter, PageModal, SummaryCard } from '@/components/ui'

// Use composables
const { formatCurrency, formatDate, formatNumber } = useFormatters()
const { selectedMonth, selectedYear, years, dateRange } = useMonthYearFilter()
const confirmModal = useConfirmModal()

// Data
const expenses = ref<CourierExpense[]>([])
const summary = ref<CourierExpenseSummary | null>(null)
const loading = ref(true)
const error = ref('')

// Modal State
const showModal = ref(false)
const showBulkModal = ref(false)
const editingId = ref<number | null>(null)
const submitting = ref(false)

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
    date: string
    package_count: number
    amount: number
    vat_rate: number
  }>
})

// Month/Year filter value for v-model
const filterValue = computed({
  get: () => ({ month: selectedMonth.value, year: selectedYear.value }),
  set: (val) => {
    selectedMonth.value = val.month
    selectedYear.value = val.year
  }
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
    error.value = 'Veriler yuklenemedi'
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
  confirmModal.confirm('Bu kurye giderini silmek istediginize emin misiniz?', async () => {
    try {
      await courierExpensesApi.delete(id)
      expenses.value = expenses.value.filter(e => e.id !== id)
      await loadData()
    } catch (e) {
      console.error('Failed to delete:', e)
      error.value = 'Silme basarisiz!'
    }
  })
}

// Bulk Entry Functions
function openBulkModal() {
  bulkForm.value = {
    start_date: dateRange.value.startStr,
    end_date: dateRange.value.endStr,
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

function getBulkEntryVat(entry: { amount: number; vat_rate: number }): number {
  return entry.amount * (entry.vat_rate / 100)
}

function getBulkEntryTotal(entry: { amount: number; vat_rate: number }): number {
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
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between flex-wrap gap-4">
      <h1 data-testid="heading-courier-expenses" class="text-2xl font-display font-bold text-gray-900">Kurye Giderleri</h1>
    </div>

    <!-- Error -->
    <ErrorAlert :message="error" @dismiss="error = ''" />

    <!-- Filters -->
    <div class="flex items-center justify-between flex-wrap gap-4">
      <MonthYearFilter v-model="filterValue" :years="years" />
      <div class="flex gap-2">
        <button data-testid="btn-bulk-entry" @click="openBulkModal" class="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700">
          Toplu Giris
        </button>
        <button data-testid="btn-add-courier-expense" @click="openAddModal" class="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700">
          + Kayit Ekle
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <SummaryCard
        data-testid="total-packages-card"
        label="Toplam Paket"
        :value="formatNumber(summary?.total_packages || 0)"
        variant="primary"
      />
      <SummaryCard
        data-testid="total-amount-card"
        label="KDV Haric Tutar"
        :value="formatCurrency(summary?.total_amount || 0)"
      />
      <SummaryCard
        data-testid="total-vat-card"
        label="KDV Tutari"
        :value="formatCurrency(summary?.total_vat || 0)"
        variant="warning"
      />
      <SummaryCard
        data-testid="total-expenses-card"
        label="KDV Dahil Toplam"
        :value="formatCurrency(summary?.total_with_vat || 0)"
        variant="success"
      />
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <SummaryCard
        label="Gun Sayisi"
        :value="summary?.days_count || 0"
        variant="primary"
        :gradient="true"
      />
      <SummaryCard
        label="Gunluk Ort. Paket"
        :value="formatNumber(Math.round(summary?.avg_daily_packages || 0))"
        variant="purple"
        :gradient="true"
      />
      <SummaryCard
        label="Paket Basi Maliyet"
        :value="formatCurrency(summary?.avg_package_cost || 0)"
        variant="success"
        :gradient="true"
      />
    </div>

    <!-- Table -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <LoadingState v-if="loading" />

      <div v-else-if="expenses.length === 0" class="p-8 text-center text-gray-500">
        Bu donemde kayit bulunamadi
      </div>

      <div v-else class="overflow-x-auto">
        <table data-testid="courier-expenses-table" class="w-full">
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
                {{ formatDate(expense.expense_date, { showWeekday: true }) }}
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
                    :data-testid="`btn-edit-expense-${expense.id}`"
                    @click="openEditModal(expense)"
                    class="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    Duzenle
                  </button>
                  <button
                    :data-testid="`btn-delete-expense-${expense.id}`"
                    @click="deleteExpense(expense.id)"
                    class="text-red-500 hover:text-red-700 text-sm"
                  >
                    Sil
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
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

    <!-- Add/Edit Modal -->
    <PageModal
      :show="showModal"
      :title="editingId ? 'Kurye Gideri Duzenle' : 'Yeni Kurye Gideri'"
      @close="showModal = false"
    >
      <form @submit.prevent="submitForm" class="p-4 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Tarih *</label>
          <input
            data-testid="input-expense-date"
            v-model="form.expense_date"
            type="date"
            class="w-full border rounded-lg px-3 py-2"
            required
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Paket Sayisi *</label>
          <input
            data-testid="input-package-count"
            v-model.number="form.package_count"
            type="number"
            min="0"
            class="w-full border rounded-lg px-3 py-2"
            required
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Tutar (KDV Haric) *</label>
          <div class="relative">
            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">TL</span>
            <input
              data-testid="input-amount"
              v-model.number="form.amount"
              type="number"
              step="0.01"
              min="0"
              class="w-full border rounded-lg pl-10 pr-3 py-2"
              required
            />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">KDV Orani (%)</label>
          <input
            data-testid="input-vat-rate"
            v-model.number="form.vat_rate"
            type="number"
            step="0.01"
            min="0"
            max="100"
            class="w-full border rounded-lg px-3 py-2"
          />
        </div>

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

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Not (opsiyonel)</label>
          <input
            data-testid="textarea-notes"
            v-model="form.notes"
            type="text"
            class="w-full border rounded-lg px-3 py-2"
            placeholder="Aciklama..."
          />
        </div>

        <div class="flex gap-3 pt-2">
          <button
            data-testid="btn-cancel-expense"
            type="button"
            @click="showModal = false"
            class="flex-1 py-2 border rounded-lg text-gray-700 hover:bg-gray-100"
          >
            Iptal
          </button>
          <button
            data-testid="btn-save-expense"
            type="submit"
            :disabled="submitting"
            class="flex-1 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
          >
            {{ submitting ? 'Kaydediliyor...' : 'Kaydet' }}
          </button>
        </div>
      </form>
    </PageModal>

    <!-- Bulk Entry Modal -->
    <PageModal
      :show="showBulkModal"
      title="Toplu Kurye Gideri Girisi"
      subtitle="Birden fazla gun icin kurye gideri girebilirsiniz"
      size="full"
      @close="showBulkModal = false"
    >
      <form @submit.prevent="submitBulkForm" class="flex-1 overflow-hidden flex flex-col">
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
              <tr
                v-for="(entry, idx) in bulkForm.entries"
                :key="entry.date"
                :class="idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'"
              >
                <td class="px-3 py-2 font-medium text-gray-700 whitespace-nowrap">
                  {{ formatDate(entry.date, { showWeekday: true }) }}
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
    </PageModal>

    <ConfirmModal
      :show="confirmModal.isOpen.value"
      :message="confirmModal.message.value"
      @confirm="confirmModal.handleConfirm"
      @cancel="confirmModal.handleCancel"
    />
  </div>
</template>
