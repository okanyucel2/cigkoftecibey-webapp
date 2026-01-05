<template>
  <div class="w-full">
    <!-- Label -->
    <label
      v-if="label"
      :for="inputId"
      class="block text-sm font-medium text-slate-700 mb-1"
    >
      {{ label }}
      <span v-if="required" class="text-danger-600">*</span>
    </label>

    <!-- Input Container -->
    <div class="relative">
      <!-- Left Icon -->
      <div
        v-if="$slots.icon || icon"
        class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"
      >
        <slot name="icon">
          <component :is="icon" class="h-5 w-5 text-slate-400" />
        </slot>
      </div>

      <!-- Input -->
      <input
        :id="inputId"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :required="required"
        :class="[
          // Base
          'block w-full rounded-lg border bg-white text-slate-900 placeholder-slate-400',
          'transition-colors duration-fast',
          'focus:outline-none focus:ring-1',
          // Size
          sizeClasses,
          // Icon padding
          { 'pl-10': $slots.icon || icon },
          // States
          errorClasses,
          { 'bg-slate-50 cursor-not-allowed': disabled },
        ]"
        @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        v-bind="$attrs"
      />

      <!-- Right Icon (Error or Custom) -->
      <div
        v-if="error"
        class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none"
      >
        <svg class="h-5 w-5 text-danger-600" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>
      </div>
    </div>

    <!-- Helper Text -->
    <p
      v-if="hint && !error"
      class="mt-1 text-sm text-slate-500"
    >
      {{ hint }}
    </p>

    <!-- Error Message -->
    <p
      v-if="error"
      class="mt-1 text-sm text-danger-600"
    >
      {{ error }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Component } from 'vue'

interface Props {
  modelValue?: string | number
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search'
  label?: string
  placeholder?: string
  hint?: string
  error?: string
  disabled?: boolean
  readonly?: boolean
  required?: boolean
  size?: 'sm' | 'md' | 'lg' | 'pos'
  icon?: Component
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  size: 'md',
  disabled: false,
  readonly: false,
  required: false,
})

defineEmits<{
  'update:modelValue': [value: string]
}>()

const inputId = computed(() => `input-${Math.random().toString(36).substr(2, 9)}`)

const sizeClasses = computed(() => {
  const sizes = {
    sm: 'h-8 px-3 text-xs',
    md: 'h-10 px-3 text-sm',
    lg: 'h-12 px-4 text-base',
    pos: 'h-[52px] px-4 text-lg', // Touch-friendly
  }
  return sizes[props.size]
})

const errorClasses = computed(() => {
  if (props.error) {
    return 'border-danger-500 focus:border-danger-500 focus:ring-danger-500 pr-10'
  }
  return 'border-slate-300 focus:border-primary-500 focus:ring-primary-500'
})
</script>
