<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition ease-out duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="modelValue"
        data-testid="slide-over"
        class="fixed inset-0 z-50 overflow-hidden"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-gray-900/50 backdrop-blur-sm"
          @click="close"
        />

        <!-- Panel -->
        <Transition
          enter-active-class="transform transition ease-out duration-300"
          enter-from-class="translate-x-full"
          enter-to-class="translate-x-0"
          leave-active-class="transform transition ease-in duration-200"
          leave-from-class="translate-x-0"
          leave-to-class="translate-x-full"
        >
          <div
            v-if="modelValue"
            class="fixed inset-y-0 right-0 w-full max-w-md bg-white shadow-xl flex flex-col"
            :class="{ 'sm:max-w-md': true }"
          >
            <!-- Header -->
            <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <div class="flex items-center gap-3">
                <component
                  v-if="icon"
                  :is="icon"
                  class="w-6 h-6"
                  :class="iconColorClass"
                />
                <h2 class="text-lg font-semibold text-gray-900">{{ title }}</h2>
              </div>
              <button
                type="button"
                class="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
                @click="close"
              >
                <X class="w-5 h-5" />
              </button>
            </div>

            <!-- Subtitle -->
            <div v-if="subtitle" class="px-6 py-2 bg-gray-50 text-sm text-gray-600">
              {{ subtitle }}
            </div>

            <!-- Content -->
            <div class="flex-1 overflow-y-auto px-6 py-4">
              <slot />
            </div>

            <!-- Footer -->
            <div
              v-if="$slots.footer"
              class="px-6 py-4 border-t border-gray-200 bg-gray-50"
            >
              <slot name="footer" />
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, watch, type Component } from 'vue'
import { X } from 'lucide-vue-next'

interface Props {
  modelValue: boolean
  title: string
  subtitle?: string
  icon?: Component
  iconColor?: 'blue' | 'amber' | 'emerald' | 'purple'
}

const props = withDefaults(defineProps<Props>(), {
  iconColor: 'blue'
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'close'): void
}>()

const iconColorClass = computed(() => {
  const colors = {
    blue: 'text-blue-600',
    amber: 'text-amber-600',
    emerald: 'text-emerald-600',
    purple: 'text-purple-600'
  }
  return colors[props.iconColor]
})

function close() {
  emit('update:modelValue', false)
  emit('close')
}

// Handle Escape key
function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && props.modelValue) {
    close()
  }
}

// Lock body scroll when open
watch(
  () => props.modelValue,
  (isOpen) => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
      document.addEventListener('keydown', handleKeydown)
    } else {
      document.body.style.overflow = ''
      document.removeEventListener('keydown', handleKeydown)
    }
  }
)
</script>
