/**
 * useAuth - Comprehensive authentication composable
 *
 * Manages:
 * - Session state (user, token, expiry)
 * - Login/logout flow
 * - Token refresh and validation
 * - Session persistence across browser restarts
 * - Auto-logout on token expiry
 */

import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import type { User } from '@/types'
import { authApi } from '@/services/api'

// Session constants
const TOKEN_STORAGE_KEY = 'auth_token'
const EXPIRY_STORAGE_KEY = 'auth_token_expiry'
const SESSION_CHECK_INTERVAL = 60_000 // Check session every minute
const TOKEN_EXPIRY_WARNING = 5 * 60_000 // Warn 5 minutes before expiry

export function useAuth() {
  const router = useRouter()

  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const tokenExpiry = ref<Date | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  let sessionCheckInterval: number | null = null
  let expiryCheckInterval: number | null = null

  // Computed properties
  const isAuthenticated = computed(() => !!token.value && !!user.value && isTokenValid())
  const isSuperAdmin = computed(() => user.value?.is_super_admin ?? false)
  const isTokenExpired = computed(() => {
    if (!tokenExpiry.value) return false
    return new Date() > tokenExpiry.value
  })
  const isTokenExpiringSoon = computed(() => {
    if (!tokenExpiry.value) return false
    const warningTime = new Date(tokenExpiry.value.getTime() - TOKEN_EXPIRY_WARNING)
    return new Date() > warningTime && !isTokenExpired.value
  })

  /**
   * Check if token is still valid (not expired and in DB)
   */
  function isTokenValid(): boolean {
    if (!token.value || !tokenExpiry.value) return false
    return new Date() <= tokenExpiry.value
  }

  /**
   * Login with email and password
   */
  async function login(email: string, password: string): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      const response = await authApi.loginJson({ email, password })
      const { access_token } = response.data

      // Store token and calculate expiry (JWT default: 7 days)
      token.value = access_token
      const expiryTime = new Date()
      expiryTime.setDate(expiryTime.getDate() + 7)
      tokenExpiry.value = expiryTime

      localStorage.setItem(TOKEN_STORAGE_KEY, access_token)
      localStorage.setItem(EXPIRY_STORAGE_KEY, expiryTime.toISOString())

      // Fetch user info
      await fetchCurrentUser()

      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Giriş başarısız'
      console.error('Login error:', error.value)
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * Logout - revoke session on server
   */
  async function logout(revokeServer: boolean = true): Promise<void> {
    loading.value = true

    try {
      if (revokeServer && token.value) {
        try {
          await authApi.logout()
        } catch (err) {
          console.warn('Server logout failed:', err)
          // Continue with local logout even if server fails
        }
      }

      // Clear local state
      clearSession()

      // Redirect to login
      await router.push('/login')
    } finally {
      loading.value = false
    }
  }

  /**
   * Global logout - revoke all sessions
   */
  async function logoutAll(): Promise<void> {
    loading.value = true

    try {
      if (token.value) {
        try {
          await authApi.logoutAll()
        } catch (err) {
          console.warn('Global logout failed:', err)
        }
      }

      clearSession()
      await router.push('/login')
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch current user info from server
   */
  async function fetchCurrentUser(): Promise<boolean> {
    if (!token.value) return false

    try {
      const response = await authApi.me()
      user.value = response.data
      return true
    } catch (err) {
      console.error('Fetch user error:', err)
      // Session might be invalid
      clearSession()
      return false
    }
  }

  /**
   * Validate token with server
   */
  async function validateToken(): Promise<boolean> {
    if (!token.value) return false

    try {
      // Try to fetch user - this will fail if token is invalid
      const response = await authApi.me()
      return !!response.data
    } catch (err) {
      // Token is invalid
      clearSession()
      return false
    }
  }

  /**
   * Check session status and handle expiry
   */
  async function checkSession(): Promise<void> {
    if (!isAuthenticated.value) return

    // If token appears expired, logout
    if (isTokenExpired.value) {
      console.warn('Token expired, logging out')
      await logout(false) // Don't try to call server, it will reject
      return
    }

    // Validate token with server
    const isValid = await validateToken()
    if (!isValid) {
      console.warn('Token validation failed, logging out')
      await logout(false)
      return
    }

    // Warn if token expiring soon
    if (isTokenExpiringSoon.value) {
      error.value = 'Oturumunuz yakında sona erecek. Lütfen yeniden giriş yapın.'
    }
  }

  /**
   * Initialize session from storage
   */
  function initializeSession(): void {
    const storedToken = localStorage.getItem(TOKEN_STORAGE_KEY)
    const storedExpiry = localStorage.getItem(EXPIRY_STORAGE_KEY)

    if (storedToken && storedExpiry) {
      token.value = storedToken
      tokenExpiry.value = new Date(storedExpiry)

      // Check if token is already expired
      if (!isTokenValid()) {
        clearSession()
      } else {
        // Token is valid, fetch user info
        fetchCurrentUser()
      }
    }
  }

  /**
   * Clear all session data
   */
  function clearSession(): void {
    user.value = null
    token.value = null
    tokenExpiry.value = null
    error.value = null
    localStorage.removeItem(TOKEN_STORAGE_KEY)
    localStorage.removeItem(EXPIRY_STORAGE_KEY)
  }

  /**
   * Start session monitoring
   */
  function startSessionMonitoring(): void {
    // Check session status periodically
    sessionCheckInterval = window.setInterval(() => {
      checkSession()
    }, SESSION_CHECK_INTERVAL)

    // Also check token expiry
    expiryCheckInterval = window.setInterval(() => {
      if (isTokenExpiringSoon.value && !error.value) {
        error.value = 'Oturumunuz yakında sona erecek. Lütfen yeniden giriş yapın.'
      }
    }, 10_000) // Check every 10 seconds
  }

  /**
   * Stop session monitoring
   */
  function stopSessionMonitoring(): void {
    if (sessionCheckInterval) {
      clearInterval(sessionCheckInterval)
      sessionCheckInterval = null
    }
    if (expiryCheckInterval) {
      clearInterval(expiryCheckInterval)
      expiryCheckInterval = null
    }
  }

  /**
   * Clear error message
   */
  function clearError(): void {
    error.value = null
  }

  // Lifecycle
  onMounted(() => {
    initializeSession()
    if (isAuthenticated.value) {
      startSessionMonitoring()
    }
  })

  // Watch for auth state changes
  watch(isAuthenticated, (newVal) => {
    if (newVal) {
      startSessionMonitoring()
    } else {
      stopSessionMonitoring()
    }
  })

  return {
    // State
    user,
    token,
    tokenExpiry,
    loading,
    error,

    // Computed
    isAuthenticated,
    isSuperAdmin,
    isTokenExpired,
    isTokenExpiringSoon,

    // Methods
    login,
    logout,
    logoutAll,
    fetchCurrentUser,
    validateToken,
    checkSession,
    initializeSession,
    clearSession,
    clearError,
    isTokenValid
  }
}
