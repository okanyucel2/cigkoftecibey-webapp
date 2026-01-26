<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { Employee } from '@/types'
import { personnelApi } from '@/services/api'
import { useFormatters } from '@/composables'
import { Loader2, Users, UserCheck, Clock, Briefcase } from 'lucide-vue-next'

interface Props {
  embedded?: boolean
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'action', type: 'add' | 'view' | 'edit', item?: Employee): void
}>()

const { formatCurrency } = useFormatters()

// Data
const employees = ref<Employee[]>([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  await loadEmployees()
})

async function loadEmployees() {
  loading.value = true
  try {
    const { data } = await personnelApi.getEmployees()
    employees.value = data
  } catch (e) {
    error.value = 'Personel listesi yüklenemedi'
  } finally {
    loading.value = false
  }
}

// Computed summaries
const activeCount = computed(() => employees.value.filter(e => e.is_active).length)
const fullTimeCount = computed(() => employees.value.filter(e => !e.is_part_time && e.is_active).length)
const partTimeCount = computed(() => employees.value.filter(e => e.is_part_time && e.is_active).length)
const totalSalary = computed(() => employees.value.filter(e => e.is_active).reduce((sum, e) => sum + Number(e.base_salary || 0), 0))

// Format helpers
function getEmploymentTypeLabel(isPartTime: boolean) {
  return isPartTime ? 'Part-time' : 'Tam Zamanlı'
}

function getEmploymentTypeClass(isPartTime: boolean) {
  return isPartTime ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'
}

function getStatusClass(isActive: boolean) {
  return isActive ? 'text-emerald-600' : 'text-gray-400'
}
</script>

<template>
  <div class="space-y-4">
    <!-- Summary Row -->
    <div class="grid grid-cols-4 gap-2">
      <div class="bg-emerald-50 rounded-lg p-3 text-center">
        <Users class="w-4 h-4 mx-auto text-emerald-600 mb-1" />
        <div class="text-lg font-bold text-emerald-700">
          {{ activeCount }}
        </div>
        <div class="text-xs text-emerald-600">Aktif</div>
      </div>
      <div class="bg-blue-50 rounded-lg p-3 text-center">
        <Briefcase class="w-4 h-4 mx-auto text-blue-600 mb-1" />
        <div class="text-lg font-bold text-blue-700">
          {{ fullTimeCount }}
        </div>
        <div class="text-xs text-blue-600">Tam Zamanlı</div>
      </div>
      <div class="bg-purple-50 rounded-lg p-3 text-center">
        <Clock class="w-4 h-4 mx-auto text-purple-600 mb-1" />
        <div class="text-lg font-bold text-purple-700">
          {{ partTimeCount }}
        </div>
        <div class="text-xs text-purple-600">Part-time</div>
      </div>
      <div class="bg-gray-50 rounded-lg p-3 text-center">
        <div class="text-lg font-bold text-gray-700">
          {{ formatCurrency(totalSalary) }}
        </div>
        <div class="text-xs text-gray-600">Toplam Maaş</div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-8">
      <Loader2 class="w-6 h-6 animate-spin text-gray-400" />
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">
      {{ error }}
    </div>

    <!-- Empty State -->
    <div v-else-if="employees.length === 0" class="text-center py-8 text-gray-500">
      Henüz personel kaydı bulunamadı
    </div>

    <!-- Table -->
    <div v-else class="overflow-y-auto max-h-[50vh] rounded-lg border border-gray-200">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 sticky top-0">
          <tr>
            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Ad Soyad</th>
            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Görev</th>
            <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase">Tip</th>
            <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">Maaş</th>
            <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase">Durum</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr
            v-for="employee in employees"
            :key="employee.id"
            class="hover:bg-gray-50 cursor-pointer"
            @click="emit('action', 'view', employee)"
          >
            <td class="px-3 py-2 text-gray-900 font-medium">{{ employee.name }}</td>
            <td class="px-3 py-2 text-gray-600">{{ employee.payment_type === 'monthly' ? 'Aylık' : 'Haftalık' }}</td>
            <td class="px-3 py-2 text-center">
              <span
                class="px-2 py-0.5 rounded text-xs font-medium"
                :class="getEmploymentTypeClass(employee.is_part_time)"
              >
                {{ getEmploymentTypeLabel(employee.is_part_time) }}
              </span>
            </td>
            <td class="px-3 py-2 text-right text-gray-700">
              {{ formatCurrency(Number(employee.base_salary || 0)) }}
            </td>
            <td class="px-3 py-2 text-center">
              <UserCheck
                class="w-4 h-4 mx-auto"
                :class="getStatusClass(employee.is_active)"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add Button -->
    <button
      type="button"
      class="w-full py-2 text-sm font-medium text-emerald-600 bg-emerald-50 rounded-lg hover:bg-emerald-100 transition-colors"
      @click="emit('action', 'add')"
    >
      + Yeni Personel Ekle
    </button>
  </div>
</template>
