<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition ease-out duration-300"
      enter-from-class="opacity-0 translate-y-4 sm:translate-y-0 sm:translate-x-4"
      enter-to-class="opacity-100 translate-y-0 sm:translate-x-0"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="opacity-100 translate-y-0 sm:translate-x-0"
      leave-to-class="opacity-0 translate-y-4 sm:translate-y-0 sm:translate-x-4"
    >
      <div
        v-if="visible"
        class="fixed z-[100]
               bottom-4 left-1/2 -translate-x-1/2
               sm:left-auto sm:right-4 sm:translate-x-0
               flex items-center gap-3 px-4 py-3
               bg-gray-900 text-white rounded-xl shadow-lg
               min-w-[280px] max-w-[400px]"
      >
        <!-- Icon -->
        <div class="flex-shrink-0">
          <CheckCircle class="w-5 h-5 text-emerald-400" />
        </div>

        <!-- Message -->
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium truncate">{{ message }}</p>
        </div>

        <!-- Progress + Undo Button -->
        <div class="flex items-center gap-2 flex-shrink-0">
          <!-- Countdown Circle -->
          <div class="relative w-8 h-8">
            <svg class="w-8 h-8 -rotate-90" viewBox="0 0 32 32">
              <!-- Background circle -->
              <circle
                cx="16"
                cy="16"
                r="14"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                class="text-gray-700"
              />
              <!-- Progress circle -->
              <circle
                cx="16"
                cy="16"
                r="14"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                :stroke-dasharray="circumference"
                :stroke-dashoffset="dashOffset"
                class="text-emerald-400 transition-all duration-100"
              />
            </svg>
            <span class="absolute inset-0 flex items-center justify-center text-xs font-medium">
              {{ remainingSeconds }}
            </span>
          </div>

          <!-- Undo Button -->
          <button
            type="button"
            class="px-3 py-1.5 text-sm font-medium bg-white text-gray-900 rounded-lg
                   hover:bg-gray-100 transition-colors"
            @click="handleUndo"
          >
            Geri Al
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { CheckCircle } from 'lucide-vue-next'

interface Props {
  message?: string
  duration?: number // in milliseconds
}

const props = withDefaults(defineProps<Props>(), {
  message: 'Kaydedildi',
  duration: 7000
})

const emit = defineEmits<{
  undo: []
  timeout: []
}>()

const visible = ref(false)
const remaining = ref(props.duration)
let intervalId: ReturnType<typeof setInterval> | null = null

// Circle progress calculations
const circumference = computed(() => 2 * Math.PI * 14) // radius = 14
const dashOffset = computed(() => {
  const progress = remaining.value / props.duration
  return circumference.value * (1 - progress)
})
const remainingSeconds = computed(() => Math.ceil(remaining.value / 1000))

function show() {
  visible.value = true
  remaining.value = props.duration
  startCountdown()
}

function hide() {
  visible.value = false
  stopCountdown()
}

function startCountdown() {
  stopCountdown()
  intervalId = setInterval(() => {
    remaining.value -= 100
    if (remaining.value <= 0) {
      emit('timeout')
      hide()
    }
  }, 100)
}

function stopCountdown() {
  if (intervalId) {
    clearInterval(intervalId)
    intervalId = null
  }
}

function handleUndo() {
  emit('undo')
  hide()
}

// Cleanup on unmount
onUnmounted(() => {
  stopCountdown()
})

// Expose methods for parent
defineExpose({
  show,
  hide
})
</script>
