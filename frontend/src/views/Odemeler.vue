<script setup lang="ts">
import { ref } from 'vue'
import PaymentRecordsList from '@/components/payments/PaymentRecordsList.vue'
import { DateRangePicker } from '@/components/ui'
import type { DateRange } from '@/types'

const dateRange = ref<DateRange>({
  mode: 'single',
  value: {
    start: new Date().toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  }
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-display font-bold text-gray-900">Tedarikçi Ödemeleri</h1>
        <p class="text-sm text-gray-500 mt-1">Tedarikçilere yapılan ödemeleri görüntüleyin</p>
      </div>
      <DateRangePicker v-model="dateRange" />
    </div>

    <!-- Payment Records List -->
    <PaymentRecordsList />
  </div>
</template>
