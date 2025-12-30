<script setup lang="ts">
import { ref } from 'vue'
import SupplierARList from '@/components/payments/SupplierARList.vue'
import PaymentRecordsList from '@/components/payments/PaymentRecordsList.vue'

const activeTab = ref<'cari' | 'records'>('cari')

const tabs = [
  { id: 'cari' as const, label: 'Tedarikçi Cari', icon: '' },
  { id: 'records' as const, label: 'Ödeme Kayıtları', icon: '' }
]
</script>

<template>
  <div class="max-w-7xl mx-auto space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-display font-bold text-gray-900">💳 Ödemeler</h1>
    </div>

    <!-- Tabs -->
    <div class="bg-white rounded-lg shadow">
      <div class="border-b">
        <nav class="flex -mb-px">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'px-6 py-4 text-sm font-medium border-b-2 transition-colors',
              activeTab === tab.id
                ? 'border-brand-red text-brand-red'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            ]"
          >
            <span class="mr-2">{{ tab.icon }}</span>
            {{ tab.label }}
          </button>
        </nav>
      </div>

      <!-- Tab Content -->
      <div class="p-6">
        <SupplierARList v-if="activeTab === 'cari'" />
        <PaymentRecordsList v-else />
      </div>
    </div>
  </div>
</template>
