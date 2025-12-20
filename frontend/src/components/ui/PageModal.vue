<script setup lang="ts">
defineProps<{
  show: boolean
  title: string
  subtitle?: string
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  loading?: boolean
}>()

const emit = defineEmits<{
  close: []
}>()

const sizeClasses = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-2xl',
  xl: 'max-w-4xl',
  full: 'max-w-5xl'
}
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="show"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
        @click.self="emit('close')"
      >
        <div
          :class="[
            'bg-white rounded-lg shadow-xl w-full mx-4 max-h-[90vh] overflow-hidden flex flex-col',
            sizeClasses[size || 'md']
          ]"
        >
          <!-- Header -->
          <div class="p-4 border-b flex justify-between items-center flex-shrink-0 bg-white sticky top-0">
            <div>
              <h2 class="text-lg font-semibold text-gray-900">{{ title }}</h2>
              <p v-if="subtitle" class="text-sm text-gray-500">{{ subtitle }}</p>
            </div>
            <button
              @click="emit('close')"
              class="text-gray-400 hover:text-gray-600 text-2xl leading-none p-1 -mr-1"
              aria-label="Kapat"
            >
              &times;
            </button>
          </div>

          <!-- Content -->
          <div class="flex-1 overflow-auto">
            <slot />
          </div>

          <!-- Footer (optional) -->
          <div v-if="$slots.footer" class="p-4 border-t bg-gray-50 flex-shrink-0">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
