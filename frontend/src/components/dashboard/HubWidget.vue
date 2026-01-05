<template>
  <div
    :data-testid="testId"
    class="relative"
  >
    <!-- Hub Button -->
    <button
      type="button"
      class="w-full bg-white rounded-xl shadow-sm border border-gray-100 p-4 text-left transition-all duration-200"
      :class="{
        'ring-2 ring-offset-2': isExpanded,
        [ringColorClass]: isExpanded,
        'hover:shadow-md hover:border-gray-200': !isExpanded
      }"
      @click="toggleExpanded"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div
            class="w-10 h-10 rounded-lg flex items-center justify-center"
            :class="iconBgClass"
          >
            <component :is="icon" class="w-5 h-5 text-white" />
          </div>
          <div>
            <div class="font-semibold text-gray-900">{{ label }}</div>
            <div class="text-sm text-gray-500">{{ formattedValue }}</div>
          </div>
        </div>
        <ChevronDown
          class="w-5 h-5 text-gray-400 transition-transform duration-200"
          :class="{ 'rotate-180': isExpanded }"
        />
      </div>
    </button>

    <!-- Dropdown -->
    <Transition
      enter-active-class="transition ease-out duration-150"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition ease-in duration-100"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <div
        v-if="isExpanded"
        class="absolute z-10 mt-2 w-full bg-white rounded-lg shadow-lg border border-gray-100 py-1 overflow-hidden"
      >
        <button
          v-for="action in actions"
          :key="action.id"
          :data-testid="`action-${action.id}`"
          type="button"
          class="w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center gap-3 transition-colors"
          @click="handleActionClick(action)"
        >
          <component
            v-if="action.icon"
            :is="action.icon"
            class="w-5 h-5 text-gray-500"
          />
          <span class="text-gray-700">{{ action.label }}</span>
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onUnmounted, type Component } from 'vue'
import { ChevronDown } from 'lucide-vue-next'

export interface HubAction {
  id: string
  label: string
  icon?: Component
}

interface Props {
  testId?: string
  label: string
  value: number
  icon: Component
  color: 'blue' | 'amber' | 'emerald' | 'purple'
  actions: HubAction[]
}

const props = withDefaults(defineProps<Props>(), {
  testId: 'hub-widget'
})

const emit = defineEmits<{
  (e: 'action-selected', action: HubAction): void
}>()

const isExpanded = ref(false)

const formattedValue = computed(() => {
  return `₺${new Intl.NumberFormat('tr-TR').format(props.value)}`
})

const iconBgClass = computed(() => {
  const colors = {
    blue: 'bg-blue-600',
    amber: 'bg-amber-600',
    emerald: 'bg-emerald-600',
    purple: 'bg-purple-600'
  }
  return colors[props.color]
})

const ringColorClass = computed(() => {
  const colors = {
    blue: 'ring-blue-500',
    amber: 'ring-amber-500',
    emerald: 'ring-emerald-500',
    purple: 'ring-purple-500'
  }
  return colors[props.color]
})

function toggleExpanded() {
  console.log('Hub clicked:', props.testId)
  isExpanded.value = !isExpanded.value
  console.log('Dropdown state:', isExpanded.value)
}

function handleActionClick(action: HubAction) {
  console.log('Action clicked:', action.id)
  isExpanded.value = false
  emit('action-selected', action)
}

// Close dropdown when clicking outside
function handleClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement
  const isInside = target.closest(`[data-testid="${props.testId}"]`)
  console.log('Outside click detected, isInside:', !!isInside, 'testId:', props.testId)
  if (!isInside) {
    isExpanded.value = false
  }
}

// Add/remove click outside listener only when dropdown is open
watch(isExpanded, (newVal) => {
  if (newVal) {
    // Use nextTick to add listener AFTER current click event completes
    nextTick(() => {
      document.addEventListener('click', handleClickOutside)
      console.log('Added outside click listener for:', props.testId)
    })
  } else {
    document.removeEventListener('click', handleClickOutside)
    console.log('Removed outside click listener for:', props.testId)
  }
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
