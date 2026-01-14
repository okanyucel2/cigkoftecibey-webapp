/**
 * useImportHub - Composable for Import Hub functionality
 *
 * TASK-bb5b30d3: Create Import Dashboard Vue component
 *
 * Features:
 * - Load import history with filters
 * - Detect pending imports
 * - Poll for status updates when imports are processing
 * - Undo imports
 *
 * Wisdom Applied:
 * - W7: Tenant isolation via branch_id (enforced by backend API)
 * - Optimistic upload pattern (immediate feedback)
 */
import { ref, computed, onUnmounted } from 'vue'
import { importHistoryApi } from '@/services/api'

export interface ImportHistoryRecord {
  id: number
  import_type: string
  import_date: string
  source_filename?: string
  status: 'pending' | 'completed' | 'failed' | 'undone'
  error_message?: string
  created_at: string
}

export interface ImportFilters {
  import_type: string
  start_date: string
  end_date: string
}

// Polling interval in milliseconds (5 seconds)
const POLL_INTERVAL = 5000

export function useImportHub() {
  // State
  const history = ref<ImportHistoryRecord[]>([])
  const loading = ref(false)
  const error = ref<Error | null>(null)
  const isPolling = ref(false)

  // Filters
  const filters = ref<ImportFilters>({
    import_type: '',
    start_date: '',
    end_date: ''
  })

  // Polling interval reference
  let pollInterval: ReturnType<typeof setInterval> | null = null

  // Computed: Check if any imports are pending
  const hasPendingImports = computed(() => {
    return history.value.some(h => h.status === 'pending')
  })

  // Load history from API
  async function loadHistory(): Promise<void> {
    loading.value = true
    error.value = null

    try {
      const params: Record<string, string> = {}
      if (filters.value.import_type) params.import_type = filters.value.import_type
      if (filters.value.start_date) params.start_date = filters.value.start_date
      if (filters.value.end_date) params.end_date = filters.value.end_date

      const response = await importHistoryApi.getAll(params)
      history.value = response.data
    } catch (e) {
      error.value = e instanceof Error ? e : new Error(String(e))
      console.error('Failed to load import history:', e)
    } finally {
      loading.value = false
    }
  }

  // Start polling for status updates
  function startPolling(): void {
    if (isPolling.value) return // Already polling

    isPolling.value = true

    pollInterval = setInterval(async () => {
      await loadHistory()

      // Stop polling if no more pending imports
      if (!hasPendingImports.value) {
        stopPolling()
      }
    }, POLL_INTERVAL)
  }

  // Stop polling
  function stopPolling(): void {
    if (pollInterval) {
      clearInterval(pollInterval)
      pollInterval = null
    }
    isPolling.value = false
  }

  // Undo an import
  async function undoImport(id: number): Promise<boolean> {
    try {
      await importHistoryApi.undo(id)
      await loadHistory() // Refresh after undo
      return true
    } catch (e) {
      error.value = e instanceof Error ? e : new Error(String(e))
      console.error('Failed to undo import:', e)
      return false
    }
  }

  // Cleanup on unmount
  onUnmounted(() => {
    stopPolling()
  })

  return {
    // State
    history,
    loading,
    error,
    filters,
    isPolling,

    // Computed
    hasPendingImports,

    // Actions
    loadHistory,
    startPolling,
    stopPolling,
    undoImport
  }
}
