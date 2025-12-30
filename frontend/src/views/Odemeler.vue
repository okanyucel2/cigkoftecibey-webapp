<script setup lang="ts">
import PaymentRecordsList from '@/components/payments/PaymentRecordsList.vue'
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-display font-bold text-gray-900">Tedarikçi Ödemeleri</h1>
      <p class="text-sm text-gray-500 mt-1">Tedarikçilere yapılan ödemeleri görüntüleyin</p>
    </div>

    <!-- Payment Records List -->
    <PaymentRecordsList />
  </div>
</template>
