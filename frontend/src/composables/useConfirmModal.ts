import { ref } from 'vue'

export interface ConfirmOptions {
  message: string
  title?: string
  confirmText?: string
  cancelText?: string
  variant?: 'danger' | 'warning' | 'info'
}

/**
 * Composable for confirmation modal management
 * Provides a clean API for showing confirm dialogs
 */
export function useConfirmModal() {
  const isOpen = ref(false)
  const message = ref('')
  const title = ref('')
  const confirmText = ref('Onayla')
  const cancelText = ref('Iptal')
  const variant = ref<'danger' | 'warning' | 'info'>('danger')
  const pendingAction = ref<(() => Promise<void>) | null>(null)
  const isProcessing = ref(false)

  /**
   * Open confirm dialog with a message and action
   */
  function confirm(
    options: string | ConfirmOptions,
    action: () => Promise<void>
  ): void {
    if (typeof options === 'string') {
      message.value = options
      title.value = ''
      confirmText.value = 'Onayla'
      cancelText.value = 'Iptal'
      variant.value = 'danger'
    } else {
      message.value = options.message
      title.value = options.title || ''
      confirmText.value = options.confirmText || 'Onayla'
      cancelText.value = options.cancelText || 'Iptal'
      variant.value = options.variant || 'danger'
    }

    pendingAction.value = action
    isOpen.value = true
  }

  /**
   * Handle confirm button click
   */
  async function handleConfirm(): Promise<void> {
    if (!pendingAction.value) return

    isProcessing.value = true
    try {
      await pendingAction.value()
    } finally {
      isProcessing.value = false
      close()
    }
  }

  /**
   * Handle cancel button click
   */
  function handleCancel(): void {
    close()
  }

  /**
   * Close the modal and reset state
   */
  function close(): void {
    isOpen.value = false
    pendingAction.value = null
    // Reset after animation
    setTimeout(() => {
      message.value = ''
      title.value = ''
    }, 200)
  }

  return {
    // State
    isOpen,
    message,
    title,
    confirmText,
    cancelText,
    variant,
    isProcessing,

    // Actions
    confirm,
    handleConfirm,
    handleCancel,
    close
  }
}
