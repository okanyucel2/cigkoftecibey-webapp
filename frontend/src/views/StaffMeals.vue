<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import type { StaffMeal, StaffMealSummary } from '@/types'
import { staffMealsApi } from '@/services/api'
import ConfirmModal from '@/components/ui/ConfirmModal.vue'

const meals = ref<StaffMeal[]>([])
const summary = ref<StaffMealSummary | null>(null)
const loading = ref(true)
const error = ref('')
const submitting = ref(false)

// Ay/Yıl filtreleme
const currentDate = new Date()
const selectedMonth = ref(currentDate.getMonth() + 1)
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

const years = computed(() => {
  const currentYear = new Date().getFullYear()
  return [currentYear, currentYear - 1, currentYear - 2]
})

// Form state
const showForm = ref(false)
const editingId = ref<number | null>(null)
const form = ref({
  meal_date: new Date().toISOString().split('T')[0],
  unit_price: 145,
  staff_count: 0,
  notes: ''
})

// Son girilen birim fiyatı hatırla
const lastUnitPrice = ref(145)

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
  await loadData()
})

watch([selectedMonth, selectedYear], () => {
  loadData()
})

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const [mealsRes, summaryRes] = await Promise.all([
      staffMealsApi.getAll({ month: selectedMonth.value, year: selectedYear.value }),
      staffMealsApi.getSummary({ month: selectedMonth.value, year: selectedYear.value })
    ])
    meals.value = mealsRes.data
    summary.value = summaryRes.data

    // Son girilen fiyatı bul
    if (mealsRes.data.length > 0) {
      lastUnitPrice.value = Number(mealsRes.data[0].unit_price)
    }
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Veri yuklenemedi'
  } finally {
    loading.value = false
  }
}

function openAddForm() {
  editingId.value = null
  form.value = {
    meal_date: new Date().toISOString().split('T')[0],
    unit_price: lastUnitPrice.value,
    staff_count: 0,
    notes: ''
  }
  showForm.value = true
}

function openEditForm(meal: StaffMeal) {
  editingId.value = meal.id
  form.value = {
    meal_date: meal.meal_date,
    unit_price: Number(meal.unit_price),
    staff_count: meal.staff_count,
    notes: meal.notes || ''
  }
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editingId.value = null
}

async function handleSubmit() {
  if (form.value.staff_count <= 0) {
    error.value = 'Personel adedi 0 dan buyuk olmali'
    return
  }

  submitting.value = true
  error.value = ''
  try {
    const data = {
      meal_date: form.value.meal_date,
      unit_price: form.value.unit_price,
      staff_count: form.value.staff_count,
      notes: form.value.notes || undefined
    }

    if (editingId.value) {
      await staffMealsApi.update(editingId.value, data)
    } else {
      await staffMealsApi.create(data)
    }

    lastUnitPrice.value = form.value.unit_price
    closeForm()
    await loadData()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Kayit basarisiz'
  } finally {
    submitting.value = false
  }
}

async function deleteMeal(id: number) {
  openConfirm('Bu kaydi silmek istediginize emin misiniz?', async () => {
    try {
      await staffMealsApi.delete(id)
      const index = meals.value.findIndex(m => m.id === id)
      if (index > -1) {
        meals.value.splice(index, 1)
      }
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Silme basarisiz'
    }
  })
}

function formatCurrency(value: number | string) {
  const num = Number(value) || 0
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 0
  }).format(num)
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('tr-TR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    weekday: 'long'
  })
}

// Hesaplanan toplam
const formTotal = computed(() => form.value.unit_price * form.value.staff_count)
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between flex-wrap gap-4">
      <h1 class="text-2xl font-display font-bold text-gray-900">Personel Yemek</h1>
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
          @click="openAddForm"
          class="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
        >
          + Yeni Kayit
        </button>
      </div>
    </div>

    <!-- Error -->
    <div v-if="error" class="bg-red-100 text-red-700 p-4 rounded-lg">
      {{ error }}
      <button @click="error = ''" class="ml-2 text-red-800 font-bold">x</button>
    </div>

    <!-- Aylık Özet -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow p-4">
        <p class="text-sm text-gray-500">Toplam Tutar</p>
        <p class="text-2xl font-bold text-gray-900">{{ formatCurrency(summary?.total_cost || 0) }}</p>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <p class="text-sm text-gray-500">Toplam Kisi</p>
        <p class="text-2xl font-bold text-gray-900">{{ summary?.total_staff_count || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <p class="text-sm text-gray-500">Gunluk Ortalama</p>
        <p class="text-2xl font-bold text-gray-900">{{ Number(summary?.avg_daily_staff || 0).toFixed(1) }} kisi</p>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <p class="text-sm text-gray-500">Kayit Sayisi</p>
        <p class="text-2xl font-bold text-gray-900">{{ summary?.days_count || 0 }} gun</p>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-8 text-gray-500">
      Yukleniyor...
    </div>

    <!-- Kayıt Listesi -->
    <div v-else class="bg-white rounded-lg shadow overflow-hidden">
      <div v-if="meals.length === 0" class="p-8 text-center text-gray-500">
        Bu ay icin kayit bulunamadi
      </div>

      <table v-else class="w-full">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tarih</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Birim Fiyat</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Adet</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Toplam</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Not</th>
            <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Islemler</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="meal in meals" :key="meal.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 text-sm text-gray-900">
              {{ formatDate(meal.meal_date) }}
            </td>
            <td class="px-6 py-4 text-right text-sm text-gray-900">
              {{ formatCurrency(meal.unit_price) }}
            </td>
            <td class="px-6 py-4 text-right text-sm font-medium text-gray-900">
              {{ meal.staff_count }}
            </td>
            <td class="px-6 py-4 text-right font-semibold text-gray-900">
              {{ formatCurrency(meal.total) }}
            </td>
            <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
              {{ meal.notes || '-' }}
            </td>
            <td class="px-6 py-4 text-center">
              <div class="flex items-center justify-center gap-2">
                <button
                  @click="openEditForm(meal)"
                  class="text-blue-600 hover:text-blue-800 text-sm px-2 py-1"
                >
                  Duzenle
                </button>
                <button
                  @click="deleteMeal(meal.id)"
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

    <!-- Form Modal -->
    <div v-if="showForm" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        <div class="p-6 border-b flex justify-between items-center">
          <h2 class="text-xl font-semibold">
            {{ editingId ? 'Kayit Duzenle' : 'Yeni Personel Yemek Kaydi' }}
          </h2>
          <button @click="closeForm" class="text-gray-500 hover:text-gray-700 text-2xl">&times;</button>
        </div>

        <form @submit.prevent="handleSubmit" class="p-6 space-y-4">
          <!-- Tarih -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Tarih *</label>
            <input
              v-model="form.meal_date"
              type="date"
              class="w-full border rounded-lg px-3 py-2"
              required
            />
          </div>

          <!-- Birim Fiyat -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Birim Fiyat (TL) *</label>
            <input
              v-model.number="form.unit_price"
              type="number"
              step="0.01"
              min="0"
              class="w-full border rounded-lg px-3 py-2"
              required
            />
          </div>

          <!-- Personel Adedi -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Personel Adedi *</label>
            <input
              v-model.number="form.staff_count"
              type="number"
              min="1"
              class="w-full border rounded-lg px-3 py-2"
              required
            />
          </div>

          <!-- Hesaplanan Toplam -->
          <div class="bg-gray-50 rounded-lg p-4">
            <p class="text-sm text-gray-500">Toplam Tutar</p>
            <p class="text-2xl font-bold text-gray-900">{{ formatCurrency(formTotal) }}</p>
          </div>

          <!-- Not -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Not</label>
            <input
              v-model="form.notes"
              type="text"
              class="w-full border rounded-lg px-3 py-2"
              placeholder="Opsiyonel not..."
            />
          </div>

          <!-- Buttons -->
          <div class="flex justify-end gap-3 pt-4">
            <button
              type="button"
              @click="closeForm"
              class="px-4 py-2 border rounded-lg text-gray-700 hover:bg-gray-100"
            >
              Iptal
            </button>
            <button
              type="submit"
              :disabled="submitting"
              class="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
            >
              {{ submitting ? 'Kaydediliyor...' : (editingId ? 'Guncelle' : 'Kaydet') }}
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
