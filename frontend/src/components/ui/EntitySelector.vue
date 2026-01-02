<script setup lang="ts">
/**
 * EntitySelector - Custom dropdown selector for categories, suppliers, employees, etc.
 *
 * Features:
 * - Custom dropdown (not native select) for consistent mobile experience
 * - Optional settings button (opens management modal)
 * - Optional item count display
 * - "All items" option with custom label
 * - Click outside to close
 *
 * Usage:
 * <EntitySelector
 *   v-model="selectedCategoryId"
 *   :items="categories"
 *   all-label="Tüm Kategoriler"
 *   :show-count="true"
 *   :show-settings="true"
 *   @settings="openCategoryModal"
 * />
 */

import { ref, computed, onMounted, onUnmounted } from 'vue'

export interface EntityItem {
  id: string | number
  label: string
  icon?: string
  count?: number
}

const props = withDefaults(
  defineProps<{
    items: EntityItem[]
    modelValue: string | number | null
    allLabel?: string
    allValue?: null
    showSettings?: boolean
    showCount?: boolean
  }>(),
  {
    allLabel: 'Tümü',
    allValue: null,
    showSettings: false,
    showCount: false
  }
)

const emit = defineEmits<{
  'update:modelValue': [value: string | number | null]
  settings: []
}>()

// State
const isOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

// Computed: Current selection label
const currentLabel = computed(() => {
  if (props.modelValue === null || props.modelValue === props.allValue) {
    return props.allLabel
  }
  const item = props.items.find(i => i.id === props.modelValue)
  if (!item) return props.allLabel

  let label = ''
  if (item.icon) label += item.icon + ' '
  label += item.label
  if (props.showCount && item.count !== undefined) {
    label += ` (${item.count})`
  }
  return label
})

// Computed: Current icon
const currentIcon = computed(() => {
  if (props.modelValue === null || props.modelValue === props.allValue) return ''
  const item = props.items.find(i => i.id === props.modelValue)
  return item?.icon || ''
})

// Toggle dropdown
function toggleDropdown() {
  console.log('[EntitySelector] toggleDropdown called, current isOpen:', isOpen.value)
  isOpen.value = !isOpen.value
  console.log('[EntitySelector] isOpen after toggle:', isOpen.value)
}

// Select item
function selectItem(id: string | number | null) {
  emit('update:modelValue', id)
  isOpen.value = false
}

// Close dropdown
function closeDropdown() {
  isOpen.value = false
}

// Handle click outside
function handleClickOutside(event: MouseEvent) {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    closeDropdown()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div class="entity-selector" ref="dropdownRef">
    <div class="select-wrapper" :class="{ 'has-settings': props.showSettings }">
      <button
        @click="toggleDropdown"
        class="select-button"
        :class="{ 'is-open': isOpen }"
        type="button"
      >
        <span v-if="currentIcon" class="item-icon">{{ currentIcon }}</span>
        <span class="item-label">{{ currentLabel }}</span>
        <svg
          class="dropdown-arrow"
          :class="{ 'rotate-180': isOpen }"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      <!-- Custom Dropdown Menu -->
      <div v-if="isOpen" class="dropdown-menu">
        {{ console.log('[EntitySelector] Rendering dropdown menu, isOpen:', isOpen) }}
        <!-- All Option -->
        <button
          @click="selectItem(props.allValue)"
          class="dropdown-item"
          :class="{ 'is-selected': props.modelValue === props.allValue }"
          type="button"
        >
          <span class="item-label">{{ props.allLabel }}</span>
          <svg
            v-if="props.modelValue === props.allValue"
            class="check-icon"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fill-rule="evenodd"
              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
              clip-rule="evenodd"
            />
          </svg>
        </button>

        <!-- Items -->
        <button
          v-for="item in items"
          :key="item.id"
          @click="selectItem(item.id)"
          class="dropdown-item"
          :class="{ 'is-selected': props.modelValue === item.id }"
          type="button"
        >
          <span v-if="item.icon" class="item-icon">{{ item.icon }}</span>
          <span class="item-label">{{ item.label }}</span>
          <span v-if="props.showCount && item.count !== undefined" class="item-count">
            ({{ item.count }})
          </span>
          <svg
            v-if="props.modelValue === item.id"
            class="check-icon"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fill-rule="evenodd"
              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
              clip-rule="evenodd"
            />
          </svg>
        </button>
      </div>
    </div>

    <button
      v-if="props.showSettings"
      @click="$emit('settings')"
      class="settings-btn"
      type="button"
      :title="'Yönet'"
    >
      ⚙️
    </button>
  </div>
</template>

<style scoped>
.entity-selector {
  display: flex;
  align-items: center;
  gap: 0;
}

.select-wrapper {
  position: relative;
}

.select-button {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #f3f4f6;
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  min-width: 160px;
  transition: background 0.15s;
  text-align: left;
}

.select-wrapper.has-settings .select-button {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}

.select-button:hover {
  background: #e5e7eb;
}

.select-button:focus {
  outline: none;
  box-shadow: 0 0 0 2px #fca5a5;
}

.select-button.is-open {
  background: #e5e7eb;
}

.item-icon {
  font-size: 16px;
  line-height: 1;
  flex-shrink: 0;
}

.item-label {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dropdown-arrow {
  width: 16px;
  height: 16px;
  color: #6b7280;
  transition: transform 0.2s;
  flex-shrink: 0;
}

.dropdown-arrow.rotate-180 {
  transform: rotate(180deg);
}

/* Dropdown Menu */
.dropdown-menu {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: auto;
  min-width: 100%;
  background: white;
  border-radius: 8px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  padding: 4px;
  z-index: 100;
  max-height: 300px;
  overflow-y: auto;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 10px 12px;
  border: none;
  background: transparent;
  border-radius: 6px;
  font-size: 14px;
  color: #374151;
  cursor: pointer;
  transition: background 0.1s;
  text-align: left;
}

.dropdown-item:hover {
  background: #f3f4f6;
}

.dropdown-item.is-selected {
  background: #fef2f2;
  color: #dc2626;
  font-weight: 500;
}

.item-count {
  color: #9ca3af;
  font-size: 13px;
}

.check-icon {
  width: 16px;
  height: 16px;
  color: #dc2626;
  margin-left: auto;
  flex-shrink: 0;
}

/* Settings Button */
.settings-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  border: none;
  border-radius: 8px;
  padding: 8px 10px;
  cursor: pointer;
  font-size: 16px;
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  transition: background 0.15s;
  min-width: 38px;
}

.settings-btn:hover {
  background: #e5e7eb;
}

.settings-btn:focus {
  outline: none;
  box-shadow: 0 0 0 2px #fca5a5;
}

/* Mobile specific styles */
@media (max-width: 640px) {
  .select-button {
    min-width: 140px;
    font-size: 16px; /* Prevent iOS zoom on focus */
  }

  .dropdown-menu {
    left: 0;
    right: 0;
    min-width: 200px;
  }

  .dropdown-item {
    padding: 12px;
  }
}
</style>
