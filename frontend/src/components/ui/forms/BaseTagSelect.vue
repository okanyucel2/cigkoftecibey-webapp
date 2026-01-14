<template>
  <div class="w-full">
    <label
      v-if="label"
      class="block text-sm font-medium text-slate-700 mb-2"
    >
      {{ label }}
    </label>

    <div class="flex flex-wrap gap-2">
      <button
        v-for="option in options"
        :key="option.value"
        type="button"
        :class="[
          'inline-flex items-center px-4 py-2 rounded-full text-sm font-medium',
          'border transition-all duration-fast',
          'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-1',
          isSelected(option.value)
            ? 'bg-primary-600 text-white border-primary-600'
            : 'bg-white text-slate-700 border-slate-300 hover:border-primary-500 hover:bg-primary-50',
          // POS mode: larger touch targets
          { 'py-3 px-5 text-base': posMode }
        ]"
        @click="toggle(option.value)"
      >
        <!-- Optional Icon -->
        <component
          v-if="option.icon"
          :is="option.icon"
          :class="['w-4 h-4 mr-2', { 'w-5 h-5': posMode }]"
        />
        {{ option.label }}

        <!-- Check indicator for selected -->
        <svg
          v-if="isSelected(option.value)"
          class="w-4 h-4 ml-2"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>

    <p v-if="hint" class="mt-2 text-sm text-slate-500">
      {{ hint }}
    </p>
  </div>
</template>

<script setup lang="ts">
import type { Component } from 'vue'

interface Option {
  value: string | number
  label: string
  icon?: Component
}

interface Props {
  modelValue: (string | number)[]
  options: Option[]
  label?: string
  hint?: string
  multiple?: boolean
  posMode?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  multiple: true,
  posMode: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: (string | number)[]]
}>()

const isSelected = (value: string | number) => props.modelValue.includes(value)

const toggle = (value: string | number) => {
  if (props.multiple) {
    const newValue = isSelected(value)
      ? props.modelValue.filter(v => v !== value)
      : [...props.modelValue, value]
    emit('update:modelValue', newValue)
  } else {
    emit('update:modelValue', [value])
  }
}
</script>
