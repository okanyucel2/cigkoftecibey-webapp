<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ExcelParseResult, POSParseResult } from '@/types'
import { cashDifferenceApi } from '@/services/api'
import { useFormatters } from '@/composables'
import { ErrorAlert, LoadingState } from '@/components/ui'

// Use composables
const { formatCurrency, formatDate } = useFormatters()

// State
const loading = ref(false)
const error = ref('')
const successMessage = ref('')

// File uploads
const excelFile = ref<File | null>(null)
const posImageFile = ref<File | null>(null)
const excelFileName = ref('')
const posImageFileName = ref('')

// Drag and drop states
const excelDragOver = ref(false)
const posDragOver = ref(false)

// Parsed data
const excelData = ref<ExcelParseResult | null>(null)
const posData = ref<POSParseResult | null>(null)
const parsingExcel = ref(false)
const parsingPOS = ref(false)

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

// POS image handlers
function handlePOSFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    posImageFile.value = target.files[0]
    posImageFileName.value = target.files[0].name
  }
}

function handlePOSDrop(event: DragEvent) {
  posDragOver.value = false
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    posImageFile.value = event.dataTransfer.files[0]
    posImageFileName.value = event.dataTransfer.files[0].name
  }
}

function handlePOSDragOver(event: DragEvent) {
  event.preventDefault()
  posDragOver.value = true
}

function handlePOSDragLeave() {
  posDragOver.value = false
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
  } catch (e: any) {
    console.error('Excel parse error:', e)
    error.value = e.response?.data?.detail || 'Excel dosyasi okunamadi'
  } finally {
    parsingExcel.value = false
  }
}

// Parse POS Image
async function parsePOSImage() {
  if (!posImageFile.value) {
    error.value = 'Lutfen bir POS gorsel dosyasi secin'
    return
  }

  parsingPOS.value = true
  error.value = ''

  try {
    const response = await cashDifferenceApi.parsePOSImage(posImageFile.value)
    posData.value = response.data
  } catch (e: any) {
    console.error('POS parse error:', e)
    error.value = e.response?.data?.detail || 'POS gorseli okunamadi'
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
  successMessage.value = ''

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

    // Success! Reset form
    successMessage.value = 'Kasa farki basariyla kaydedildi!'
    excelFile.value = null
    posImageFile.value = null
    excelFileName.value = ''
    posImageFileName.value = ''
    excelData.value = null
    posData.value = null

    // Clear success message after 5 seconds
    setTimeout(() => {
      successMessage.value = ''
    }, 5000)
  } catch (e: any) {
    console.error('Import error:', e)
    error.value = e.response?.data?.detail || 'Kayit basarisiz'
  } finally {
    loading.value = false
  }
}

// Reset form
function resetForm() {
  excelFile.value = null
  posImageFile.value = null
  excelFileName.value = ''
  posImageFileName.value = ''
  excelData.value = null
  posData.value = null
  error.value = ''
  successMessage.value = ''
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between flex-wrap gap-4">
      <div>
        <h1 data-testid="heading-cash-difference-import" class="text-2xl font-display font-bold text-gray-900">
          Kasa Farki - Veri Yukleme
        </h1>
        <p class="text-sm text-gray-500 mt-1">Excel kasa raporu ve POS gorselini yukleyerek kasa farkini kaydedin</p>
      </div>
      <button
        v-if="excelData || posData"
        @click="resetForm"
        class="px-4 py-2 text-gray-700 border rounded-lg hover:bg-gray-100"
        data-testid="btn-reset"
      >
        Sifirla
      </button>
    </div>

    <!-- Error -->
    <ErrorAlert :message="error" @dismiss="error = ''" />

    <!-- Success Message -->
    <div
      v-if="successMessage"
      class="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-3"
      data-testid="success-message"
    >
      <svg class="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
      </svg>
      <span class="text-green-800 font-medium">{{ successMessage }}</span>
    </div>

    <!-- Upload Section -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Excel Upload -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">1. Excel Kasa Raporu</h2>

        <div
          @drop.prevent="handleExcelDrop"
          @dragover.prevent="handleExcelDragOver"
          @dragleave="handleExcelDragLeave"
          :class="[
            'border-2 border-dashed rounded-lg p-8 text-center transition-colors',
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
            <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
              <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <p class="mt-2 text-sm text-gray-600">
              <span class="text-red-600 font-medium">Excel dosyasi sec</span> veya surukle birak
            </p>
            <p class="text-xs text-gray-500 mt-1">.xlsx veya .xls</p>
          </label>

          <div v-if="excelFileName" class="mt-4 text-sm text-gray-700">
            Secilen: <strong>{{ excelFileName }}</strong>
          </div>
        </div>

        <button
          @click="parseExcel"
          :disabled="!excelFile || parsingExcel"
          class="w-full mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
          data-testid="btn-parse-excel"
        >
          {{ parsingExcel ? 'Okunuyor...' : 'Excel Oku' }}
        </button>

        <!-- Excel Preview -->
        <div v-if="excelData" class="mt-4 p-4 bg-green-50 rounded-lg border border-green-200">
          <div class="flex items-center gap-2 mb-2">
            <svg class="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <span class="text-sm font-medium text-green-800">Excel basariyla okundu</span>
          </div>
          <div class="text-xs text-gray-600">
            <p>Tarih: <strong>{{ formatDate(excelData.date) }}</strong></p>
            <p>Toplam: <strong>{{ formatCurrency(excelData.total) }}</strong></p>
            <p v-if="excelData.expenses && excelData.expenses.length > 0">
              Giderler: <strong>{{ excelData.expenses.length }} adet</strong>
            </p>
          </div>
        </div>
      </div>

      <!-- POS Image Upload -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">2. POS Hasilat Gorseli</h2>

        <div
          @drop.prevent="handlePOSDrop"
          @dragover.prevent="handlePOSDragOver"
          @dragleave="handlePOSDragLeave"
          :class="[
            'border-2 border-dashed rounded-lg p-8 text-center transition-colors',
            posDragOver ? 'border-red-500 bg-red-50' : 'border-gray-300 hover:border-gray-400'
          ]"
        >
          <input
            type="file"
            accept="image/*"
            @change="handlePOSFileSelect"
            class="hidden"
            id="pos-upload"
            data-testid="input-pos-file"
          />

          <label for="pos-upload" class="cursor-pointer">
            <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
              <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <p class="mt-2 text-sm text-gray-600">
              <span class="text-red-600 font-medium">Gorsel sec</span> veya surukle birak
            </p>
            <p class="text-xs text-gray-500 mt-1">PNG, JPG, JPEG</p>
          </label>

          <div v-if="posImageFileName" class="mt-4 text-sm text-gray-700">
            Secilen: <strong>{{ posImageFileName }}</strong>
          </div>
        </div>

        <button
          @click="parsePOSImage"
          :disabled="!posImageFile || parsingPOS"
          class="w-full mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
          data-testid="btn-parse-pos"
        >
          {{ parsingPOS ? 'Okunuyor...' : 'POS Oku (OCR)' }}
        </button>

        <!-- POS Preview -->
        <div v-if="posData" class="mt-4 p-4 bg-green-50 rounded-lg border border-green-200">
          <div class="flex items-center gap-2 mb-2">
            <svg class="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <span class="text-sm font-medium text-green-800">POS basariyla okundu</span>
          </div>
          <div class="text-xs text-gray-600">
            <p>Tarih: <strong>{{ formatDate(posData.date) }}</strong></p>
            <p>Toplam: <strong>{{ formatCurrency(posData.total) }}</strong></p>
            <p>Guven: <strong>{{ (posData.confidence_score * 100).toFixed(1) }}%</strong></p>
          </div>
        </div>
      </div>
    </div>

    <!-- Comparison Table -->
    <div v-if="excelData && posData" class="bg-white rounded-lg shadow overflow-hidden">
      <div class="px-6 py-4 border-b">
        <h2 class="text-lg font-semibold text-gray-900">Karsilastirma Onizleme</h2>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full" data-testid="comparison-table">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Kanal</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Kasa</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">POS</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Fark</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="row in comparisonData" :key="row.label" class="hover:bg-gray-50">
              <td class="px-4 py-3 text-sm font-medium text-gray-900">{{ row.label }}</td>
              <td class="px-4 py-3 text-right text-sm text-gray-700">{{ formatCurrency(row.kasa) }}</td>
              <td class="px-4 py-3 text-right text-sm text-gray-700">{{ formatCurrency(row.pos) }}</td>
              <td class="px-4 py-3 text-right text-sm font-bold" :class="row.diffClass">
                {{ formatCurrency(row.diff) }}
              </td>
            </tr>
          </tbody>
          <tfoot v-if="totalRow" class="bg-gray-100 font-bold">
            <tr>
              <td class="px-4 py-3 text-sm text-gray-700">TOPLAM</td>
              <td class="px-4 py-3 text-right text-sm text-gray-700">{{ formatCurrency(totalRow.kasa) }}</td>
              <td class="px-4 py-3 text-right text-sm text-gray-700">{{ formatCurrency(totalRow.pos) }}</td>
              <td class="px-4 py-3 text-right text-lg" :class="totalRow.diffClass">
                {{ formatCurrency(totalRow.diff) }}
              </td>
            </tr>
          </tfoot>
        </table>
      </div>

      <!-- Expenses Preview -->
      <div v-if="excelData.expenses && excelData.expenses.length > 0" class="px-6 py-4 border-t bg-gray-50">
        <h3 class="text-sm font-semibold text-gray-700 mb-2">Giderler (Excel'den)</h3>
        <div class="space-y-1">
          <div
            v-for="(exp, idx) in excelData.expenses"
            :key="idx"
            class="flex justify-between text-sm"
          >
            <span class="text-gray-600">{{ exp.description }}</span>
            <span class="font-medium text-gray-900">{{ formatCurrency(exp.amount) }}</span>
          </div>
        </div>
      </div>

      <!-- Submit Button -->
      <div class="px-6 py-4 border-t bg-gray-50">
        <button
          @click="submitImport"
          :disabled="!canSubmit"
          class="w-full px-6 py-3 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
          data-testid="btn-submit-import"
        >
          {{ loading ? 'Kaydediliyor...' : 'Kasa Farkini Kaydet' }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <LoadingState v-if="loading" />
  </div>
</template>
