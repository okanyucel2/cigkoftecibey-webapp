<script setup lang="ts">
defineProps<{
  label: string
  value: string | number
  subtext?: string
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'purple'
  gradient?: boolean
  borderLeft?: boolean
}>()

const variantClasses = {
  default: {
    card: 'bg-white',
    value: 'text-gray-900',
    label: 'text-gray-500'
  },
  primary: {
    card: 'bg-white',
    value: 'text-blue-600',
    label: 'text-gray-500'
  },
  success: {
    card: 'bg-white',
    value: 'text-green-600',
    label: 'text-gray-500'
  },
  warning: {
    card: 'bg-white',
    value: 'text-orange-600',
    label: 'text-gray-500'
  },
  danger: {
    card: 'bg-white border-l-4 border-red-500',
    value: 'text-red-600',
    label: 'text-gray-500'
  },
  info: {
    card: 'bg-white',
    value: 'text-cyan-600',
    label: 'text-gray-500'
  },
  purple: {
    card: 'bg-white',
    value: 'text-purple-600',
    label: 'text-gray-500'
  }
}

const gradientClasses = {
  default: 'bg-gradient-to-r from-gray-500 to-gray-600',
  primary: 'bg-gradient-to-r from-blue-500 to-blue-600',
  success: 'bg-gradient-to-r from-green-500 to-green-600',
  warning: 'bg-gradient-to-r from-orange-500 to-orange-600',
  danger: 'bg-gradient-to-r from-red-500 to-red-600',
  info: 'bg-gradient-to-r from-cyan-500 to-cyan-600',
  purple: 'bg-gradient-to-r from-purple-500 to-purple-600'
}
</script>

<template>
  <div
    :class="[
      'rounded-lg shadow p-4',
      gradient
        ? [gradientClasses[variant || 'default'], 'text-white']
        : [variantClasses[variant || 'default'].card],
      borderLeft && !gradient ? 'border-l-4' : ''
    ]"
  >
    <p
      :class="[
        'text-sm',
        gradient ? 'text-white/80' : variantClasses[variant || 'default'].label
      ]"
    >
      {{ label }}
    </p>
    <p
      :class="[
        'text-xl font-bold',
        gradient ? 'text-white' : variantClasses[variant || 'default'].value
      ]"
    >
      {{ value }}
    </p>
    <p v-if="subtext" :class="['text-xs', gradient ? 'text-white/60' : 'text-gray-400']">
      {{ subtext }}
    </p>
  </div>
</template>
