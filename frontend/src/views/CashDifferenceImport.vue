<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ExcelParseResult, POSParseResult, ExpenseCategory } from '@/types'
import { cashDifferenceApi, categorizationApi, expenseCategoriesApi } from '@/services/api'
import { useFormatters } from '@/composables'
import { ErrorAlert, LoadingState } from '@/components/ui'

// Emit success event when import is completed
const emit = defineEmits<{
  (e: 'success'): void
  (e: 'cancel'): void
}>()

// Use composables
const { formatCurrency, formatDate } = useFormatters()

// State
const loading = ref(false)
const error = ref('')

// File uploads
const excelFile = ref<File | null>(null)
const hasilatExcelFile = ref<File | null>(null)
const excelFileName = ref('')
const hasilatExcelFileName = ref('')

// Drag and drop states
const excelDragOver = ref(false)
const hasilatDragOver = ref(false)

// Parsed data
const excelData = ref<ExcelParseResult | null>(null)
const posData = ref<POSParseResult | null>(null)
const parsingExcel = ref(false)
const parsingPOS = ref(false)

// Categories
const categories = ref<ExpenseCategory[]>([])
const loadingCategories = ref(false)

// Computed: check if both files are parsed and ready
const canSubmit = computed(() => excelData.value && posData.value && !loading.value)

// Computed: comparison data for table
const comparisonData = computed(() => {
  if (!excelData.value || !posData.value) return []

  const channels = [
    { key: 'visa', label: 'Visa' },
    { key: 'nakit', label: 'Nakit' },
    { key: 'trendyol', label: 'Trendyol' },
    { key: 'getir', label: 'Getir' },
    { key: 'yemeksepeti', label: 'Yemek Sepeti' },
    { key: 'migros', label: 'Migros' }
  ]

  return channels.map(ch => {
    const kasaVal = (excelData.value as any)[ch.key] || 0
    const posVal = (posData.value as any)[ch.key] || 0
    const diff = kasaVal - posVal
    return {
      label: ch.label,
      kasa: kasaVal,
      pos: posVal,
      diff,
      diffClass: diff === 0 ? 'text-gray-600' : diff > 0 ? 'text-green-600' : 'text-red-600'
    }
  })
})

// Computed: total row
const totalRow = computed(() => {
  if (!excelData.value || !posData.value) return null
  const diff = excelData.value.total - posData.value.total
  return {
    kasa: excelData.value.total,
    pos: posData.value.total,
    diff,
    diffClass: diff === 0 ? 'text-gray-600' : diff > 0 ? 'text-green-600' : 'text-red-600'
  }
})

// Excel file handlers
function handleExcelFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    excelFile.value = target.files[0]
    excelFileName.value = target.files[0].name
  }
}

function handleExcelDrop(event: DragEvent) {
  excelDragOver.value = false
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    excelFile.value = event.dataTransfer.files[0]
    excelFileName.value = event.dataTransfer.files[0].name
  }
}

function handleExcelDragOver(event: DragEvent) {
  event.preventDefault()
  excelDragOver.value = true
}

function handleExcelDragLeave() {
  excelDragOver.value = false
}

// Hasılat Excel handlers
function handleHasilatFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    hasilatExcelFile.value = target.files[0]
    hasilatExcelFileName.value = target.files[0].name
  }
}

function handleHasilatDrop(event: DragEvent) {
  hasilatDragOver.value = false
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    hasilatExcelFile.value = event.dataTransfer.files[0]
    hasilatExcelFileName.value = event.dataTransfer.files[0].name
  }
}

function handleHasilatDragOver(event: DragEvent) {
  event.preventDefault()
  hasilatDragOver.value = true
}

function handleHasilatDragLeave() {
  hasilatDragOver.value = false
}

// Load categories
async function loadCategories() {
  loadingCategories.value = true
  try {
    const { data } = await expenseCategoriesApi.getAll()
    categories.value = data
  } catch (e: any) {
    console.error('Failed to load categories:', e)
  } finally {
    loadingCategories.value = false
  }
}

// Get categorization suggestions
async function getCategorizationSuggestions() {
  if (!excelData.value?.expenses || excelData.value.expenses.length === 0) return

  try {
    const response = await categorizationApi.suggestBatch(
      excelData.value.expenses.map(e => ({
        description: e.description,
        amount: e.amount
      }))
    )

    // Merge suggestions into expenses
    response.data.forEach((suggestion: any, index: number) => {
      if (excelData.value!.expenses[index]) {
        excelData.value!.expenses[index].suggested_category = suggestion.suggested_category
        excelData.value!.expenses[index].suggested_category_id = suggestion.category_id
        excelData.value!.expenses[index].category_id = suggestion.category_id
      }
    })
  } catch (error) {
    console.error('Failed to get category suggestions:', error)
  }
}

// Parse Excel
async function parseExcel() {
  if (!excelFile.value) {
    error.value = 'Lutfen bir Excel dosyasi secin'
    return
  }

  parsingExcel.value = true
  error.value = ''

  try {
    const response = await cashDifferenceApi.parseExcel(excelFile.value)
    excelData.value = response.data

    // Load categories if not already loaded
    if (categories.value.length === 0) {
      await loadCategories()
    }

    // Get AI category suggestions for expenses
    if (excelData.value.expenses && excelData.value.expenses.length > 0) {
      await getCategorizationSuggestions()
    }
  } catch (e: any) {
    console.error('Excel parse error:', e)
    error.value = e.response?.data?.detail || 'Excel dosyasi okunamadi'
  } finally {
    parsingExcel.value = false
  }
}

// Parse Hasılat Excel
async function parseHasilatExcel() {
  if (!hasilatExcelFile.value) {
    error.value = 'Lutfen bir Hasılat Excel dosyasi secin'
    return
  }

  parsingPOS.value = true
  error.value = ''

  try {
    const response = await cashDifferenceApi.parseHasilatExcel(hasilatExcelFile.value)
    posData.value = response.data
  } catch (e: any) {
    console.error('Hasılat parse error:', e)
    error.value = e.response?.data?.detail || 'Hasılat Excel okunamadi'
  } finally {
    parsingPOS.value = false
  }
}

// Submit import
async function submitImport() {
  if (!excelData.value || !posData.value) {
    error.value = 'Lutfen hem Excel hem de POS gorselini yukleyin'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const importData = {
      difference_date: excelData.value.date,
      kasa_visa: excelData.value.visa,
      kasa_nakit: excelData.value.nakit,
      kasa_trendyol: excelData.value.trendyol,
      kasa_getir: excelData.value.getir,
      kasa_yemeksepeti: excelData.value.yemeksepeti,
      kasa_migros: excelData.value.migros,
      kasa_total: excelData.value.total,
      pos_visa: posData.value.visa,
      pos_nakit: posData.value.nakit,
      pos_trendyol: posData.value.trendyol,
      pos_getir: posData.value.getir,
      pos_yemeksepeti: posData.value.yemeksepeti,
      pos_migros: posData.value.migros,
      pos_total: posData.value.total,
      ocr_confidence_score: posData.value.confidence_score
    }

    await cashDifferenceApi.import(importData, excelData.value.expenses)

    // Emit success and let parent handle the rest
    emit('success')
  } catch (e: any) {
    console.error('Import error:', e)
    error.value = e.response?.data?.detail || 'Kayit basarisiz'
  } finally {
    loading.value = false
  }
}

</script>

<template>
  <div class="space-y-6">
    <!-- Error -->
    <ErrorAlert :message="error" @dismiss="error = ''" />

    <!-- Upload Section -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Excel Upload -->
      <div class="bg-gray-50 rounded-lg p-4">
        <h2 class="text-base font-semibold text-gray-900 mb-3">1. Excel Kasa Raporu</h2>

        <div
          @drop.prevent="handleExcelDrop"
          @dragover.prevent="handleExcelDragOver"
          @dragleave="handleExcelDragLeave"
          :class="[
            'border-2 border-dashed rounded-lg p-6 text-center transition-colors',
            excelDragOver ? 'border-red-500 bg-red-50' : 'border-gray-300 hover:border-gray-400'
          ]"
        >
          <input
            type="file"
            accept=".xlsx,.xls"
            @change="handleExcelFileSelect"
            class="hidden"
            id="excel-upload"
            data-testid="input-excel-file"
          />

          <label for="excel-upload" class="cursor-pointer">
            <svg class="mx-auto h-10 w-10 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
              <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <p class="mt-2 text-sm text-gray-600">
              <span class="text-red-600 font-medium">Excel dosyasi sec</span> veya surukle birak
            </p>
            <p class="text-xs text-gray-500 mt-1">.xlsx veya .xls</p>
          </label>

          <div v-if="excelFileName" class="mt-3 text-sm text-gray-700">
            Secilen: <strong>{{ excelFileName }}</strong>
          </div>
        </div>

        <button
          @click="parseExcel"
          :disabled="!excelFile || parsingExcel"
          class="w-full mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
          data-testid="btn-parse-excel"
        >
          {{ parsingExcel ? 'Okunuyor...' : 'Excel Oku' }}
        </button>

        <!-- Excel Preview -->
        <div v-if="excelData" class="mt-3 p-3 bg-green-50 rounded-lg border border-green-200">
          <div class="flex items-center gap-2 mb-1">
            <svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <span class="text-xs font-medium text-green-800">Excel basariyla okundu</span>
          </div>
          <div class="text-xs text-gray-600">
            <p>Tarih: <strong>{{ formatDate(excelData.date) }}</strong></p>
            <p>Toplam: <strong>{{ formatCurrency(excelData.total) }}</strong></p>
          </div>
        </div>
      </div>

      <!-- Hasılat Excel Upload -->
      <div class="bg-gray-50 rounded-lg p-4">
        <h2 class="text-base font-semibold text-gray-900 mb-3">2. Şefim Hasılat Raporu (Excel)</h2>

        <div
          @drop.prevent="handleHasilatDrop"
          @dragover.prevent="handleHasilatDragOver"
          @dragleave="handleHasilatDragLeave"
          :class="[
            'border-2 border-dashed rounded-lg p-6 text-center transition-colors',
            hasilatDragOver ? 'border-red-500 bg-red-50' : 'border-gray-300 hover:border-gray-400'
          ]"
        >
          <input
            type="file"
            accept=".xlsx,.xls"
            @change="handleHasilatFileSelect"
            class="hidden"
            id="hasilat-upload"
            data-testid="input-hasilat-file"
          />

          <label for="hasilat-upload" class="cursor-pointer">
            <svg class="mx-auto h-10 w-10 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
              <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <p class="mt-2 text-sm text-gray-600">
              <span class="text-red-600 font-medium">Excel sec</span> veya surukle birak
            </p>
            <p class="text-xs text-gray-500 mt-1">.xlsx veya .xls</p>
          </label>

          <div v-if="hasilatExcelFileName" class="mt-3 text-sm text-gray-700">
            Secilen: <strong>{{ hasilatExcelFileName }}</strong>
          </div>
        </div>

        <button
          @click="parseHasilatExcel"
          :disabled="!hasilatExcelFile || parsingPOS"
          class="w-full mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
          data-testid="btn-parse-hasilat"
        >
          {{ parsingPOS ? 'Okunuyor...' : 'Hasılat Excel Oku' }}
        </button>

        <!-- Hasılat Preview -->
        <div v-if="posData" class="mt-3 p-3 bg-green-50 rounded-lg border border-green-200">
          <div class="flex items-center gap-2 mb-1">
            <svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <span class="text-xs font-medium text-green-800">Hasılat raporu basariyla okundu</span>
          </div>
          <div class="text-xs text-gray-600">
            <p>Tarih: <strong>{{ formatDate(posData.date) }}</strong></p>
            <p>Toplam: <strong>{{ formatCurrency(posData.total) }}</strong></p>
          </div>
        </div>
      </div>
    </div>

    <!-- Comparison Table -->
    <div v-if="excelData && posData" class="border rounded-lg overflow-hidden">
      <div class="px-4 py-3 border-b bg-gray-50">
        <h2 class="text-base font-semibold text-gray-900">Karsilastirma</h2>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full" data-testid="comparison-table">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Kanal</th>
              <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">Kasa</th>
              <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">POS</th>
              <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">Fark</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="row in comparisonData" :key="row.label" class="hover:bg-gray-50">
              <td class="px-3 py-2 text-sm font-medium text-gray-900">{{ row.label }}</td>
              <td class="px-3 py-2 text-right text-sm text-gray-700">{{ formatCurrency(row.kasa) }}</td>
              <td class="px-3 py-2 text-right text-sm text-gray-700">{{ formatCurrency(row.pos) }}</td>
              <td class="px-3 py-2 text-right text-sm font-bold" :class="row.diffClass">
                {{ formatCurrency(row.diff) }}
              </td>
            </tr>
          </tbody>
          <tfoot v-if="totalRow" class="bg-gray-100 font-bold">
            <tr>
              <td class="px-3 py-2 text-sm text-gray-700">TOPLAM</td>
              <td class="px-3 py-2 text-right text-sm text-gray-700">{{ formatCurrency(totalRow.kasa) }}</td>
              <td class="px-3 py-2 text-right text-sm text-gray-700">{{ formatCurrency(totalRow.pos) }}</td>
              <td class="px-3 py-2 text-right text-base" :class="totalRow.diffClass">
                {{ formatCurrency(totalRow.diff) }}
              </td>
            </tr>
          </tfoot>
        </table>
      </div>

      <!-- Expenses Preview -->
      <div v-if="excelData.expenses && excelData.expenses.length > 0" class="px-4 py-3 border-t bg-gray-50">
        <h3 class="text-xs font-semibold text-gray-700 mb-3">Giderler (Excel'den)</h3>
        <div class="space-y-2">
          <div
            v-for="(exp, idx) in excelData.expenses"
            :key="idx"
            class="grid grid-cols-3 gap-2 items-center text-xs"
          >
            <span class="text-gray-600 truncate" :title="exp.description">{{ exp.description }}</span>
            <select
              v-model="exp.category_id"
              class="border rounded px-2 py-1 text-xs"
              data-testid="select-category"
            >
              <option v-if="exp.suggested_category" :value="exp.suggested_category_id">
                {{ exp.suggested_category }} (Onerilen)
              </option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
            <span class="font-medium text-gray-900 text-right">{{ formatCurrency(exp.amount) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex gap-3 pt-2">
      <button
        @click="emit('cancel')"
        class="flex-1 px-4 py-2.5 border rounded-lg text-gray-700 hover:bg-gray-100"
      >
        Iptal
      </button>
      <button
        @click="submitImport"
        :disabled="!canSubmit"
        class="flex-1 px-4 py-2.5 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
        data-testid="btn-submit-import"
      >
        {{ loading ? 'Kaydediliyor...' : 'Kaydet' }}
      </button>
    </div>

    <!-- Loading State -->
    <LoadingState v-if="loading" />
  </div>
</template>
