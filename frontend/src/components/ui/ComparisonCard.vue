<!-- frontend/src/components/ui/ComparisonCard.vue -->
<script setup lang="ts">
import { computed } from 'vue'
import type { BilancoPeriodData } from '@/types/comparison'

const props = defineProps<{
  data: BilancoPeriodData
  position: 'left' | 'right'
}>()

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

const totalRevenue = computed(() => props.data.total_revenue)

const profitMarginColor = computed(() => {
  return props.data.profit_margin >= 50 ? 'text-green-600' : props.data.profit_margin >= 30 ? 'text-yellow-600' : 'text-red-600'
})

const profitCardBackground = computed(() => {
  return props.data.net_profit >= 0
    ? 'bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200'
    : 'bg-gradient-to-br from-red-50 to-red-100 border-red-200'
})
</script>

<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-800">
        {{ data.period_label }}
      </h3>
      <span class="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded-full">
        {{ data.start_date === data.end_date
          ? new Date(data.start_date).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' })
          : `${new Date(data.start_date).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' })} - ${new Date(data.end_date).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' })}`
        }}
      </span>
    </div>

    <!-- Revenue Channels -->
    <p class="text-xs text-gray-500 font-medium mb-2">Ciro Kanallari</p>
    <div class="grid grid-cols-3 gap-2 mb-4">
      <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-2 border border-blue-200">
        <p class="text-xs text-blue-600 flex items-center gap-1">
          <span>💳</span> Visa
        </p>
        <p class="text-sm font-bold text-blue-700">{{ formatCurrency(data.revenue_breakdown.visa) }}</p>
      </div>
      <div class="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-lg p-2 border border-emerald-200">
        <p class="text-xs text-emerald-600 flex items-center gap-1">
          <span>💵</span> Nakit
        </p>
        <p class="text-sm font-bold text-emerald-700">{{ formatCurrency(data.revenue_breakdown.nakit) }}</p>
      </div>
      <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-2 border border-purple-200">
        <p class="text-xs text-purple-600 flex items-center gap-1">
          <span>📱</span> Online
        </p>
        <p class="text-sm font-bold text-purple-700">{{ formatCurrency(data.revenue_breakdown.online) }}</p>
      </div>
    </div>

    <!-- Total Revenue -->
    <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-3 border border-green-200 mb-4">
      <p class="text-sm text-green-600 font-medium flex items-center gap-1">
        <span>💰</span> Toplam Ciro
      </p>
      <p class="text-xl font-bold text-green-700">{{ formatCurrency(totalRevenue) }}</p>
    </div>

    <!-- Expense Breakdown -->
    <p class="text-xs text-gray-500 font-medium mb-2">Gider Detaylari</p>
    <div class="grid grid-cols-2 gap-x-4 gap-y-1 text-sm text-gray-600 mb-3">
      <span>Mal Alimi {{ formatCurrency(data.expense_breakdown.mal_alimi) }}</span>
      <span>Isletme Giderleri {{ formatCurrency(data.expense_breakdown.gider) }}</span>
      <span>Personel Yemekleri {{ formatCurrency(data.expense_breakdown.staff) }}</span>
      <span>Kurye {{ formatCurrency(data.expense_breakdown.kurye) }}</span>
      <span>Part-Time {{ formatCurrency(data.expense_breakdown.parttime) }}</span>
      <span>Uretim {{ formatCurrency(data.expense_breakdown.uretim) }}</span>
    </div>

    <!-- Total Expenses -->
    <div class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-3 border border-orange-200 mb-4">
      <p class="text-sm text-orange-600 font-medium flex items-center gap-1">
        <span>📦</span> Toplam Gider
      </p>
      <p class="text-xl font-bold text-orange-700">{{ formatCurrency(data.total_expenses) }}</p>
    </div>

    <!-- Net Profit -->
    <div :class="['rounded-xl p-3 border', profitCardBackground]">
      <p :class="['text-sm font-medium flex items-center gap-1', props.data.net_profit >= 0 ? 'text-blue-600' : 'text-red-600']">
        <span>📈</span> Net Kar
      </p>
      <p :class="['text-xl font-bold', props.data.net_profit >= 0 ? 'text-blue-700' : 'text-red-700']">
        {{ formatCurrency(data.net_profit) }}
      </p>
      <p :class="['text-xs mt-1', profitMarginColor]">
        Karlilik: %{{ data.profit_margin.toFixed(0) }}
      </p>
    </div>
  </div>
</template>
