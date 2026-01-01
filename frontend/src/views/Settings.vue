<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import type { Branch } from '@/types'
import { branchesApi, usersApi, type UserWithBranches } from '@/services/api'
import ConfirmModal from '@/components/ui/ConfirmModal.vue'

const authStore = useAuthStore()

// Redirect if not super admin
if (!authStore.isSuperAdmin) {
  window.location.href = '/'
}

const activeTab = ref<'branches' | 'users'>('branches')
const loading = ref(true)

// Branches
const branches = ref<Branch[]>([])

// Sorted branches (alphabetically)
const sortedBranches = computed(() => {
  return [...branches.value].sort((a, b) => a.name.localeCompare(b.name, 'tr'))
})

const showBranchModal = ref(false)
const editingBranch = ref<Branch | null>(null)
const branchForm = ref({
  name: '',
  code: '',
  city: '',
  address: '',
  phone: ''
})

// Users
const users = ref<UserWithBranches[]>([])
const showUserModal = ref(false)
const editingUser = ref<UserWithBranches | null>(null)
const userForm = ref({
  email: '',
  password: '',
  name: '',
  role: 'owner',
  branch_id: 0
})

// Branch assignment modal
const showAssignModal = ref(false)
const assigningUser = ref<UserWithBranches | null>(null)
const assignForm = ref({
  branch_id: 0,
  role: 'owner',
  is_default: false
})

const roles = [
  { value: 'owner', label: 'Sube Sahibi' },
  { value: 'manager', label: 'Mudur' },
  { value: 'cashier', label: 'Kasiyer' }
]

onMounted(async () => {
  await loadData()
})

async function loadData() {
  loading.value = true
  try {
    const [branchesRes, usersRes] = await Promise.all([
      branchesApi.getAll(),
      usersApi.getAll()
    ])
    branches.value = branchesRes.data
    users.value = usersRes.data
  } catch (error) {
    console.error('Failed to load data:', error)
  } finally {
    loading.value = false
  }
}

// Branch functions
function openBranchModal(branch?: Branch) {
  if (branch) {
    editingBranch.value = branch
    branchForm.value = {
      name: branch.name,
      code: branch.code,
      city: branch.city || '',
      address: branch.address || '',
      phone: branch.phone || ''
    }
  } else {
    editingBranch.value = null
    branchForm.value = { name: '', code: '', city: '', address: '', phone: '' }
  }
  showBranchModal.value = true
}

async function saveBranch() {
  try {
    if (editingBranch.value) {
      await branchesApi.update(editingBranch.value.id, branchForm.value)
    } else {
      await branchesApi.create(branchForm.value)
    }
    showBranchModal.value = false
    await loadData()
    // Refresh auth to update accessible branches
    await authStore.fetchUser()
  } catch (error: any) {
    alert(error.response?.data?.detail || 'Bir hata olustu')
  }
}

async function toggleBranchActive(branch: Branch) {
  try {
    if (branch.is_active) {
      await branchesApi.delete(branch.id)
    } else {
      await branchesApi.activate(branch.id)
    }
    await loadData()
    await authStore.fetchUser()
  } catch (error: any) {
    alert(error.response?.data?.detail || 'Bir hata olustu')
  }
}

// User functions
function openUserModal(user?: UserWithBranches) {
  if (user) {
    editingUser.value = user
    userForm.value = {
      email: user.email,
      password: '',
      name: user.name,
      role: user.role,
      branch_id: user.branch_id
    }
  } else {
    editingUser.value = null
    userForm.value = {
      email: '',
      password: '',
      name: '',
      role: 'owner',
      branch_id: branches.value[0]?.id || 0
    }
  }
  showUserModal.value = true
}

async function saveUser() {
  try {
    if (editingUser.value) {
      await usersApi.update(editingUser.value.id, {
        name: userForm.value.name,
        role: userForm.value.role
      })
    } else {
      if (!userForm.value.password) {
        alert('Sifre gerekli')
        return
      }
      await usersApi.create(userForm.value)
    }
    showUserModal.value = false
    await loadData()
  } catch (error: any) {
    alert(error.response?.data?.detail || 'Bir hata olustu')
  }
}

async function toggleUserActive(user: UserWithBranches) {
  try {
    await usersApi.update(user.id, { is_active: !user.is_active })
    await loadData()
  } catch (error: any) {
    alert(error.response?.data?.detail || 'Bir hata olustu')
  }
}

async function toggleUserSuperAdmin(user: UserWithBranches) {
  try {
    await usersApi.update(user.id, { is_super_admin: !user.is_super_admin })
    await loadData()
  } catch (error: any) {
    alert(error.response?.data?.detail || 'Bir hata olustu')
  }
}

// Branch assignment functions
function openAssignModal(user: UserWithBranches) {
  assigningUser.value = user
  const unassignedBranches = branches.value.filter(
    b => !user.branches.some(ub => ub.branch_id === b.id)
  )
  assignForm.value = {
    branch_id: unassignedBranches[0]?.id || 0,
    role: 'owner',
    is_default: false
  }
  showAssignModal.value = true
}

const availableBranchesForAssign = computed(() => {
  if (!assigningUser.value) return []
  return branches.value
    .filter(b => !assigningUser.value!.branches.some(ub => ub.branch_id === b.id))
    .sort((a, b) => a.name.localeCompare(b.name, 'tr'))
})

async function assignBranch() {
  if (!assigningUser.value) return
  try {
    await usersApi.assignToBranch(assigningUser.value.id, {
      user_id: assigningUser.value.id,
      branch_id: assignForm.value.branch_id,
      role: assignForm.value.role,
      is_default: assignForm.value.is_default
    })
    showAssignModal.value = false
    await loadData()
  } catch (error: any) {
    alert(error.response?.data?.detail || 'Bir hata olustu')
  }
}

// Confirm Modal
const showConfirm = ref(false)
const confirmMessage = ref('')
const confirmAction = ref<(() => Promise<void>) | null>(null)

function openConfirm(message: string, action: () => Promise<void>) {
  confirmMessage.value = message
  confirmAction.value = action
  showConfirm.value = true
}

async function handleConfirm() {
  if (confirmAction.value) {
    await confirmAction.value()
  }
  showConfirm.value = false
}

async function removeBranchAssignment(user: UserWithBranches, branchId: number) {
  openConfirm('Bu kullaniciyi subeden cikarmak istediginize emin misiniz?', async () => {
    try {
      await usersApi.removeFromBranch(user.id, branchId)
      // Optimistic
      user.branches = user.branches.filter(b => b.branch_id !== branchId)
      await loadData()
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Bir hata olustu')
    }
  })
}

function getRoleLabel(role: string) {
  return roles.find(r => r.value === role)?.label || role
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-display font-bold text-gray-800">Sistem Ayarlari</h1>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="flex gap-4">
        <button
          @click="activeTab = 'branches'"
          :class="[
            'py-3 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === 'branches'
              ? 'border-brand-red text-brand-red'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          Subeler
        </button>
        <button
          @click="activeTab = 'users'"
          :class="[
            'py-3 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === 'users'
              ? 'border-brand-red text-brand-red'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          Kullanicilar
        </button>
      </nav>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="text-gray-500">Yukleniyor...</div>
    </div>

    <!-- Branches Tab -->
    <div v-else-if="activeTab === 'branches'" class="space-y-4">
      <div class="flex justify-end">
        <button @click="openBranchModal()" class="btn btn-primary">
          + Yeni Sube
        </button>
      </div>

      <div class="card">
        <table class="w-full">
          <thead>
            <tr class="border-b">
              <th class="text-left py-3 px-4 font-medium text-gray-600">Sube Adi</th>
              <th class="text-left py-3 px-4 font-medium text-gray-600">Kod</th>
              <th class="text-left py-3 px-4 font-medium text-gray-600">Adres</th>
              <th class="text-left py-3 px-4 font-medium text-gray-600">Telefon</th>
              <th class="text-center py-3 px-4 font-medium text-gray-600">Durum</th>
              <th class="text-right py-3 px-4 font-medium text-gray-600">Islemler</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="branch in sortedBranches" :key="branch.id" class="border-b hover:bg-gray-50">
              <td class="py-3 px-4 font-medium">{{ branch.name }}</td>
              <td class="py-3 px-4 text-gray-600">{{ branch.code }}</td>
              <td class="py-3 px-4 text-gray-600">{{ branch.address || '-' }}</td>
              <td class="py-3 px-4 text-gray-600">{{ branch.phone || '-' }}</td>
              <td class="py-3 px-4 text-center">
                <span
                  :class="[
                    'px-2 py-1 rounded-full text-xs font-medium',
                    branch.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                  ]"
                >
                  {{ branch.is_active ? 'Aktif' : 'Pasif' }}
                </span>
              </td>
              <td class="py-3 px-4 text-right">
                <button
                  @click="openBranchModal(branch)"
                  class="text-blue-600 hover:text-blue-800 mr-3"
                >
                  Duzenle
                </button>
                <button
                  @click="toggleBranchActive(branch)"
                  :class="branch.is_active ? 'text-red-600 hover:text-red-800' : 'text-green-600 hover:text-green-800'"
                >
                  {{ branch.is_active ? 'Deaktif Et' : 'Aktif Et' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Users Tab -->
    <div v-else-if="activeTab === 'users'" class="space-y-4">
      <div class="flex justify-end">
        <button @click="openUserModal()" class="btn btn-primary">
          + Yeni Kullanici
        </button>
      </div>

      <div class="card">
        <table class="w-full">
          <thead>
            <tr class="border-b">
              <th class="text-left py-3 px-4 font-medium text-gray-600">Ad Soyad</th>
              <th class="text-left py-3 px-4 font-medium text-gray-600">Email</th>
              <th class="text-left py-3 px-4 font-medium text-gray-600">Rol</th>
              <th class="text-left py-3 px-4 font-medium text-gray-600">Subeler</th>
              <th class="text-center py-3 px-4 font-medium text-gray-600">Durum</th>
              <th class="text-right py-3 px-4 font-medium text-gray-600">Islemler</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id" class="border-b hover:bg-gray-50">
              <td class="py-3 px-4">
                <div class="flex items-center gap-2">
                  <span class="font-medium">{{ user.name }}</span>
                  <span v-if="user.is_super_admin" class="px-2 py-0.5 bg-purple-100 text-purple-700 rounded-full text-xs">
                    Super Admin
                  </span>
                </div>
              </td>
              <td class="py-3 px-4 text-gray-600">{{ user.email }}</td>
              <td class="py-3 px-4 text-gray-600">{{ getRoleLabel(user.role) }}</td>
              <td class="py-3 px-4">
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="ub in user.branches"
                    :key="ub.id"
                    class="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 rounded text-xs"
                  >
                    {{ ub.branch_name }}
                    <span v-if="ub.is_default" class="text-green-600">*</span>
                    <button
                      @click="removeBranchAssignment(user, ub.branch_id)"
                      class="text-red-500 hover:text-red-700 ml-1"
                      title="Subeden Cikar"
                    >
                      x
                    </button>
                  </span>
                  <button
                    @click="openAssignModal(user)"
                    class="px-2 py-1 bg-blue-50 text-blue-600 rounded text-xs hover:bg-blue-100"
                  >
                    + Sube Ekle
                  </button>
                </div>
              </td>
              <td class="py-3 px-4 text-center">
                <span
                  :class="[
                    'px-2 py-1 rounded-full text-xs font-medium',
                    user.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                  ]"
                >
                  {{ user.is_active ? 'Aktif' : 'Pasif' }}
                </span>
              </td>
              <td class="py-3 px-4 text-right">
                <button
                  @click="openUserModal(user)"
                  class="text-blue-600 hover:text-blue-800 mr-2"
                >
                  Duzenle
                </button>
                <button
                  @click="toggleUserSuperAdmin(user)"
                  class="text-purple-600 hover:text-purple-800 mr-2"
                  :title="user.is_super_admin ? 'Super Admin kaldir' : 'Super Admin yap'"
                >
                  {{ user.is_super_admin ? 'SA-' : 'SA+' }}
                </button>
                <button
                  @click="toggleUserActive(user)"
                  :class="user.is_active ? 'text-red-600 hover:text-red-800' : 'text-green-600 hover:text-green-800'"
                >
                  {{ user.is_active ? 'Deaktif' : 'Aktif' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Branch Modal -->
    <div v-if="showBranchModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-lg font-semibold mb-4">
          {{ editingBranch ? 'Sube Duzenle' : 'Yeni Sube' }}
        </h2>
        <form @submit.prevent="saveBranch" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Sube Adi *</label>
            <input
              v-model="branchForm.name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-transparent"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Sube Kodu *</label>
            <input
              v-model="branchForm.code"
              type="text"
              required
              maxlength="20"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-transparent"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Sehir</label>
            <select
              v-model="branchForm.city"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-transparent"
            >
              <option value="">Sehir Seciniz</option>
              <option v-for="city in ['Adana', 'Adiyaman', 'Afyonkarahisar', 'Agri', 'Aksaray', 'Amasya', 'Ankara', 'Antalya', 'Ardahan', 'Artvin', 'Aydin', 'Balikesir', 'Bartin', 'Batman', 'Bayburt', 'Bilecik', 'Bingol', 'Bitlis', 'Bolu', 'Burdur', 'Bursa', 'Canakkale', 'Cankiri', 'Corum', 'Denizli', 'Diyarbakir', 'Duzce', 'Edirne', 'Elazig', 'Erzincan', 'Erzurum', 'Eskisehir', 'Gaziantep', 'Giresun', 'Gumushane', 'Hakkari', 'Hatay', 'Igdir', 'Isparta', 'Istanbul', 'Izmir', 'Kahramanmaras', 'Karabuk', 'Karaman', 'Kars', 'Kastamonu', 'Kayseri', 'Kilis', 'Kirikkale', 'Kirklareli', 'Kirsehir', 'Kocaeli', 'Konya', 'Kutahya', 'Malatya', 'Manisa', 'Mardin', 'Mersin', 'Mugla', 'Mus', 'Nevsehir', 'Nigde', 'Ordu', 'Osmaniye', 'Rize', 'Sakarya', 'Samsun', 'Sanliurfa', 'Siirt', 'Sinop', 'Sirnak', 'Sivas', 'Tekirdag', 'Tokat', 'Trabzon', 'Tunceli', 'Usak', 'Van', 'Yalova', 'Yozgat', 'Zonguldak']" :key="city" :value="city">
                {{ city }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Adres</label>
            <input
              v-model="branchForm.address"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-transparent"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Telefon</label>
            <input
              v-model="branchForm.phone"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-transparent"
            />
          </div>
          <div class="flex justify-end gap-3 pt-4">
            <button
              type="button"
              @click="showBranchModal = false"
              class="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              Iptal
            </button>
            <button type="submit" class="btn btn-primary">
              Kaydet
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- User Modal -->
    <div v-if="showUserModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-lg font-semibold mb-4">
          {{ editingUser ? 'Kullanici Duzenle' : 'Yeni Kullanici' }}
        </h2>
        <form @submit.prevent="saveUser" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Ad Soyad *</label>
            <input
              v-model="userForm.name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-transparent"
            />
          </div>
          <div v-if="!editingUser">
            <label class="block text-sm font-medium text-gray-700 mb-1">Email *</label>
            <input
              v-model="userForm.email"
              type="email"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-transparent"
            />
          </div>
          <div v-if="!editingUser">
            <label class="block text-sm font-medium text-gray-700 mb-1">Sifre *</label>
            <input
              v-model="userForm.password"
              type="password"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-transparent"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Rol *</label>
            <select
              v-model="userForm.role"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-transparent"
            >
              <option v-for="role in roles" :key="role.value" :value="role.value">
                {{ role.label }}
              </option>
            </select>
          </div>
          <div v-if="!editingUser">
            <label class="block text-sm font-medium text-gray-700 mb-1">Varsayilan Sube *</label>
            <select
              v-model="userForm.branch_id"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-transparent"
            >
              <option v-for="branch in sortedBranches" :key="branch.id" :value="branch.id">
                {{ branch.name }}
              </option>
            </select>
          </div>
          <div class="flex justify-end gap-3 pt-4">
            <button
              type="button"
              @click="showUserModal = false"
              class="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              Iptal
            </button>
            <button type="submit" class="btn btn-primary">
              Kaydet
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Assign Branch Modal -->
    <div v-if="showAssignModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-lg font-semibold mb-4">
          {{ assigningUser?.name }} - Sube Ekle
        </h2>
        <form @submit.prevent="assignBranch" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Sube *</label>
            <select
              v-model="assignForm.branch_id"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-transparent"
            >
              <option v-for="branch in availableBranchesForAssign" :key="branch.id" :value="branch.id">
                {{ branch.name }}
              </option>
            </select>
            <p v-if="availableBranchesForAssign.length === 0" class="text-sm text-gray-500 mt-1">
              Atanabilecek sube kalmadi
            </p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Rol *</label>
            <select
              v-model="assignForm.role"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-transparent"
            >
              <option v-for="role in roles" :key="role.value" :value="role.value">
                {{ role.label }}
              </option>
            </select>
          </div>
          <div class="flex items-center gap-2">
            <input
              v-model="assignForm.is_default"
              type="checkbox"
              id="is_default"
              class="rounded border-gray-300"
            />
            <label for="is_default" class="text-sm text-gray-700">Varsayilan sube olarak ayarla</label>
          </div>
          <div class="flex justify-end gap-3 pt-4">
            <button
              type="button"
              @click="showAssignModal = false"
              class="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              Iptal
            </button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="availableBranchesForAssign.length === 0"
            >
              Ekle
            </button>
          </div>
        </form>
      </div>
    </div>
    
    <ConfirmModal 
      :show="showConfirm"
      :message="confirmMessage"
      @confirm="handleConfirm"
      @cancel="showConfirm = false"
    />
  </div>
</template>
