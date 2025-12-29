<script setup lang="ts">
/**
 * QuickActions - Quick action buttons (search, export, etc.)
 *
 * Usage:
 * <QuickActions
 *   :show-search="true"
 *   :show-export="true"
 *   @search="openSearch"
 *   @export="exportData"
 * />
 */

withDefaults(
  defineProps<{
    showSearch?: boolean
    showExport?: boolean
    showRefresh?: boolean
    showPrint?: boolean
  }>(),
  {
    showSearch: false,
    showExport: false,
    showRefresh: false,
    showPrint: false
  }
)

defineEmits<{
  search: []
  export: []
  refresh: []
  print: []
}>()
</script>

<template>
  <div class="quick-actions">
    <button
      v-if="showSearch"
      @click="$emit('search')"
      class="action-btn"
      type="button"
      :title="'Ara'"
    >
      🔍
    </button>
    <button
      v-if="showRefresh"
      @click="$emit('refresh')"
      class="action-btn"
      type="button"
      :title="'Yenile'"
    >
      🔄
    </button>
    <button
      v-if="showExport"
      @click="$emit('export')"
      class="action-btn"
      type="button"
      :title="'Dışa Aktar'"
    >
      📤
    </button>
    <button
      v-if="showPrint"
      @click="$emit('print')"
      class="action-btn"
      type="button"
      :title="'Yazdır'"
    >
      🖨️
    </button>
  </div>
</template>

<style scoped>
.quick-actions {
  display: flex;
  gap: 4px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.15s;
}

.action-btn:hover {
  background: #f3f4f6;
}

.action-btn:focus {
  outline: none;
  box-shadow: 0 0 0 2px #dc2626;
}

.action-btn:active {
  transform: scale(0.95);
}
</style>
