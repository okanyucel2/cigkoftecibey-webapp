<template>
  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
    <!-- Header -->
    <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <Activity class="w-5 h-5 text-gray-500" />
        <h3 class="font-semibold text-gray-900">Son İşlemler</h3>
      </div>
      <span class="text-xs text-gray-500">Son 5 işlem</span>
    </div>

    <!-- Activity List -->
    <div class="divide-y divide-gray-50">
      <div
        v-for="activity in activities"
        :key="activity.id"
        :class="[
          'group px-4 py-3 flex items-center gap-3 transition-colors',
          activity.is_cancelled ? 'bg-gray-50 opacity-60' : 'hover:bg-gray-50'
        ]"
      >
        <!-- Time -->
        <span
          :class="[
            'text-sm font-mono w-12 flex-shrink-0',
            activity.is_cancelled ? 'text-gray-400 line-through' : 'text-gray-500'
          ]"
        >
          {{ activity.time }}
        </span>

        <!-- Icon -->
        <div
          :class="[
            'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0',
            activity.is_cancelled ? 'bg-gray-200' : activityIconBg(activity.type)
          ]"
        >
          <component
            :is="activityIcon(activity.type)"
            class="w-4 h-4"
            :class="activity.is_cancelled ? 'text-gray-400' : activityIconColor(activity.type)"
          />
        </div>

        <!-- Description -->
        <div class="flex-1 min-w-0">
          <span
            :class="[
              'text-sm truncate block',
              activity.is_cancelled ? 'text-gray-400 line-through' : 'text-gray-900'
            ]"
          >
            {{ activity.description }}
          </span>
          <span v-if="activity.cancel_reason" class="text-xs text-red-500">
            İptal: {{ getCancelReasonText(activity.cancel_reason) }}
          </span>
          <span v-else-if="activity.detail" class="text-xs text-gray-500">
            {{ activity.detail }}
          </span>
        </div>

        <!-- Amount -->
        <span
          :class="[
            'text-sm font-medium flex-shrink-0',
            activity.is_cancelled
              ? 'text-gray-400 line-through'
              : activity.amount >= 0 ? 'text-emerald-600' : 'text-red-600'
          ]"
        >
          {{ activity.amount >= 0 ? '+' : '' }}₺{{ formatAmount(activity.amount) }}
        </span>

        <!-- Cancel Button (hover'da görünür) -->
        <button
          v-if="!activity.is_cancelled"
          type="button"
          class="opacity-0 group-hover:opacity-100 p-1 rounded text-gray-400 hover:text-red-500 hover:bg-red-50 transition-all"
          title="İptal Et"
          @click.stop="openCancelModal(activity)"
        >
          <X class="w-4 h-4" />
        </button>
        <span v-else class="w-6" />
      </div>

      <!-- Empty State -->
      <div
        v-if="activities.length === 0"
        class="px-4 py-8 text-center text-gray-500"
      >
        <Clock class="w-8 h-8 mx-auto mb-2 text-gray-300" />
        <p class="text-sm">Henüz işlem yok</p>
      </div>
    </div>

    <!-- Cancel Modal -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition-opacity duration-150"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition-opacity duration-150"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="showCancelModal"
          class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          @click.self="closeCancelModal"
        >
          <div class="bg-white rounded-xl shadow-xl w-full max-w-sm overflow-hidden">
            <!-- Modal Header -->
            <div class="px-4 py-3 border-b flex items-center justify-between">
              <h3 class="font-semibold text-gray-900">İşlemi İptal Et</h3>
              <button
                type="button"
                class="p-1 rounded text-gray-400 hover:text-gray-600"
                @click="closeCancelModal"
              >
                <X class="w-5 h-5" />
              </button>
            </div>

            <!-- Modal Body -->
            <div class="p-4 space-y-4">
              <!-- Activity Preview -->
              <div class="bg-gray-50 rounded-lg p-3 text-sm">
                <div class="flex justify-between items-center">
                  <span class="text-gray-600">{{ cancelTarget?.description }}</span>
                  <span class="font-medium text-gray-900">
                    ₺{{ formatAmount(cancelTarget?.amount ?? 0) }}
                  </span>
                </div>
              </div>

              <!-- Reason Selection -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  İptal Sebebi
                </label>
                <div class="space-y-2">
                  <label
                    v-for="reason in cancelReasons"
                    :key="reason.value"
                    :class="[
                      'flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors',
                      selectedReason === reason.value
                        ? 'border-red-300 bg-red-50'
                        : 'border-gray-200 hover:bg-gray-50'
                    ]"
                  >
                    <input
                      v-model="selectedReason"
                      type="radio"
                      :value="reason.value"
                      class="w-4 h-4 text-red-600 focus:ring-red-500"
                    />
                    <span class="text-sm text-gray-700">{{ reason.label }}</span>
                  </label>
                </div>
              </div>
            </div>

            <!-- Modal Footer -->
            <div class="px-4 py-3 border-t bg-gray-50 flex gap-2">
              <button
                type="button"
                class="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
                @click="closeCancelModal"
              >
                Vazgeç
              </button>
              <button
                type="button"
                :disabled="!selectedReason"
                class="flex-1 px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:bg-red-300"
                @click="confirmCancel"
              >
                İptal Et
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Component } from 'vue'
import {
  Activity,
  Clock,
  ShoppingCart,
  Smartphone,
  CreditCard,
  Wallet,
  Truck,
  Package,
  Coffee,
  Factory,
  AlertTriangle,
  X
} from 'lucide-vue-next'

export interface ActivityItem {
  id: string | number
  time: string
  type: 'sale' | 'online-sale' | 'expense' | 'salary' | 'courier' | 'purchase' | 'meal' | 'legen' | 'fire' | 'cash-count'
  description: string
  detail?: string
  amount: number
  is_cancelled?: boolean
  cancel_reason?: string
}

interface Props {
  activities?: ActivityItem[]
}

withDefaults(defineProps<Props>(), {
  activities: () => []
})

const emit = defineEmits<{
  cancel: [activity: ActivityItem, reason: string]
}>()

// Cancel Modal State
const showCancelModal = ref(false)
const cancelTarget = ref<ActivityItem | null>(null)
const selectedReason = ref('')

const cancelReasons = [
  { value: 'wrong_entry', label: 'Yanlış Giriş' },
  { value: 'duplicate', label: 'Mükerrer Kayıt' },
  { value: 'customer_refund', label: 'Müşteri İadesi' },
  { value: 'other', label: 'Diğer' }
]

function getCancelReasonText(reason: string): string {
  const found = cancelReasons.find(r => r.value === reason)
  return found?.label || reason
}

function openCancelModal(activity: ActivityItem) {
  cancelTarget.value = activity
  selectedReason.value = ''
  showCancelModal.value = true
}

function closeCancelModal() {
  showCancelModal.value = false
  cancelTarget.value = null
  selectedReason.value = ''
}

function confirmCancel() {
  if (cancelTarget.value && selectedReason.value) {
    emit('cancel', cancelTarget.value, selectedReason.value)
    closeCancelModal()
  }
}

function activityIcon(type: ActivityItem['type']): Component {
  const icons: Record<ActivityItem['type'], Component> = {
    'sale': ShoppingCart,
    'online-sale': Smartphone,
    'expense': CreditCard,
    'salary': Wallet,
    'courier': Truck,
    'purchase': Package,
    'meal': Coffee,
    'legen': Factory,
    'fire': AlertTriangle,
    'cash-count': Wallet
  }
  return icons[type] ?? Activity
}

function activityIconBg(type: ActivityItem['type']): string {
  const positive = ['sale', 'online-sale', 'legen']
  const neutral = ['cash-count']

  if (positive.includes(type)) return 'bg-emerald-100'
  if (neutral.includes(type)) return 'bg-blue-100'
  return 'bg-red-100'
}

function activityIconColor(type: ActivityItem['type']): string {
  const positive = ['sale', 'online-sale', 'legen']
  const neutral = ['cash-count']

  if (positive.includes(type)) return 'text-emerald-600'
  if (neutral.includes(type)) return 'text-blue-600'
  return 'text-red-600'
}

function formatAmount(amount: number): string {
  return Math.abs(amount).toLocaleString('tr-TR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}
</script>
