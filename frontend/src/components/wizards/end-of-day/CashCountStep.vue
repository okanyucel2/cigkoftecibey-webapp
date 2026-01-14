<template>
  <div class="space-y-6">
    <!-- Instruction -->
    <div class="bg-amber-50 border border-amber-200 rounded-lg p-4">
      <div class="flex gap-3">
        <AlertCircle class="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
        <div>
          <h4 class="font-medium text-amber-800">Kasa Sayimi (Blind Count)</h4>
          <p class="text-sm text-amber-700 mt-1">
            Kasadaki nakit miktarini, sistemi gormeden sayiniz.
            Bu yontem sayim hatalarini azaltir.
          </p>
        </div>
      </div>
    </div>

    <!-- Cash Input -->
    <div class="space-y-2">
      <label class="block text-sm font-medium text-gray-700">
        Kasada Sayilan Nakit
      </label>
      <div class="relative">
        <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 font-medium">
          TL
        </span>
        <input
          type="number"
          :value="countedAmount ?? ''"
          @input="handleInput"
          placeholder="0.00"
          class="w-full pl-10 pr-4 py-3 text-lg font-semibold border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
          min="0"
          step="0.01"
        />
      </div>
    </div>

    <!-- Result Display (only shows after input) -->
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 transform -translate-y-2"
      enter-to-class="opacity-100 transform translate-y-0"
    >
      <div v-if="countedAmount !== null && countedAmount >= 0" class="space-y-3">
        <!-- Difference Display -->
        <div
          :class="[
            'rounded-lg p-4 border',
            differenceClass
          ]"
        >
          <div class="flex justify-between items-center">
            <span class="text-sm font-medium">Kasa Farki</span>
            <span class="text-lg font-bold">
              {{ difference >= 0 ? '+' : '' }}{{ formatCurrency(difference) }}
            </span>
          </div>
          <p class="text-xs mt-1 opacity-80">
            {{ differenceText }}
          </p>
        </div>

        <!-- Expected Amount (revealed after count) -->
        <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <div class="flex justify-between items-center text-sm">
            <span class="text-gray-600">Beklenen Miktar</span>
            <span class="font-medium text-gray-900">{{ formatCurrency(expectedAmount) }}</span>
          </div>
          <div class="flex justify-between items-center text-sm mt-2">
            <span class="text-gray-600">Sayilan Miktar</span>
            <span class="font-medium text-gray-900">{{ formatCurrency(countedAmount) }}</span>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { AlertCircle } from 'lucide-vue-next'

interface Props {
  countedAmount: number | null
  expectedAmount: number
  difference: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:countedAmount': [value: number | null]
}>()

function handleInput(event: Event) {
  const target = event.target as HTMLInputElement
  const value = target.value === '' ? null : parseFloat(target.value)
  emit('update:countedAmount', value)
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 2
  }).format(value)
}

const differenceClass = computed(() => {
  const absDiff = Math.abs(props.difference)
  if (absDiff <= 20) {
    return 'bg-emerald-50 border-emerald-200 text-emerald-800'
  } else if (absDiff <= 50) {
    return 'bg-amber-50 border-amber-200 text-amber-800'
  } else {
    return 'bg-red-50 border-red-200 text-red-800'
  }
})

const differenceText = computed(() => {
  const absDiff = Math.abs(props.difference)
  if (absDiff <= 20) {
    return 'Fark kabul edilebilir sinirda'
  } else if (absDiff <= 50) {
    return 'Fark biraz yuksek, kontrol edin'
  } else {
    return 'Fark yuksek! Sebep belirtmeniz gerekecek'
  }
})
</script>
