<template>
  <Teleport to="body">
    <div class="fixed bottom-4 right-4 z-[100] flex flex-col gap-2">
      <TransitionGroup
        enter-active-class="transition ease-out duration-200"
        enter-from-class="transform translate-x-full opacity-0"
        enter-to-class="transform translate-x-0 opacity-100"
        leave-active-class="transition ease-in duration-150"
        leave-from-class="transform translate-x-0 opacity-100"
        leave-to-class="transform translate-x-full opacity-0"
      >
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="[
            'flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg min-w-[280px] max-w-[400px]',
            bgClass(toast.type)
          ]"
        >
          <span class="text-lg">{{ icon(toast.type) }}</span>
          <span :class="textClass(toast.type)">{{ toast.message }}</span>
          <button
            type="button"
            class="ml-auto text-gray-400 hover:text-gray-600"
            @click="remove(toast.id)"
          >
            ✕
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { useToast } from '@/composables/useToast'

const { toasts, remove } = useToast()

function icon(type: string): string {
  const icons: Record<string, string> = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ'
  }
  return icons[type] ?? 'ℹ'
}

function bgClass(type: string): string {
  const classes: Record<string, string> = {
    success: 'bg-success-50 border border-success-200',
    error: 'bg-danger-50 border border-danger-200',
    warning: 'bg-warning-50 border border-warning-200',
    info: 'bg-primary-50 border border-primary-200'
  }
  return classes[type] ?? classes.info
}

function textClass(type: string): string {
  const classes: Record<string, string> = {
    success: 'text-success-800',
    error: 'text-danger-800',
    warning: 'text-warning-800',
    info: 'text-primary-800'
  }
  return classes[type] ?? classes.info
}
</script>
