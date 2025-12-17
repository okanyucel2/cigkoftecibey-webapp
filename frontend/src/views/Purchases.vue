<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import type { Purchase, Supplier } from '@/types'
import { purchasesApi, suppliersApi } from '@/services/api'

const purchases = ref<Purchase[]>([])
const suppliers = ref<Supplier[]>([])
const loading = ref(true)
const error = ref('')

// Ay/Yıl filtreleme
const currentDate = new Date()
const selectedMonth = ref(currentDate.getMonth() + 1) // 1-12
const selectedYear = ref(currentDate.getFullYear())

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

// Yıl seçenekleri (son 3 yıl)
const years = computed(() => {
  const currentYear = new Date().getFullYear()
  return [currentYear, currentYear - 1, currentYear - 2]
})

// Aylık toplam
const monthlyTotal = computed(() => {
  return purchases.value.reduce((sum, p) => sum + Number(p.total || 0), 0)
})

// Supplier modal
const showSupplierModal = ref(false)
const supplierLoading = ref(false)
const editingSupplierId = ref<number | null>(null)
const supplierForm = ref({
  name: '',
  phone: ''
})

onMounted(async () => {
  await loadData()
})

// Ay/yıl değiştiğinde yeniden yükle
watch([selectedMonth, selectedYear], () => {
  loadPurchases()
})

async function loadData() {
  loading.value = true
  try {
    const [suppliersRes] = await Promise.all([
      suppliersApi.getAll()
    ])
    suppliers.value = suppliersRes.data
    await loadPurchases()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Veri yuklenemedi'
  } finally {
    loading.value = false
  }
}

async function loadPurchases() {
  try {
    // Ay başlangıç ve bitiş tarihleri
    const startDate = `${selectedYear.value}-${String(selectedMonth.value).padStart(2, '0')}-01`
    const lastDay = new Date(selectedYear.value, selectedMonth.value, 0).getDate()
    const endDate = `${selectedYear.value}-${String(selectedMonth.value).padStart(2, '0')}-${lastDay}`

    const { data } = await purchasesApi.getAll({ start_date: startDate, end_date: endDate })
    purchases.value = data
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Mal alimlari yuklenemedi'
  }
}

async function loadSuppliers() {
  try {
    const { data } = await suppliersApi.getAll()
    suppliers.value = data
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Tedarikciler yuklenemedi'
  }
}

function openSupplierModal() {
  editingSupplierId.value = null
  supplierForm.value = { name: '', phone: '' }
  showSupplierModal.value = true
}

function editSupplier(supplier: Supplier) {
  editingSupplierId.value = supplier.id
  supplierForm.value = {
    name: supplier.name,
    phone: supplier.phone || ''
  }
  showSupplierModal.value = true
}

async function saveSupplier() {
  if (!supplierForm.value.name.trim()) {
    error.value = 'Tedarikci adi zorunlu'
    return
  }

  supplierLoading.value = true
  error.value = ''
  try {
    if (editingSupplierId.value) {
      await suppliersApi.update(editingSupplierId.value, supplierForm.value)
    } else {
      await suppliersApi.create(supplierForm.value)
    }
    await loadSuppliers()
    closeSupplierForm()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Kayit basarisiz'
  } finally {
    supplierLoading.value = false
  }
}

async function deleteSupplier(id: number) {
  if (!confirm('Bu tedarikciyi silmek istediginize emin misiniz?')) return

  supplierLoading.value = true
  error.value = ''
  try {
    await suppliersApi.delete(id)
    await loadSuppliers()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Silme basarisiz'
  } finally {
    supplierLoading.value = false
  }
}

function closeSupplierForm() {
  editingSupplierId.value = null
  supplierForm.value = { name: '', phone: '' }
}

// Purchase silme
async function deletePurchase(id: number) {
  if (!confirm('Bu mal alimini silmek istediginize emin misiniz?')) return

  try {
    await purchasesApi.delete(id)
    await loadPurchases()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Silme basarisiz'
  }
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 0
  }).format(value)
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('tr-TR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between flex-wrap gap-4">
      <h1 class="text-2xl font-display font-bold text-gray-900">Mal Alimlari</h1>
      <div class="flex gap-3 items-center flex-wrap">
        <!-- Ay/Yıl Filtreleri -->
        <div class="flex gap-2 items-center bg-gray-100 rounded-lg px-3 py-1.5">
          <select
            v-model="selectedMonth"
            class="bg-transparent border-none text-sm font-medium focus:ring-0 cursor-pointer"
          >
            <option v-for="month in months" :key="month.value" :value="month.value">
              {{ month.label }}
            </option>
          </select>
          <select
            v-model="selectedYear"
            class="bg-transparent border-none text-sm font-medium focus:ring-0 cursor-pointer"
          >
            <option v-for="year in years" :key="year" :value="year">
              {{ year }}
            </option>
          </select>
        </div>
        <button
          @click="openSupplierModal"
          class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
        >
          Tedarikciler ({{ suppliers.length }})
        </button>
        <router-link to="/purchases/new" class="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700">
          + Yeni Alim
        </router-link>
      </div>
    </div>

    <!-- Aylık Özet -->
    <div class="bg-white rounded-lg shadow p-4 flex items-center justify-between">
      <div>
        <p class="text-sm text-gray-500">{{ months.find(m => m.value === selectedMonth)?.label }} {{ selectedYear }} Toplam</p>
        <p class="text-2xl font-bold text-gray-900">{{ formatCurrency(monthlyTotal) }}</p>
      </div>
      <div class="text-sm text-gray-500">
        {{ purchases.length }} kalem mal alimi
      </div>
    </div>

    <!-- Error -->
    <div v-if="error" class="bg-red-100 text-red-700 p-4 rounded-lg">
      {{ error }}
      <button @click="error = ''" class="ml-2 text-red-800 font-bold">x</button>
    </div>

    <!-- Purchases Table -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-gray-500">
        Yukleniyor...
      </div>

      <div v-else-if="purchases.length === 0" class="p-8 text-center text-gray-500">
        Mal alimi bulunamadi
      </div>

      <table v-else class="w-full">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Tarih
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Tedarikci
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Kalem Sayisi
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Not
            </th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
              Toplam
            </th>
            <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
              Islemler
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="purchase in purchases" :key="purchase.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 text-sm text-gray-900">
              {{ formatDate(purchase.purchase_date) }}
            </td>
            <td class="px-6 py-4">
              <span class="font-medium text-gray-900">{{ purchase.supplier?.name || '-' }}</span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-500">
              {{ purchase.items?.length || 0 }} kalem
            </td>
            <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
              {{ purchase.notes || '-' }}
            </td>
            <td class="px-6 py-4 text-right font-semibold text-gray-900">
              {{ formatCurrency(Number(purchase.total)) }}
            </td>
            <td class="px-6 py-4 text-center">
              <div class="flex items-center justify-center gap-2">
                <router-link
                  :to="`/purchases/${purchase.id}/edit`"
                  class="text-blue-600 hover:text-blue-800 text-sm px-2 py-1"
                >
                  Duzenle
                </router-link>
                <button
                  @click="deletePurchase(purchase.id)"
                  class="text-red-600 hover:text-red-800 text-sm px-2 py-1"
                >
                  Sil
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Supplier Management Modal -->
    <div v-if="showSupplierModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-hidden flex flex-col">
        <div class="p-6 border-b flex justify-between items-center">
          <h2 class="text-xl font-semibold">Tedarikci Yonetimi</h2>
          <button @click="showSupplierModal = false" class="text-gray-500 hover:text-gray-700 text-2xl">&times;</button>
        </div>

        <div class="p-6 flex-1 overflow-auto">
          <!-- Add/Edit Form -->
          <div class="bg-gray-50 rounded-lg p-4 mb-6">
            <h3 class="font-medium text-gray-700 mb-3">
              {{ editingSupplierId ? 'Tedarikci Duzenle' : 'Yeni Tedarikci Ekle' }}
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Tedarikci Adi *</label>
                <input
                  type="text"
                  v-model="supplierForm.name"
                  class="w-full border rounded-lg px-3 py-2"
                  placeholder="Tedarikci adi"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Telefon</label>
                <input
                  type="text"
                  v-model="supplierForm.phone"
                  class="w-full border rounded-lg px-3 py-2"
                  placeholder="0532 XXX XX XX"
                />
              </div>
            </div>
            <div class="mt-4 flex gap-2">
              <button
                @click="saveSupplier"
                :disabled="supplierLoading"
                class="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 disabled:opacity-50"
              >
                {{ supplierLoading ? 'Kaydediliyor...' : (editingSupplierId ? 'Guncelle' : 'Ekle') }}
              </button>
              <button
                v-if="editingSupplierId"
                @click="closeSupplierForm"
                class="px-4 py-2 border rounded-lg text-gray-700 hover:bg-gray-100"
              >
                Iptal
              </button>
            </div>
          </div>

          <!-- Suppliers List -->
          <div>
            <h3 class="font-medium text-gray-700 mb-3">Mevcut Tedarikciler ({{ suppliers.length }})</h3>
            <div v-if="suppliers.length === 0" class="text-gray-500 text-center py-4">
              Henuz tedarikci eklenmemis
            </div>
            <div v-else class="space-y-2">
              <div
                v-for="supplier in suppliers"
                :key="supplier.id"
                class="flex items-center justify-between bg-white border rounded-lg p-3 hover:bg-gray-50"
              >
                <div>
                  <div class="font-medium text-gray-900">{{ supplier.name }}</div>
                  <div v-if="supplier.phone" class="text-sm text-gray-500">{{ supplier.phone }}</div>
                </div>
                <div class="flex gap-2">
                  <button
                    @click="editSupplier(supplier)"
                    class="text-blue-600 hover:text-blue-800 text-sm px-2 py-1"
                  >
                    Duzenle
                  </button>
                  <button
                    @click="deleteSupplier(supplier.id)"
                    class="text-red-600 hover:text-red-800 text-sm px-2 py-1"
                  >
                    Sil
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="p-4 border-t bg-gray-50">
          <button
            @click="showSupplierModal = false"
            class="w-full px-4 py-2 border rounded-lg text-gray-700 hover:bg-gray-100"
          >
            Kapat
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
