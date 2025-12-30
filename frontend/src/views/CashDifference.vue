<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import type { CashDifference, CashDifferenceSummary } from '@/types'
import { cashDifferenceApi } from '@/services/api'
import type { DateRangeValue } from '@/types/filters'
import { useFormatters, useConfirmModal } from '@/composables'
import { ConfirmModal, ErrorAlert, LoadingState, UnifiedFilterBar, PageModal, SummaryCard } from '@/components/ui'
import CashDifferenceImport from './CashDifferenceImport.vue'

// Use composables
const { formatCurrency, formatDate } = useFormatters()
const confirmModal = useConfirmModal()

// Data
const records = ref<CashDifference[]>([])
const summary = ref<CashDifferenceSummary | null>(null)
const loading = ref(true)
const error = ref('')

// Detail Modal
const showDetailModal = ref(false)
const selectedRecord = ref<CashDifference | null>(null)
const updatingStatus = ref(false)
const statusForm = ref({
  status: 'pending' as 'pending' | 'reviewed' | 'resolved' | 'flagged',
  resolution_note: ''
})

// Import Modal
const showImportModal = ref(false)

function openImportModal() {
  showImportModal.value = true
}

function closeImportModal() {
  showImportModal.value = false
}

async function handleImportSuccess() {
  showImportModal.value = false
  await loadData()
}

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
    const [recordsRes, summaryRes] = await Promise.all([
      cashDifferenceApi.getAll({ month: filterMonth.value, year: filterYear.value }),
      cashDifferenceApi.getSummary({ month: filterMonth.value, year: filterYear.value })
    ])
    records.value = recordsRes.data
    summary.value = summaryRes.data
  } catch (e: any) {
    console.error('Failed to load cash differences:', e)
    error.value = e.response?.data?.detail || 'Veriler yuklenemedi'
  } finally {
    loading.value = false
  }
}

function openDetailModal(record: CashDifference) {
  selectedRecord.value = record
  statusForm.value = {
    status: record.status,
    resolution_note: record.resolution_note || ''
  }
  showDetailModal.value = true
}

function closeDetailModal() {
  showDetailModal.value = false
  selectedRecord.value = null
}

async function updateStatus() {
  if (!selectedRecord.value) return

  updatingStatus.value = true
  error.value = ''
  try {
    const { data } = await cashDifferenceApi.update(selectedRecord.value.id, statusForm.value)

    // Update the record in the list
    const index = records.value.findIndex(r => r.id === selectedRecord.value!.id)
    if (index !== -1) {
      records.value[index] = data
    }

    closeDetailModal()
    await loadData() // Reload to update summary
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Guncelleme basarisiz'
  } finally {
    updatingStatus.value = false
  }
}

async function deleteRecord(id: number) {
  try {
    // First, get preview of what will be deleted
    const { data: preview } = await cashDifferenceApi.previewDelete(id)

    // Build confirmation message with details
    let message = `Bu kaydı silmek istediğinizden emin misiniz?\n\n`
    message += `Tarih: ${preview.cash_difference.difference_date}\n`
    message += `Kasa Toplam: ₺${preview.cash_difference.kasa_total.toLocaleString('tr-TR')}\n`
    message += `POS Toplam: ₺${preview.cash_difference.pos_total.toLocaleString('tr-TR')}\n`

    // Show what will be deleted
    if (preview.summary.total_expenses > 0 || preview.summary.total_sales > 0) {
      message += `\nSilinecek ilişikili kayıtlar:\n`
      if (preview.summary.total_expenses > 0) {
        message += `• ${preview.summary.total_expenses} gider kaydı\n`
      }
      if (preview.summary.total_sales > 0) {
        message += `• ${preview.summary.total_sales} online satış kaydı\n`
      }
    }

    // Show what will be skipped (modified after import)
    if (preview.summary.skipped_expenses > 0 || preview.summary.skipped_sales > 0) {
      message += `\n⚠️ Değiştirildiği için atlanacak:\n`
      if (preview.summary.skipped_expenses > 0) {
        message += `• ${preview.summary.skipped_expenses} gider (düzenlendi)\n`
      }
      if (preview.summary.skipped_sales > 0) {
        message += `• ${preview.summary.skipped_sales} satış (düzenlendi)\n`
      }
      message += `\nBu kayıtlar import sonrası değiştirildiği için silinmeyecek.`
    }

    message += `\n\n⚠️ Bu işlem geri alınamaz!`

    confirmModal.confirm(message, async () => {
      try {
        const { data: result } = await cashDifferenceApi.delete(id)
        records.value = records.value.filter(r => r.id !== id)
        await loadData() // Reload to update summary

        // Show success message with details
        let successMsg = result.message || 'Kayıt silindi'
        if (result.skipped_expenses > 0 || result.skipped_sales > 0) {
          if (result.skipped_expenses > 0) {
            successMsg += `\n• ${result.skipped_expenses} gider değiştirildiği için atlandı`
          }
          if (result.skipped_sales > 0) {
            successMsg += `\n• ${result.skipped_sales} satış değiştirildiği için atlandı`
          }
        }
        // Show notification or toast here if available
      } catch (e: any) {
        error.value = e.response?.data?.detail || 'Silme başarısız'
      }
    })
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Önizleme yüklenemedi'
  }
}

// Status badge styling
function getStatusBadgeClass(status: string) {
  switch (status) {
    case 'pending':
      return 'bg-yellow-100 text-yellow-800'
    case 'reviewed':
      return 'bg-blue-100 text-blue-800'
    case 'resolved':
      return 'bg-green-100 text-green-800'
    case 'flagged':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

function getStatusLabel(status: string) {
  switch (status) {
    case 'pending':
      return 'Beklemede'
    case 'reviewed':
      return 'Incelendi'
    case 'resolved':
      return 'Cozuldu'
    case 'flagged':
      return 'Isaretlendi'
    default:
      return status
  }
}

// Severity badge styling
function getSeverityBadgeClass(severity: string) {
  switch (severity) {
    case 'ok':
      return 'bg-green-100 text-green-800'
    case 'warning':
      return 'bg-yellow-100 text-yellow-800'
    case 'critical':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

function getSeverityLabel(severity: string) {
  switch (severity) {
    case 'ok':
      return 'OK'
    case 'warning':
      return 'Dikkat'
    case 'critical':
      return 'Kritik'
    default:
      return severity
  }
}

// Computed: Channel-wise comparison for detail view
const channelComparison = computed(() => {
  if (!selectedRecord.value) return []

  const channels = [
    { key: 'visa', label: 'Visa' },
    { key: 'nakit', label: 'Nakit' },
    { key: 'trendyol', label: 'Trendyol' },
    { key: 'getir', label: 'Getir' },
    { key: 'yemeksepeti', label: 'Yemek Sepeti' },
    { key: 'migros', label: 'Migros' }
  ]

  return channels.map(ch => {
    const kasaKey = `kasa_${ch.key}` as keyof CashDifference
    const posKey = `pos_${ch.key}` as keyof CashDifference
    const diffKey = `diff_${ch.key}` as keyof CashDifference

    const kasaVal = Number(selectedRecord.value![kasaKey]) || 0
    const posVal = Number(selectedRecord.value![posKey]) || 0
    const diff = Number(selectedRecord.value![diffKey]) || 0

    return {
      label: ch.label,
      kasa: kasaVal,
      pos: posVal,
      diff,
      diffClass: diff === 0 ? 'text-gray-600' : diff > 0 ? 'text-green-600' : 'text-red-600'
    }
  })
})
</script>

<template>
  <div class="space-y-6">
    <!-- Unified Filter Bar -->
    <UnifiedFilterBar
      v-model:date-range="dateRangeFilter"
      :primary-action="{ label: 'Veri Yükle', onClick: openImportModal }"
    />

    <!-- Error -->
    <ErrorAlert :message="error" @dismiss="error = ''" />

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
      <SummaryCard
        label="Toplam Kayit"
        :value="summary?.total_records?.toString() || '0'"
        data-testid="total-records-card"
      />
      <SummaryCard
        label="Beklemede"
        :value="summary?.pending_count?.toString() || '0'"
        variant="warning"
      />
      <SummaryCard
        label="Cozuldu"
        :value="summary?.resolved_count?.toString() || '0'"
        variant="success"
      />
      <SummaryCard
        label="Kritik"
        :value="summary?.critical_count?.toString() || '0'"
        variant="danger"
      />
      <SummaryCard
        label="Toplam Fark"
        :value="formatCurrency(summary?.total_diff || 0)"
        :variant="(summary?.total_diff || 0) === 0 ? 'default' : (summary?.total_diff || 0) > 0 ? 'success' : 'danger'"
      />
    </div>

    <!-- Records Table -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <LoadingState v-if="loading" />

      <div v-else-if="records.length === 0" class="p-8 text-center text-gray-500">
        Bu donemde kayit bulunamadi
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full" data-testid="records-table">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tarih</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Kasa Total</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">POS Total</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Fark</th>
              <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Durum</th>
              <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Oncelik</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Islem</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr
              v-for="record in records"
              :key="record.id"
              class="hover:bg-gray-50 cursor-pointer"
              @click="openDetailModal(record)"
              data-testid="record-row"
            >
              <td class="px-4 py-3 text-sm text-gray-900">
                {{ formatDate(record.difference_date) }}
              </td>
              <td class="px-4 py-3 text-right text-sm text-gray-700">
                {{ formatCurrency(record.kasa_total) }}
              </td>
              <td class="px-4 py-3 text-right text-sm text-gray-700">
                {{ formatCurrency(record.pos_total) }}
              </td>
              <td
                class="px-4 py-3 text-right text-sm font-bold"
                :class="record.diff_total === 0 ? 'text-gray-600' : record.diff_total > 0 ? 'text-green-600' : 'text-red-600'"
              >
                {{ formatCurrency(record.diff_total) }}
              </td>
              <td class="px-4 py-3 text-center">
                <span
                  :class="[
                    'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                    getStatusBadgeClass(record.status)
                  ]"
                >
                  {{ getStatusLabel(record.status) }}
                </span>
              </td>
              <td class="px-4 py-3 text-center">
                <span
                  :class="[
                    'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                    getSeverityBadgeClass(record.severity)
                  ]"
                >
                  {{ getSeverityLabel(record.severity) }}
                </span>
              </td>
              <td class="px-4 py-3 text-right">
                <button
                  @click.stop="deleteRecord(record.id)"
                  class="text-red-500 hover:text-red-700 text-sm"
                  data-testid="btn-delete"
                >
                  Sil
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Detail Modal -->
    <PageModal
      :show="showDetailModal"
      title="Kasa Farki Detayi"
      size="lg"
      @close="closeDetailModal"
    >
      <div v-if="selectedRecord" class="p-6 space-y-6">
        <!-- Header Info -->
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-lg font-semibold text-gray-900">
              {{ formatDate(selectedRecord.difference_date) }}
            </h3>
            <p class="text-sm text-gray-500 mt-1">
              Kayit ID: #{{ selectedRecord.id }}
            </p>
          </div>
          <div class="flex gap-2">
            <span
              :class="[
                'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium',
                getStatusBadgeClass(selectedRecord.status)
              ]"
            >
              {{ getStatusLabel(selectedRecord.status) }}
            </span>
            <span
              :class="[
                'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium',
                getSeverityBadgeClass(selectedRecord.severity)
              ]"
            >
              {{ getSeverityLabel(selectedRecord.severity) }}
            </span>
          </div>
        </div>

        <!-- Channel-wise Comparison Table -->
        <div class="border rounded-lg overflow-hidden">
          <table class="w-full">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Kanal</th>
                <th class="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Kasa</th>
                <th class="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">POS</th>
                <th class="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Fark</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr v-for="row in channelComparison" :key="row.label" class="hover:bg-gray-50">
                <td class="px-4 py-2 text-sm font-medium text-gray-900">{{ row.label }}</td>
                <td class="px-4 py-2 text-right text-sm text-gray-700">{{ formatCurrency(row.kasa) }}</td>
                <td class="px-4 py-2 text-right text-sm text-gray-700">{{ formatCurrency(row.pos) }}</td>
                <td class="px-4 py-2 text-right text-sm font-bold" :class="row.diffClass">
                  {{ formatCurrency(row.diff) }}
                </td>
              </tr>
            </tbody>
            <tfoot class="bg-gray-100 font-bold">
              <tr>
                <td class="px-4 py-2 text-sm text-gray-700">TOPLAM</td>
                <td class="px-4 py-2 text-right text-sm text-gray-700">{{ formatCurrency(selectedRecord.kasa_total) }}</td>
                <td class="px-4 py-2 text-right text-sm text-gray-700">{{ formatCurrency(selectedRecord.pos_total) }}</td>
                <td
                  class="px-4 py-2 text-right text-lg"
                  :class="selectedRecord.diff_total === 0 ? 'text-gray-600' : selectedRecord.diff_total > 0 ? 'text-green-600' : 'text-red-600'"
                >
                  {{ formatCurrency(selectedRecord.diff_total) }}
                </td>
              </tr>
            </tfoot>
          </table>
        </div>

        <!-- OCR Confidence -->
        <div v-if="selectedRecord.ocr_confidence_score" class="text-sm text-gray-600">
          OCR Guven Skoru: <strong>{{ (selectedRecord.ocr_confidence_score * 100).toFixed(1) }}%</strong>
        </div>

        <!-- Status Update Form -->
        <div class="border-t pt-4">
          <h4 class="text-sm font-semibold text-gray-900 mb-3">Durum Guncelle</h4>

          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Durum</label>
              <select
                v-model="statusForm.status"
                class="w-full border rounded-lg px-3 py-2"
                data-testid="select-status"
              >
                <option value="pending">Beklemede</option>
                <option value="reviewed">Incelendi</option>
                <option value="resolved">Cozuldu</option>
                <option value="flagged">Isaretlendi</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Not (Opsiyonel)</label>
              <textarea
                v-model="statusForm.resolution_note"
                rows="3"
                class="w-full border rounded-lg px-3 py-2"
                placeholder="Aciklama veya cozum notlari..."
                data-testid="textarea-note"
              ></textarea>
            </div>

            <!-- Current Note (if exists) -->
            <div v-if="selectedRecord.resolution_note" class="p-3 bg-gray-50 rounded-lg">
              <p class="text-xs text-gray-500 mb-1">Mevcut Not:</p>
              <p class="text-sm text-gray-700">{{ selectedRecord.resolution_note }}</p>
            </div>

            <div class="flex gap-3 pt-2">
              <button
                @click="closeDetailModal"
                class="flex-1 py-2 border rounded-lg text-gray-700 hover:bg-gray-100"
              >
                Iptal
              </button>
              <button
                @click="updateStatus"
                :disabled="updatingStatus"
                class="flex-1 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                data-testid="btn-update-status"
              >
                {{ updatingStatus ? 'Guncelleniyor...' : 'Guncelle' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </PageModal>

    <ConfirmModal
      :show="confirmModal.isOpen.value"
      :message="confirmModal.message.value"
      @confirm="confirmModal.handleConfirm"
      @cancel="confirmModal.handleCancel"
    />

    <!-- Import Modal -->
    <PageModal
      :show="showImportModal"
      title="Kasa Farki - Veri Yukleme"
      size="xl"
      @close="closeImportModal"
    >
      <div class="p-6">
        <CashDifferenceImport
          @success="handleImportSuccess"
          @cancel="closeImportModal"
        />
      </div>
    </PageModal>
  </div>
</template>
