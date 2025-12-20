<script setup lang="ts">
defineProps<{
  message: string
  dismissible?: boolean
}>()

const emit = defineEmits<{
  dismiss: []
}>()
</script>

<template>
  <div v-if="message" class="bg-red-100 text-red-700 p-4 rounded-lg flex items-center justify-between">
    <span>{{ message }}</span>
    <button
      v-if="dismissible !== false"
      @click="emit('dismiss')"
      class="ml-2 text-red-800 font-bold hover:text-red-900 transition-colors"
      aria-label="Kapat"
    >
      &times;
    </button>
  </div>
</template>
