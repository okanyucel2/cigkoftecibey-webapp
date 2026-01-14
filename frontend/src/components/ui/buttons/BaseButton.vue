<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="[
      // Base styles
      'inline-flex items-center justify-center font-medium rounded-lg transition-colors duration-fast',
      'focus:outline-none focus:ring-2 focus:ring-offset-2',
      // Size variants
      sizeClasses,
      // Variant styles
      variantClasses,
      // Disabled state
      { 'opacity-50 cursor-not-allowed': disabled || loading }
    ]"
    v-bind="$attrs"
  >
    <!-- Loading Spinner -->
    <svg
      v-if="loading"
      class="animate-spin -ml-1 mr-2 h-4 w-4"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        class="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        stroke-width="4"
      />
      <path
        class="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>

    <!-- Icon (Left) -->
    <component
      v-if="icon && !iconRight"
      :is="icon"
      :class="['w-4 h-4', { 'mr-2': $slots.default }]"
    />

    <!-- Content -->
    <slot />

    <!-- Icon (Right) -->
    <component
      v-if="icon && iconRight"
      :is="icon"
      :class="['w-4 h-4', { 'ml-2': $slots.default }]"
    />
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Component } from 'vue'

interface Props {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'success'
  size?: 'sm' | 'md' | 'lg' | 'pos'
  type?: 'button' | 'submit' | 'reset'
  disabled?: boolean
  loading?: boolean
  icon?: Component
  iconRight?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  type: 'button',
  disabled: false,
  loading: false,
  iconRight: false,
})

const sizeClasses = computed(() => {
  const sizes = {
    sm: 'h-8 px-3 text-xs gap-1.5',
    md: 'h-10 px-4 text-sm gap-2',
    lg: 'h-12 px-6 text-base gap-2',
    pos: 'h-[52px] px-6 text-lg gap-2', // Touch-friendly
  }
  return sizes[props.size]
})

const variantClasses = computed(() => {
  const variants = {
    primary: [
      'bg-primary-600 text-white shadow-sm',
      'hover:bg-primary-700',
      'focus:ring-primary-500',
    ].join(' '),
    secondary: [
      'bg-white text-slate-700 border border-slate-300',
      'hover:bg-slate-50',
      'focus:ring-primary-500',
    ].join(' '),
    danger: [
      'bg-danger-600 text-white shadow-sm',
      'hover:bg-danger-700',
      'focus:ring-danger-500',
    ].join(' '),
    ghost: [
      'text-slate-700',
      'hover:bg-slate-100',
      'focus:ring-primary-500',
    ].join(' '),
    success: [
      'bg-success-600 text-white shadow-sm',
      'hover:bg-success-800',
      'focus:ring-success-600',
    ].join(' '),
  }
  return variants[props.variant]
})
</script>
