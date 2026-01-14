import { h, render, type VNode } from 'vue'
import UndoToast from '@/components/ui/UndoToast.vue'

export interface UndoToastOptions {
  message: string
  duration?: number
}

export interface UndoToastResult {
  undone: boolean
}

// Singleton container for the toast
let toastContainer: HTMLDivElement | null = null
let toastVNode: VNode | null = null
let currentResolve: ((result: UndoToastResult) => void) | null = null

function ensureContainer() {
  if (!toastContainer) {
    toastContainer = document.createElement('div')
    toastContainer.id = 'undo-toast-container'
    document.body.appendChild(toastContainer)
  }
  return toastContainer
}

export function useUndoToast() {
  /**
   * Show an undo toast with a countdown.
   * Returns a promise that resolves when:
   * - User clicks "Geri Al" (undone: true)
   * - Timer expires (undone: false)
   */
  async function showUndoToast(
    options: UndoToastOptions | string
  ): Promise<UndoToastResult> {
    const opts = typeof options === 'string'
      ? { message: options, duration: 7000 }
      : { duration: 7000, ...options }

    return new Promise((resolve) => {
      // Store the resolve function
      currentResolve = resolve

      const container = ensureContainer()

      // Create the toast component
      const vnode = h(UndoToast, {
        message: opts.message,
        duration: opts.duration,
        onUndo: () => {
          resolve({ undone: true })
          cleanup()
        },
        onTimeout: () => {
          resolve({ undone: false })
          cleanup()
        }
      })

      // Render and show
      render(vnode, container)
      toastVNode = vnode

      // Access the component instance and call show
      // We need to wait for next tick for the component to be mounted
      setTimeout(() => {
        const instance = vnode.component
        if (instance?.exposed?.show) {
          instance.exposed.show()
        }
      }, 0)
    })
  }

  function cleanup() {
    if (toastContainer && toastVNode) {
      const instance = toastVNode.component
      if (instance?.exposed?.hide) {
        instance.exposed.hide()
      }
      // Wait for transition, then unmount
      setTimeout(() => {
        if (toastContainer) {
          render(null, toastContainer)
        }
        toastVNode = null
        currentResolve = null
      }, 200)
    }
  }

  /**
   * Cancel any pending undo toast
   */
  function cancel() {
    if (currentResolve) {
      currentResolve({ undone: false })
      cleanup()
    }
  }

  return {
    showUndoToast,
    cancel
  }
}
