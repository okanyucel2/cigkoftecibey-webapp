<script setup lang="ts">
defineProps<{
  text?: string
  size?: 'sm' | 'md' | 'lg'
}>()
</script>

<template>
  <div
    :class="[
      'flex flex-col items-center justify-center text-gray-500',
      size === 'sm' ? 'p-4' : size === 'lg' ? 'p-12' : 'p-8'
    ]"
  >
    <div class="animate-spin rounded-full border-2 border-gray-300 border-t-brand-red h-8 w-8 mb-3"></div>
    <span :class="size === 'sm' ? 'text-sm' : ''">{{ text || 'Yukleniyor...' }}</span>
  </div>
</template>
