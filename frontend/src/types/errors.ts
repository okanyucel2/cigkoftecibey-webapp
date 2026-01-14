/**
 * Type-safe error handling utilities
 *
 * Replace `catch (e: any)` with `catch (e: unknown)` and use these helpers
 * to extract error messages safely.
 */

/**
 * Standard API error shape from Axios/backend responses
 */
export interface ApiErrorResponse {
  response?: {
    data?: {
      detail?: string
      message?: string
      error?: string
    }
    status?: number
    statusText?: string
  }
  message?: string
  code?: string
}

/**
 * Type guard to check if error has response property
 */
export function isApiError(error: unknown): error is ApiErrorResponse {
  return (
    typeof error === 'object' &&
    error !== null &&
    ('response' in error || 'message' in error)
  )
}

/**
 * Extract user-friendly error message from unknown error
 *
 * @param error - The caught error (unknown type)
 * @param fallback - Default message if extraction fails
 * @returns User-friendly error message in Turkish
 *
 * @example
 * ```typescript
 * try {
 *   await api.call()
 * } catch (e: unknown) {
 *   error.value = extractErrorMessage(e, 'Veri yüklenemedi')
 * }
 * ```
 */
export function extractErrorMessage(error: unknown, fallback = 'İşlem başarısız'): string {
  // Handle null/undefined
  if (error == null) {
    return fallback
  }

  // Handle ApiErrorResponse (Axios errors)
  if (isApiError(error)) {
    const data = error.response?.data
    if (data?.detail) return data.detail
    if (data?.message) return data.message
    if (data?.error) return data.error
    if (error.message) return error.message
  }

  // Handle standard Error objects
  if (error instanceof Error) {
    return error.message
  }

  // Handle string errors
  if (typeof error === 'string') {
    return error
  }

  return fallback
}

/**
 * Extract HTTP status code from error
 */
export function extractErrorStatus(error: unknown): number | undefined {
  if (isApiError(error)) {
    return error.response?.status
  }
  return undefined
}
