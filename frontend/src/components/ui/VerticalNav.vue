<script setup lang="ts">
import { ref, watch } from 'vue'

/**
 * VerticalNav - Vertical navigation component with nested item support
 *
 * Usage:
 * <VerticalNav v-model="activeId" :items="navItems" />
 *
 * const navItems = [
 *   { id: 'dashboard', label: 'Genel Bakış', icon: '📊' },
 *   {
 *     id: 'procurement',
 *     label: 'Hizmet Alımları',
 *     icon: '🛒',
 *     subItems: [
 *       { id: 'procurement/personnel', label: 'Personel İaşe' },
 *       { id: 'procurement/courier', label: 'Kurye' },
 *     ]
 *   }
 * ]
 */

export interface NavItem {
  id: string
  label: string
  icon?: string
  subItems?: NavItem[]
}

interface Props {
  items: NavItem[]
  modelValue: string
  collapsible?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: string): void
}

const props = withDefaults(defineProps<Props>(), {
  collapsible: true
})

const emit = defineEmits<Emits>()

const expandedItems = ref<Set<string>>(new Set())

function toggleExpand(id: string) {
  const newSet = new Set(expandedItems.value)
  if (newSet.has(id)) {
    newSet.delete(id)
  } else {
    newSet.add(id)
  }
  expandedItems.value = newSet
}

function selectItem(id: string) {
  emit('update:modelValue', id)
}

function isActive(item: NavItem): boolean {
  return props.modelValue === item.id ||
    props.modelValue.startsWith(item.id + '/')
}

function isExpanded(id: string): boolean {
  return expandedItems.value.has(id)
}

// Auto-expand parent of active item
watch(() => props.modelValue, (newVal: string) => {
  if (newVal) {
    const parts = newVal.split('/')
    for (let i = 1; i < parts.length; i++) {
      const parentId = parts.slice(0, i).join('/')
      expandedItems.value.add(parentId)
    }
  }
}, { immediate: true })
</script>

<template>
  <nav class="vertical-nav">
    <div
      v-for="item in items"
      :key="item.id"
      class="nav-item"
      :class="{ 'has-subitems': item.subItems && item.subItems.length > 0 }"
    >
      <button
        @click="item.subItems && item.subItems.length > 0 && collapsible ? toggleExpand(item.id) : selectItem(item.id)"
        :class="[
          'nav-button',
          {
            'active': isActive(item),
            'has-children': item.subItems && item.subItems.length > 0
          }
        ]"
        :aria-expanded="item.subItems && item.subItems.length > 0 ? isExpanded(item.id) : undefined"
        :aria-current="isActive(item) ? 'page' : undefined"
      >
        <span v-if="item.icon" class="nav-icon">{{ item.icon }}</span>
        <span class="nav-label">{{ item.label }}</span>
        <span
          v-if="item.subItems && item.subItems.length > 0"
          class="expand-icon"
          :class="{ 'expanded': isExpanded(item.id) }"
        >
          ▼
        </span>
      </button>

      <div
        v-if="item.subItems && item.subItems.length > 0"
        v-show="!collapsible || isExpanded(item.id)"
        class="nav-subitems"
      >
        <button
          v-for="subItem in item.subItems"
          :key="subItem.id"
          @click="selectItem(subItem.id)"
          :class="[
            'nav-button',
            'subitem',
            { 'active': isActive(subItem) }
          ]"
          :aria-current="isActive(subItem) ? 'page' : undefined"
        >
          <span v-if="subItem.icon" class="nav-icon">{{ subItem.icon }}</span>
          <span class="nav-label">{{ subItem.label }}</span>
        </button>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.vertical-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  width: 100%;
}

.nav-item {
  display: flex;
  flex-direction: column;
}

.nav-button {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 12px 16px;
  border: none;
  background: transparent;
  color: #374151;
  font-size: 14px;
  font-weight: 500;
  text-align: left;
  cursor: pointer;
  transition: all 0.15s ease;
  border-radius: 6px;
  user-select: none;
}

.nav-button:hover {
  background: #f3f4f6;
}

.nav-button.active {
  background: #dc2626;
  color: white;
}

.nav-button.has-children {
  padding-right: 32px;
  position: relative;
}

.nav-icon {
  font-size: 16px;
  line-height: 1;
  flex-shrink: 0;
}

.nav-label {
  flex: 1;
  line-height: 1.4;
}

.expand-icon {
  position: absolute;
  right: 12px;
  font-size: 10px;
  color: #9ca3af;
  transition: transform 0.15s ease;
}

.expand-icon.expanded {
  transform: rotate(180deg);
}

.nav-button.active .expand-icon {
  color: rgba(255, 255, 255, 0.8);
}

.nav-subitems {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-top: 2px;
  padding-left: 16px;
  overflow: hidden;
  animation: slideDown 0.15s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.nav-button.subitem {
  padding-left: 24px;
  font-size: 13px;
}

.nav-button.subitem.active {
  background: #b91c1c;
}

/* Mobile Responsive */
@media (max-width: 640px) {
  .vertical-nav {
    flex-direction: row;
    overflow-x: auto;
    gap: 4px;
    scrollbar-width: none; /* Firefox */
  }

  .vertical-nav::-webkit-scrollbar {
    display: none; /* Chrome/Safari */
  }

  .nav-item {
    flex-shrink: 0;
  }

  .nav-button {
    padding: 10px 14px;
    white-space: nowrap;
  }

  .nav-button.has-children {
    padding-right: 28px;
  }

  .expand-icon {
    right: 10px;
  }

  .nav-subitems {
    position: absolute;
    top: 100%;
    left: 0;
    z-index: 10;
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    padding: 4px;
    margin-top: 4px;
    margin-left: 0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    min-width: 200px;
  }

  .nav-button.subitem {
    padding-left: 16px;
  }
}
</style>
