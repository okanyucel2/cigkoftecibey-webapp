<script setup lang="ts">
/**
 * EntitySelector - Dropdown selector for categories, suppliers, employees, etc.
 *
 * Features:
 * - Native select with custom styling
 * - Optional settings button (opens management modal)
 * - Optional item count display
 * - "All items" option with custom label
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

defineEmits<{
  'update:modelValue': [value: string | number | null]
  settings: []
}>()

// Format option text with icon, label, and optional count
function formatOption(item: EntityItem): string {
  let text = ''
  if (item.icon) text += item.icon + ' '
  text += item.label
  if (props.showCount && item.count !== undefined) {
    text += ` (${item.count})`
  }
  return text
}
</script>

<template>
  <div class="entity-selector">
    <select
      :value="modelValue ?? props.allValue"
      @change="$emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
      :class="['select-input', { 'has-settings': props.showSettings }]"
    >
      <option :value="props.allValue">{{ props.allLabel }}</option>
      <option v-for="item in items" :key="item.id" :value="item.id">
        {{ formatOption(item) }}
      </option>
    </select>
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

.select-input {
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
}

.select-input.has-settings {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}

.select-input:hover {
  background: #e5e7eb;
}

.select-input:focus {
  outline: none;
  ring: 2px;
  ring-color: #dc2626;
  background: #e5e7eb;
}

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
  ring: 2px;
  ring-color: #dc2626;
}
</style>
