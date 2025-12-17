import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'
import { authApi } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const loading = ref(false)

  // Multi-branch state
  const currentBranchId = ref<number | null>(
    localStorage.getItem('currentBranchId')
      ? parseInt(localStorage.getItem('currentBranchId')!)
      : null
  )

  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isSuperAdmin = computed(() => user.value?.is_super_admin ?? false)
  const accessibleBranches = computed(() => user.value?.accessible_branches ?? [])
  const currentBranch = computed(() =>
    accessibleBranches.value.find(b => b.id === currentBranchId.value) ?? null
  )
  const hasMultipleBranches = computed(() => accessibleBranches.value.length > 1)

  async function login(email: string, password: string) {
    loading.value = true
    try {
      const { data } = await authApi.login(email, password)
      token.value = data.access_token
      localStorage.setItem('token', data.access_token)
      await fetchUser()
      return true
    } catch (error) {
      console.error('Login failed:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      const { data } = await authApi.me()
      user.value = data

      // Always use server's default branch (set via switch-branch API)
      currentBranchId.value = data.current_branch_id
      localStorage.setItem('currentBranchId', String(data.current_branch_id))
    } catch (error) {
      logout()
    }
  }

  async function switchBranch(branchId: number) {
    try {
      await authApi.switchBranch(branchId)
      currentBranchId.value = branchId
      localStorage.setItem('currentBranchId', String(branchId))
      // Refresh user data
      await fetchUser()
      return true
    } catch (error) {
      console.error('Switch branch failed:', error)
      return false
    }
  }

  function logout() {
    user.value = null
    token.value = null
    currentBranchId.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('currentBranchId')
  }

  // Initialize
  if (token.value) {
    fetchUser()
  }

  return {
    user,
    token,
    loading,
    currentBranchId,
    isAuthenticated,
    isSuperAdmin,
    accessibleBranches,
    currentBranch,
    hasMultipleBranches,
    login,
    fetchUser,
    switchBranch,
    logout
  }
})
