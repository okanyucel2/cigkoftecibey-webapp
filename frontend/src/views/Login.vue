<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
    <!-- Background decoration -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute top-20 left-10 w-72 h-72 bg-primary/10 rounded-full blur-3xl"></div>
      <div class="absolute bottom-20 right-10 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl"></div>
    </div>

    <!-- Login card -->
    <div class="relative w-full max-w-md">
      <div class="bg-card border border-border rounded-lg shadow-2xl p-8 sm:p-10">
        <!-- Logo/Title -->
        <div class="text-center mb-8">
          <h1 class="text-3xl font-bold text-foreground mb-2">Çiğ Köfte</h1>
          <p class="text-muted-foreground">Yönetim Sistemi</p>
        </div>

        <!-- Session Error Alert -->
        <div v-if="sessionError" class="mb-6 p-4 bg-destructive/10 border border-destructive/30 rounded-md">
          <p class="text-sm text-destructive">{{ sessionError }}</p>
        </div>

        <!-- Login Form -->
        <form @submit.prevent="handleLogin" class="space-y-6">
          <!-- Email Input -->
          <div>
            <label for="email" class="block text-sm font-medium text-foreground mb-2">
              E-posta
            </label>
            <input
              id="email"
              v-model="formData.email"
              type="email"
              placeholder="ornek@cigkofte.com"
              required
              :disabled="loading"
              class="w-full px-4 py-2 bg-background border border-border rounded-lg text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
            />
          </div>

          <!-- Password Input -->
          <div>
            <label for="password" class="block text-sm font-medium text-foreground mb-2">
              Şifre
            </label>
            <input
              id="password"
              v-model="formData.password"
              type="password"
              placeholder="••••••••"
              required
              :disabled="loading"
              class="w-full px-4 py-2 bg-background border border-border rounded-lg text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
            />
          </div>

          <!-- Login Error -->
          <div v-if="error" class="p-4 bg-destructive/10 border border-destructive/30 rounded-lg">
            <p class="text-sm text-destructive">{{ error }}</p>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full px-4 py-2.5 bg-primary text-primary-foreground font-medium rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            <span v-if="!loading">Giriş Yap</span>
            <span v-else class="flex items-center gap-2">
              <svg class="w-4 h-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Giriş yapılıyor...
            </span>
          </button>
        </form>

        <!-- Test User Info -->
        <div v-if="!isProduction" class="mt-8 pt-6 border-t border-border">
          <p class="text-xs text-muted-foreground mb-3">🧪 Test Kullanıcısı:</p>
          <div class="bg-muted/30 p-3 rounded text-xs font-mono space-y-1">
            <p><span class="text-muted-foreground">E-posta:</span> admin@cigkofte.com</p>
            <p><span class="text-muted-foreground">Şifre:</span> admin123</p>
          </div>
        </div>

        <!-- Footer -->
        <div class="mt-8 text-center text-xs text-muted-foreground">
          <p>Çiğ Köfte Yönetim Sistemi v1.0</p>
          <p class="mt-1">{{ new Date().getFullYear() }} © Tüm hakları saklıdır.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// Form state
const formData = ref({
  email: '',
  password: ''
})
const loading = ref(false)
const error = ref<string | null>(null)
const sessionError = ref<string | null>(null)

// Computed
const isProduction = computed(() => {
  return import.meta.env.PROD
})

// Methods
async function handleLogin() {
  error.value = null
  loading.value = true

  try {
    const success = await authStore.login(formData.value.email, formData.value.password)

    if (success) {
      // Redirect to intended page or home
      const redirect = route.query.redirect as string
      await router.push(redirect || '/')
    } else {
      error.value = 'Giriş başarısız. Email veya şifre hatalı.'
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || 'Giriş sırasında bir hata oluştu'
    console.error('Login error:', err)
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  // If already authenticated, redirect to home
  if (authStore.isAuthenticated) {
    router.push('/')
  }

  // Check if coming from a session expiry
  if (route.query.expired === 'true') {
    sessionError.value = 'Oturumunuz sona erdi. Lütfen yeniden giriş yapın.'
  }
})
</script>

<style scoped>
/* Smooth animations */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

:deep(.bg-card) {
  animation: fadeIn 0.3s ease-out;
}
</style>
