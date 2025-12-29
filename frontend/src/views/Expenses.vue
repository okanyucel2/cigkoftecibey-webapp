<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import type { Expense, ExpenseCategory, DateRangeValue } from '@/types'
import { expensesApi, expenseCategoriesApi } from '@/services/api'

// Composables
import { useFormatters, useConfirmModal } from '@/composables'

// UI Components
import { ConfirmModal, ErrorAlert, LoadingState, PageModal, SummaryCard } from '@/components/ui'
import { UnifiedFilterBar } from '@/components/ui'
import type { EntityConfig } from '@/components/ui'

// Use composables
const { formatCurrency, formatDate } = useFormatters()
const confirmModal = useConfirmModal()

// Data
const expenses = ref<Expense[]>([])
const categories = ref<ExpenseCategory[]>([])
const loading = ref(true)
const error = ref('')

// Filters
const selectedCategoryId = ref<number | null>(null)

// Date Range Filter
const dateRangeFilter = ref<DateRangeValue>({
  mode: 'month',
  start: new Date().toISOString().split('T')[0],
  end: new Date().toISOString().split('T')[0],
  month: new Date().getMonth() + 1,
  year: new Date().getFullYear()
})

// Category Modal State
const showCategoryModal = ref(false)
const showCategoryForm = ref(false)
const editingCategoryId = ref<number | null>(null)
const categorySubmitting = ref(false)
const categoryForm = ref({
  name: '',
  is_fixed: false
})

onMounted(async () => {
  await Promise.all([loadExpenses(), loadCategories()])
})

watch(() => dateRangeFilter.value, () => {
  loadExpenses()
}, { deep: true })

watch(selectedCategoryId, () => {
  loadExpenses()
})

async function loadCategories() {
  try {
    const { data } = await expenseCategoriesApi.getAll()
    categories.value = data
  } catch (e) {
    console.error('Failed to load categories:', e)
  }
}

async function loadExpenses() {
  loading.value = true
  try {
    const params: { start_date: string; end_date: string; category_id?: number } = {
      start_date: dateRangeFilter.value.start,
      end_date: dateRangeFilter.value.end
    }
    if (selectedCategoryId.value) {
      params.category_id = selectedCategoryId.value
    }

    const { data } = await expensesApi.getAll(params)
    expenses.value = data
  } catch (e) {
    console.error('Failed to load expenses:', e)
    error.value = 'Giderler yuklenemedi'
  } finally {
    loading.value = false
  }
}

async function deleteExpense(id: number) {
  confirmModal.confirm('Bu gideri silmek istediginizden emin misiniz?', async () => {
    try {
      await expensesApi.delete(id)
      expenses.value = expenses.value.filter(e => e.id !== id)
    } catch (e) {
      console.error('Failed to delete expense:', e)
      error.value = 'Gider silinemedi!'
    }
  })
}

// Category Management
function openCategoryForm(category?: ExpenseCategory) {
  if (category) {
    editingCategoryId.value = category.id
    categoryForm.value = {
      name: category.name,
      is_fixed: category.is_fixed
    }
  } else {
    editingCategoryId.value = null
    categoryForm.value = {
      name: '',
      is_fixed: false
    }
  }
  showCategoryForm.value = true
}

async function submitCategoryForm() {
  if (!categoryForm.value.name.trim()) {
    error.value = 'Kategori adi zorunlu'
    return
  }

  categorySubmitting.value = true
  error.value = ''
  try {
    if (editingCategoryId.value) {
      await expenseCategoriesApi.update(editingCategoryId.value, categoryForm.value)
    } else {
      await expenseCategoriesApi.create(categoryForm.value)
    }
    showCategoryForm.value = false
    await loadCategories()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Kayit basarisiz'
  } finally {
    categorySubmitting.value = false
  }
}

async function deleteCategory(id: number) {
  confirmModal.confirm('Bu kategoriyi silmek istediginize emin misiniz?', async () => {
    error.value = ''
    try {
      await expenseCategoriesApi.delete(id)
      await loadCategories()
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Silme basarisiz'
    }
  })
}

// Entity selector config for categories
const categoryEntities = computed<EntityConfig>(() => ({
  items: categories.value.map(cat => ({
    id: cat.id,
    label: cat.name,
    icon: cat.is_fixed ? '📌' : '📦'
  })),
  allLabel: 'Tüm Kategoriler',
  showSettings: true,
  showCount: false
}))

// Summary calculations
const totalAmount = computed(() => {
  return expenses.value.reduce((sum, e) => sum + Number(e.amount), 0)
})

const fixedExpensesTotal = computed(() => {
  return expenses.value
    .filter(e => e.category?.is_fixed)
    .reduce((sum, e) => sum + Number(e.amount), 0)
})

const variableExpensesTotal = computed(() => {
  return expenses.value
    .filter(e => !e.category?.is_fixed)
    .reduce((sum, e) => sum + Number(e.amount), 0)
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between flex-wrap gap-4">
      <h1 class="text-2xl font-display font-bold text-gray-900">
        <span class="mr-2">💸</span> İşletme Giderleri
      </h1>
    </div>

    <!-- Error -->
    <ErrorAlert :message="error" @dismiss="error = ''" />

    <!-- Unified Filter Bar -->
    <UnifiedFilterBar
      v-model:date-range="dateRangeFilter"
      v-model:entity-id="selectedCategoryId"
      :entities="categoryEntities"
      :primary-action="{ label: '+ Yeni Gider', icon: 'add', route: '/expenses/new' }"
      @entity-settings="showCategoryModal = true"
    />

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <SummaryCard label="Sabit Giderler" :value="formatCurrency(fixedExpensesTotal)" variant="purple" />
      <SummaryCard label="Değişken Giderler" :value="formatCurrency(variableExpensesTotal)" />
      <SummaryCard label="Toplam Gider" :value="formatCurrency(totalAmount)" :subtext="`${expenses.length} kayıt`"
        variant="danger" data-testid="total-expenses-card" />
    </div>

    <!-- Expenses Table -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <LoadingState v-if="loading" />

      <div v-else-if="expenses.length === 0" class="p-8 text-center text-gray-500">
        Bu dönemde gider bulunamadı
      </div>

      <table v-else class="w-full">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tarih</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Kategori</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Açıklama</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Tutar</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">İşlem</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="expense in expenses" :key="expense.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 text-sm text-gray-900">
              {{ formatDate(expense.expense_date, { showWeekday: true }) }}
            </td>
            <td class="px-6 py-4">
              <span :class="[
                'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                expense.category?.is_fixed
                  ? 'bg-purple-100 text-purple-800'
                  : 'bg-gray-100 text-gray-800'
              ]">
                <span v-if="expense.category?.is_fixed" class="mr-1">📌</span>
                {{ expense.category?.name || '-' }}
              </span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
              {{ expense.description || '-' }}
            </td>
            <td class="px-6 py-4 text-right font-semibold text-gray-900">
              {{ formatCurrency(Number(expense.amount)) }}
            </td>
            <td class="px-6 py-4 text-right">
              <button @click="deleteExpense(expense.id)" class="text-red-500 hover:text-red-700 text-sm">
                Sil
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Category Management Modal -->
    <PageModal :show="showCategoryModal" title="Gider Kategorileri" @close="showCategoryModal = false">
      <div class="p-4">
        <!-- Category List -->
        <div v-if="!showCategoryForm" class="space-y-2">
          <div v-for="cat in categories" :key="cat.id"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div class="flex items-center gap-2">
              <span :class="[
                'text-lg',
                cat.is_fixed ? '' : 'opacity-50'
              ]">{{ cat.is_fixed ? '📌' : '📦' }}</span>
              <span class="font-medium">{{ cat.name }}</span>
              <span v-if="cat.is_fixed" class="text-xs text-purple-600">(Sabit)</span>
            </div>
            <div class="flex gap-2">
              <button @click="openCategoryForm(cat)" class="text-blue-600 hover:text-blue-800 text-sm">Düzenle</button>
              <button @click="deleteCategory(cat.id)" class="text-red-600 hover:text-red-800 text-sm">Sil</button>
            </div>
          </div>

          <div v-if="categories.length === 0" class="text-center py-4 text-gray-500">
            Henüz kategori yok
          </div>

          <button @click="openCategoryForm()"
            class="w-full mt-4 py-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-gray-400 hover:text-gray-700">
            + Yeni Kategori Ekle
          </button>
        </div>

        <!-- Category Form -->
        <div v-else class="space-y-4">
          <div class="flex items-center gap-2 mb-4">
            <button @click="showCategoryForm = false" class="text-gray-500 hover:text-gray-700">
              ←
            </button>
            <h3 class="font-medium">{{ editingCategoryId ? 'Kategori Düzenle' : 'Yeni Kategori' }}</h3>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Kategori Adı *</label>
            <input v-model="categoryForm.name" type="text" class="w-full border rounded-lg px-3 py-2"
              placeholder="örneğin: Kira, Elektrik, Temizlik..." />
          </div>

          <div class="flex items-center gap-2">
            <input v-model="categoryForm.is_fixed" type="checkbox" id="is_fixed" class="rounded text-purple-600" />
            <label for="is_fixed" class="text-sm text-gray-700">
              Sabit gider kategorisi (Kira, SGK gibi her ay tekrar eden)
            </label>
          </div>

          <div class="flex gap-3 pt-2">
            <button @click="showCategoryForm = false"
              class="flex-1 py-2 border rounded-lg text-gray-700 hover:bg-gray-100">
              İptal
            </button>
            <button @click="submitCategoryForm" :disabled="categorySubmitting"
              class="flex-1 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50">
              {{ categorySubmitting ? 'Kaydediliyor...' : 'Kaydet' }}
            </button>
          </div>
        </div>
      </div>
    </PageModal>

    <ConfirmModal :show="confirmModal.isOpen.value" :message="confirmModal.message.value"
      @confirm="confirmModal.handleConfirm" @cancel="confirmModal.handleCancel" />
  </div>
</template>
