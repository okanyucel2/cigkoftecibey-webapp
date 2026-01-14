<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/services/api'
import { extractErrorMessage } from '@/types'

declare global {
  interface Window {
    google: {
      accounts: {
        id: {
          initialize: (config: {
            client_id: string
            callback: (response: { credential: string }) => void
            auto_select?: boolean
          }) => void
          renderButton: (element: HTMLElement | null, options: {
            theme?: string
            size?: string
            width?: number
            text?: string
          }) => void
        }
      }
    }
  }
}

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref('')
const googleLoading = ref(false)

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || ''

async function handleLogin() {
  error.value = ''
  const success = await authStore.login(email.value, password.value)
  if (success) {
    router.push('/')
  } else {
    error.value = 'Email veya sifre hatali'
  }
}

async function handleGoogleCallback(response: { credential: string }) {
  googleLoading.value = true
  error.value = ''

  try {
    const { data } = await authApi.googleLogin(response.credential)

    // Store the credential for potential onboarding use
    sessionStorage.setItem('google_credential', response.credential)

    if (data.requires_onboarding) {
      // User needs to enter invitation code
      localStorage.setItem('token', data.access_token)
      router.push('/onboarding')
    } else {
      // Full login successful
      localStorage.setItem('token', data.access_token)
      await authStore.fetchUser()
      router.push('/')
    }
  } catch (e: unknown) {
    error.value = extractErrorMessage(e, 'Google giris basarisiz')
  } finally {
    googleLoading.value = false
  }
}

onMounted(() => {
  if (GOOGLE_CLIENT_ID && window.google) {
    window.google.accounts.id.initialize({
      client_id: GOOGLE_CLIENT_ID,
      callback: handleGoogleCallback
    })

    window.google.accounts.id.renderButton(
      document.getElementById('google-signin-btn'),
      {
        theme: 'outline',
        size: 'large',
        width: 320,
        text: 'signin_with'
      }
    )
  }
})
</script>

<template>
  <div class="min-h-screen bg-brand-warm flex items-center justify-center px-4">
    <div class="max-w-md w-full">
      <!-- Logo / Title -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-brand-red rounded-full mb-4">
          <span class="text-2xl">🥙</span>
        </div>
        <h1 class="text-2xl font-display font-bold text-brand-dark">
          Cig Kofte Yonetim
        </h1>
        <p class="text-gray-600 mt-2">Hesabiniza giris yapin</p>
      </div>

      <!-- Login Form -->
      <div class="card">
        <div v-if="error" data-testid="login-error-message"
          class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
          {{ error }}
        </div>

        <!-- Google Sign In Button -->
        <div v-if="GOOGLE_CLIENT_ID" class="mb-6">
          <div id="google-signin-btn" class="flex justify-center"></div>
          <div v-if="googleLoading" class="mt-2 text-center text-sm text-gray-500">
            Google ile giris yapiliyor...
          </div>
        </div>

        <!-- Divider -->
        <div v-if="GOOGLE_CLIENT_ID" class="relative mb-6">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-gray-300"></div>
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-2 bg-white text-gray-500">veya</span>
          </div>
        </div>

        <!-- Email/Password Form -->
        <form @submit.prevent="handleLogin">
          <div class="space-y-4">
            <div>
              <label for="email" class="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input id="email" v-model="email" type="email" required class="input" placeholder="ornek@email.com" data-testid="input-email" />
            </div>

            <div>
              <label for="password" class="block text-sm font-medium text-gray-700 mb-1">
                Sifre
              </label>
              <input id="password" v-model="password" type="password" required class="input" placeholder="••••••••" data-testid="input-password" />
            </div>

            <button type="submit" :disabled="authStore.loading" class="w-full btn btn-primary h-11" data-testid="btn-login">
              <span v-if="authStore.loading">Giris yapiliyor...</span>
              <span v-else>Giris Yap</span>
            </button>
          </div>
        </form>
      </div>

      <!-- Demo Credentials -->
      <div class="mt-4 text-center text-sm text-gray-500">
        <p>Demo: admin@cigkofte.com / admin123</p>
      </div>
    </div>
  </div>
</template>
