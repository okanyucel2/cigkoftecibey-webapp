<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { VueDatePicker } from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'
import { tr } from 'date-fns/locale'
import type { DateRange } from '@/types/filters'

const props = defineProps<{
  show: boolean
  initialStart?: string
  initialEnd?: string
  maxDate?: Date
}>()

const emit = defineEmits<{
  close: []
  apply: [range: DateRange]
}>()

// Local state for date picker
const startValue = ref<Date>(new Date())
const endValue = ref<Date>(new Date())

// Computed for v-model (array of dates)
const dateRange = computed<Date[]>({
  get: () => [startValue.value, endValue.value],
  set: (dates) => {
    if (dates && dates.length === 2) {
      startValue.value = dates[0]
      endValue.value = dates[1]
    }
  }
})

// Initialize from props
watch(() => props.show, (isOpen) => {
  if (isOpen) {
    if (props.initialStart) {
      startValue.value = new Date(props.initialStart)
    }
    if (props.initialEnd) {
      endValue.value = new Date(props.initialEnd)
    }
  }
})

// Handle apply
function handleApply() {
  // Ensure start <= end
  if (startValue.value > endValue.value) {
    // Swap if needed
    ;[startValue.value, endValue.value] = [endValue.value, startValue.value]
  }

  emit('apply', {
    start: startValue.value,
    end: endValue.value
  })
  emit('close')
}

// Handle close
function handleClose() {
  emit('close')
}
</script>

<template>
  <div
    v-if="show"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
    @click.self="handleClose"
  >
    <div
      class="bg-white rounded-xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden"
      @click.stop
    >
      <!-- Header -->
      <div class="bg-red-600 px-6 py-4">
        <h2 class="text-lg font-semibold text-white">Özel Tarih Aralığı</h2>
      </div>

      <!-- Body -->
      <div class="p-6">
        <!-- Inline Calendar (range selection) -->
        <div class="flex justify-center">
          <VueDatePicker
            v-model="dateRange"
            :range="true"
            :inline="true"
            :enable-time-picker="false"
            :max-date="maxDate"
            :auto-apply="true"
            :locale="tr"
          />
        </div>
      </div>

      <!-- Footer -->
      <div class="bg-gray-50 px-6 py-4 flex justify-end gap-3">
        <button
          @click="handleClose"
          class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
        >
          İptal
        </button>
        <button
          @click="handleApply"
          class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Uygula
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
:deep(.dp__main) {
  border: none;
  box-shadow: none;
}

:deep(.dp__today) {
  border-color: rgb(220 38 38);
}

:deep(.dp__range_end, .dp__range_start, .dp__active_date) {
  background-color: rgb(220 38 38);
}

:deep(.dp__range_between) {
  background-color: rgb(254 226 226);
}

:deep(.dp__action_select) {
  background-color: rgb(220 38 38);
}

:deep(.dp__action_select:hover) {
  background-color: rgb(185 28 28);
}

/* Hide action buttons in inline mode */
:deep(.dp__actions) {
  display: none;
}
</style>
