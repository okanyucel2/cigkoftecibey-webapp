import { ref } from 'vue'
import { useToast } from '@/composables/useToast'
import { useUndoToast } from '@/composables/useUndoToast'

export interface SaveOptions<T, R = T> {
  // Optimistic update function - called immediately before API call
  onOptimisticUpdate?: (data: T) => void
  // Rollback function - called on API failure
  onRollback?: (data: T, error: Error) => void
  // Success callback - called after API succeeds, receives API response
  onSuccess?: (response: R, data: T) => void
  // Custom success message
  successMessage?: string
  // Custom error message
  errorMessage?: string
}

export interface SaveResult<R> {
  success: boolean
  data?: R
  error?: Error
}

export function useOptimisticSave() {
  const toast = useToast()
  const { showUndoToast } = useUndoToast()
  const saving = ref(false)
  const error = ref<Error | null>(null)

  async function save<T, R = T>(
    apiCall: (data: T) => Promise<R>,
    data: T,
    options: SaveOptions<T, R> = {}
  ): Promise<SaveResult<R>> {
    const {
      onOptimisticUpdate,
      onRollback,
      onSuccess,
      successMessage = 'Kaydedildi',
      errorMessage = 'Kaydetme hatasi'
    } = options

    saving.value = true
    error.value = null

    // Step 1: Optimistic update (immediate UI feedback)
    if (onOptimisticUpdate) {
      try {
        onOptimisticUpdate(data)
      } catch (e) {
        console.error('Optimistic update failed:', e)
      }
    }

    // Step 2: Show immediate success toast (optimistic)
    toast.success(successMessage)

    try {
      // Step 3: Make API call in background
      const response = await apiCall(data)

      // Step 4: Call success callback with API response
      if (onSuccess) {
        onSuccess(response, data)
      }

      return { success: true, data: response }
    } catch (e) {
      const err = e instanceof Error ? e : new Error(String(e))
      error.value = err

      // Step 5: On failure, rollback and show error
      if (onRollback) {
        try {
          onRollback(data, err)
        } catch (rollbackError) {
          console.error('Rollback failed:', rollbackError)
        }
      }

      // Show error toast (replaces the optimistic success toast)
      toast.error(errorMessage)

      return { success: false, error: err }
    } finally {
      saving.value = false
    }
  }

  /**
   * Save with Undo Toast (7 second window)
   * Shows undo toast, waits for user decision, then calls API if not undone.
   * For CREATE operations only (not updates/deletes).
   */
  async function saveWithUndo<T, R = T>(
    apiCall: (data: T) => Promise<R>,
    data: T,
    options: SaveOptions<T, R> = {}
  ): Promise<SaveResult<R>> {
    const {
      onOptimisticUpdate,
      onRollback,
      onSuccess,
      successMessage = 'Kaydedildi',
      errorMessage = 'Kaydetme hatasi'
    } = options

    saving.value = true
    error.value = null

    // Step 1: Optimistic update (immediate UI feedback)
    if (onOptimisticUpdate) {
      try {
        onOptimisticUpdate(data)
      } catch (e) {
        console.error('Optimistic update failed:', e)
      }
    }

    // Step 2: Show Undo Toast with 7 second countdown
    const { undone } = await showUndoToast({
      message: successMessage,
      duration: 7000
    })

    // Step 3: If user clicked Undo, rollback and return
    if (undone) {
      if (onRollback) {
        try {
          onRollback(data, new Error('Kullanici geri aldi'))
        } catch (rollbackError) {
          console.error('Rollback failed:', rollbackError)
        }
      }
      saving.value = false
      return { success: false, error: new Error('Geri alindi') }
    }

    // Step 4: Timer expired, make API call
    try {
      const response = await apiCall(data)

      if (onSuccess) {
        onSuccess(response, data)
      }

      return { success: true, data: response }
    } catch (e) {
      const err = e instanceof Error ? e : new Error(String(e))
      error.value = err

      // On failure, rollback
      if (onRollback) {
        try {
          onRollback(data, err)
        } catch (rollbackError) {
          console.error('Rollback failed:', rollbackError)
        }
      }

      toast.error(errorMessage)
      return { success: false, error: err }
    } finally {
      saving.value = false
    }
  }

  // Simplified version for fire-and-forget saves (no rollback needed)
  async function quickSave<T, R = T>(
    apiCall: (data: T) => Promise<R>,
    data: T,
    successMessage = 'Kaydedildi'
  ): Promise<SaveResult<R>> {
    return save(apiCall, data, { successMessage })
  }

  // Batch save multiple items
  async function batchSave<T, R = T>(
    apiCall: (data: T) => Promise<R>,
    items: T[],
    options: SaveOptions<T, R> = {}
  ): Promise<SaveResult<R>[]> {
    saving.value = true
    const results: SaveResult<R>[] = []

    for (const item of items) {
      const result = await save(apiCall, item, {
        ...options,
        // Don't show individual toasts for batch operations
        successMessage: undefined,
        errorMessage: undefined
      })
      results.push(result)
    }

    // Show summary toast
    const successCount = results.filter(r => r.success).length
    const failCount = results.length - successCount

    if (failCount === 0) {
      toast.success(`${successCount} kayit basariyla kaydedildi`)
    } else if (successCount === 0) {
      toast.error(`${failCount} kayit kaydedilemedi`)
    } else {
      toast.warning(`${successCount} basarili, ${failCount} hatali`)
    }

    saving.value = false
    return results
  }

  return {
    saving,
    error,
    save,
    saveWithUndo,
    quickSave,
    batchSave
  }
}
