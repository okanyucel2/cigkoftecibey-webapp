<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authApi, invitationCodesApi } from '@/services/api'
import type { InvitationCodeValidation } from '@/types'

const router = useRouter()
const authStore = useAuthStore()

const code = ref('')
const loading = ref(false)
const validating = ref(false)
const error = ref('')
const validation = ref<InvitationCodeValidation | null>(null)

// Auto-validate code when 8 characters entered
const codeFormatted = computed(() => code.value.toUpperCase().replace(/[^A-Z0-9]/g, ''))

watch(codeFormatted, async (newCode) => {
  if (newCode.length === 8) {
    await validateCode()
  } else {
    validation.value = null
  }
})

async function validateCode() {
  if (codeFormatted.value.length !== 8) return

  validating.value = true
  error.value = ''

  try {
    const { data } = await invitationCodesApi.validate(codeFormatted.value)
    validation.value = data
    if (!data.valid) {
      error.value = data.message
    }
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Kod dogrulanamadi'
    validation.value = null
  } finally {
    validating.value = false
  }
}

async function handleSubmit() {
  if (!validation.value?.valid) {
    error.value = 'Lutfen gecerli bir davet kodu girin'
    return
  }

  const googleCredential = sessionStorage.getItem('google_credential')
  if (!googleCredential) {
    error.value = 'Google kimlik bilgisi bulunamadi. Lutfen tekrar giris yapin.'
    router.push('/login')
    return
  }

  loading.value = true
  error.value = ''

  try {
    const { data } = await authApi.registerWithCode(codeFormatted.value, googleCredential)
    localStorage.setItem('token', data.access_token)
    sessionStorage.removeItem('google_credential')
    await authStore.fetchUser()
    router.push('/')
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Kayit tamamlanamadi'
  } finally {
    loading.value = false
  }
}

function handleLogout() {
  localStorage.removeItem('token')
  sessionStorage.removeItem('google_credential')
  router.push('/login')
}

const roleNames: Record<string, string> = {
  owner: 'Sahip',
  manager: 'Yonetici',
  cashier: 'Kasiyer'
}
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
          Hos Geldiniz!
        </h1>
        <p class="text-gray-600 mt-2">
          Sisteme erisim icin davet kodunuzu girin
        </p>
      </div>

      <!-- Onboarding Form -->
      <div class="card">
        <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
          {{ error }}
        </div>

        <form @submit.prevent="handleSubmit">
          <div class="space-y-4">
            <!-- Code Input -->
            <div>
              <label for="code" class="block text-sm font-medium text-gray-700 mb-1">
                Davet Kodu
              </label>
              <input
                id="code"
                v-model="code"
                type="text"
                maxlength="8"
                required
                class="input text-center text-2xl tracking-widest font-mono uppercase"
                placeholder="XXXXXXXX"
                :disabled="loading"
              />
              <p class="text-xs text-gray-500 mt-1">8 karakterli davet kodunuzu girin</p>
            </div>

            <!-- Validation Status -->
            <div v-if="validating" class="text-center text-sm text-gray-500">
              Kod dogrulaniyor...
            </div>

            <!-- Validation Success -->
            <div v-if="validation?.valid" class="p-4 bg-green-50 border border-green-200 rounded-lg">
              <div class="flex items-center text-green-700 mb-2">
                <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                <span class="font-medium">Kod Gecerli</span>
              </div>
              <div class="text-sm text-green-600 space-y-1">
                <p v-if="validation.organization_name">
                  <span class="font-medium">Organizasyon:</span> {{ validation.organization_name }}
                </p>
                <p v-if="validation.branch_name">
                  <span class="font-medium">Sube:</span> {{ validation.branch_name }}
                </p>
                <p v-else>
                  <span class="font-medium">Sube:</span> Tum subeler
                </p>
                <p v-if="validation.role">
                  <span class="font-medium">Rol:</span> {{ roleNames[validation.role] || validation.role }}
                </p>
              </div>
            </div>

            <button
              type="submit"
              :disabled="loading || !validation?.valid"
              class="w-full btn btn-primary h-11"
            >
              <span v-if="loading">Kaydediliyor...</span>
              <span v-else>Devam Et</span>
            </button>
          </div>
        </form>

        <!-- Logout option -->
        <div class="mt-6 pt-4 border-t">
          <button
            @click="handleLogout"
            class="w-full text-sm text-gray-500 hover:text-gray-700"
          >
            Farkli bir hesapla giris yap
          </button>
        </div>
      </div>

      <!-- Help Text -->
      <div class="mt-4 text-center text-sm text-gray-500">
        <p>Davet kodunuz yok mu?</p>
        <p>Restoran yoneticinizden talep edin.</p>
      </div>
    </div>
  </div>
</template>
