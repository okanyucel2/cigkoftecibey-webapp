<script setup lang="ts">
/**
 * InsightBanner - Dismissible banner for warnings, AI insights, and notifications
 *
 * Usage:
 * <InsightBanner
 *   :insight="warningInsight"
 *   @dismiss="clearWarning"
 * />
 *
 * const warningInsight = {
 *   type: 'warning',
 *   icon: '⚠️',
 *   title: '3 personelin bu hafta timesheet\'i eksik',
 *   detail: 'Ahmet, Mehmet, Ayşe',
 *   action: { label: 'Detay', onClick: () => showDetails() }
 * }
 */

import { ref, watch } from 'vue'

export interface InsightAction {
  label: string
  onClick: () => void
}

export interface Insight {
  type: 'info' | 'warning' | 'success' | 'error'
  icon?: string
  title: string
  detail?: string
  action?: InsightAction
}

const props = withDefaults(
  defineProps<{
    insight: Insight | null
    dismissible?: boolean
  }>(),
  {
    dismissible: true
  }
)

const emit = defineEmits<{
  dismiss: []
}>()

const show = ref(true)

// Reset show when insight changes
watch(() => props.insight, () => {
  show.value = true
})

function dismiss() {
  if (props.dismissible) {
    show.value = false
    emit('dismiss')
  }
}

// Default icons by type
const defaultIcons: Record<Insight['type'], string> = {
  info: 'ℹ️',
  warning: '⚠️',
  success: '✅',
  error: '❌'
}

function getIcon(insight: Insight): string {
  return insight.icon || defaultIcons[insight.type]
}
</script>

<template>
  <Transition name="slide">
    <div
      v-if="show && insight"
      :class="['insight-banner', `insight-${insight.type}`]"
      role="alert"
    >
      <span class="insight-icon">{{ getIcon(insight) }}</span>
      <div class="insight-content">
        <p class="insight-title">{{ insight.title }}</p>
        <p v-if="insight.detail" class="insight-detail">{{ insight.detail }}</p>
      </div>
      <button
        v-if="insight.action"
        @click="insight.action.onClick"
        class="insight-action"
        type="button"
      >
        {{ insight.action.label }}
      </button>
      <button
        v-if="dismissible"
        @click="dismiss"
        class="insight-dismiss"
        type="button"
        :aria-label="'Kapat'"
      >
        ✕
      </button>
    </div>
  </Transition>
</template>

<style scoped>
.insight-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 14px;
}

/* Type variants */
.insight-info {
  background: #eff6ff;
  color: #1e40af;
  border: 1px solid #bfdbfe;
}

.insight-warning {
  background: #fefce8;
  color: #a16207;
  border: 1px solid #fde047;
}

.insight-success {
  background: #f0fdf4;
  color: #166534;
  border: 1px solid #86efac;
}

.insight-error {
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fca5a5;
}

.insight-icon {
  font-size: 18px;
  line-height: 1;
  flex-shrink: 0;
}

.insight-content {
  flex: 1;
  min-width: 0;
}

.insight-title {
  font-weight: 500;
  margin: 0;
  line-height: 1.4;
}

.insight-detail {
  font-size: 13px;
  opacity: 0.9;
  margin: 2px 0 0 0;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.insight-action {
  background: white;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.15s;
  flex-shrink: 0;
}

.insight-action:hover {
  opacity: 0.9;
}

.insight-action:focus {
  outline: none;
  box-shadow: 0 0 0 2px currentColor;
}

.insight-dismiss {
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0.6;
  font-size: 16px;
  padding: 4px;
  margin-left: 4px;
  flex-shrink: 0;
  transition: opacity 0.15s;
}

.insight-dismiss:hover {
  opacity: 1;
}

.insight-dismiss:focus {
  outline: none;
  opacity: 1;
}

/* Slide transition */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.2s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
