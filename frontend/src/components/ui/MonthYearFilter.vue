<script setup lang="ts">
import { MONTHS } from '@/composables'

const props = defineProps<{
  modelValue: { month: number; year: number }
  years?: number[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: { month: number; year: number }]
}>()

// Default years if not provided
const defaultYears = () => {
  const currentYear = new Date().getFullYear()
  return [currentYear, currentYear - 1, currentYear - 2]
}

function updateMonth(month: number) {
  emit('update:modelValue', { ...props.modelValue, month })
}

function updateYear(year: number) {
  emit('update:modelValue', { ...props.modelValue, year })
}
</script>

<template>
  <div class="flex gap-2 items-center bg-gray-100 rounded-lg px-3 py-1.5">
    <select
      :value="modelValue.month"
      @change="updateMonth(Number(($event.target as HTMLSelectElement).value))"
      class="bg-transparent border-none text-sm font-medium focus:ring-0 cursor-pointer"
    >
      <option v-for="month in MONTHS" :key="month.value" :value="month.value">
        {{ month.label }}
      </option>
    </select>
    <select
      :value="modelValue.year"
      @change="updateYear(Number(($event.target as HTMLSelectElement).value))"
      class="bg-transparent border-none text-sm font-medium focus:ring-0 cursor-pointer"
    >
      <option v-for="year in (years || defaultYears())" :key="year" :value="year">
        {{ year }}
      </option>
    </select>
  </div>
</template>
