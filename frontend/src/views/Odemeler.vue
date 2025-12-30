<script setup lang="ts">
import { ref } from 'vue'
import SupplierARList from '@/components/payments/SupplierARList.vue'
import PaymentRecordsList from '@/components/payments/PaymentRecordsList.vue'

const activeTab = ref<'cari' | 'records'>('cari')

// Reference to AR list for manual refresh
const arListRef = ref<InstanceType<typeof SupplierARList>>()

const tabs = [
  { id: 'cari' as const, label: 'Tedarikçi Cari', icon: '🏪' },
  { id: 'records' as const, label: 'Ödeme Kayıtları', icon: '📋' }
]

// Handle payment creation - refresh AR list
function handlePaymentCreated() {
  if (arListRef.value) {
    arListRef.value.refresh()
  }
}

// Watch tab changes to refresh data when switching
function handleTabChange(tabId: 'cari' | 'records') {
  activeTab.value = tabId
}
</script>

<template>
  <div class="max-w-7xl mx-auto space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-display font-bold text-gray-900">💳 Ödemeler</h1>
        <p class="text-sm text-gray-500 mt-1">Tedarikçi cari hesapları ve ödeme takibi</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="bg-white rounded-lg shadow">
      <div class="border-b">
        <nav class="flex -mb-px">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="handleTabChange(tab.id)"
            :class="[
              'px-6 py-4 text-sm font-medium border-b-2 transition-colors flex items-center gap-2',
              activeTab === tab.id
                ? 'border-brand-red text-brand-red'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            <span>{{ tab.icon }}</span>
            {{ tab.label }}
          </button>
        </nav>
      </div>

      <!-- Tab Content -->
      <div class="p-6">
        <SupplierARList
          v-if="activeTab === 'cari'"
          ref="arListRef"
        />
        <PaymentRecordsList
          v-else
          @payment-created="handlePaymentCreated"
        />
      </div>
    </div>
  </div>
</template>
