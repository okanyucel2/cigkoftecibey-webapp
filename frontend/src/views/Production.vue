<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { productionApi } from '@/services/api'
import type { DailyProduction, ProductionSummary } from '@/types'

const productions = ref<DailyProduction[]>([])
const summary = ref<ProductionSummary | null>(null)
const loading = ref(false)
const error = ref('')

// Filtre
const selectedMonth = ref(new Date().getMonth() + 1)
const selectedYear = ref(new Date().getFullYear())

// Form
const showForm = ref(false)
const editingId = ref<number | null>(null)
const form = ref({
  production_date: new Date().toISOString().split('T')[0],
  kneaded_kg: 0,
  legen_kg: 11.2,
  legen_cost: 1040,
  notes: ''
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
  { value: 12, label: 'Aralik' }
]

const years = computed(() => {
  const currentYear = new Date().getFullYear()
  return [currentYear - 1, currentYear, currentYear + 1]
})

// Hesaplanan form degerleri
const formLegenCount = computed(() => {
  if (form.value.legen_kg > 0) {
    return form.value.kneaded_kg / form.value.legen_kg
  }
  return 0
})

const formTotalCost = computed(() => {
  return formLegenCount.value * form.value.legen_cost
})

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const [prodRes, summaryRes] = await Promise.all([
      productionApi.getAll({ month: selectedMonth.value, year: selectedYear.value }),
      productionApi.getSummary({ month: selectedMonth.value, year: selectedYear.value })
    ])
    productions.value = prodRes.data
    summary.value = summaryRes.data
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Veri yuklenemedi'
  } finally {
    loading.value = false
  }
}

function openNewForm() {
  editingId.value = null
  form.value = {
    production_date: new Date().toISOString().split('T')[0],
    kneaded_kg: 0,
    legen_kg: 11.2,
    legen_cost: 1040,
    notes: ''
  }
  showForm.value = true
}

function editProduction(prod: DailyProduction) {
  editingId.value = prod.id
  form.value = {
    production_date: prod.production_date,
    kneaded_kg: prod.kneaded_kg,
    legen_kg: prod.legen_kg,
    legen_cost: prod.legen_cost,
    notes: prod.notes || ''
  }
  showForm.value = true
}

async function saveProduction() {
  if (form.value.kneaded_kg <= 0) {
    error.value = 'Yogrulan kilo 0\'dan buyuk olmali'
    return
  }

  loading.value = true
  error.value = ''
  try {
    if (editingId.value) {
      await productionApi.update(editingId.value, form.value)
    } else {
      await productionApi.create(form.value)
    }
    showForm.value = false
    await loadData()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Kayit basarisiz'
  } finally {
    loading.value = false
  }
}

async function deleteProduction(id: number) {
  if (!confirm('Bu kaydi silmek istediginize emin misiniz?')) return

  loading.value = true
  try {
    await productionApi.delete(id)
    await loadData()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Silme basarisiz'
  } finally {
    loading.value = false
  }
}

function formatNumber(num: number, decimals = 2): string {
  return new Intl.NumberFormat('tr-TR', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }).format(num)
}

function formatCurrency(num: number): string {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY'
  }).format(num)
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('tr-TR')
}

watch([selectedMonth, selectedYear], () => {
  loadData()
})

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-800">Gunluk Uretim / Legen Takibi</h1>
      <button
        @click="openNewForm"
        class="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
      >
        + Yeni Giris
      </button>
    </div>

    <!-- Filtreler -->
    <div class="bg-white rounded-lg shadow p-4 mb-6">
      <div class="flex gap-4 items-center">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Ay</label>
          <select
            v-model="selectedMonth"
            class="border rounded-lg px-3 py-2"
          >
            <option v-for="m in months" :key="m.value" :value="m.value">
              {{ m.label }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Yil</label>
          <select
            v-model="selectedYear"
            class="border rounded-lg px-3 py-2"
          >
            <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Ozet -->
    <div v-if="summary" class="bg-red-50 rounded-lg shadow p-4 mb-6">
      <h2 class="text-lg font-semibold text-red-800 mb-3">
        {{ months.find(m => m.value === selectedMonth)?.label }} {{ selectedYear }} Ozeti
      </h2>
      <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div class="bg-white rounded-lg p-3">
          <div class="text-sm text-gray-500">Toplam Yogrulan</div>
          <div class="text-xl font-bold text-gray-800">{{ formatNumber(summary.total_kneaded_kg) }} kg</div>
        </div>
        <div class="bg-white rounded-lg p-3">
          <div class="text-sm text-gray-500">Toplam Legen</div>
          <div class="text-xl font-bold text-gray-800">{{ formatNumber(summary.total_legen_count) }}</div>
        </div>
        <div class="bg-white rounded-lg p-3">
          <div class="text-sm text-gray-500">Toplam Maliyet</div>
          <div class="text-xl font-bold text-red-600">{{ formatCurrency(summary.total_cost) }}</div>
        </div>
        <div class="bg-white rounded-lg p-3">
          <div class="text-sm text-gray-500">Gunluk Ort.</div>
          <div class="text-xl font-bold text-gray-800">{{ formatNumber(summary.avg_daily_kg) }} kg</div>
        </div>
        <div class="bg-white rounded-lg p-3">
          <div class="text-sm text-gray-500">Gun Sayisi</div>
          <div class="text-xl font-bold text-gray-800">{{ summary.days_count }}</div>
        </div>
      </div>
    </div>

    <!-- Hata -->
    <div v-if="error" class="bg-red-100 text-red-700 p-4 rounded-lg mb-4">
      {{ error }}
    </div>

    <!-- Tablo -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="w-full">
        <thead class="bg-gray-100">
          <tr>
            <th class="px-4 py-3 text-left text-sm font-semibold text-gray-700">Tarih</th>
            <th class="px-4 py-3 text-right text-sm font-semibold text-gray-700">Yogrulan Kilo</th>
            <th class="px-4 py-3 text-right text-sm font-semibold text-gray-700">1 Legen (kg)</th>
            <th class="px-4 py-3 text-right text-sm font-semibold text-gray-700">Legen Sayisi</th>
            <th class="px-4 py-3 text-right text-sm font-semibold text-gray-700">1 Legen Maliyet</th>
            <th class="px-4 py-3 text-right text-sm font-semibold text-gray-700">Toplam Maliyet</th>
            <th class="px-4 py-3 text-left text-sm font-semibold text-gray-700">Not</th>
            <th class="px-4 py-3 text-center text-sm font-semibold text-gray-700">Islemler</th>
          </tr>
        </thead>
        <tbody class="divide-y">
          <tr v-if="loading">
            <td colspan="8" class="px-4 py-8 text-center text-gray-500">
              Yukleniyor...
            </td>
          </tr>
          <tr v-else-if="productions.length === 0">
            <td colspan="8" class="px-4 py-8 text-center text-gray-500">
              Bu donem icin uretim kaydi bulunamadi
            </td>
          </tr>
          <tr v-else v-for="prod in productions" :key="prod.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 text-sm">{{ formatDate(prod.production_date) }}</td>
            <td class="px-4 py-3 text-sm text-right font-medium">{{ formatNumber(prod.kneaded_kg) }}</td>
            <td class="px-4 py-3 text-sm text-right text-gray-600">{{ formatNumber(prod.legen_kg) }}</td>
            <td class="px-4 py-3 text-sm text-right font-medium text-blue-600">{{ formatNumber(prod.legen_count) }}</td>
            <td class="px-4 py-3 text-sm text-right text-gray-600">{{ formatCurrency(prod.legen_cost) }}</td>
            <td class="px-4 py-3 text-sm text-right font-bold text-red-600">{{ formatCurrency(prod.total_cost) }}</td>
            <td class="px-4 py-3 text-sm text-gray-500 truncate max-w-[150px]">{{ prod.notes || '-' }}</td>
            <td class="px-4 py-3 text-center">
              <button
                @click="editProduction(prod)"
                class="text-blue-600 hover:text-blue-800 text-sm mr-2"
              >
                Duzenle
              </button>
              <button
                @click="deleteProduction(prod.id)"
                class="text-red-600 hover:text-red-800 text-sm"
              >
                Sil
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Form Modal -->
    <div v-if="showForm" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-lg mx-4">
        <div class="p-6 border-b">
          <h2 class="text-xl font-semibold">
            {{ editingId ? 'Uretim Duzenle' : 'Yeni Uretim Girisi' }}
          </h2>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Tarih</label>
            <input
              type="date"
              v-model="form.production_date"
              class="w-full border rounded-lg px-3 py-2"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Yogrulan Kilo</label>
            <input
              type="number"
              step="0.1"
              v-model.number="form.kneaded_kg"
              class="w-full border rounded-lg px-3 py-2"
              placeholder="220"
            />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">1 Legen Kilosu</label>
              <input
                type="number"
                step="0.1"
                v-model.number="form.legen_kg"
                class="w-full border rounded-lg px-3 py-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">1 Legen Maliyeti</label>
              <input
                type="number"
                step="1"
                v-model.number="form.legen_cost"
                class="w-full border rounded-lg px-3 py-2"
              />
            </div>
          </div>

          <!-- Hesaplanan degerler -->
          <div class="bg-gray-50 rounded-lg p-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <div class="text-sm text-gray-500">Legen Sayisi</div>
                <div class="text-lg font-bold text-blue-600">{{ formatNumber(formLegenCount) }}</div>
              </div>
              <div>
                <div class="text-sm text-gray-500">Toplam Maliyet</div>
                <div class="text-lg font-bold text-red-600">{{ formatCurrency(formTotalCost) }}</div>
              </div>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Not (Opsiyonel)</label>
            <textarea
              v-model="form.notes"
              rows="2"
              class="w-full border rounded-lg px-3 py-2"
              placeholder="Aciklama..."
            ></textarea>
          </div>
        </div>
        <div class="p-6 border-t bg-gray-50 flex justify-end gap-3">
          <button
            @click="showForm = false"
            class="px-4 py-2 text-gray-700 border rounded-lg hover:bg-gray-100"
          >
            Iptal
          </button>
          <button
            @click="saveProduction"
            :disabled="loading"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
          >
            {{ loading ? 'Kaydediliyor...' : 'Kaydet' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
