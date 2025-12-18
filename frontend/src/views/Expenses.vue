<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import type { Expense, ExpenseCategory } from '@/types'
import { expensesApi, expenseCategoriesApi } from '@/services/api'
import ConfirmModal from '@/components/ui/ConfirmModal.vue'

const expenses = ref<Expense[]>([])
const categories = ref<ExpenseCategory[]>([])
const loading = ref(true)
const error = ref('')

// Filtreler
const currentDate = new Date()
const selectedMonth = ref(currentDate.getMonth() + 1)
const selectedYear = ref(currentDate.getFullYear())
const selectedCategoryId = ref<number | null>(null)

// Kategori Modal State
const showCategoryModal = ref(false)
const showCategoryForm = ref(false)
const editingCategoryId = ref<number | null>(null)
const categorySubmitting = ref(false)
const categoryForm = ref({
  name: '',
  is_fixed: false
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

// Confirm Modal
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

onMounted(async () => {
  await Promise.all([loadExpenses(), loadCategories()])
})

watch([selectedMonth, selectedYear, selectedCategoryId], () => {
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
    // Ay baslangic ve bitis tarihleri
    const startDate = new Date(selectedYear.value, selectedMonth.value - 1, 1)
    const endDate = new Date(selectedYear.value, selectedMonth.value, 0)

    const params: { start_date: string; end_date: string; category_id?: number } = {
      start_date: startDate.toISOString().split('T')[0],
      end_date: endDate.toISOString().split('T')[0]
    }
    if (selectedCategoryId.value) {
      params.category_id = selectedCategoryId.value
    }

    const { data } = await expensesApi.getAll(params)
    expenses.value = data
  } catch (e) {
    console.error('Failed to load expenses:', e)
  } finally {
    loading.value = false
  }
}

async function deleteExpense(id: number) {
  openConfirm('Bu gideri silmek istediginizden emin misiniz?', async () => {
    try {
      await expensesApi.delete(id)
      expenses.value = expenses.value.filter(e => e.id !== id) // Optimistic
    } catch (e) {
      console.error('Failed to delete expense:', e)
      alert('Gider silinemedi!')
    }
  })
}

// ==================== KATEGORI YONETIMI ====================

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
  openConfirm('Bu kategoriyi silmek istediginize emin misiniz?', async () => {
    error.value = ''
    try {
      await expenseCategoriesApi.delete(id)
      await loadCategories()
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Silme basarisiz'
    }
  })
}

// Ozet hesaplamalari
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
    month: 'long',
    weekday: 'short'
  })
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between flex-wrap gap-4">
      <h1 class="text-2xl font-display font-bold text-gray-900">Isletme Giderleri</h1>
    </div>

    <!-- Error -->
    <div v-if="error" class="bg-red-100 text-red-700 p-4 rounded-lg">
      {{ error }}
      <button @click="error = ''" class="ml-2 text-red-800 font-bold">x</button>
    </div>

    <!-- Filtreler -->
    <div class="flex items-center justify-between flex-wrap gap-4">
      <div class="flex gap-3 items-center flex-wrap">
        <!-- Ay/Yil -->
        <div class="flex gap-2 items-center bg-gray-100 rounded-lg px-3 py-1.5">
          <select v-model="selectedMonth" class="bg-transparent border-none text-sm font-medium focus:ring-0">
            <option v-for="month in months" :key="month.value" :value="month.value">{{ month.label }}</option>
          </select>
          <select v-model="selectedYear" class="bg-transparent border-none text-sm font-medium focus:ring-0">
            <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
          </select>
        </div>
        <!-- Kategori Filtresi + Ayar -->
        <div class="flex items-center gap-1">
          <select
            v-model="selectedCategoryId"
            class="bg-gray-100 border-none rounded-lg px-3 py-1.5 text-sm font-medium focus:ring-0"
          >
            <option :value="null">Tum Kategoriler</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
          <button
            @click="showCategoryModal = true"
            class="p-1.5 text-gray-500 hover:text-gray-700 hover:bg-gray-200 rounded-lg"
            title="Kategorileri Yonet"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
      </div>
      <router-link to="/expenses/new" class="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700">
        + Yeni Gider
      </router-link>
    </div>

    <!-- Ozet Kartlari -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white rounded-lg shadow p-4">
        <p class="text-sm text-gray-500">Sabit Giderler</p>
        <p class="text-xl font-bold text-purple-600">{{ formatCurrency(fixedExpensesTotal) }}</p>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <p class="text-sm text-gray-500">Degisken Giderler</p>
        <p class="text-xl font-bold text-gray-900">{{ formatCurrency(variableExpensesTotal) }}</p>
      </div>
      <div class="bg-white rounded-lg shadow p-4 border-l-4 border-red-500">
        <p class="text-sm text-gray-500">Toplam Gider</p>
        <p class="text-xl font-bold text-red-600">{{ formatCurrency(totalAmount) }}</p>
        <p class="text-xs text-gray-400">{{ expenses.length }} kayit</p>
      </div>
    </div>

    <!-- Expenses Table -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-gray-500">
        Yukleniyor...
      </div>

      <div v-else-if="expenses.length === 0" class="p-8 text-center text-gray-500">
        Bu donemde gider bulunamadi
      </div>

      <table v-else class="w-full">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Tarih
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Kategori
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Aciklama
            </th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
              Tutar
            </th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
              Islem
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="expense in expenses" :key="expense.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 text-sm text-gray-900">
              {{ formatDate(expense.expense_date) }}
            </td>
            <td class="px-6 py-4">
              <span :class="[
                'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                expense.category?.is_fixed
                  ? 'bg-purple-100 text-purple-800'
                  : 'bg-gray-100 text-gray-800'
              ]">
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
              <button
                @click="deleteExpense(expense.id)"
                class="text-red-500 hover:text-red-700 text-sm"
              >
                Sil
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ==================== KATEGORI YONETIM MODAL ==================== -->
    <div v-if="showCategoryModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-4 border-b flex justify-between items-center sticky top-0 bg-white">
          <h2 class="text-lg font-semibold">Gider Kategorileri</h2>
          <button @click="showCategoryModal = false" class="text-gray-500 hover:text-gray-700 text-2xl">&times;</button>
        </div>

        <div class="p-4">
          <!-- Kategori Listesi -->
          <div v-if="!showCategoryForm" class="space-y-2">
            <div
              v-for="cat in categories"
              :key="cat.id"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div class="flex items-center gap-2">
                <span :class="[
                  'w-3 h-3 rounded-full',
                  cat.is_fixed ? 'bg-purple-500' : 'bg-gray-400'
                ]"></span>
                <span class="font-medium">{{ cat.name }}</span>
                <span v-if="cat.is_fixed" class="text-xs text-purple-600">(Sabit)</span>
              </div>
              <div class="flex gap-2">
                <button @click="openCategoryForm(cat)" class="text-blue-600 hover:text-blue-800 text-sm">Duzenle</button>
                <button @click="deleteCategory(cat.id)" class="text-red-600 hover:text-red-800 text-sm">Sil</button>
              </div>
            </div>

            <div v-if="categories.length === 0" class="text-center py-4 text-gray-500">
              Henuz kategori yok
            </div>

            <button
              @click="openCategoryForm()"
              class="w-full mt-4 py-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-gray-400 hover:text-gray-700"
            >
              + Yeni Kategori Ekle
            </button>
          </div>

          <!-- Kategori Formu -->
          <div v-else class="space-y-4">
            <div class="flex items-center gap-2 mb-4">
              <button @click="showCategoryForm = false" class="text-gray-500 hover:text-gray-700">
                &larr;
              </button>
              <h3 class="font-medium">{{ editingCategoryId ? 'Kategori Duzenle' : 'Yeni Kategori' }}</h3>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Kategori Adi *</label>
              <input
                v-model="categoryForm.name"
                type="text"
                class="w-full border rounded-lg px-3 py-2"
                placeholder="ornegin: Kira, Elektrik, Temizlik..."
              />
            </div>

            <div class="flex items-center gap-2">
              <input
                v-model="categoryForm.is_fixed"
                type="checkbox"
                id="is_fixed"
                class="rounded text-purple-600"
              />
              <label for="is_fixed" class="text-sm text-gray-700">
                Sabit gider kategorisi (Kira, SGK gibi her ay tekrar eden)
              </label>
            </div>

            <div class="flex gap-3 pt-2">
              <button
                @click="showCategoryForm = false"
                class="flex-1 py-2 border rounded-lg text-gray-700 hover:bg-gray-100"
              >
                Iptal
              </button>
              <button
                @click="submitCategoryForm"
                :disabled="categorySubmitting"
                class="flex-1 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
              >
                {{ categorySubmitting ? 'Kaydediliyor...' : 'Kaydet' }}
              </button>
            </div>
          </div>
        </div>
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
