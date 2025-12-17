<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import type { ChannelsGrouped, OnlineSale, OnlineSalesSummary } from '@/types'
import { unifiedSalesApi, onlineSalesApi } from '@/services/api'

// Channel data
const channels = ref<ChannelsGrouped>({ pos: [], online: [] })
const sales = ref<OnlineSale[]>([])
const summary = ref<OnlineSalesSummary | null>(null)
const loading = ref(true)
const error = ref('')

// Filtreler
const currentDate = new Date()
const selectedMonth = ref(currentDate.getMonth() + 1)
const selectedYear = ref(currentDate.getFullYear())

// Modal State
const showModal = ref(false)
const showPlatformModal = ref(false)
const showPlatformForm = ref(false)
const editingPlatformId = ref<number | null>(null)
const submitting = ref(false)

// Form - channel_id -> amount
const saleForm = ref({
  sale_date: new Date().toISOString().split('T')[0],
  entries: {} as Record<number, number>,
  notes: ''
})

const platformForm = ref({
  name: '',
  display_order: 0
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

// All channels combined for table display
const allChannels = computed(() => [...channels.value.pos, ...channels.value.online])

onMounted(async () => {
  await loadChannels()
  await loadData()
})

watch([selectedMonth, selectedYear], () => {
  loadData()
})

async function loadChannels() {
  try {
    const { data } = await unifiedSalesApi.getChannels()
    channels.value = data
  } catch (e) {
    console.error('Failed to load channels:', e)
  }
}

async function loadData() {
  loading.value = true
  try {
    const startDate = new Date(selectedYear.value, selectedMonth.value - 1, 1)
    const endDate = new Date(selectedYear.value, selectedMonth.value, 0)

    const [salesRes, summaryRes] = await Promise.all([
      onlineSalesApi.getSales({
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0]
      }),
      onlineSalesApi.getSummary({
        year: selectedYear.value,
        month: selectedMonth.value
      })
    ])

    sales.value = salesRes.data
    summary.value = summaryRes.data
  } catch (e) {
    console.error('Failed to load data:', e)
  } finally {
    loading.value = false
  }
}

// Group sales by date
const salesByDate = computed(() => {
  const grouped: Record<string, Record<number, OnlineSale>> = {}

  for (const sale of sales.value) {
    if (!grouped[sale.sale_date]) {
      grouped[sale.sale_date] = {}
    }
    grouped[sale.sale_date][sale.platform_id] = sale
  }

  return Object.entries(grouped)
    .sort((a, b) => b[0].localeCompare(a[0]))
    .map(([date, channelSales]) => ({
      date,
      sales: channelSales,
      total: Object.values(channelSales).reduce((sum, s) => sum + Number(s.amount), 0)
    }))
})

// Totals
const totalAmount = computed(() => summary.value?.total_amount || 0)

function getChannelTotal(channelName: string): number {
  return Number(summary.value?.platform_totals?.[channelName] || 0)
}

// POS totals (Salon + Telefon)
const posTotals = computed(() => {
  let total = 0
  for (const ch of channels.value.pos) {
    total += getChannelTotal(ch.name)
  }
  return total
})

// Online totals
const onlineTotals = computed(() => {
  let total = 0
  for (const ch of channels.value.online) {
    total += getChannelTotal(ch.name)
  }
  return total
})

function openAddModal() {
  saleForm.value = {
    sale_date: new Date().toISOString().split('T')[0],
    entries: {},
    notes: ''
  }
  // Initialize all channels to 0
  allChannels.value.forEach(ch => {
    saleForm.value.entries[ch.id] = 0
  })
  showModal.value = true
}

async function openEditModal(dateStr: string) {
  saleForm.value = {
    sale_date: dateStr,
    entries: {},
    notes: ''
  }

  // Initialize all to 0
  allChannels.value.forEach(ch => {
    saleForm.value.entries[ch.id] = 0
  })

  // Load existing values
  const dayData = salesByDate.value.find(d => d.date === dateStr)
  if (dayData) {
    for (const [channelId, sale] of Object.entries(dayData.sales)) {
      saleForm.value.entries[Number(channelId)] = Number(sale.amount)
      if (sale.notes) saleForm.value.notes = sale.notes
    }
  }

  showModal.value = true
}

// Computed totals for form
const formPosTotal = computed(() => {
  let total = 0
  for (const ch of channels.value.pos) {
    total += saleForm.value.entries[ch.id] || 0
  }
  return total
})

const formOnlineTotal = computed(() => {
  let total = 0
  for (const ch of channels.value.online) {
    total += saleForm.value.entries[ch.id] || 0
  }
  return total
})

const formGrandTotal = computed(() => formPosTotal.value + formOnlineTotal.value)

async function submitSaleForm() {
  submitting.value = true
  error.value = ''

  try {
    const entries = Object.entries(saleForm.value.entries)
      .filter(([_, amount]) => amount > 0)
      .map(([channelId, amount]) => ({
        platform_id: Number(channelId),
        amount: Number(amount)
      }))

    if (entries.length === 0) {
      error.value = 'En az bir kanal icin tutar girin'
      submitting.value = false
      return
    }

    await unifiedSalesApi.saveDailySales({
      sale_date: saleForm.value.sale_date,
      entries,
      notes: saleForm.value.notes || undefined
    })

    showModal.value = false
    await loadData()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Kayit basarisiz'
  } finally {
    submitting.value = false
  }
}

async function deleteDay(dateStr: string) {
  if (!confirm(`${formatDate(dateStr)} tarihindeki tum satislari silmek istediginize emin misiniz?`)) return

  try {
    await onlineSalesApi.deleteDailySales(dateStr)
    await loadData()
  } catch (e) {
    console.error('Failed to delete:', e)
    alert('Silme basarisiz!')
  }
}

// Platform management (only for online channels)
function openPlatformForm(platform?: any) {
  if (platform) {
    editingPlatformId.value = platform.id
    platformForm.value = {
      name: platform.name,
      display_order: platform.display_order
    }
  } else {
    editingPlatformId.value = null
    platformForm.value = {
      name: '',
      display_order: channels.value.online.length + 10
    }
  }
  showPlatformForm.value = true
}

async function submitPlatformForm() {
  if (!platformForm.value.name.trim()) {
    error.value = 'Platform adi zorunlu'
    return
  }

  submitting.value = true
  error.value = ''
  try {
    if (editingPlatformId.value) {
      await onlineSalesApi.updatePlatform(editingPlatformId.value, platformForm.value)
    } else {
      await onlineSalesApi.createPlatform(platformForm.value)
    }
    showPlatformForm.value = false
    await loadChannels()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Kayit basarisiz'
  } finally {
    submitting.value = false
  }
}

async function deletePlatform(id: number) {
  if (!confirm('Bu platformu silmek istediginize emin misiniz?')) return

  error.value = ''
  try {
    await onlineSalesApi.deletePlatform(id)
    await loadChannels()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Silme basarisiz'
  }
}

// Format helpers
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

// Channel colors
function getChannelColor(channel: any): string {
  if (channel.channel_type === 'pos_salon') return 'bg-blue-500'
  if (channel.channel_type === 'pos_telefon') return 'bg-orange-500'
  // Online platforms
  const colors = ['bg-green-500', 'bg-red-500', 'bg-purple-500', 'bg-pink-500', 'bg-indigo-500']
  const index = channels.value.online.findIndex(c => c.id === channel.id)
  return colors[index % colors.length]
}

function getChannelTextColor(channel: any): string {
  if (channel.channel_type === 'pos_salon') return 'text-blue-600'
  if (channel.channel_type === 'pos_telefon') return 'text-orange-600'
  const colors = ['text-green-600', 'text-red-600', 'text-purple-600', 'text-pink-600', 'text-indigo-600']
  const index = channels.value.online.findIndex(c => c.id === channel.id)
  return colors[index % colors.length]
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between flex-wrap gap-4">
      <h1 class="text-2xl font-display font-bold text-gray-900">Gunluk Satis Girisi</h1>
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
        <!-- Platform Ayarlari -->
        <button
          @click="showPlatformModal = true"
          class="flex items-center gap-1 px-3 py-1.5 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg"
          title="Online Platformlari Yonet"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd" />
          </svg>
          <span class="text-sm">Platformlar</span>
        </button>
      </div>
      <button @click="openAddModal" class="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700">
        + Satis Ekle
      </button>
    </div>

    <!-- Ozet Kartlari -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <!-- POS Channels -->
      <div
        v-for="channel in channels.pos"
        :key="channel.id"
        class="bg-white rounded-lg shadow p-4"
      >
        <div class="flex items-center gap-2 mb-2">
          <div :class="['w-3 h-3 rounded-full', getChannelColor(channel)]"></div>
          <p class="text-sm text-gray-500">{{ channel.name }}</p>
        </div>
        <p :class="['text-xl font-bold', getChannelTextColor(channel)]">
          {{ formatCurrency(getChannelTotal(channel.name)) }}
        </p>
      </div>

      <!-- Online Channels -->
      <div
        v-for="channel in channels.online"
        :key="channel.id"
        class="bg-white rounded-lg shadow p-4"
      >
        <div class="flex items-center gap-2 mb-2">
          <div :class="['w-3 h-3 rounded-full', getChannelColor(channel)]"></div>
          <p class="text-sm text-gray-500 truncate">{{ channel.name }}</p>
        </div>
        <p :class="['text-xl font-bold', getChannelTextColor(channel)]">
          {{ formatCurrency(getChannelTotal(channel.name)) }}
        </p>
      </div>
    </div>

    <!-- Toplam Kartlar -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <!-- POS Toplam -->
      <div class="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg shadow p-4 text-white">
        <p class="text-blue-100 text-sm">POS Toplam</p>
        <p class="text-2xl font-bold">{{ formatCurrency(posTotals) }}</p>
        <p class="text-blue-100 text-xs mt-1">Salon + Telefon</p>
      </div>

      <!-- Online Toplam -->
      <div class="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg shadow p-4 text-white">
        <p class="text-purple-100 text-sm">Online Toplam</p>
        <p class="text-2xl font-bold">{{ formatCurrency(onlineTotals) }}</p>
        <p class="text-purple-100 text-xs mt-1">{{ channels.online.length }} platform</p>
      </div>

      <!-- Genel Toplam -->
      <div class="bg-gradient-to-r from-green-500 to-green-600 rounded-lg shadow p-4 text-white">
        <p class="text-green-100 text-sm">Genel Toplam</p>
        <p class="text-2xl font-bold">{{ formatCurrency(Number(totalAmount)) }}</p>
        <p class="text-green-100 text-xs mt-1">{{ summary?.days_count || 0 }} gun</p>
      </div>
    </div>

    <!-- Tablo -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-gray-500">
        Yukleniyor...
      </div>

      <div v-else-if="salesByDate.length === 0" class="p-8 text-center text-gray-500">
        Bu donemde kayit bulunamadi
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Tarih
              </th>
              <th
                v-for="channel in allChannels"
                :key="channel.id"
                class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase"
              >
                <div class="flex items-center justify-end gap-1">
                  <div :class="['w-2 h-2 rounded-full', getChannelColor(channel)]"></div>
                  {{ channel.name }}
                </div>
              </th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                Toplam
              </th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase w-24">
                Islem
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="day in salesByDate" :key="day.date" class="hover:bg-gray-50">
              <td class="px-4 py-3 text-sm font-medium text-gray-900 whitespace-nowrap">
                {{ formatDate(day.date) }}
              </td>
              <td
                v-for="channel in allChannels"
                :key="channel.id"
                class="px-4 py-3 text-right text-sm"
              >
                <span v-if="day.sales[channel.id]" class="font-medium text-gray-900">
                  {{ formatCurrency(Number(day.sales[channel.id].amount)) }}
                </span>
                <span v-else class="text-gray-300">-</span>
              </td>
              <td class="px-4 py-3 text-right font-bold text-gray-900">
                {{ formatCurrency(day.total) }}
              </td>
              <td class="px-4 py-3 text-right">
                <div class="flex justify-end gap-2">
                  <button
                    @click="openEditModal(day.date)"
                    class="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    Duzenle
                  </button>
                  <button
                    @click="deleteDay(day.date)"
                    class="text-red-500 hover:text-red-700 text-sm"
                  >
                    Sil
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
          <!-- Footer Totals -->
          <tfoot class="bg-gray-100 font-bold">
            <tr>
              <td class="px-4 py-3 text-sm text-gray-700">TOPLAM</td>
              <td
                v-for="channel in allChannels"
                :key="channel.id"
                class="px-4 py-3 text-right text-sm text-gray-900"
              >
                {{ formatCurrency(getChannelTotal(channel.name)) }}
              </td>
              <td class="px-4 py-3 text-right text-green-600">
                {{ formatCurrency(Number(totalAmount)) }}
              </td>
              <td></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>

    <!-- ==================== SATIS EKLEME/DUZENLEME MODAL ==================== -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-4 border-b flex justify-between items-center sticky top-0 bg-white">
          <h2 class="text-lg font-semibold">Gunluk Satis Girisi</h2>
          <button @click="showModal = false" class="text-gray-500 hover:text-gray-700 text-2xl">&times;</button>
        </div>

        <form @submit.prevent="submitSaleForm" class="p-4 space-y-4">
          <!-- Tarih -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Tarih *</label>
            <input
              v-model="saleForm.sale_date"
              type="date"
              class="w-full border rounded-lg px-3 py-2"
              required
            />
          </div>

          <!-- POS Satislari -->
          <div class="space-y-3">
            <label class="block text-sm font-medium text-gray-700 border-b pb-2">POS Satislari</label>
            <div
              v-for="channel in channels.pos"
              :key="channel.id"
              class="flex items-center gap-3"
            >
              <div class="flex items-center gap-2 w-36">
                <div :class="['w-3 h-3 rounded-full', getChannelColor(channel)]"></div>
                <span class="text-sm font-medium">{{ channel.name }}</span>
              </div>
              <div class="flex-1 relative">
                <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">TL</span>
                <input
                  v-model.number="saleForm.entries[channel.id]"
                  type="number"
                  step="0.01"
                  min="0"
                  class="w-full border rounded-lg pl-10 pr-3 py-2"
                  placeholder="0"
                />
              </div>
            </div>
            <div class="flex justify-end text-sm text-gray-500">
              POS Toplam: <span class="font-bold text-blue-600 ml-2">{{ formatCurrency(formPosTotal) }}</span>
            </div>
          </div>

          <!-- Online Platformlar -->
          <div class="space-y-3">
            <label class="block text-sm font-medium text-gray-700 border-b pb-2">Online Platformlar</label>
            <div
              v-for="channel in channels.online"
              :key="channel.id"
              class="flex items-center gap-3"
            >
              <div class="flex items-center gap-2 w-36">
                <div :class="['w-3 h-3 rounded-full', getChannelColor(channel)]"></div>
                <span class="text-sm font-medium truncate">{{ channel.name }}</span>
              </div>
              <div class="flex-1 relative">
                <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">TL</span>
                <input
                  v-model.number="saleForm.entries[channel.id]"
                  type="number"
                  step="0.01"
                  min="0"
                  class="w-full border rounded-lg pl-10 pr-3 py-2"
                  placeholder="0"
                />
              </div>
            </div>
            <div class="flex justify-end text-sm text-gray-500">
              Online Toplam: <span class="font-bold text-purple-600 ml-2">{{ formatCurrency(formOnlineTotal) }}</span>
            </div>
          </div>

          <!-- Genel Toplam -->
          <div class="bg-gray-50 rounded-lg p-3">
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium text-gray-600">Genel Toplam</span>
              <span class="text-lg font-bold text-green-600">
                {{ formatCurrency(formGrandTotal) }}
              </span>
            </div>
          </div>

          <!-- Not -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Not (opsiyonel)</label>
            <input
              v-model="saleForm.notes"
              type="text"
              class="w-full border rounded-lg px-3 py-2"
              placeholder="Aciklama..."
            />
          </div>

          <!-- Butonlar -->
          <div class="flex gap-3 pt-2">
            <button
              type="button"
              @click="showModal = false"
              class="flex-1 py-2 border rounded-lg text-gray-700 hover:bg-gray-100"
            >
              Iptal
            </button>
            <button
              type="submit"
              :disabled="submitting"
              class="flex-1 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
            >
              {{ submitting ? 'Kaydediliyor...' : 'Kaydet' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ==================== PLATFORM YONETIM MODAL ==================== -->
    <div v-if="showPlatformModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-4 border-b flex justify-between items-center sticky top-0 bg-white">
          <h2 class="text-lg font-semibold">Satis Kanallari</h2>
          <button @click="showPlatformModal = false" class="text-gray-500 hover:text-gray-700 text-2xl">&times;</button>
        </div>

        <div class="p-4">
          <!-- Platform Listesi -->
          <div v-if="!showPlatformForm" class="space-y-4">
            <!-- Sistem Kanallari (Silinemez) -->
            <div>
              <h3 class="text-sm font-medium text-gray-500 mb-2">Sistem Kanallari</h3>
              <div
                v-for="channel in channels.pos"
                :key="channel.id"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-lg mb-2"
              >
                <div class="flex items-center gap-2">
                  <div :class="['w-3 h-3 rounded-full', getChannelColor(channel)]"></div>
                  <span class="font-medium">{{ channel.name }}</span>
                  <span class="text-xs bg-gray-200 text-gray-600 px-2 py-0.5 rounded">Sistem</span>
                </div>
              </div>
            </div>

            <!-- Online Platformlar -->
            <div>
              <h3 class="text-sm font-medium text-gray-500 mb-2">Online Platformlar</h3>
              <div
                v-for="channel in channels.online"
                :key="channel.id"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-lg mb-2"
              >
                <div class="flex items-center gap-2">
                  <div :class="['w-3 h-3 rounded-full', getChannelColor(channel)]"></div>
                  <span class="font-medium">{{ channel.name }}</span>
                </div>
                <div class="flex gap-2">
                  <button @click="openPlatformForm(channel)" class="text-blue-600 hover:text-blue-800 text-sm">Duzenle</button>
                  <button @click="deletePlatform(channel.id)" class="text-red-600 hover:text-red-800 text-sm">Sil</button>
                </div>
              </div>

              <div v-if="channels.online.length === 0" class="text-center py-4 text-gray-500 text-sm">
                Henuz online platform yok
              </div>

              <button
                @click="openPlatformForm()"
                class="w-full mt-4 py-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-gray-400 hover:text-gray-700"
              >
                + Yeni Platform Ekle
              </button>
            </div>
          </div>

          <!-- Platform Formu -->
          <div v-else class="space-y-4">
            <div class="flex items-center gap-2 mb-4">
              <button @click="showPlatformForm = false" class="text-gray-500 hover:text-gray-700">
                &larr;
              </button>
              <h3 class="font-medium">{{ editingPlatformId ? 'Platform Duzenle' : 'Yeni Platform' }}</h3>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Platform Adi *</label>
              <input
                v-model="platformForm.name"
                type="text"
                class="w-full border rounded-lg px-3 py-2"
                placeholder="ornegin: Trendyol, Getir..."
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Sira No</label>
              <input
                v-model.number="platformForm.display_order"
                type="number"
                class="w-full border rounded-lg px-3 py-2"
                min="0"
              />
            </div>

            <div class="flex gap-3 pt-2">
              <button
                @click="showPlatformForm = false"
                class="flex-1 py-2 border rounded-lg text-gray-700 hover:bg-gray-100"
              >
                Iptal
              </button>
              <button
                @click="submitPlatformForm"
                :disabled="submitting"
                class="flex-1 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
              >
                {{ submitting ? 'Kaydediliyor...' : 'Kaydet' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
