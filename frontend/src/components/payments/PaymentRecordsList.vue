<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { paymentsApi } from '@/services'
import { suppliersApi } from '@/services/api'
import { useConfirmModal } from '@/composables'
import { ConfirmModal } from '@/components/ui'
import type { SupplierPayment, PaymentFilters, PaymentType, Supplier } from '@/types'

// Emits for parent component to refresh AR list
const emit = defineEmits<{
  'payment-created': []
}>()

const payments = ref<SupplierPayment[]>([])
const suppliers = ref<Supplier[]>([])
const loading = ref(true)
const error = ref('')
const successMessage = ref('')

// Filters
const filters = ref<PaymentFilters>({})
const dateRange = ref<'today' | 'thisWeek' | 'thisMonth' | 'all'>('all')

// Modal state
const showModal = ref(false)
const modalLoading = ref(false)
const editingId = ref<number | null>(null)

// Confirm modal for delete
const confirmModal = useConfirmModal()

const paymentTypes: { value: PaymentType; label: string }[] = [
  { value: 'cash', label: 'Nakit' },
  { value: 'eft', label: 'EFT' },
  { value: 'check', label: 'Çek' },
  { value: 'promissory', label: 'Senet' },
  { value: 'partial', label: 'Kısmi Ödeme' }
]

const newPayment = ref({
  supplier_id: null as number | null,
  payment_type: 'cash' as PaymentType,
  amount: '',
  payment_date: new Date().toISOString().split('T')[0],
  description: '',
  reference: '',
  // EFT için
  bank_name: '',
  transfer_code: '',
  // Çek/Senet için
  due_date: '',
  serial_number: ''
})

const paymentTypeLabels: Record<PaymentType, string> = {
  cash: 'Nakit',
  eft: 'EFT',
  check: 'Çek',
  promissory: 'Senet',
  partial: 'Kısmi'
}

// Date range presets
function setDateRange(preset: string) {
  dateRange.value = preset as any
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  switch (preset) {
    case 'today':
      filters.value.start_date = today.toISOString().split('T')[0]
      filters.value.end_date = today.toISOString().split('T')[0]
      break
    case 'thisWeek':
      const weekStart = new Date(today)
      weekStart.setDate(today.getDate() - today.getDay())
      filters.value.start_date = weekStart.toISOString().split('T')[0]
      filters.value.end_date = today.toISOString().split('T')[0]
      break
    case 'thisMonth':
      const monthStart = new Date(today.getFullYear(), today.getMonth(), 1)
      filters.value.start_date = monthStart.toISOString().split('T')[0]
      filters.value.end_date = today.toISOString().split('T')[0]
      break
    case 'all':
      filters.value.start_date = undefined
      filters.value.end_date = undefined
      break
  }
  applyFilters()
}

function clearFilters() {
  filters.value = {}
  dateRange.value = 'all'
  applyFilters()
}

function applyFilters() {
  loadPayments()
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

// Conditional fields visibility
const showEftFields = computed(() => newPayment.value.payment_type === 'eft')
const showCheckFields = computed(() => newPayment.value.payment_type === 'check' || newPayment.value.payment_type === 'promissory')

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const [paymentsRes, suppliersRes] = await Promise.all([
      paymentsApi.getPayments(filters.value),
      suppliersApi.getAll()
    ])
    payments.value = paymentsRes.data
    suppliers.value = suppliersRes.data.sort((a, b) => a.name.localeCompare(b.name, 'tr'))
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Veri yüklenemedi'
  } finally {
    loading.value = false
  }
}

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

function openModal() {
  editingId.value = null
  newPayment.value = {
    supplier_id: null,
    payment_type: 'cash',
    amount: '',
    payment_date: new Date().toISOString().split('T')[0],
    description: '',
    reference: '',
    bank_name: '',
    transfer_code: '',
    due_date: '',
    serial_number: ''
  }
  successMessage.value = ''
  error.value = ''
  showModal.value = true
}

function editPayment(payment: SupplierPayment) {
  editingId.value = payment.id
  newPayment.value = {
    supplier_id: payment.supplier_id,
    payment_type: payment.payment_type,
    amount: String(payment.amount),
    payment_date: payment.payment_date.split('T')[0],
    description: payment.description || '',
    reference: payment.reference || '',
    bank_name: payment.bank_name || '',
    transfer_code: payment.transfer_code || '',
    due_date: payment.due_date ? payment.due_date.split('T')[0] : '',
    serial_number: payment.serial_number || ''
  }
  successMessage.value = ''
  error.value = ''
  showModal.value = true
}

async function deletePayment(id: number) {
  confirmModal.confirm('Bu ödeme kaydını silmek istediğinize emin misiniz? Bu işlem geri alınamaz.', async () => {
    loading.value = true
    error.value = ''
    try {
      await paymentsApi.deletePayment(id)
      payments.value = payments.value.filter(p => p.id !== id)

      // Show success message
      successMessage.value = 'Ödeme kaydı başarıyla silindi'

      // Notify parent to refresh AR list
      emit('payment-created')

      // Auto-hide success message after 3 seconds
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Silme başarısız'
    } finally {
      loading.value = false
    }
  })
}

async function savePayment() {
  if (!newPayment.value.supplier_id || !newPayment.value.amount) {
    error.value = 'Tedarikçi ve tutar zorunludur'
    return
  }

  modalLoading.value = true
  error.value = ''

  try {
    const data: any = {
      supplier_id: newPayment.value.supplier_id,
      payment_type: newPayment.value.payment_type,
      amount: parseFloat(newPayment.value.amount),
      payment_date: new Date(newPayment.value.payment_date).toISOString()
    }

    // Optional fields
    if (newPayment.value.description) data.description = newPayment.value.description
    if (newPayment.value.reference) data.reference = newPayment.value.reference

    // EFT fields
    if (showEftFields.value) {
      if (newPayment.value.bank_name) data.bank_name = newPayment.value.bank_name
      if (newPayment.value.transfer_code) data.transfer_code = newPayment.value.transfer_code
    }

    // Check/Promissory fields
    if (showCheckFields.value) {
      if (newPayment.value.due_date) data.due_date = new Date(newPayment.value.due_date).toISOString()
      if (newPayment.value.bank_name) data.bank_name = newPayment.value.bank_name
      if (newPayment.value.serial_number) data.serial_number = newPayment.value.serial_number
    }

    if (editingId.value) {
      // Update existing payment
      await paymentsApi.updatePayment(editingId.value, data)
      const index = payments.value.findIndex(p => p.id === editingId.value)
      if (index !== -1) {
        // Update the payment in the list
        const { data: updated } = await paymentsApi.getPayment(editingId.value)
        payments.value[index] = updated
      }
      successMessage.value = 'Ödeme kaydı başarıyla güncellendi'
    } else {
      // Create new payment
      await paymentsApi.createPayment(data)
      successMessage.value = `Yeni ödeme başarıyla kaydedildi`
    }

    showModal.value = false

    // Refresh data to get updated list
    await loadPayments()

    // Notify parent to refresh AR list
    emit('payment-created')

    // Auto-hide success message after 5 seconds
    setTimeout(() => {
      successMessage.value = ''
    }, 5000)
  } catch (e: any) {
    error.value = e.response?.data?.detail || (editingId.value ? 'Güncelleme başarısız' : 'Ödeme oluşturulamadı')
  } finally {
    modalLoading.value = false
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

onMounted(loadData)
</script>

<template>
  <div class="space-y-6">
    <!-- Success Message -->
    <div v-if="successMessage" class="bg-green-100 text-green-800 p-4 rounded-lg flex items-center gap-3">
      <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span class="flex-1">{{ successMessage }}</span>
      <button @click="successMessage = ''" class="text-green-600 hover:text-green-800 font-bold">✕</button>
    </div>

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
          <p class="text-sm text-gray-500">Toplam (Filtreli)</p>
          <p class="text-2xl font-bold text-gray-900">
            {{ formatCurrency(summary.total) }}
          </p>
        </div>
      </div>

      <!-- Filters Section -->
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex flex-wrap items-center gap-4">
          <!-- Date Range Presets -->
          <div class="flex items-center gap-2">
            <span class="text-sm text-gray-600 font-medium">Tarih:</span>
            <button
              v-for="preset in [
                { id: 'today', label: 'Bugün' },
                { id: 'thisWeek', label: 'Bu Hafta' },
                { id: 'thisMonth', label: 'Bu Ay' },
                { id: 'all', label: 'Tümü' }
              ]"
              :key="preset.id"
              @click="setDateRange(preset.id)"
              :class="[
                'px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
                dateRange === preset.id
                  ? 'bg-brand-red text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              ]"
            >
              {{ preset.label }}
            </button>
          </div>

          <!-- Divider -->
          <div class="h-6 w-px bg-gray-300"></div>

          <!-- Supplier Filter -->
          <div class="flex items-center gap-2">
            <span class="text-sm text-gray-600 font-medium">Tedarikçi:</span>
            <select
              v-model="filters.supplier_id"
              @change="applyFilters"
              class="border rounded-lg px-3 py-1.5 text-sm"
            >
              <option :value="undefined">Tümü</option>
              <option v-for="supplier in suppliers" :key="supplier.id" :value="supplier.id">
                {{ supplier.name }}
              </option>
            </select>
          </div>

          <!-- Payment Type Filter -->
          <div class="flex items-center gap-2">
            <span class="text-sm text-gray-600 font-medium">Tür:</span>
            <select
              v-model="filters.payment_type"
              @change="applyFilters"
              class="border rounded-lg px-3 py-1.5 text-sm"
            >
              <option :value="undefined">Tümü</option>
              <option v-for="type in paymentTypes" :key="type.value" :value="type.value">
                {{ type.label }}
              </option>
            </select>
          </div>

          <!-- Clear Filters -->
          <button
            v-if="filters.supplier_id || filters.payment_type || dateRange !== 'all'"
            @click="clearFilters"
            class="ml-auto text-sm text-gray-500 hover:text-gray-700 underline"
          >
            Filtreleri Temizle
          </button>
        </div>
      </div>

      <!-- Table with Header -->
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <!-- Header with Add Button -->
        <div class="p-4 border-b flex justify-between items-center">
          <div>
            <h3 class="font-semibold text-gray-900">Ödeme Kayıtları</h3>
            <p class="text-sm text-gray-500">{{ payments.length }} kayıt</p>
          </div>
          <button
            @click="openModal"
            class="px-4 py-2 bg-brand-red text-white rounded-lg hover:bg-red-700 text-sm font-medium flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Yeni Ödeme
          </button>
        </div>

        <div v-if="payments.length === 0" class="p-12 text-center text-gray-500">
          <svg class="w-16 h-16 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="text-lg font-medium">Ödeme kaydı bulunamadı</p>
          <p class="text-sm mt-1">Filtreleri değiştirin veya yeni ödeme ekleyin</p>
        </div>

        <table v-else class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tarih</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tedarikçi</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tür</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Tutar</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Açıklama</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">İşlemler</th>
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
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="{
                    'bg-green-100 text-green-800': payment.payment_type === 'cash',
                    'bg-blue-100 text-blue-800': payment.payment_type === 'eft',
                    'bg-yellow-100 text-yellow-800': payment.payment_type === 'check',
                    'bg-orange-100 text-orange-800': payment.payment_type === 'promissory',
                    'bg-gray-100 text-gray-800': payment.payment_type === 'partial'
                  }">
                  {{ paymentTypeLabels[payment.payment_type] }}
                </span>
              </td>
              <td class="px-6 py-4 text-sm text-right font-semibold text-gray-900">
                {{ formatCurrency(Number(payment.amount)) }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                {{ payment.description || '-' }}
              </td>
              <td class="px-6 py-4 text-sm text-center">
                <button
                  @click="editPayment(payment)"
                  class="text-blue-600 hover:text-blue-800 font-medium mr-3"
                >
                  Düzenle
                </button>
                <button
                  @click="deletePayment(payment.id)"
                  class="text-red-600 hover:text-red-800 font-medium"
                >
                  Sil
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <!-- New Payment Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex min-h-full items-center justify-center p-4">
        <div class="fixed inset-0 bg-black/50" @click="showModal = false"></div>
        <div class="relative bg-white rounded-lg shadow-xl w-full max-w-md p-6 max-h-[90vh] overflow-y-auto">
          <h3 class="text-lg font-semibold mb-4">{{ editingId ? 'Ödeme Düzenle' : 'Yeni Ödeme' }}</h3>

          <form @submit.prevent="savePayment" class="space-y-4">
            <!-- Tedarikçi -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Tedarikçi *</label>
              <select
                v-model="newPayment.supplier_id"
                class="w-full border rounded-lg px-3 py-2"
                required
              >
                <option :value="null">Seçiniz</option>
                <option v-for="supplier in suppliers" :key="supplier.id" :value="supplier.id">
                  {{ supplier.name }}
                </option>
              </select>
            </div>

            <!-- Ödeme Türü -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Ödeme Türü *</label>
              <div class="flex gap-2 flex-wrap">
                <label
                  v-for="type in paymentTypes"
                  :key="type.value"
                  class="flex items-center gap-1 px-3 py-2 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                  :class="newPayment.payment_type === type.value ? 'bg-brand-red/10 border-brand-red' : ''"
                >
                  <input
                    :id="'type-' + type.value"
                    v-model="newPayment.payment_type"
                    type="radio"
                    :value="type.value"
                    class="sr-only"
                  />
                  <span class="text-sm">{{ type.label }}</span>
                </label>
              </div>
            </div>

            <!-- Tutar -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Tutar (₺) *</label>
              <input
                v-model.number="newPayment.amount"
                type="number"
                step="0.01"
                min="0"
                class="w-full border rounded-lg px-3 py-2"
                placeholder="0.00"
                required
              />
            </div>

            <!-- Tarih -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Ödeme Tarihi *</label>
              <input
                v-model="newPayment.payment_date"
                type="date"
                class="w-full border rounded-lg px-3 py-2"
                required
              />
            </div>

            <!-- EFT Fields -->
            <template v-if="showEftFields">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Banka</label>
                <input
                  v-model="newPayment.bank_name"
                  type="text"
                  class="w-full border rounded-lg px-3 py-2"
                  placeholder="Garanti BBVA"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Transfer Kodu</label>
                <input
                  v-model="newPayment.transfer_code"
                  type="text"
                  class="w-full border rounded-lg px-3 py-2"
                  placeholder="1234567890"
                />
              </div>
            </template>

            <!-- Check/Promissory Fields -->
            <template v-if="showCheckFields">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Vade Tarihi</label>
                <input
                  v-model="newPayment.due_date"
                  type="date"
                  class="w-full border rounded-lg px-3 py-2"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Banka</label>
                <input
                  v-model="newPayment.bank_name"
                  type="text"
                  class="w-full border rounded-lg px-3 py-2"
                  placeholder="Yapı Kredi"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Seri No</label>
                <input
                  v-model="newPayment.serial_number"
                  type="text"
                  class="w-full border rounded-lg px-3 py-2"
                  placeholder="TK123456"
                />
              </div>
            </template>

            <!-- Açıklama -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Açıklama</label>
              <input
                v-model="newPayment.description"
                type="text"
                class="w-full border rounded-lg px-3 py-2"
                placeholder="Opsiyonel açıklama"
              />
            </div>

            <!-- Referans -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Referans</label>
              <input
                v-model="newPayment.reference"
                type="text"
                class="w-full border rounded-lg px-3 py-2"
                placeholder="Sipariş/makbuz numarası"
              />
            </div>

            <!-- Actions -->
            <div class="flex justify-end gap-3 pt-4 border-t">
              <button
                type="button"
                @click="showModal = false"
                class="px-4 py-2 border rounded-lg text-gray-700 hover:bg-gray-100"
                :disabled="modalLoading"
              >
                İptal
              </button>
              <button
                type="submit"
                :disabled="modalLoading"
                class="px-4 py-2 bg-brand-red text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
              >
                {{ modalLoading ? 'Kaydediliyor...' : 'Kaydet' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Confirm Modal -->
    <ConfirmModal
      :show="confirmModal.isOpen.value"
      :message="confirmModal.message.value"
      @confirm="confirmModal.handleConfirm"
      @cancel="confirmModal.handleCancel"
    />
  </div>
</template>
