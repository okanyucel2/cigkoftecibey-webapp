<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { productionApi } from '@/services/api'
import type { DailyProduction, ProductionSummary } from '@/types'
import type { DateRangeValue } from '@/types/filters'
import { extractErrorMessage } from '@/types'

// Composables
import { useFormatters, useConfirmModal } from '@/composables'

// UI Components
import { ConfirmModal, ErrorAlert, LoadingState, UnifiedFilterBar, PageModal, SummaryCard } from '@/components/ui'

// Use composables
const { formatCurrency, formatDate, formatNumber } = useFormatters()
const confirmModal = useConfirmModal()

// Data
const productions = ref<DailyProduction[]>([])
const summary = ref<ProductionSummary | null>(null)
const loading = ref(false)
const error = ref('')

// Form
const showForm = ref(false)
const editingId = ref<number | null>(null)
const form = ref({
  production_date: new Date().toISOString().split('T')[0],
  production_type: 'etli' as 'etli' | 'etsiz',
  kneaded_kg: 0,
  legen_kg: 11.2,
  legen_cost: 1040,
  notes: ''
})

// Production type options
const productionTypes = [
  { value: 'etli', label: 'Etli Çiğ Köfte' },
  { value: 'etsiz', label: 'Etsiz Çiğ Köfte' }
]

// Date range filter (defaults to current month)
const dateRangeFilter = ref<DateRangeValue>({
  mode: 'range',
  start: new Date().toISOString().split('T')[0],
  end: new Date().toISOString().split('T')[0]
})

// Extract month/year from date range for API
const filterMonth = computed(() => new Date(dateRangeFilter.value.start).getMonth() + 1)
const filterYear = computed(() => new Date(dateRangeFilter.value.start).getFullYear())

// Summary label based on filter
const summaryLabel = computed(() => {
  const date = new Date(dateRangeFilter.value.start)
  const months = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
  return `${months[date.getMonth()]} ${date.getFullYear()} Özeti`
})

// Calculated form values
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
      productionApi.getAll({ month: filterMonth.value, year: filterYear.value }),
      productionApi.getSummary({ month: filterMonth.value, year: filterYear.value })
    ])
    productions.value = prodRes.data
    summary.value = summaryRes.data
  } catch (e: unknown) {
    error.value = extractErrorMessage(e, 'Veri yuklenemedi')
  } finally {
    loading.value = false
  }
}

function openNewForm() {
  editingId.value = null
  form.value = {
    production_date: new Date().toISOString().split('T')[0],
    production_type: 'etli',
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
    production_type: (prod.production_type || 'etli') as 'etli' | 'etsiz',
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
  } catch (e: unknown) {
    error.value = extractErrorMessage(e, 'Kayit basarisiz')
  } finally {
    loading.value = false
  }
}

async function deleteProduction(id: number) {
  confirmModal.confirm('Bu kaydi silmek istediginize emin misiniz?', async () => {
    loading.value = true
    try {
      await productionApi.delete(id)
      const index = productions.value.findIndex(p => p.id === id)
      if (index > -1) {
        productions.value.splice(index, 1)
      }
    } catch (e: unknown) {
      error.value = extractErrorMessage(e, 'Silme basarisiz')
    } finally {
      loading.value = false
    }
  })
}

watch(() => dateRangeFilter.value, () => {
  loadData()
}, { deep: true })

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Unified Filter Bar -->
    <UnifiedFilterBar
      v-model:date-range="dateRangeFilter"
      :primary-action="{ label: 'Yeni Giriş', onClick: openNewForm }"
    />

    <!-- Error -->
    <ErrorAlert :message="error" @dismiss="error = ''" />

    <!-- Summary -->
    <div v-if="summary" class="bg-red-50 rounded-lg shadow p-4">
      <h2 class="text-lg font-semibold text-red-800 mb-3">
        📊 {{ summaryLabel }}
      </h2>
      <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
        <SummaryCard
          label="Toplam Yogrulan"
          :value="`${formatNumber(summary.total_kneaded_kg)} kg`"
        />
        <SummaryCard
          label="Toplam Legen"
          :value="formatNumber(summary.total_legen_count)"
          variant="primary"
        />
        <SummaryCard
          label="Toplam Maliyet"
          :value="formatCurrency(summary.total_cost)"
          variant="danger"
        />
        <SummaryCard
          label="Gunluk Ort."
          :value="`${formatNumber(summary.avg_daily_kg)} kg`"
          variant="info"
        />
        <SummaryCard
          label="Gun Sayisi"
          :value="summary.days_count"
          variant="purple"
        />
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <LoadingState v-if="loading" />

      <div v-else-if="productions.length === 0" class="p-8 text-center text-gray-500">
        Bu donem icin uretim kaydi bulunamadi
      </div>

      <table v-else class="w-full">
        <thead class="bg-gray-100">
          <tr>
            <th class="px-4 py-3 text-left text-sm font-semibold text-gray-700">Tarih</th>
            <th class="px-4 py-3 text-left text-sm font-semibold text-gray-700">Tip</th>
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
          <tr v-for="prod in productions" :key="prod.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 text-sm">{{ formatDate(prod.production_date, { format: 'short' }) }}</td>
            <td class="px-4 py-3 text-sm">
              <span
                :class="{
                  'bg-red-100 text-red-700': prod.production_type === 'etli',
                  'bg-green-100 text-green-700': prod.production_type === 'etsiz'
                }"
                class="px-2 py-1 text-xs font-medium rounded-full"
              >
                {{ prod.production_type === 'etli' ? 'Etli' : 'Etsiz' }}
              </span>
            </td>
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
    <PageModal
      :show="showForm"
      :title="editingId ? 'Uretim Duzenle' : 'Yeni Uretim Girisi'"
      size="lg"
      @close="showForm = false"
    >
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
          <label class="block text-sm font-medium text-gray-700 mb-1">Üretim Tipi</label>
          <select
            v-model="form.production_type"
            class="w-full border rounded-lg px-3 py-2"
          >
            <option v-for="type in productionTypes" :key="type.value" :value="type.value">
              {{ type.label }}
            </option>
          </select>
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

        <!-- Calculated values -->
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

      <template #footer>
        <div class="flex justify-end gap-3">
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
      </template>
    </PageModal>

    <ConfirmModal
      :show="confirmModal.isOpen.value"
      :message="confirmModal.message.value"
      @confirm="confirmModal.handleConfirm"
      @cancel="confirmModal.handleCancel"
    />
  </div>
</template>
