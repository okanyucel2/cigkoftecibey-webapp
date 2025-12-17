<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { invitationCodesApi, branchesApi } from '@/services/api'
import type { InvitationCode, Branch } from '@/types'

const codes = ref<InvitationCode[]>([])
const branches = ref<Branch[]>([])
const loading = ref(true)
const error = ref('')

// New code modal
const showModal = ref(false)
const modalLoading = ref(false)
const newCode = ref({
  role: 'cashier',
  max_uses: 1,
  branch_id: null as number | null,
  expires_at: ''
})

const roleOptions = [
  { value: 'owner', label: 'Sahip' },
  { value: 'manager', label: 'Yonetici' },
  { value: 'cashier', label: 'Kasiyer' }
]

const roleNames: Record<string, string> = {
  owner: 'Sahip',
  manager: 'Yonetici',
  cashier: 'Kasiyer'
}

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const [codesRes, branchesRes] = await Promise.all([
      invitationCodesApi.getAll(),
      branchesApi.getAll()
    ])
    codes.value = codesRes.data
    branches.value = branchesRes.data
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Veri yuklenemedi'
  } finally {
    loading.value = false
  }
}

onMounted(loadData)

function openModal() {
  newCode.value = {
    role: 'cashier',
    max_uses: 1,
    branch_id: null,
    expires_at: ''
  }
  showModal.value = true
}

async function createCode() {
  modalLoading.value = true
  error.value = ''
  try {
    const data: any = {
      role: newCode.value.role,
      max_uses: newCode.value.max_uses
    }
    if (newCode.value.branch_id) {
      data.branch_id = newCode.value.branch_id
    }
    if (newCode.value.expires_at) {
      data.expires_at = new Date(newCode.value.expires_at).toISOString()
    }

    await invitationCodesApi.create(data)
    showModal.value = false
    await loadData()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Kod olusturulamadi'
  } finally {
    modalLoading.value = false
  }
}

async function deactivateCode(code: InvitationCode) {
  if (!confirm(`${code.code} kodunu devre disi birakmak istiyor musunuz?`)) {
    return
  }

  try {
    await invitationCodesApi.delete(code.id)
    await loadData()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Kod devre disi birakilamadi'
  }
}

function copyCode(code: string) {
  navigator.clipboard.writeText(code)
}

function formatDate(dateStr: string | null) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('tr-TR')
}

const activeCodes = computed(() => codes.value.filter(c => c.is_valid))
const inactiveCodes = computed(() => codes.value.filter(c => !c.is_valid))
</script>

<template>
  <div class="max-w-6xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-display font-bold text-gray-900">Davet Kodlari</h1>
      <button @click="openModal" class="btn btn-primary">
        + Yeni Kod
      </button>
    </div>

    <!-- Error -->
    <div v-if="error" class="bg-red-100 text-red-700 p-4 rounded-lg mb-4">
      {{ error }}
      <button @click="error = ''" class="ml-2 font-bold">x</button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-8 text-gray-500">
      Yukleniyor...
    </div>

    <!-- Active Codes -->
    <div v-else>
      <div class="bg-white rounded-lg shadow mb-6">
        <div class="p-4 border-b">
          <h2 class="font-semibold text-gray-900">Aktif Kodlar ({{ activeCodes.length }})</h2>
        </div>

        <div v-if="activeCodes.length === 0" class="p-8 text-center text-gray-500">
          Henuz aktif davet kodu yok
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Kod</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rol</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sube</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Kullanim</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Son Kullanma</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Islemler</th>
              </tr>
            </thead>
            <tbody class="divide-y">
              <tr v-for="code in activeCodes" :key="code.id" class="hover:bg-gray-50">
                <td class="px-4 py-3">
                  <div class="flex items-center">
                    <code class="font-mono text-lg font-bold text-gray-900">{{ code.code }}</code>
                    <button
                      @click="copyCode(code.code)"
                      class="ml-2 p-1 text-gray-400 hover:text-gray-600"
                      title="Kopyala"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </button>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <span class="px-2 py-1 text-xs font-medium rounded-full"
                    :class="{
                      'bg-purple-100 text-purple-700': code.role === 'owner',
                      'bg-blue-100 text-blue-700': code.role === 'manager',
                      'bg-gray-100 text-gray-700': code.role === 'cashier'
                    }">
                    {{ roleNames[code.role] || code.role }}
                  </span>
                </td>
                <td class="px-4 py-3 text-sm text-gray-600">
                  {{ code.branch?.name || 'Tum Subeler' }}
                </td>
                <td class="px-4 py-3 text-sm">
                  <span :class="code.used_count >= code.max_uses ? 'text-red-600' : 'text-gray-600'">
                    {{ code.used_count }} / {{ code.max_uses }}
                  </span>
                </td>
                <td class="px-4 py-3 text-sm text-gray-600">
                  {{ formatDate(code.expires_at) }}
                </td>
                <td class="px-4 py-3">
                  <button
                    @click="deactivateCode(code)"
                    class="text-red-600 hover:text-red-800 text-sm"
                  >
                    Devre Disi Birak
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Inactive Codes -->
      <div v-if="inactiveCodes.length > 0" class="bg-white rounded-lg shadow">
        <div class="p-4 border-b">
          <h2 class="font-semibold text-gray-500">Gecersiz Kodlar ({{ inactiveCodes.length }})</h2>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Kod</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rol</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Kullanim</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Durum</th>
              </tr>
            </thead>
            <tbody class="divide-y">
              <tr v-for="code in inactiveCodes" :key="code.id" class="bg-gray-50 opacity-60">
                <td class="px-4 py-3">
                  <code class="font-mono text-gray-500">{{ code.code }}</code>
                </td>
                <td class="px-4 py-3 text-sm text-gray-500">
                  {{ roleNames[code.role] || code.role }}
                </td>
                <td class="px-4 py-3 text-sm text-gray-500">
                  {{ code.used_count }} / {{ code.max_uses }}
                </td>
                <td class="px-4 py-3 text-sm text-gray-500">
                  <span v-if="!code.is_active">Devre Disi</span>
                  <span v-else-if="code.used_count >= code.max_uses">Limit Doldu</span>
                  <span v-else>Suresi Doldu</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- New Code Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex min-h-full items-center justify-center p-4">
        <div class="fixed inset-0 bg-black/50" @click="showModal = false"></div>
        <div class="relative bg-white rounded-lg shadow-xl w-full max-w-md p-6">
          <h3 class="text-lg font-semibold mb-4">Yeni Davet Kodu</h3>

          <form @submit.prevent="createCode" class="space-y-4">
            <!-- Role -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Rol *</label>
              <select v-model="newCode.role" class="w-full border rounded-lg px-3 py-2">
                <option v-for="opt in roleOptions" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                </option>
              </select>
            </div>

            <!-- Branch -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Sube</label>
              <select v-model="newCode.branch_id" class="w-full border rounded-lg px-3 py-2">
                <option :value="null">Tum Subeler</option>
                <option v-for="branch in branches" :key="branch.id" :value="branch.id">
                  {{ branch.name }}
                </option>
              </select>
              <p class="text-xs text-gray-500 mt-1">Bos birakirsaniz tum subelere erisim verilir</p>
            </div>

            <!-- Max Uses -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Maksimum Kullanim</label>
              <input
                v-model.number="newCode.max_uses"
                type="number"
                min="1"
                class="w-full border rounded-lg px-3 py-2"
              />
            </div>

            <!-- Expires At -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Son Kullanma Tarihi</label>
              <input
                v-model="newCode.expires_at"
                type="date"
                class="w-full border rounded-lg px-3 py-2"
              />
              <p class="text-xs text-gray-500 mt-1">Bos birakirsaniz sure siniri olmaz</p>
            </div>

            <!-- Actions -->
            <div class="flex justify-end gap-3 mt-6">
              <button
                type="button"
                @click="showModal = false"
                class="px-4 py-2 border rounded-lg text-gray-700 hover:bg-gray-100"
              >
                Iptal
              </button>
              <button
                type="submit"
                :disabled="modalLoading"
                class="px-4 py-2 bg-brand-red text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
              >
                {{ modalLoading ? 'Olusturuluyor...' : 'Olustur' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>
