<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="text-center pb-4 border-b">
      <div
        :class="[
          'w-16 h-16 rounded-full mx-auto flex items-center justify-center',
          Math.abs(cashDifference) <= 20
            ? 'bg-emerald-100'
            : Math.abs(cashDifference) <= 50
              ? 'bg-amber-100'
              : 'bg-red-100'
        ]"
      >
        <CheckCircle
          v-if="Math.abs(cashDifference) <= 20"
          class="w-8 h-8 text-emerald-600"
        />
        <AlertTriangle v-else class="w-8 h-8 text-amber-600" />
      </div>
      <h3 class="mt-3 text-lg font-semibold text-gray-900">Gun Sonu Ozeti</h3>
      <p class="text-sm text-gray-500">{{ todayFormatted }}</p>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-2 gap-3">
      <!-- Cash Count -->
      <div class="bg-gray-50 rounded-lg p-3">
        <span class="text-xs text-gray-500">Sayilan Kasa</span>
        <p class="text-lg font-bold text-gray-900">
          {{ formatCurrency(wizardData.countedAmount ?? 0) }}
        </p>
      </div>

      <!-- Cash Difference -->
      <div
        :class="[
          'rounded-lg p-3',
          Math.abs(cashDifference) <= 20
            ? 'bg-emerald-50'
            : Math.abs(cashDifference) <= 50
              ? 'bg-amber-50'
              : 'bg-red-50'
        ]"
      >
        <span class="text-xs text-gray-500">Kasa Farki</span>
        <p
          :class="[
            'text-lg font-bold',
            Math.abs(cashDifference) <= 20
              ? 'text-emerald-700'
              : Math.abs(cashDifference) <= 50
                ? 'text-amber-700'
                : 'text-red-700'
          ]"
        >
          {{ cashDifference >= 0 ? '+' : '' }}{{ formatCurrency(cashDifference) }}
        </p>
      </div>

      <!-- Total Expenses -->
      <div class="bg-gray-50 rounded-lg p-3">
        <span class="text-xs text-gray-500">Toplam Gider</span>
        <p class="text-lg font-bold text-gray-900">
          {{ formatCurrency(totalExpenses) }}
        </p>
      </div>

      <!-- Platform Sales -->
      <div class="bg-gray-50 rounded-lg p-3">
        <span class="text-xs text-gray-500">Platform Cirosu</span>
        <p class="text-lg font-bold text-gray-900">
          {{ formatCurrency(totalPlatformSales) }}
        </p>
      </div>
    </div>

    <!-- Difference Reason (Required if > 20 TL) -->
    <div v-if="requireReason" class="space-y-2">
      <label class="block text-sm font-medium text-gray-700">
        Fark Sebebi <span class="text-red-500">*</span>
      </label>
      <select
        :value="differenceReason"
        @change="handleReasonChange"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
      >
        <option value="">Sebep secin...</option>
        <option value="sayim_hatasi">Sayim Hatasi</option>
        <option value="bozuk_para">Bozuk Para Eksigi</option>
        <option value="pos_farki">POS Farki</option>
        <option value="kayit_eksik">Kayit Edilmemis Islem</option>
        <option value="para_ustu">Para Ustu Hatasi</option>
        <option value="diger">Diger</option>
      </select>

      <!-- Additional Note for "Diger" -->
      <Transition
        enter-active-class="transition-all duration-200"
        enter-from-class="opacity-0 h-0"
        enter-to-class="opacity-100 h-auto"
      >
        <textarea
          v-if="differenceReason === 'diger'"
          :value="customReason"
          @input="handleCustomReasonInput"
          placeholder="Aciklama yazin..."
          rows="2"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-sm"
        />
      </Transition>

      <p class="text-xs text-amber-600 flex items-center gap-1">
        <AlertTriangle class="w-3 h-3" />
        Fark 20 TL'yi astigindan sebep belirtmeniz zorunludur
      </p>
    </div>

    <!-- Expense Breakdown -->
    <div v-if="wizardData.expenses.length > 0" class="border-t pt-4">
      <h4 class="text-sm font-medium text-gray-700 mb-2">Gider Detayi</h4>
      <div class="space-y-1">
        <div
          v-for="expense in wizardData.expenses"
          :key="expense.id"
          class="flex justify-between text-sm"
        >
          <span class="text-gray-600">{{ expense.description }}</span>
          <span class="text-gray-900">{{ formatCurrency(expense.amount) }}</span>
        </div>
      </div>
    </div>

    <!-- Platform Breakdown -->
    <div v-if="wizardData.platforms.length > 0" class="border-t pt-4">
      <h4 class="text-sm font-medium text-gray-700 mb-2">Platform Detayi</h4>
      <div class="space-y-1">
        <div
          v-for="platform in wizardData.platforms"
          :key="platform.id"
          class="flex justify-between text-sm"
        >
          <span class="text-gray-600">{{ platform.name }}</span>
          <span class="text-gray-900">{{ formatCurrency(platform.confirmedAmount) }}</span>
        </div>
      </div>
    </div>

    <!-- Print Button (placeholder) -->
    <div class="border-t pt-4 mt-4">
      <button
        type="button"
        class="w-full flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
        @click="handlePrint"
      >
        <Printer class="w-4 h-4" />
        Yazdir
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { CheckCircle, AlertTriangle, Printer } from 'lucide-vue-next'

interface ExpenseItem {
  id: number
  description: string
  amount: number
  confirmed: boolean
}

interface PlatformItem {
  id: number
  name: string
  systemAmount: number
  confirmedAmount: number
  confirmed: boolean
}

interface WizardData {
  countedAmount: number | null
  expectedAmount: number
  expenses: ExpenseItem[]
  platforms: PlatformItem[]
  differenceReason: string
}

interface Props {
  wizardData: WizardData
  cashDifference: number
  differenceReason: string
  requireReason: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:differenceReason': [value: string]
}>()

const customReason = ref('')

const todayFormatted = computed(() => {
  return new Date().toLocaleDateString('tr-TR', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

const totalExpenses = computed(() =>
  props.wizardData.expenses.reduce((sum, e) => sum + e.amount, 0)
)

const totalPlatformSales = computed(() =>
  props.wizardData.platforms.reduce((sum, p) => sum + p.confirmedAmount, 0)
)

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 2
  }).format(value)
}

function handleReasonChange(event: Event) {
  const target = event.target as HTMLSelectElement
  emit('update:differenceReason', target.value)
}

function handleCustomReasonInput(event: Event) {
  const target = event.target as HTMLTextAreaElement
  customReason.value = target.value
  // Combine "diger" with custom reason
  emit('update:differenceReason', `diger:${target.value}`)
}

function handlePrint() {
  // TODO: Implement thermal printer / PDF export
  // For now, use browser print dialog
  window.print()
}
</script>
