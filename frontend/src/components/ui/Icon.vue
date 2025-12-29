<script setup lang="ts">
import { computed } from 'vue'
import { ICONS, type IconName } from '@/icons'

const props = withDefaults(
  defineProps<{
    name: IconName | string
    size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  }>(),
  {
    size: 'md'
  }
)

// Get icon emoji or fallback to the name itself (allows custom emojis)
const icon = computed(() => {
  // If name is in ICONS registry, use it
  if (props.name in ICONS) {
    return ICONS[props.name as IconName]
  }
  // Otherwise, use the name directly (allows passing custom emojis like '🎉')
  return props.name
})

const sizeClass = computed(() => `icon-${props.size}`)
</script>

<template>
  <span class="icon" :class="sizeClass" :aria-hidden="true">{{ icon }}</span>
</template>

<style scoped>
.icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.icon-xs {
  font-size: 12px;
}

.icon-sm {
  font-size: 14px;
}

.icon-md {
  font-size: 16px;
}

.icon-lg {
  font-size: 20px;
}

.icon-xl {
  font-size: 24px;
}
</style>
