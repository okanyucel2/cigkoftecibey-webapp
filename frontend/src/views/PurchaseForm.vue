<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { Supplier, PurchaseProductGroup, PurchaseProduct } from '@/types'
import { suppliersApi, purchasesApi, purchaseProductsApi } from '@/services/api'

const router = useRouter()
const route = useRoute()

// Edit mode
const isEditMode = computed(() => !!route.params.id)
const purchaseId = computed(() => route.params.id ? Number(route.params.id) : null)

interface PurchaseItemForm {
  product_id: number | null
  description: string
  quantity: number
  unit: string
  unit_price: number
  selectedGroupId: number | null
}

const suppliers = ref<Supplier[]>([])
const productGroups = ref<PurchaseProductGroup[]>([])
const selectedSupplierId = ref<number | null>(null)
const purchaseDate = ref(new Date().toISOString().split('T')[0])
const notes = ref('')
const items = ref<PurchaseItemForm[]>([])
const loading = ref(true)
const submitting = ref(false)
const error = ref('')

const total = computed(() => {
  return items.value.reduce((sum, item) => sum + item.quantity * item.unit_price, 0)
})

// Seçili gruba göre ürünleri getir
function getProductsForGroup(groupId: number | null): PurchaseProduct[] {
  if (!groupId) return []
  const group = productGroups.value.find(g => g.id === groupId)
  return group?.products?.filter(p => p.is_active) || []
}

onMounted(async () => {
  try {
    const [suppliersRes, groupsRes] = await Promise.all([
      suppliersApi.getAll(),
      purchaseProductsApi.getGroups()
    ])
    suppliers.value = suppliersRes.data
    productGroups.value = groupsRes.data

    // Edit modunda mevcut veriyi yükle
    if (isEditMode.value && purchaseId.value) {
      const { data: purchase } = await purchasesApi.getById(purchaseId.value)
      selectedSupplierId.value = purchase.supplier_id
      purchaseDate.value = purchase.purchase_date
      notes.value = purchase.notes || ''

      // Mevcut kalemleri yükle
      items.value = purchase.items.map(item => {
        // Ürünün grubunu bul
        let selectedGroupId: number | null = null
        if (item.product_id) {
          for (const group of productGroups.value) {
            const product = group.products?.find(p => p.id === item.product_id)
            if (product) {
              selectedGroupId = group.id
              break
            }
          }
        }
        return {
          product_id: item.product_id || null,
          description: item.description,
          quantity: Number(item.quantity),
          unit: item.unit,
          unit_price: Number(item.unit_price),
          selectedGroupId
        }
      })
    } else {
      // Yeni kayıt - boş satır ekle
      addItem()
    }
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Veri yuklenemedi'
  } finally {
    loading.value = false
  }
})

function addItem() {
  items.value.push({
    product_id: null,
    description: '',
    quantity: 1,
    unit: 'kg',
    unit_price: 0,
    selectedGroupId: null
  })
}

function removeItem(index: number) {
  if (items.value.length > 1) {
    items.value.splice(index, 1)
  }
}

// Ürün seçildiğinde
function onProductSelect(index: number, productId: number | null) {
  const item = items.value[index]
  if (!productId) {
    item.product_id = null
    item.description = ''
    item.unit = 'kg'
    return
  }

  const products = getProductsForGroup(item.selectedGroupId)
  const product = products.find(p => p.id === productId)
  if (product) {
    item.product_id = product.id
    item.description = product.name
    item.unit = product.default_unit
  }
}

// Grup değiştiğinde ürün seçimini sıfırla
function onGroupChange(index: number) {
  const item = items.value[index]
  item.product_id = null
  item.description = ''
}

async function handleSubmit() {
  if (!selectedSupplierId.value) {
    error.value = 'Lutfen tedarikci secin'
    return
  }

  const validItems = items.value.filter(item => item.description && item.unit_price > 0)
  if (validItems.length === 0) {
    error.value = 'Lutfen en az bir urun ekleyin'
    return
  }

  submitting.value = true
  error.value = ''
  try {
    const purchaseData = {
      supplier_id: selectedSupplierId.value,
      purchase_date: purchaseDate.value,
      notes: notes.value || undefined,
      items: validItems.map(item => ({
        product_id: item.product_id || undefined,
        description: item.description,
        quantity: item.quantity,
        unit: item.unit,
        unit_price: item.unit_price
      }))
    }

    if (isEditMode.value && purchaseId.value) {
      await purchasesApi.update(purchaseId.value, purchaseData)
    } else {
      await purchasesApi.create(purchaseData)
    }
    router.push('/purchases')
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Alim kaydedilemedi!'
  } finally {
    submitting.value = false
  }
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 0
  }).format(value)
}
</script>

<template>
  <div class="max-w-5xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-display font-bold text-gray-900">
        {{ isEditMode ? 'Mal Alimi Duzenle' : 'Yeni Mal Alimi' }}
      </h1>
      <router-link to="/purchases" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">
        ← Geri
      </router-link>
    </div>

    <!-- Error -->
    <div v-if="error" class="bg-red-100 text-red-700 p-4 rounded-lg mb-4">
      {{ error }}
      <button @click="error = ''" class="ml-2 font-bold">x</button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-8 text-gray-500">
      Yukleniyor...
    </div>

    <form v-else @submit.prevent="handleSubmit" class="space-y-6">
      <!-- Supplier & Date -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Tedarikci *
            </label>
            <select v-model="selectedSupplierId" class="w-full border rounded-lg px-3 py-2" required>
              <option :value="null">Tedarikci Secin</option>
              <option v-for="supplier in suppliers" :key="supplier.id" :value="supplier.id">
                {{ supplier.name }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Tarih *
            </label>
            <input v-model="purchaseDate" type="date" class="w-full border rounded-lg px-3 py-2" required />
          </div>
        </div>
      </div>

      <!-- Items -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-gray-900">Urunler</h2>
          <button type="button" @click="addItem" class="bg-gray-100 text-gray-700 px-3 py-1 rounded-lg hover:bg-gray-200 text-sm">
            + Urun Ekle
          </button>
        </div>

        <!-- Header -->
        <div class="grid grid-cols-12 gap-2 mb-2 text-xs text-gray-500 font-medium px-1">
          <div class="col-span-2">Grup</div>
          <div class="col-span-3">Urun</div>
          <div class="col-span-2">Miktar</div>
          <div class="col-span-1">Birim</div>
          <div class="col-span-2">Birim Fiyat</div>
          <div class="col-span-1 text-right">Tutar</div>
          <div class="col-span-1"></div>
        </div>

        <div class="space-y-3">
          <div
            v-for="(item, index) in items"
            :key="index"
            class="grid grid-cols-12 gap-2 items-center bg-gray-50 rounded-lg p-2"
          >
            <!-- Grup Seçimi -->
            <div class="col-span-2">
              <select
                v-model="item.selectedGroupId"
                @change="onGroupChange(index)"
                class="w-full border rounded px-2 py-1.5 text-sm"
              >
                <option :value="null">Grup Sec</option>
                <option v-for="group in productGroups" :key="group.id" :value="group.id">
                  {{ group.name }}
                </option>
              </select>
            </div>

            <!-- Ürün Seçimi -->
            <div class="col-span-3">
              <select
                v-model="item.product_id"
                @change="onProductSelect(index, item.product_id)"
                class="w-full border rounded px-2 py-1.5 text-sm"
                :disabled="!item.selectedGroupId"
              >
                <option :value="null">Urun Sec</option>
                <option
                  v-for="product in getProductsForGroup(item.selectedGroupId)"
                  :key="product.id"
                  :value="product.id"
                >
                  {{ product.name }}
                </option>
              </select>
            </div>

            <!-- Miktar -->
            <div class="col-span-2">
              <input
                v-model.number="item.quantity"
                type="number"
                step="0.01"
                min="0"
                class="w-full border rounded px-2 py-1.5 text-sm"
                placeholder="Miktar"
              />
            </div>

            <!-- Birim -->
            <div class="col-span-1">
              <input
                v-model="item.unit"
                type="text"
                class="w-full border rounded px-2 py-1.5 text-sm bg-gray-100"
                readonly
              />
            </div>

            <!-- Birim Fiyat -->
            <div class="col-span-2">
              <input
                v-model.number="item.unit_price"
                type="number"
                step="0.01"
                min="0"
                class="w-full border rounded px-2 py-1.5 text-sm"
                placeholder="Fiyat"
              />
            </div>

            <!-- Tutar -->
            <div class="col-span-1 text-right font-medium text-gray-700 text-sm">
              {{ formatCurrency(item.quantity * item.unit_price) }}
            </div>

            <!-- Sil -->
            <div class="col-span-1 text-center">
              <button
                type="button"
                @click="removeItem(index)"
                :disabled="items.length === 1"
                class="p-1 text-red-500 hover:bg-red-50 rounded disabled:opacity-30"
              >
                X
              </button>
            </div>
          </div>
        </div>

        <div class="mt-6 pt-4 border-t flex justify-end">
          <div class="text-right">
            <p class="text-sm text-gray-500">Toplam</p>
            <p class="text-2xl font-bold text-gray-900">{{ formatCurrency(total) }}</p>
          </div>
        </div>
      </div>

      <!-- Notes -->
      <div class="bg-white rounded-lg shadow p-6">
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Notlar
        </label>
        <textarea
          v-model="notes"
          rows="2"
          class="w-full border rounded-lg px-3 py-2"
          placeholder="Opsiyonel notlar..."
        />
      </div>

      <!-- Actions -->
      <div class="flex justify-end gap-3">
        <router-link to="/purchases" class="px-4 py-2 border rounded-lg text-gray-700 hover:bg-gray-100">
          Iptal
        </router-link>
        <button type="submit" :disabled="submitting" class="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50">
          {{ submitting ? 'Kaydediliyor...' : (isEditMode ? 'Guncelle' : 'Kaydet') }}
        </button>
      </div>
    </form>
  </div>
</template>
