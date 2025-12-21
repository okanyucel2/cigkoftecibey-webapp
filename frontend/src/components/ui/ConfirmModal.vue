<template>
  <div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60]">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-sm mx-4 p-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">{{ title || 'Onay' }}</h3>
      <p class="text-gray-600 mb-6">{{ message }}</p>
      <div class="flex justify-end gap-3">
        <button
          data-testid="btn-cancel-confirm"
          @click="$emit('cancel')"
          class="px-4 py-2 border rounded-lg text-gray-700 hover:bg-gray-100"
        >
          {{ cancelText || 'Iptal' }}
        </button>
        <button
          data-testid="btn-confirm-delete"
          @click="$emit('confirm')"
          class="px-4 py-2 text-white rounded-lg hover:bg-opacity-90 transition-colors"
          :class="type === 'danger' ? 'bg-red-600 hover:bg-red-700' : 'bg-blue-600 hover:bg-blue-700'"
        >
          {{ confirmText || 'Evet, Sil' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  show: boolean
  title?: string
  message: string
  confirmText?: string
  cancelText?: string
  type?: 'danger' | 'primary'
}>()

defineEmits(['confirm', 'cancel'])
</script>
