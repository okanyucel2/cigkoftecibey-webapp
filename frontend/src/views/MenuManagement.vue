<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import type { MenuCategory, MenuItem } from '@/types'
import { extractErrorMessage } from '@/types'
import { menuCategoriesApi, menuItemsApi } from '@/services/api'
import ConfirmModal from '@/components/ui/ConfirmModal.vue'

const activeTab = ref<'categories' | 'items'>('categories')
const loading = ref(true)

// Categories
const categories = ref<MenuCategory[]>([])
const showCategoryModal = ref(false)
const editingCategory = ref<MenuCategory | null>(null)
const categoryForm = ref({
  name: '',
  description: '',
  display_order: 0,
  is_global: true
})

// Items
const items = ref<MenuItem[]>([])
const selectedCategoryId = ref<number | null>(null)
const showItemModal = ref(false)
const editingItem = ref<MenuItem | null>(null)
const itemForm = ref({
  name: '',
  description: '',
  image_url: '',
  display_order: 0,
  category_id: 0,
  default_price: null as number | null
})

// Sorted categories by display order
const sortedCategories = computed(() => {
  return [...categories.value]
    .filter(c => c.is_active)
    .sort((a, b) => a.display_order - b.display_order)
})

// Filtered and sorted items
const filteredItems = computed(() => {
  let result = [...items.value]
  if (selectedCategoryId.value) {
    result = result.filter(i => i.category_id === selectedCategoryId.value)
  }
  return result.sort((a, b) => a.display_order - b.display_order)
})

onMounted(async () => {
  await loadData()
})

async function loadData() {
  loading.value = true
  try {
    const [categoriesRes, itemsRes] = await Promise.all([
      menuCategoriesApi.getAll(),
      menuItemsApi.getAll()
    ])
    categories.value = categoriesRes.data
    items.value = itemsRes.data
  } catch (error) {
    console.error('Failed to load data:', error)
  } finally {
    loading.value = false
  }
}

function openCategoryModal(category?: MenuCategory) {
  if (category) {
    editingCategory.value = category
    categoryForm.value = {
      name: category.name,
      description: category.description || '',
      display_order: category.display_order,
      is_global: category.branch_id === null
    }
  } else {
    editingCategory.value = null
    categoryForm.value = { name: '', description: '', display_order: 0, is_global: true }
  }
  showCategoryModal.value = true
}

async function saveCategory() {
  try {
    if (editingCategory.value) {
      await menuCategoriesApi.update(editingCategory.value.id, {
        name: categoryForm.value.name,
        description: categoryForm.value.description || undefined,
        display_order: categoryForm.value.display_order
      })
    } else {
      await menuCategoriesApi.create({
        name: categoryForm.value.name,
        description: categoryForm.value.description || undefined,
        display_order: categoryForm.value.display_order,
        is_global: categoryForm.value.is_global
      })
    }
    showCategoryModal.value = false
    await loadData()
  } catch (error: unknown) {
    alert(extractErrorMessage(error, 'Bir hata olustu'))
  }
}

async function toggleCategoryActive(category: MenuCategory) {
  try {
    await menuCategoriesApi.update(category.id, { is_active: !category.is_active })
    await loadData()
  } catch (error: unknown) {
    alert(extractErrorMessage(error, 'Bir hata olustu'))
  }
}

function openItemModal(item?: MenuItem) {
  if (item) {
    editingItem.value = item
    itemForm.value = {
      name: item.name,
      description: item.description || '',
      image_url: item.image_url || '',
      display_order: item.display_order,
      category_id: item.category_id,
      default_price: item.price ?? null
    }
  } else {
    editingItem.value = null
    itemForm.value = {
      name: '',
      description: '',
      image_url: '',
      display_order: 0,
      category_id: selectedCategoryId.value || sortedCategories.value[0]?.id || 0,
      default_price: null
    }
  }
  showItemModal.value = true
}

async function saveItem() {
  try {
    if (editingItem.value) {
      await menuItemsApi.update(editingItem.value.id, {
        name: itemForm.value.name,
        description: itemForm.value.description || undefined,
        image_url: itemForm.value.image_url || undefined,
        display_order: itemForm.value.display_order,
        category_id: itemForm.value.category_id
      })
      if (itemForm.value.default_price !== null) {
        await menuItemsApi.setPrice(editingItem.value.id, { price: itemForm.value.default_price })
      }
    } else {
      await menuItemsApi.create({
        name: itemForm.value.name,
        description: itemForm.value.description || undefined,
        image_url: itemForm.value.image_url || undefined,
        display_order: itemForm.value.display_order,
        category_id: itemForm.value.category_id,
        default_price: itemForm.value.default_price ?? undefined
      })
    }
    showItemModal.value = false
    await loadData()
  } catch (error: unknown) {
    alert(extractErrorMessage(error, 'Bir hata olustu'))
  }
}

async function toggleItemActive(item: MenuItem) {
  try {
    await menuItemsApi.update(item.id, { is_active: !item.is_active })
    await loadData()
  } catch (error: unknown) {
    alert(extractErrorMessage(error, 'Bir hata olustu'))
  }
}

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

async function deleteCategory(category: MenuCategory) {
  openConfirm('Bu kategoriyi silmek istediginize emin misiniz?', async () => {
    try {
      await menuCategoriesApi.delete(category.id)
      await loadData()
    } catch (error: unknown) {
      alert(extractErrorMessage(error, 'Bir hata olustu'))
    }
  })
}

async function deleteItem(item: MenuItem) {
  openConfirm('Bu urunu silmek istediginize emin misiniz?', async () => {
    try {
      await menuItemsApi.delete(item.id)
      await loadData()
    } catch (error: unknown) {
      alert(extractErrorMessage(error, 'Bir hata olustu'))
    }
  })
}

function getCategoryName(categoryId: number): string {
  return categories.value.find(c => c.id === categoryId)?.name || '-'
}

function formatPrice(price?: number): string {
  if (price === undefined || price === null) return '-'
  return new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(price)
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-display font-bold text-gray-800">Menu Yonetimi</h1>
    </div>

    <div class="border-b border-gray-200">
      <nav class="flex gap-4">
        <button
          @click="activeTab = 'categories'"
          :class="[
            'py-3 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === 'categories'
              ? 'border-brand-red text-brand-red'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          Kategoriler
        </button>
        <button
          @click="activeTab = 'items'"
          :class="[
            'py-3 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === 'items'
              ? 'border-brand-red text-brand-red'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          Urunler
        </button>
      </nav>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="text-gray-500">Yukleniyor...</div>
    </div>

    <div v-else-if="activeTab === 'categories'" class="space-y-4">
      <div class="flex justify-end">
        <button @click="openCategoryModal()" class="btn btn-primary">+ Yeni Kategori</button>
      </div>
      <div class="card">
        <table class="w-full">
          <thead>
            <tr class="border-b">
              <th class="text-left py-3 px-4 font-medium text-gray-600">Sira</th>
              <th class="text-left py-3 px-4 font-medium text-gray-600">Kategori Adi</th>
              <th class="text-left py-3 px-4 font-medium text-gray-600">Aciklama</th>
              <th class="text-center py-3 px-4 font-medium text-gray-600">Kapsam</th>
              <th class="text-center py-3 px-4 font-medium text-gray-600">Durum</th>
              <th class="text-right py-3 px-4 font-medium text-gray-600">Islemler</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="category in categories" :key="category.id" class="border-b hover:bg-gray-50">
              <td class="py-3 px-4 text-gray-600">{{ category.display_order }}</td>
              <td class="py-3 px-4 font-medium">{{ category.name }}</td>
              <td class="py-3 px-4 text-gray-600">{{ category.description || '-' }}</td>
              <td class="py-3 px-4 text-center">
                <span :class="['px-2 py-1 rounded-full text-xs font-medium', category.branch_id === null ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700']">
                  {{ category.branch_id === null ? 'Genel' : 'Sube' }}
                </span>
              </td>
              <td class="py-3 px-4 text-center">
                <span :class="['px-2 py-1 rounded-full text-xs font-medium', category.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700']">
                  {{ category.is_active ? 'Aktif' : 'Pasif' }}
                </span>
              </td>
              <td class="py-3 px-4 text-right">
                <button @click="openCategoryModal(category)" class="text-blue-600 hover:text-blue-800 mr-3">Duzenle</button>
                <button @click="toggleCategoryActive(category)" :class="category.is_active ? 'text-orange-600 hover:text-orange-800' : 'text-green-600 hover:text-green-800'" class="mr-3">{{ category.is_active ? 'Deaktif' : 'Aktif' }}</button>
                <button @click="deleteCategory(category)" class="text-red-600 hover:text-red-800">Sil</button>
              </td>
            </tr>
            <tr v-if="categories.length === 0">
              <td colspan="6" class="py-8 text-center text-gray-500">Henuz kategori eklenmemis</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-else-if="activeTab === 'items'" class="space-y-4">
      <div class="flex justify-between items-center">
        <div class="flex items-center gap-2">
          <label class="text-sm text-gray-600">Kategori:</label>
          <select v-model="selectedCategoryId" class="px-3 py-2 border border-gray-300 rounded-lg text-sm">
            <option :value="null">Tumu</option>
            <option v-for="cat in sortedCategories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
        </div>
        <button @click="openItemModal()" class="btn btn-primary">+ Yeni Urun</button>
      </div>
      <div class="card">
        <table class="w-full">
          <thead>
            <tr class="border-b">
              <th class="text-left py-3 px-4 font-medium text-gray-600">Sira</th>
              <th class="text-left py-3 px-4 font-medium text-gray-600">Urun Adi</th>
              <th class="text-left py-3 px-4 font-medium text-gray-600">Kategori</th>
              <th class="text-left py-3 px-4 font-medium text-gray-600">Aciklama</th>
              <th class="text-right py-3 px-4 font-medium text-gray-600">Fiyat</th>
              <th class="text-center py-3 px-4 font-medium text-gray-600">Durum</th>
              <th class="text-right py-3 px-4 font-medium text-gray-600">Islemler</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredItems" :key="item.id" class="border-b hover:bg-gray-50">
              <td class="py-3 px-4 text-gray-600">{{ item.display_order }}</td>
              <td class="py-3 px-4 font-medium">{{ item.name }}</td>
              <td class="py-3 px-4 text-gray-600">{{ getCategoryName(item.category_id) }}</td>
              <td class="py-3 px-4 text-gray-600 truncate max-w-xs">{{ item.description || '-' }}</td>
              <td class="py-3 px-4 text-right">
                <span :class="item.price_is_default ? 'text-gray-600' : 'text-green-600 font-medium'">{{ formatPrice(item.price) }}</span>
                <span v-if="item.price_is_default" class="text-xs text-gray-400 ml-1">(varsayilan)</span>
              </td>
              <td class="py-3 px-4 text-center">
                <span :class="['px-2 py-1 rounded-full text-xs font-medium', item.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700']">
                  {{ item.is_active ? 'Aktif' : 'Pasif' }}
                </span>
              </td>
              <td class="py-3 px-4 text-right">
                <button @click="openItemModal(item)" class="text-blue-600 hover:text-blue-800 mr-3">Duzenle</button>
                <button @click="toggleItemActive(item)" :class="item.is_active ? 'text-orange-600 hover:text-orange-800' : 'text-green-600 hover:text-green-800'" class="mr-3">{{ item.is_active ? 'Deaktif' : 'Aktif' }}</button>
                <button @click="deleteItem(item)" class="text-red-600 hover:text-red-800">Sil</button>
              </td>
            </tr>
            <tr v-if="filteredItems.length === 0">
              <td colspan="7" class="py-8 text-center text-gray-500">{{ selectedCategoryId ? 'Bu kategoride urun yok' : 'Henuz urun eklenmemis' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showCategoryModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-lg font-semibold mb-4">{{ editingCategory ? 'Kategori Duzenle' : 'Yeni Kategori' }}</h2>
        <form @submit.prevent="saveCategory" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Kategori Adi *</label>
            <input v-model="categoryForm.name" type="text" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-transparent" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Aciklama</label>
            <textarea v-model="categoryForm.description" rows="2" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-transparent" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Siralama</label>
            <input v-model.number="categoryForm.display_order" type="number" min="0" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-transparent" />
          </div>
          <div v-if="!editingCategory" class="flex items-center gap-2">
            <input v-model="categoryForm.is_global" type="checkbox" id="is_global" class="rounded border-gray-300" />
            <label for="is_global" class="text-sm text-gray-700">Tum subelerde gorunsun (Genel)</label>
          </div>
          <div class="flex justify-end gap-3 pt-4">
            <button type="button" @click="showCategoryModal = false" class="px-4 py-2 text-gray-600 hover:text-gray-800">Iptal</button>
            <button type="submit" class="btn btn-primary">Kaydet</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showItemModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-lg font-semibold mb-4">{{ editingItem ? 'Urun Duzenle' : 'Yeni Urun' }}</h2>
        <form @submit.prevent="saveItem" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Urun Adi *</label>
            <input v-model="itemForm.name" type="text" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-transparent" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Kategori *</label>
            <select v-model="itemForm.category_id" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-transparent">
              <option v-for="cat in sortedCategories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Aciklama</label>
            <textarea v-model="itemForm.description" rows="2" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-transparent" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Resim URL</label>
            <input v-model="itemForm.image_url" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-transparent" placeholder="/images/urun.jpg" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Siralama</label>
              <input v-model.number="itemForm.display_order" type="number" min="0" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-transparent" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Varsayilan Fiyat (TL)</label>
              <input v-model.number="itemForm.default_price" type="number" min="0" step="0.01" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-transparent" placeholder="0.00" />
            </div>
          </div>
          <div class="flex justify-end gap-3 pt-4">
            <button type="button" @click="showItemModal = false" class="px-4 py-2 text-gray-600 hover:text-gray-800">Iptal</button>
            <button type="submit" class="btn btn-primary">Kaydet</button>
          </div>
        </form>
      </div>
    </div>

    <ConfirmModal :show="showConfirm" :message="confirmMessage" @confirm="handleConfirm" @cancel="showConfirm = false" />
  </div>
</template>
