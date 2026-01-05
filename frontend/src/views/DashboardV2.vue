<template>
  <div class="min-h-screen bg-gray-50 p-4 md:p-6">
    <!-- Header -->
    <header class="mb-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Bilanço</h1>
          <p class="text-sm text-gray-500">
            {{ formattedDate }} • Son güncelleme: {{ lastUpdateText }}
          </p>
        </div>
        <button
          type="button"
          class="hidden md:flex items-center gap-2 px-3 py-2 text-sm text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50"
        >
          <Search class="w-4 h-4" />
          <span>⌘K Hızlı işlem</span>
        </button>
      </div>
    </header>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <Loader2 class="w-8 h-8 text-primary-500 animate-spin" />
    </div>

    <!-- Error State -->
    <div
      v-else-if="error"
      class="bg-danger-50 border border-danger-200 rounded-lg p-4 mb-6"
    >
      <div class="flex items-center gap-3">
        <AlertCircle class="w-5 h-5 text-danger-600" />
        <p class="text-danger-700">{{ error }}</p>
      </div>
      <button
        type="button"
        class="mt-3 text-sm text-danger-600 hover:underline"
        @click="refresh"
      >
        Tekrar dene
      </button>
    </div>

    <!-- Main Content -->
    <div v-else class="space-y-6">
      <!-- KPI Cards Grid -->
      <div
        data-testid="kpi-grid"
        class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        <!-- Net Ciro -->
        <KPICard
          data-testid="kpi-net-ciro"
          label="Net Ciro"
          :value="netCiro"
          prefix="₺"
          :badge="netCiroTrend"
          :trend="netCiroTrendDirection"
          :subtitle="netCiroSubtitle"
          format-as-currency
        />

        <!-- Kasa Farkı -->
        <KPICard
          data-testid="kpi-kasa-farki"
          label="Kasa Farkı"
          :value="kasaFarki"
          prefix="₺"
          :badge="kasaFarkiBadge"
          :badge-type="kasaFarkiBadgeType"
          :subtitle="kasaFarkiSubtitle"
          format-as-currency
        />

        <!-- İşçilik Oranı -->
        <KPICard
          data-testid="kpi-iscilik"
          label="İşçilik Oranı"
          :value="iscilikOrani"
          format-as-percent
          :badge="iscilikBadge"
          :badge-type="iscilikBadgeType"
          show-progress
          :progress-percent="iscilikOrani"
          :progress-color="iscilikProgressColor"
          target="%20"
        />

        <!-- Legen/Ciro -->
        <KPICard
          data-testid="kpi-legen"
          label="Legen/Ciro"
          :value="legenCiro"
          prefix="₺"
          :badge="`${legenCount} legen`"
          badge-type="info"
          format-as-currency
        />
      </div>

      <!-- Hub Widgets Grid -->
      <div
        data-testid="hub-grid"
        class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        <!-- Satış Hub -->
        <HubWidget
          data-testid="hub-satis"
          label="Satış"
          :value="netCiro"
          :icon="Wallet"
          color="blue"
          :actions="satisActions"
          @action-selected="handleSatisAction"
        />

        <!-- Gider Hub -->
        <HubWidget
          data-testid="hub-gider"
          label="Gider"
          :value="totalExpenses"
          :icon="Receipt"
          color="amber"
          :actions="giderActions"
          @action-selected="handleGiderAction"
        />

        <!-- Ekip Hub -->
        <HubWidget
          data-testid="hub-ekip"
          label="Ekip"
          :value="0"
          :icon="Users"
          color="emerald"
          :actions="ekipActions"
          @action-selected="handleEkipAction"
        />

        <!-- Üretim Hub -->
        <HubWidget
          data-testid="hub-uretim"
          label="Üretim"
          :value="0"
          :icon="Factory"
          color="purple"
          :actions="uretimActions"
          @action-selected="handleUretimAction"
        />
      </div>

      <!-- Middle Section: Platform Distribution + Operational Summary -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Platform Distribution -->
        <div
          data-testid="platform-distribution"
          class="bg-white rounded-xl shadow-sm border border-gray-100 p-6"
        >
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Platform Dağılımı</h3>
          <div class="space-y-3">
            <div
              v-for="(amount, platform) in onlineBreakdown"
              :key="platform"
              class="flex items-center justify-between"
            >
              <div class="flex items-center gap-3">
                <div
                  class="w-3 h-3 rounded-full"
                  :style="{ backgroundColor: getPlatformColor(platform as string) }"
                />
                <span class="text-gray-700">{{ platform }}</span>
              </div>
              <div class="text-right">
                <span class="font-medium text-gray-900">
                  ₺{{ formatNumber(amount) }}
                </span>
                <span class="text-sm text-gray-500 ml-2">
                  {{ getPlatformPercent(platform as string, amount) }}%
                </span>
              </div>
            </div>
            <!-- Salon -->
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div
                  class="w-3 h-3 rounded-full"
                  :style="{ backgroundColor: '#2563EB' }"
                />
                <span class="text-gray-700">Salon</span>
              </div>
              <div class="text-right">
                <span class="font-medium text-gray-900">
                  ₺{{ formatNumber(salonSales) }}
                </span>
                <span class="text-sm text-gray-500 ml-2">
                  {{ getSalonPercent() }}%
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Operational Summary -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Operasyonel Özet</h3>
          <div class="grid grid-cols-2 gap-4">
            <div class="p-4 bg-gray-50 rounded-lg">
              <div class="text-sm text-gray-500">Brüt Kâr</div>
              <div class="text-xl font-bold text-gray-900">
                ₺{{ formatNumber(brutKar) }}
              </div>
            </div>
            <div class="p-4 bg-gray-50 rounded-lg">
              <div class="text-sm text-gray-500">Kurye/Sipariş</div>
              <div class="text-xl font-bold text-gray-900">
                ₺{{ formatNumber(kuryePerSiparis) }}
              </div>
            </div>
            <div class="p-4 bg-gray-50 rounded-lg">
              <div class="text-sm text-gray-500">Paket Sayısı</div>
              <div class="text-xl font-bold text-gray-900">
                {{ paketSayisi }}
              </div>
            </div>
            <div class="p-4 bg-gray-50 rounded-lg">
              <div class="text-sm text-gray-500">Personel Yemeği</div>
              <div class="text-xl font-bold text-gray-900">
                ₺{{ formatNumber(staffMealsCost) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Panel -->
      <div
        data-testid="action-panel"
        class="bg-white rounded-xl shadow-sm border border-gray-100 p-4"
      >
        <h3 class="text-lg font-semibold text-gray-900 mb-3">Dikkat Edilmesi Gerekenler</h3>
        <div class="space-y-2">
          <div
            v-for="alert in alerts"
            :key="alert.id"
            class="flex items-center justify-between p-3 rounded-lg"
            :class="getAlertBgClass(alert.type)"
          >
            <div class="flex items-center gap-3">
              <component
                :is="getAlertIcon(alert.type)"
                class="w-5 h-5"
                :class="getAlertIconClass(alert.type)"
              />
              <span :class="getAlertTextClass(alert.type)">{{ alert.message }}</span>
            </div>
            <button
              v-if="alert.actionLabel"
              type="button"
              class="px-3 py-1 text-sm font-medium bg-white rounded border"
              :class="getAlertButtonClass(alert.type)"
            >
              {{ alert.actionLabel }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Slide-over Panel for Sales Entry -->
    <SlideOver
      v-model="showSalesPanel"
      title="Kasa Satışı"
      subtitle="Dashboard'u izleyerek kaydet"
      :icon="Wallet"
      icon-color="blue"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Tutar</label>
          <BaseInput
            v-model="salesForm.amount"
            type="number"
            placeholder="0,00"
            prefix="₺"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Ödeme Yöntemi</label>
          <BaseTagSelect
            v-model="salesForm.paymentMethods"
            :options="paymentOptions"
            :multiple="false"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Not (opsiyonel)</label>
          <BaseInput
            v-model="salesForm.note"
            placeholder="Notlar..."
          />
        </div>
      </div>
      <template #footer>
        <div class="flex justify-end gap-3">
          <button
            type="button"
            class="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            @click="showSalesPanel = false"
          >
            İptal
          </button>
          <button
            type="button"
            class="px-4 py-2 text-white bg-primary-600 rounded-lg hover:bg-primary-700"
            @click="handleSalesSave"
          >
            💾 Kaydet
          </button>
        </div>
      </template>
    </SlideOver>

    <!-- Slide-over Panel for Expense Entry -->
    <SlideOver
      v-model="showExpensePanel"
      title="Gider Girişi"
      subtitle="Dashboard'u izleyerek kaydet"
      :icon="Receipt"
      icon-color="amber"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Kategori</label>
          <BaseTagSelect
            v-model="expenseForm.category"
            :options="expenseCategories"
            :multiple="false"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Tutar</label>
          <BaseInput
            v-model="expenseForm.amount"
            type="number"
            placeholder="0,00"
            prefix="₺"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Açıklama</label>
          <BaseInput
            v-model="expenseForm.description"
            placeholder="Açıklama..."
          />
        </div>
      </div>
      <template #footer>
        <div class="flex justify-end gap-3">
          <button
            type="button"
            class="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            @click="showExpensePanel = false"
          >
            İptal
          </button>
          <button
            type="button"
            class="px-4 py-2 text-white bg-amber-600 rounded-lg hover:bg-amber-700"
            @click="handleExpenseSave"
          >
            💾 Kaydet
          </button>
        </div>
      </template>
    </SlideOver>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  Search,
  Loader2,
  AlertCircle,
  Wallet,
  Receipt,
  Users,
  Factory,
  Store,
  Smartphone,
  Calculator,
  ShoppingCart,
  Truck,
  CreditCard,
  Coffee,
  AlertTriangle,
  CheckCircle,
  Info
} from 'lucide-vue-next'

import KPICard from '@/components/dashboard/KPICard.vue'
import HubWidget, { type HubAction } from '@/components/dashboard/HubWidget.vue'
import SlideOver from '@/components/dashboard/SlideOver.vue'
import { BaseInput, BaseTagSelect } from '@/components/ui'
import { useDashboardData } from '@/composables/useDashboardData'

// Dashboard data composable
const { data, loading, error, refresh } = useDashboardData()

// Computed values
const netCiro = computed(() => data.value?.todaySales.total ?? 0)
const kasaFarki = computed(() => data.value?.cashDifference ?? 0)
const iscilikOrani = computed(() => data.value?.laborCostPercent ?? 0)
const legenCiro = computed(() => {
  if (!data.value || data.value.legenCount === 0) return 0
  return Math.round(data.value.todaySales.total / data.value.legenCount)
})
const legenCount = computed(() => data.value?.legenCount ?? 0)
const totalExpenses = computed(() => {
  if (!data.value) return 0
  const exp = data.value.todayExpenses
  return exp.purchases + exp.expenses + exp.staffMeals + exp.courier + exp.partTime
})
const onlineBreakdown = computed(() => data.value?.onlineBreakdown ?? {})
const salonSales = computed(() => data.value?.todaySales.salon ?? 0)
const brutKar = computed(() => data.value?.todayProfit ?? 0)
const kuryePerSiparis = computed(() => 8.5) // TODO: Calculate from API
const paketSayisi = computed(() => 47) // TODO: Calculate from API
const staffMealsCost = computed(() => data.value?.todayExpenses.staffMeals ?? 0)

// KPI badges and trends
const netCiroTrend = computed(() => '+8%') // TODO: Calculate from comparison API
const netCiroTrendDirection = computed<'up' | 'down' | null>(() => 'up')
const netCiroSubtitle = computed(() => 'düne göre +₺920')

const kasaFarkiBadge = computed(() => {
  const diff = kasaFarki.value
  if (Math.abs(diff) <= 50) return '✓'
  return `₺${Math.abs(diff)}`
})
const kasaFarkiBadgeType = computed<'success' | 'warning' | 'danger'>(() => {
  const diff = Math.abs(kasaFarki.value)
  if (diff <= 50) return 'success'
  if (diff <= 200) return 'warning'
  return 'danger'
})
const kasaFarkiSubtitle = computed(() => {
  const diff = Math.abs(kasaFarki.value)
  if (diff <= 50) return 'POS = Excel ✓'
  return 'Fark tespit edildi'
})

const iscilikBadge = computed(() => {
  const ratio = iscilikOrani.value
  if (ratio <= 20) return '✓'
  return '⚠️'
})
const iscilikBadgeType = computed<'success' | 'warning'>(() => {
  return iscilikOrani.value <= 20 ? 'success' : 'warning'
})
const iscilikProgressColor = computed(() => {
  return iscilikOrani.value <= 20 ? 'bg-success-500' : 'bg-warning-500'
})

// Date formatting
const formattedDate = computed(() => {
  const now = new Date()
  return new Intl.DateTimeFormat('tr-TR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    weekday: 'long'
  }).format(now)
})
const lastUpdateText = computed(() => '2 dk önce')

// Hub actions
const satisActions: HubAction[] = [
  { id: 'kasa-satisi', label: 'Kasa Satışı', icon: Store },
  { id: 'online-satis', label: 'Online Satış', icon: Smartphone },
  { id: 'kasa-sayimi', label: 'Kasa Sayımı', icon: Calculator }
]

const giderActions: HubAction[] = [
  { id: 'mal-alimi', label: 'Mal Alımı', icon: ShoppingCart },
  { id: 'kurye-gideri', label: 'Kurye Gideri', icon: Truck },
  { id: 'genel-gider', label: 'Genel Gider', icon: CreditCard }
]

const ekipActions: HubAction[] = [
  { id: 'personel-yemegi', label: 'Personel Yemeği', icon: Coffee },
  { id: 'maas-odemesi', label: 'Maaş Ödemesi', icon: Wallet }
]

const uretimActions: HubAction[] = [
  { id: 'uretim-girisi', label: 'Üretim Girişi', icon: Factory }
]

// Slide-over panels
const showSalesPanel = ref(false)
const showExpensePanel = ref(false)

// Forms
const salesForm = ref({
  amount: '',
  paymentMethods: [] as (string | number)[],
  note: ''
})

const expenseForm = ref({
  category: [] as (string | number)[],
  amount: '',
  description: ''
})

// Payment options for BaseTagSelect
const paymentOptions = [
  { value: 'cash', label: 'Nakit' },
  { value: 'card', label: 'Kredi Kartı' },
  { value: 'meal_card', label: 'Yemek Kartı' }
]

const expenseCategories = [
  { value: 'purchase', label: 'Mal Alımı' },
  { value: 'courier', label: 'Kurye' },
  { value: 'general', label: 'Genel Gider' }
]

// Hub action handlers
function handleSatisAction(action: HubAction) {
  if (action.id === 'kasa-satisi') {
    showSalesPanel.value = true
  }
  // TODO: Handle other actions
}

function handleGiderAction(action: HubAction) {
  if (action.id === 'mal-alimi' || action.id === 'genel-gider') {
    showExpensePanel.value = true
  }
  // TODO: Handle other actions
}

function handleEkipAction(_action: HubAction) {
  // TODO: Implement
}

function handleUretimAction(_action: HubAction) {
  // TODO: Implement
}

// Save handlers
function handleSalesSave() {
  // TODO: Implement optimistic UI save
  console.log('Saving sales:', salesForm.value)
  showSalesPanel.value = false
}

function handleExpenseSave() {
  // TODO: Implement optimistic UI save
  console.log('Saving expense:', expenseForm.value)
  showExpensePanel.value = false
}

// Alerts
interface Alert {
  id: string
  type: 'warning' | 'critical' | 'success' | 'info'
  message: string
  actionLabel?: string
}

const alerts = computed<Alert[]>(() => {
  const result: Alert[] = []

  // Cash difference alert
  const diff = Math.abs(kasaFarki.value)
  if (diff > 200) {
    result.push({
      id: 'cash-critical',
      type: 'critical',
      message: `Kasada ₺${diff} fark var`,
      actionLabel: 'Kontrol Et'
    })
  } else if (diff > 50) {
    result.push({
      id: 'cash-warning',
      type: 'warning',
      message: `Kasada ₺${diff} fark var`,
      actionLabel: 'Kontrol Et'
    })
  } else {
    result.push({
      id: 'cash-ok',
      type: 'success',
      message: 'Kasa farkı normal'
    })
  }

  // TODO: Add more alerts based on data

  return result
})

// Helper functions
function formatNumber(value: number): string {
  return new Intl.NumberFormat('tr-TR').format(value)
}

function getPlatformColor(platform: string): string {
  const colors: Record<string, string> = {
    Yemeksepeti: '#FF6B35',
    Getir: '#5D3FD3',
    Trendyol: '#F27C38',
    Salon: '#2563EB'
  }
  return colors[platform] ?? '#6B7280'
}

function getPlatformPercent(_platform: string, amount: number): number {
  const total = netCiro.value
  if (total === 0) return 0
  return Math.round((amount / total) * 100)
}

function getSalonPercent(): number {
  const total = netCiro.value
  if (total === 0) return 0
  return Math.round((salonSales.value / total) * 100)
}

function getAlertIcon(type: Alert['type']) {
  const icons = {
    warning: AlertTriangle,
    critical: AlertCircle,
    success: CheckCircle,
    info: Info
  }
  return icons[type]
}

function getAlertBgClass(type: Alert['type']): string {
  const classes = {
    warning: 'bg-warning-50',
    critical: 'bg-danger-50',
    success: 'bg-success-50',
    info: 'bg-primary-50'
  }
  return classes[type]
}

function getAlertIconClass(type: Alert['type']): string {
  const classes = {
    warning: 'text-warning-600',
    critical: 'text-danger-600',
    success: 'text-success-600',
    info: 'text-primary-600'
  }
  return classes[type]
}

function getAlertTextClass(type: Alert['type']): string {
  const classes = {
    warning: 'text-warning-800',
    critical: 'text-danger-800',
    success: 'text-success-800',
    info: 'text-primary-800'
  }
  return classes[type]
}

function getAlertButtonClass(type: Alert['type']): string {
  const classes = {
    warning: 'border-warning-300 text-warning-700 hover:bg-warning-50',
    critical: 'border-danger-300 text-danger-700 hover:bg-danger-50',
    success: 'border-success-300 text-success-700 hover:bg-success-50',
    info: 'border-primary-300 text-primary-700 hover:bg-primary-50'
  }
  return classes[type]
}
</script>
