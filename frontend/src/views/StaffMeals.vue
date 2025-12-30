// Genesis Auto-Fix Version: 10 (Last: 2025-12-21 16:50:16)

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import type { StaffMeal, StaffMealSummary } from '@/types'
import { staffMealsApi } from '@/services/api'
import type { DateRangeValue } from '@/types/filters'

// Composables
import { useFormatters, useConfirmModal } from '@/composables'

// UI Components
import { ConfirmModal, ErrorAlert, LoadingState, UnifiedFilterBar, PageModal, SummaryCard } from '@/components/ui'

// Use composables
const { formatCurrency, formatDate } = useFormatters()
const confirmModal = useConfirmModal()

// Data
const meals = ref<StaffMeal[]>([])
const summary = ref<StaffMealSummary | null>(null)
const loading = ref(true)
const error = ref('')
const submitting = ref(false)

// Form state
const showForm = ref(false)
const editingId = ref<number | null>(null)
const form = ref({
  meal_date: new Date().toISOString().split('T')[0],
  unit_price: 145,
  staff_count: 0,
  notes: ''
})

// Remember last unit price
const lastUnitPrice = ref(145)

// Date range filter (defaults to current month)
const dateRangeFilter = ref<DateRangeValue>({
  mode: 'range',
  start: new Date().toISOString().split('T')[0],
  end: new Date().toISOString().split('T')[0]
})

// Extract month/year from date range for API
const filterMonth = computed(() => new Date(dateRangeFilter.value.start).getMonth() + 1)
const filterYear = computed(() => new Date(dateRangeFilter.value.start).getFullYear())

onMounted(async () => {
  await loadData()
})

watch(() => dateRangeFilter.value, () => {
  loadData()
}, { deep: true })

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const [mealsRes, summaryRes] = await Promise.all([
      staffMealsApi.getAll({ month: filterMonth.value, year: filterYear.value }),
      staffMealsApi.getSummary({ month: filterMonth.value, year: filterYear.value })
    ])
    meals.value = mealsRes.data
    summary.value = summaryRes.data

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
  confirmModal.confirm('Bu kaydi silmek istediginize emin misiniz?', async () => {
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

// Calculated total
const formTotal = computed(() => form.value.unit_price * form.value.staff_count)
</script>

<template>
  <div class="space-y-6">
    <!-- Unified Filter Bar -->
    <UnifiedFilterBar
      v-model:date-range="dateRangeFilter"
      :primary-action="{ label: 'Yeni Kayıt', onClick: openAddForm }"
    />

    <!-- Error -->
    <ErrorAlert :message="error" @dismiss="error = ''" />

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <SummaryCard
        label="Toplam Tutar"
        :value="formatCurrency(summary?.total_cost || 0)"
      />
      <SummaryCard
        label="Toplam Kisi"
        :value="summary?.total_staff_count || 0"
        variant="primary"
      />
      <SummaryCard
        label="Gunluk Ortalama"
        :value="`${Number(summary?.avg_daily_staff || 0).toFixed(1)} kisi`"
        variant="info"
      />
      <SummaryCard
        label="Kayit Sayisi"
        :value="`${summary?.days_count || 0} gun`"
        variant="purple"
      />
    </div>

    <!-- Table -->
    <div class="bg-white rounded-lg shadow overflow-hidden" data-testid="staff-meals-table">
      <LoadingState v-if="loading" />

      <div v-else-if="meals.length === 0" class="p-8 text-center text-gray-500">
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
              {{ formatDate(meal.meal_date, { format: 'long', showWeekday: true }) }}
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
                  data-testid="btn-edit-staff-meal"
                  class="text-blue-600 hover:text-blue-800 text-sm px-2 py-1"
                >
                  Duzenle
                </button>
                <button
                  @click="deleteMeal(meal.id)"
                  data-testid="btn-delete-staff-meal"
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
    <PageModal
      :show="showForm"
      :title="editingId ? 'Kayit Duzenle' : 'Yeni Personel Yemek Kaydi'"
      size="lg"
      @close="closeForm"
    >
      <form @submit.prevent="handleSubmit" class="p-6 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Tarih *</label>
          <input
            v-model="form.meal_date"
            type="date"
            data-testid="input-meal-date"
            class="w-full border rounded-lg px-3 py-2"
            required
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Birim Fiyat (TL) *</label>
          <input
            v-model.number="form.unit_price"
            type="number"
            step="0.01"
            min="0"
            data-testid="input-unit-price"
            class="w-full border rounded-lg px-3 py-2"
            required
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Personel Adedi *</label>
          <input
            v-model.number="form.staff_count"
            type="number"
            min="1"
            data-testid="input-staff-count"
            class="w-full border rounded-lg px-3 py-2"
            required
          />
        </div>

        <div class="bg-gray-50 rounded-lg p-4">
          <p class="text-sm text-gray-500">Toplam Tutar</p>
          <p class="text-2xl font-bold text-gray-900">{{ formatCurrency(formTotal) }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Not</label>
          <textarea
            v-model="form.notes"
            data-testid="textarea-notes"
            class="w-full border rounded-lg px-3 py-2"
            placeholder="Opsiyonel not..."
            rows="3"
          ></textarea>
        </div>

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
            data-testid="btn-save-staff-meal"
            :disabled="submitting"
            class="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
          >
            {{ submitting ? 'Kaydediliyor...' : (editingId ? 'Guncelle' : 'Kaydet') }}
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
