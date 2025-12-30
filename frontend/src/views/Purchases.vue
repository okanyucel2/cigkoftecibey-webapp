<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import type { Purchase, Supplier, PurchaseProductGroup, PurchaseProduct } from '@/types'
import { purchasesApi, suppliersApi, purchaseProductsApi } from '@/services/api'
import type { DateRangeValue } from '@/types/filters'

// Composables
import { useFormatters, useConfirmModal } from '@/composables'

// UI Components
import { ConfirmModal, ErrorAlert, LoadingState, UnifiedFilterBar, PageModal, SummaryCard, type EntityConfig } from '@/components/ui'

// Use composables
const { formatCurrency, formatDate } = useFormatters()
const confirmModal = useConfirmModal()

// Data
const purchases = ref<Purchase[]>([])
const suppliers = ref<Supplier[]>([])
const loading = ref(true)
const error = ref('')

// Date range filter (defaults to current month)
const dateRangeFilter = ref<DateRangeValue>({
  mode: 'range',
  start: new Date().toISOString().split('T')[0],
  end: new Date().toISOString().split('T')[0]
})

// Supplier selector state
const selectedSupplierId = ref<number | null>(null)

// Supplier entities for filter
const supplierEntities = computed<EntityConfig>(() => ({
  items: suppliers.value.map(s => ({ id: s.id, label: s.name, icon: '🏪' })),
  allLabel: 'Tüm Tedarikçiler',
  showSettings: false,
  showCount: false
}))

// Monthly total
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

// Product Groups modal
const showProductGroupsModal = ref(false)
const productGroupsLoading = ref(false)
const productGroups = ref<PurchaseProductGroup[]>([])
const editingGroupId = ref<number | null>(null)
const editingProductId = ref<number | null>(null)
const groupForm = ref({
  name: ''
})
const productForm = ref({
  name: '',
  group_id: null as number | null,
  default_unit: 'kg'
})

// Purchase Entry Modal (Quick Add)
const showPurchaseModal = ref(false)
const purchaseLoading = ref(false)
const purchaseForm = ref({
  purchase_date: new Date().toISOString().split('T')[0],
  supplier_id: null as number | null,
  notes: '',
  total: 0
})

function openPurchaseModal() {
  purchaseForm.value = {
    purchase_date: new Date().toISOString().split('T')[0],
    supplier_id: null,
    notes: '',
    total: 0
  }
  showPurchaseModal.value = true
}

async function savePurchase() {
  if (!purchaseForm.value.supplier_id) {
    error.value = 'Tedarikci seciniz'
    return
  }
  if (purchaseForm.value.total <= 0) {
    error.value = 'Tutar 0\'dan buyuk olmali'
    return
  }

  purchaseLoading.value = true
  error.value = ''
  try {
    await purchasesApi.create({
      purchase_date: purchaseForm.value.purchase_date,
      supplier_id: purchaseForm.value.supplier_id,
      notes: purchaseForm.value.notes,
      items: [{
        description: purchaseForm.value.notes || 'Genel',
        quantity: 1,
        unit: 'adet',
        unit_price: purchaseForm.value.total
      }]
    })
    showPurchaseModal.value = false
    await loadPurchases()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Kayit basarisiz'
  } finally {
    purchaseLoading.value = false
  }
}

function closePurchaseModal() {
  showPurchaseModal.value = false
}

onMounted(async () => {
  await loadData()
})

// Watch date range changes
watch(() => dateRangeFilter.value, () => {
  loadPurchases()
}, { deep: true })

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
    const params: any = {
      start_date: dateRangeFilter.value.start,
      end_date: dateRangeFilter.value.end
    }
    if (selectedSupplierId.value) {
      params.supplier_id = selectedSupplierId.value
    }
    const { data } = await purchasesApi.getAll(params)
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

async function loadProductGroups() {
  try {
    const { data } = await purchaseProductsApi.getGroups()
    productGroups.value = data
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Urun gruplari yuklenemedi'
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
  confirmModal.confirm('Bu tedarikciyi silmek istediginize emin misiniz?', async () => {
    supplierLoading.value = true
    error.value = ''
    try {
      await suppliersApi.delete(id)
      suppliers.value = suppliers.value.filter(s => s.id !== id)
      await loadSuppliers()
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Silme basarisiz'
    } finally {
      supplierLoading.value = false
    }
  })
}

function closeSupplierForm() {
  editingSupplierId.value = null
  supplierForm.value = { name: '', phone: '' }
}

// Product Groups functions
async function openProductGroupsModal() {
  showProductGroupsModal.value = true
  await loadProductGroups()
}

function editGroup(group: PurchaseProductGroup) {
  editingGroupId.value = group.id
  groupForm.value = { name: group.name }
  editingProductId.value = null
}

async function saveGroup() {
  if (!groupForm.value.name.trim()) {
    error.value = 'Grup adi zorunlu'
    return
  }

  productGroupsLoading.value = true
  error.value = ''
  try {
    if (editingGroupId.value) {
      await purchaseProductsApi.updateGroup(editingGroupId.value, groupForm.value)
    } else {
      await purchaseProductsApi.createGroup(groupForm.value)
    }
    await loadProductGroups()
    closeGroupForm()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Grup kaydedilemedi'
  } finally {
    productGroupsLoading.value = false
  }
}

async function deleteGroup(id: number) {
  confirmModal.confirm('Bu grubu ve icindeki urunleri silmek istediginize emin misiniz?', async () => {
    productGroupsLoading.value = true
    error.value = ''
    try {
      await purchaseProductsApi.deleteGroup(id)
      await loadProductGroups()
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Silme basarisiz'
    } finally {
      productGroupsLoading.value = false
    }
  })
}

function closeGroupForm() {
  editingGroupId.value = null
  groupForm.value = { name: '' }
}

// Product functions
function editProduct(product: PurchaseProduct) {
  editingProductId.value = product.id
  productForm.value = {
    name: product.name,
    group_id: product.group_id,
    default_unit: product.default_unit
  }
  editingGroupId.value = null
}

async function saveProduct() {
  if (!productForm.value.name.trim() || !productForm.value.group_id) {
    error.value = 'Urun adi ve grup zorunlu'
    return
  }

  productGroupsLoading.value = true
  error.value = ''
  try {
    if (editingProductId.value) {
      await purchaseProductsApi.updateProduct(editingProductId.value, {
        name: productForm.value.name,
        group_id: productForm.value.group_id,
        default_unit: productForm.value.default_unit
      })
    } else {
      await purchaseProductsApi.createProduct({
        name: productForm.value.name,
        group_id: productForm.value.group_id,
        default_unit: productForm.value.default_unit
      })
    }
    await loadProductGroups()
    closeProductForm()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Urun kaydedilemedi'
  } finally {
    productGroupsLoading.value = false
  }
}

async function deleteProduct(id: number) {
  confirmModal.confirm('Bu urunu silmek istediginize emin misiniz?', async () => {
    productGroupsLoading.value = true
    error.value = ''
    try {
      await purchaseProductsApi.deleteProduct(id)
      await loadProductGroups()
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Silme basarisiz'
    } finally {
      productGroupsLoading.value = false
    }
  })
}

function closeProductForm() {
  editingProductId.value = null
  productForm.value = { name: '', group_id: null, default_unit: 'kg' }
}

async function deletePurchase(id: number) {
  confirmModal.confirm('Bu mal alimini silmek istediginize emin misiniz?', async () => {
    try {
      await purchasesApi.delete(id)
      purchases.value = purchases.value.filter(p => p.id !== id)
      await loadPurchases()
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Silme basarisiz'
    }
  })
}
</script>

<template>
  <div class="space-y-6">
    <!-- Unified Filter Bar -->
    <UnifiedFilterBar
      v-model:date-range="dateRangeFilter"
      v-model:entity-id="selectedSupplierId"
      :entities="supplierEntities"
      :primary-action="{ label: 'Yeni Alım', onClick: openPurchaseModal }"
    />

    <!-- Management Buttons -->
    <div class="flex gap-3">
      <button
        @click="openSupplierModal"
        class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
      >
        🏪 Tedarikçiler ({{ suppliers.length }})
      </button>
      <button
        @click="openProductGroupsModal"
        class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
      >
        📦 Ürün Grupları
      </button>
    </div>

    <!-- Monthly Summary -->
    <SummaryCard
      label="Seçili Dönem Toplamı"
      :value="formatCurrency(monthlyTotal)"
      :subtext="`${purchases.length} kalem mal alımı`"
      variant="primary"
    />

    <!-- Error -->
    <ErrorAlert :message="error" @dismiss="error = ''" />

    <!-- Purchases Table -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <LoadingState v-if="loading" />

      <div v-else-if="purchases.length === 0" class="p-8 text-center text-gray-500">
        Mal alimi bulunamadi
      </div>

      <table v-else class="w-full">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tarih</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tedarikci</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Kalem Sayisi</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Not</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Toplam</th>
            <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Islemler</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="purchase in purchases" :key="purchase.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 text-sm text-gray-900">
              {{ formatDate(purchase.purchase_date, { format: 'short' }) }}
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
    <PageModal
      :show="showSupplierModal"
      title="Tedarikci Yonetimi"
      size="lg"
      @close="showSupplierModal = false"
    >
      <div class="p-6">
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

      <template #footer>
        <button
          @click="showSupplierModal = false"
          class="w-full px-4 py-2 border rounded-lg text-gray-700 hover:bg-gray-100"
        >
          Kapat
        </button>
      </template>
    </PageModal>

    <!-- Product Groups Management Modal -->
    <PageModal
      :show="showProductGroupsModal"
      title="Urun Gruplari Yonetimi"
      size="xl"
      @close="showProductGroupsModal = false"
    >
      <div class="p-6">
        <!-- Add/Edit Group Form -->
        <div class="bg-gray-50 rounded-lg p-4 mb-6">
          <h3 class="font-medium text-gray-700 mb-3">
            {{ editingGroupId ? 'Grup Duzenle' : 'Yeni Grup Ekle' }}
          </h3>
          <div class="flex gap-2">
            <input
              type="text"
              v-model="groupForm.name"
              class="flex-1 border rounded-lg px-3 py-2"
              placeholder="Grup adi (orn: Et Urunleri, Sebze...)"
            />
            <button
              @click="saveGroup"
              :disabled="productGroupsLoading"
              class="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 disabled:opacity-50"
            >
              {{ productGroupsLoading ? 'Kaydediliyor...' : (editingGroupId ? 'Guncelle' : 'Ekle') }}
            </button>
            <button
              v-if="editingGroupId"
              @click="closeGroupForm"
              class="px-4 py-2 border rounded-lg text-gray-700 hover:bg-gray-100"
            >
              Iptal
            </button>
          </div>
        </div>

        <!-- Groups List with Products -->
        <div class="space-y-6">
          <div
            v-for="group in productGroups"
            :key="group.id"
            class="border rounded-lg overflow-hidden"
          >
            <!-- Group Header -->
            <div class="bg-gray-50 px-4 py-3 flex items-center justify-between">
              <div class="flex items-center gap-3">
                <h3 class="font-semibold text-gray-900">{{ group.name }}</h3>
                <span class="text-xs text-gray-500 bg-white px-2 py-1 rounded">
                  {{ group.products?.length || 0 }} urun
                </span>
              </div>
              <div class="flex gap-2">
                <button
                  @click="editGroup(group)"
                  class="text-blue-600 hover:text-blue-800 text-sm px-2 py-1"
                >
                  Duzenle
                </button>
                <button
                  @click="deleteGroup(group.id)"
                  class="text-red-600 hover:text-red-800 text-sm px-2 py-1"
                >
                  Sil
                </button>
              </div>
            </div>

            <!-- Products in Group -->
            <div class="p-4 bg-white">
              <!-- Add Product Form -->
              <div class="flex gap-2 mb-3 p-3 bg-gray-50 rounded-lg">
                <input
                  type="text"
                  v-model="productForm.name"
                  class="flex-1 border rounded px-2 py-1.5 text-sm"
                  placeholder="Urun adi (orn: Kırmızı Et)"
                  :disabled="editingProductId !== null && productForm.group_id !== group.id"
                />
                <select
                  v-model="productForm.default_unit"
                  class="border rounded px-2 py-1.5 text-sm"
                  :disabled="editingProductId !== null && productForm.group_id !== group.id"
                >
                  <option value="kg">kg</option>
                  <option value="adet">adet</option>
                  <option value="litre">litre</option>
                  <option value="demet">demet</option>
                  <option value="paket">paket</option>
                </select>
                <input
                  type="hidden"
                  :value="editingProductId === null && productForm.group_id === null ? group.id : productForm.group_id"
                />
                <button
                  @click="productForm.group_id = group.id; saveProduct()"
                  :disabled="productGroupsLoading || (editingProductId !== null && productForm.group_id !== group.id)"
                  class="bg-gray-200 text-gray-700 px-3 py-1.5 rounded text-sm hover:bg-gray-300 disabled:opacity-50"
                >
                  {{ editingProductId !== null && productForm.group_id === group.id ? 'Guncelle' : '+ Urun Ekle' }}
                </button>
                <button
                  v-if="editingProductId !== null && productForm.group_id === group.id"
                  @click="closeProductForm"
                  class="px-3 py-1.5 border rounded text-sm text-gray-600 hover:bg-gray-100"
                >
                  Iptal
                </button>
              </div>

              <!-- Products List -->
              <div v-if="!group.products || group.products.length === 0" class="text-gray-500 text-center py-2 text-sm">
                Henuz urun eklenmemis
              </div>
              <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-2">
                <div
                  v-for="product in group.products.filter(p => p.is_active).sort((a, b) => a.name.localeCompare(b.name, 'tr'))"
                  :key="product.id"
                  class="flex items-center justify-between bg-white border rounded px-3 py-2 text-sm hover:bg-gray-50"
                  :class="{ 'ring-2 ring-red-200': editingProductId === product.id }"
                >
                  <div>
                    <span class="font-medium text-gray-900">{{ product.name }}</span>
                    <span class="text-xs text-gray-500 ml-2">({{ product.default_unit }})</span>
                  </div>
                  <div class="flex gap-2">
                    <button
                      @click="editProduct(product)"
                      class="text-blue-600 hover:text-blue-800"
                    >
                      Duzenle
                    </button>
                    <button
                      @click="deleteProduct(product.id)"
                      class="text-red-600 hover:text-red-800"
                    >
                      Sil
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-if="productGroups.length === 0" class="text-gray-500 text-center py-8">
            Henuz urun grubu eklenmemis. Yukaridan yeni grup olusturabilirsiniz.
          </div>
        </div>
      </div>

      <template #footer>
        <button
          @click="showProductGroupsModal = false"
          class="w-full px-4 py-2 border rounded-lg text-gray-700 hover:bg-gray-100"
        >
          Kapat
        </button>
      </template>
    </PageModal>

    <!-- Quick Purchase Entry Modal -->
    <PageModal
      :show="showPurchaseModal"
      title="Yeni Mal Alımı"
      size="lg"
      @close="closePurchaseModal"
    >
      <form @submit.prevent="savePurchase" class="p-6 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Tarih *</label>
          <input
            v-model="purchaseForm.purchase_date"
            type="date"
            class="w-full border rounded-lg px-3 py-2"
            required
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Tedarikçi *</label>
          <select
            v-model.number="purchaseForm.supplier_id"
            class="w-full border rounded-lg px-3 py-2"
            required
          >
            <option :value="null" disabled>Tedarikçi Seçiniz</option>
            <option v-for="supplier in suppliers" :key="supplier.id" :value="supplier.id">
              {{ supplier.name }}
            </option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Toplam Tutar (TL) *</label>
          <input
            v-model.number="purchaseForm.total"
            type="number"
            step="0.01"
            min="0"
            class="w-full border rounded-lg px-3 py-2"
            placeholder="0.00"
            required
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Not</label>
          <textarea
            v-model="purchaseForm.notes"
            class="w-full border rounded-lg px-3 py-2"
            rows="2"
            placeholder="Açıklama..."
          ></textarea>
        </div>

        <div class="flex justify-end gap-3 pt-4">
          <button
            type="button"
            @click="closePurchaseModal"
            class="px-4 py-2 border rounded-lg text-gray-700 hover:bg-gray-100"
          >
            İptal
          </button>
          <button
            type="submit"
            :disabled="purchaseLoading"
            class="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
          >
            {{ purchaseLoading ? 'Kaydediliyor...' : 'Kaydet' }}
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
