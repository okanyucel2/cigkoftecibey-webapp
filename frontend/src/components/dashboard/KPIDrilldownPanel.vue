<template>
  <SlideOver
    :model-value="show"
    :title="title"
    @close="emit('close')"
  >
    <!-- Loading State -->
    <div v-if="loading" class="p-4 space-y-3">
      <div v-for="i in 5" :key="i" class="animate-pulse">
        <div class="bg-gray-100 rounded-lg h-16" />
      </div>
    </div>

    <!-- Transaction List -->
    <div v-else class="p-4 space-y-2">
      <div
        v-for="item in items"
        :key="item.id"
        :class="[
          'rounded-lg border p-3 transition-colors',
          item.is_cancelled
            ? 'bg-gray-50 border-gray-200'
            : 'bg-white border-gray-200 hover:border-gray-300'
        ]"
      >
        <div class="flex items-center justify-between gap-3">
          <!-- Left: Time + Description -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="text-xs text-gray-400 font-mono">{{ item.time }}</span>
              <span
                :class="[
                  'text-sm font-medium',
                  item.is_cancelled ? 'text-gray-400 line-through' : 'text-gray-900'
                ]"
              >
                {{ item.description }}
              </span>
            </div>
            <p v-if="item.note" class="text-xs text-gray-500 mt-0.5 truncate">
              {{ item.note }}
            </p>
          </div>

          <!-- Right: Amount + Action -->
          <div class="flex items-center gap-3 flex-shrink-0">
            <span
              :class="[
                'font-semibold tabular-nums',
                item.is_cancelled ? 'text-gray-400 line-through' : 'text-gray-900'
              ]"
            >
              {{ formatCurrency(item.amount) }}
            </span>

            <!-- Cancel/Cancelled Badge -->
            <button
              v-if="!item.is_cancelled"
              type="button"
              class="px-2 py-1 text-xs font-medium text-red-600 bg-red-50 rounded hover:bg-red-100 transition-colors"
              @click="handleCancel(item)"
            >
              Iptal Et
            </button>
            <span
              v-else
              class="px-2 py-1 text-xs font-medium text-gray-500 bg-gray-100 rounded"
            >
              IPTAL
            </span>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-if="items.length === 0"
        class="text-center py-8 text-gray-500"
      >
        <Receipt class="w-12 h-12 mx-auto mb-3 text-gray-300" />
        <p>Bugune ait kayit bulunamadi</p>
      </div>
    </div>

    <!-- Footer Summary -->
    <template #footer>
      <div class="flex justify-between items-center">
        <div>
          <span class="text-sm text-gray-500">Toplam</span>
          <span class="text-xs text-gray-400 ml-1">({{ activeCount }} aktif)</span>
        </div>
        <span class="text-lg font-bold text-gray-900">
          {{ formatCurrency(activeTotal) }}
        </span>
      </div>
    </template>
  </SlideOver>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Receipt } from 'lucide-vue-next'
import SlideOver from './SlideOver.vue'
import { useUndoToast } from '@/composables/useUndoToast'

export interface DrilldownItem {
  id: number
  time: string
  description: string
  amount: number
  note?: string
  is_cancelled: boolean
}

interface Props {
  show: boolean
  title: string
  items: DrilldownItem[]
  loading?: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  cancel: [item: DrilldownItem]
}>()

const { showUndoToast } = useUndoToast()

const activeItems = computed(() =>
  props.items.filter(i => !i.is_cancelled)
)

const activeCount = computed(() => activeItems.value.length)

const activeTotal = computed(() =>
  activeItems.value.reduce((sum, i) => sum + i.amount, 0)
)

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 2
  }).format(value)
}

async function handleCancel(item: DrilldownItem) {
  // Show undo toast with 7 second window
  const { undone } = await showUndoToast({
    message: `${item.description} iptal edildi`,
    duration: 7000
  })

  if (!undone) {
    // User didn't undo - proceed with cancellation
    emit('cancel', item)
  }
}
</script>
