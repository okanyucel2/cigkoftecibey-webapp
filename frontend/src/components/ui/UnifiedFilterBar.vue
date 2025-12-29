<script setup lang="ts">
/**
 * UnifiedFilterBar - Complete filter bar for all pages
 *
 * Combines:
 * - Date filter (SingleRowDateFilter)
 * - Entity selector (categories, suppliers, etc.)
 * - Quick actions (search, export)
 * - Primary action button (new item)
 *
 * Usage - Simple (just date filter + action):
 * <UnifiedFilterBar
 *   v-model:date-range="dateRange"
 *   :primary-action="{ label: '+ Yeni Gider', route: '/expenses/new' }"
 * />
 *
 * Usage - With entity selector:
 * <UnifiedFilterBar
 *   v-model:date-range="dateRange"
 *   v-model:entity-id="selectedCategoryId"
 *   :entities="{ items: categories, allLabel: 'Tüm Kategoriler', showSettings: true }"
 *   :primary-action="{ label: '+ Yeni Gider', route: '/expenses/new' }"
 *   @entity-settings="openCategoryModal"
 * />
 */

import { ref, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import type { DateRangeValue } from '@/types/filters'
import { SingleRowDateFilter } from '@/components/ui'
import { ICONS, type IconName } from '@/icons'

export interface EntityConfig {
  items: Array<{ id: string | number; label: string; icon?: string; count?: number }>
  allLabel?: string
  showSettings?: boolean
  showCount?: boolean
}

export interface ActionConfig {
  label: string
  icon?: IconName | string
  route?: string
  onClick?: () => void
}

const props = withDefaults(
  defineProps<{
    showDateFilter?: boolean
    dateRange?: DateRangeValue
    maxDate?: Date
    entities?: EntityConfig
    entityId?: string | number | null
    quickActions?: {
      search?: boolean
      export?: boolean
      refresh?: boolean
      print?: boolean
    }
    primaryAction?: ActionConfig
  }>(),
  {
    showDateFilter: true,
    quickActions: () => ({ search: false, export: false })
  }
)

const emit = defineEmits<{
  'update:dateRange': [value: DateRangeValue]
  'update:entityId': [value: string | number | null]
  'entity-settings': []
  search: []
  export: []
  refresh: []
  print: []
}>()

const router = useRouter()

// Local state for v-model
const localDateRange = ref<DateRangeValue>(
  props.dateRange || {
    mode: 'month',
    start: new Date().toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  }
)
const localEntityId = ref<string | number | null>(props.entityId || null)

// Watch for prop changes
watch(() => props.dateRange, (val) => {
  if (val) localDateRange.value = val
}, { deep: true })

watch(() => props.entityId, (val) => {
  localEntityId.value = val ?? null
})

// Emit changes when local state changes
watch(localDateRange, (val) => emit('update:dateRange', val), { deep: true })
watch(localEntityId, (val) => emit('update:entityId', val))

// Handle primary action click
function handlePrimaryAction() {
  if (props.primaryAction) {
    if (props.primaryAction.onClick) {
      props.primaryAction.onClick()
    } else if (props.primaryAction.route) {
      router.push(props.primaryAction.route)
    }
  }
}

// Get action icon or use default
const actionIcon = computed(() => {
  return props.primaryAction?.icon || ICONS.add
})
</script>

<template>
  <div class="unified-filter-bar">
    <!-- Left: Date Filter + Entity Selector -->
    <div class="filter-left">
      <SingleRowDateFilter
        v-if="showDateFilter"
        v-model="localDateRange"
        :max-date="maxDate"
      />
      <EntitySelector
        v-if="entities"
        v-model="localEntityId"
        :items="entities.items"
        :all-label="entities.allLabel"
        :show-settings="entities.showSettings"
        :show-count="entities.showCount"
        @settings="$emit('entity-settings')"
      />
    </div>

    <!-- Center: Quick Actions -->
    <QuickActions
      v-if="quickActions"
      :show-search="quickActions.search"
      :show-export="quickActions.export"
      :show-refresh="quickActions.refresh"
      :show-print="quickActions.print"
      @search="$emit('search')"
      @export="$emit('export')"
      @refresh="$emit('refresh')"
      @print="$emit('print')"
    />

    <!-- Spacer for centering quick actions -->
    <div class="filter-spacer"></div>

    <!-- Right: Primary Action -->
    <component
      :is="primaryAction?.route ? 'router-link' : 'button'"
      v-if="primaryAction"
      :to="primaryAction.route"
      @click="handlePrimaryAction"
      class="primary-action"
    >
      <span class="action-icon">{{ actionIcon }}</span>
      <span>{{ primaryAction.label }}</span>
    </component>
  </div>
</template>

<style scoped>
.unified-filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 8px 12px;
  min-height: 42px;
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.filter-spacer {
  flex: 1;
}

.primary-action {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #dc2626;
  color: white;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  white-space: nowrap;
  transition: background 0.15s;
  border: none;
  cursor: pointer;
}

.primary-action:hover {
  background: #b91c1c;
}

.primary-action:focus {
  outline: none;
  box-shadow: 0 0 0 2px #fca5a5;
}

.action-icon {
  font-size: 16px;
  line-height: 1;
}

/* Mobile responsive */
@media (max-width: 640px) {
  .unified-filter-bar {
    flex-wrap: wrap;
    min-height: auto;
  }

  .filter-left {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .filter-spacer {
    display: none;
  }

  .primary-action {
    width: 100%;
    justify-content: center;
  }
}
</style>
