<script setup lang="ts">
/**
 * TabBar - Tab navigation component for multi-tab pages
 *
 * Usage:
 * <TabBar v-model="activeTab" :tabs="tabs" />
 *
 * const tabs = [
 *   { id: 'employees', label: 'Personel Listesi', icon: '👤' },
 *   { id: 'payroll', label: 'Personel Ödemeleri', icon: '💳', badge: 5 },
 * ]
 */

export interface Tab {
  id: string
  label: string
  icon?: string
  badge?: string | number
}

defineProps<{
  tabs: Tab[]
  modelValue: string
}>()

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<template>
  <div class="tab-bar" v-if="tabs.length > 1">
    <button
      v-for="tab in tabs"
      :key="tab.id"
      @click="$emit('update:modelValue', tab.id)"
      :class="['tab-item', { active: modelValue === tab.id }]"
      :aria-selected="modelValue === tab.id"
      role="tab"
    >
      <span v-if="tab.icon" class="tab-icon">{{ tab.icon }}</span>
      <span class="tab-label">{{ tab.label }}</span>
      <span v-if="tab.badge !== undefined" class="tab-badge">{{ tab.badge }}</span>
    </button>
  </div>
</template>

<style scoped>
.tab-bar {
  display: flex;
  gap: 4px;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 16px;
  overflow-x: auto;
  scrollbar-width: none; /* Firefox */
}

.tab-bar::-webkit-scrollbar {
  display: none; /* Chrome/Safari */
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 12px 16px;
  border-bottom: 2px solid transparent;
  font-size: 14px;
  font-weight: 500;
  color: #6b7280;
  background: none;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
  border-radius: 6px 6px 0 0;
}

.tab-item:hover {
  color: #374151;
  background: #f9fafb;
}

.tab-item.active {
  color: #dc2626;
  border-bottom-color: #dc2626;
}

.tab-icon {
  font-size: 16px;
  line-height: 1;
}

.tab-label {
  line-height: 1.4;
}

.tab-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  background: #dc2626;
  color: white;
  font-size: 11px;
  font-weight: 600;
  padding: 0 6px;
  border-radius: 9999px;
  line-height: 1;
}

/* Active tab badge gets lighter background */
.tab-item.active .tab-badge {
  background: #fca5a5;
  color: #991b1b;
}
</style>
