<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { Purchase, Supplier } from '@/types'
import { purchasesApi, suppliersApi } from '@/services/api'
import { useFormatters } from '@/composables'
import { Loader2, ShoppingCart, Building2, Package } from 'lucide-vue-next'

interface Props {
  embedded?: boolean
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'action', type: 'add' | 'view' | 'edit', item?: Purchase): void
}>()

const { formatCurrency } = useFormatters()

// Data
const purchases = ref<Purchase[]>([])
const suppliers = ref<Supplier[]>([])
const loading = ref(true)
const error = ref('')

// Get current month's data
const currentMonth = new Date().getMonth()
const currentYear = new Date().getFullYear()
const startDate = new Date(currentYear, currentMonth, 1).toISOString().split('T')[0]
const endDate = new Date(currentYear, currentMonth + 1, 0).toISOString().split('T')[0]

onMounted(async () => {
  await Promise.all([loadPurchases(), loadSuppliers()])
})

async function loadSuppliers() {
  try {
    const { data } = await suppliersApi.getAll()
    suppliers.value = data
  } catch (e) {
    console.error('Failed to load suppliers:', e)
  }
}

async function loadPurchases() {
  loading.value = true
  try {
    const { data } = await purchasesApi.getAll({ start_date: startDate, end_date: endDate })
    purchases.value = data
  } catch (e) {
    error.value = 'Alımlar yüklenemedi'
  } finally {
    loading.value = false
  }
}

// Computed summaries
const totalPurchases = computed(() => purchases.value.reduce((sum, p) => sum + Number(p.total), 0))
const purchaseCount = computed(() => purchases.value.length)

// Group by supplier
const bySupplier = computed(() => {
  const grouped: Record<string, number> = {}
  for (const purchase of purchases.value) {
    const supplierName = purchase.supplier?.name || 'Bilinmeyen'
    grouped[supplierName] = (grouped[supplierName] || 0) + Number(purchase.total)
  }
  return Object.entries(grouped)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 4)
})

// Format helpers
function formatPurchaseDate(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' })
}

function getSupplierColor(index: number) {
  const colors = [
    'bg-blue-100 text-blue-700',
    'bg-green-100 text-green-700',
    'bg-purple-100 text-purple-700',
    'bg-orange-100 text-orange-700'
  ]
  return colors[index % colors.length]
}
</script>

<template>
  <div class="space-y-4">
    <!-- Summary Row -->
    <div class="grid grid-cols-3 gap-2">
      <div class="bg-amber-50 rounded-lg p-3 text-center">
        <ShoppingCart class="w-4 h-4 mx-auto text-amber-600 mb-1" />
        <div class="text-lg font-bold text-amber-700">
          {{ formatCurrency(totalPurchases) }}
        </div>
        <div class="text-xs text-amber-600">Toplam Alım</div>
      </div>
      <div class="bg-blue-50 rounded-lg p-3 text-center">
        <Building2 class="w-4 h-4 mx-auto text-blue-600 mb-1" />
        <div class="text-lg font-bold text-blue-700">
          {{ suppliers.length }}
        </div>
        <div class="text-xs text-blue-600">Tedarikçi</div>
      </div>
      <div class="bg-gray-50 rounded-lg p-3 text-center">
        <Package class="w-4 h-4 mx-auto text-gray-600 mb-1" />
        <div class="text-lg font-bold text-gray-700">
          {{ purchaseCount }}
        </div>
        <div class="text-xs text-gray-600">Sipariş</div>
      </div>
    </div>

    <!-- Top Suppliers -->
    <div v-if="bySupplier.length > 0" class="flex flex-wrap gap-2">
      <div
        v-for="([name, amount], index) in bySupplier"
        :key="name"
        class="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium"
        :class="getSupplierColor(index)"
      >
        <span>{{ name }}</span>
        <span class="opacity-75">{{ formatCurrency(amount) }}</span>
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
    <div v-else-if="purchases.length === 0" class="text-center py-8 text-gray-500">
      Bu ay için alım kaydı bulunamadı
    </div>

    <!-- Table -->
    <div v-else class="overflow-y-auto max-h-[45vh] rounded-lg border border-gray-200">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 sticky top-0">
          <tr>
            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Tarih</th>
            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Tedarikçi</th>
            <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase">Kalem</th>
            <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">Tutar</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr
            v-for="purchase in purchases.slice(0, 20)"
            :key="purchase.id"
            class="hover:bg-gray-50 cursor-pointer"
            @click="emit('action', 'view', purchase)"
          >
            <td class="px-3 py-2 text-gray-900">{{ formatPurchaseDate(purchase.purchase_date) }}</td>
            <td class="px-3 py-2 text-gray-700 truncate max-w-[120px]">{{ purchase.supplier?.name || '-' }}</td>
            <td class="px-3 py-2 text-center text-gray-500">{{ purchase.items?.length || 1 }}</td>
            <td class="px-3 py-2 text-right font-medium text-gray-900">
              {{ formatCurrency(Number(purchase.total)) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>
