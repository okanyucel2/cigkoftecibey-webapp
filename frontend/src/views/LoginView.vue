<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-100 text-gray-800">
    <div class="w-full max-w-md p-8 space-y-6 bg-white rounded-xl shadow-md border border-gray-200">
      <h1 class="text-2xl font-bold text-center">Login (Test)</h1>
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1">Email</label>
          <input
            v-model="email"
            type="email"
            required
            data-testid="input-email"
            class="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Password</label>
          <input
            v-model="password"
            type="password"
            required
            data-testid="input-password"
            class="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          />
        </div>
        <div v-if="error" data-testid="login-error-message" class="text-red-500 text-sm p-2 bg-red-50 rounded">
          {{ error }}
        </div>
        <button
          type="submit"
          :disabled="isLoading"
          data-testid="btn-login"
          class="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50"
        >
          {{ isLoading ? 'Logging in...' : 'Login' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@/services/api'
import { extractErrorMessage } from '@/types/errors' 

const email = ref('')
const password = ref('')
const error = ref('')
const isLoading = ref(false)
const router = useRouter()

async function handleLogin() {
  isLoading.value = true
  error.value = ''

  try {
          // Try both locations for robustness
          // Vite proxy handles /api -> localhost:8000/api
          const response = await authApi.login(email.value, password.value);
    localStorage.setItem('token', response.data.access_token)
    router.push('/')
  } catch (err: unknown) {
    console.error('Login failed:', err)
    error.value = extractErrorMessage(err, 'Giriş başarısız')
  } finally {
    isLoading.value = false
  }
}
</script>
