<template>
  <div class="space-y-4">
    <!-- Instruction -->
    <div class="bg-purple-50 border border-purple-200 rounded-lg p-4">
      <p class="text-sm text-purple-700">
        Platform cirosu bilgilerini kontrol edin.
        Fark varsa gercek tutari girin ve onaylayin.
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="space-y-3">
      <div v-for="i in 3" :key="i" class="animate-pulse">
        <div class="bg-gray-100 rounded-lg h-24" />
      </div>
    </div>

    <!-- Platform List -->
    <div v-else class="space-y-3">
      <div
        v-for="platform in platforms"
        :key="platform.id"
        :class="[
          'rounded-lg border p-4 transition-colors',
          platform.confirmed
            ? 'bg-emerald-50 border-emerald-200'
            : 'bg-white border-gray-200'
        ]"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="flex-1">
            <h4 class="font-medium text-gray-900">{{ platform.name }}</h4>
            <div class="mt-2 space-y-1 text-sm">
              <div class="flex justify-between text-gray-600">
                <span>Sistem Tutari:</span>
                <span class="font-medium">{{ formatCurrency(platform.systemAmount) }}</span>
              </div>
              <div class="flex items-center gap-2">
                <span class="text-gray-600">Gercek Tutar:</span>
                <input
                  type="number"
                  :value="platform.confirmedAmount"
                  @input="(e) => updateAmount(platform.id, e)"
                  :disabled="platform.confirmed"
                  class="w-24 px-2 py-1 text-right text-sm font-medium border rounded focus:ring-1 focus:ring-emerald-500 disabled:bg-gray-100"
                  min="0"
                  step="0.01"
                />
              </div>
            </div>

            <!-- Difference indicator -->
            <div
              v-if="platform.systemAmount !== platform.confirmedAmount"
              :class="[
                'mt-2 text-xs px-2 py-1 rounded inline-flex items-center gap-1',
                Math.abs(platform.systemAmount - platform.confirmedAmount) > 50
                  ? 'bg-red-100 text-red-700'
                  : 'bg-amber-100 text-amber-700'
              ]"
            >
              <AlertTriangle class="w-3 h-3" />
              Fark: {{ formatCurrency(platform.confirmedAmount - platform.systemAmount) }}
            </div>
          </div>

          <label class="flex items-center gap-2 cursor-pointer mt-1">
            <input
              type="checkbox"
              :checked="platform.confirmed"
              @change="togglePlatform(platform.id)"
              class="h-5 w-5 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500"
            />
            <span class="text-sm text-gray-600">Onayla</span>
          </label>
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-if="platforms.length === 0"
        class="text-center py-8 text-gray-500"
      >
        <Globe class="w-12 h-12 mx-auto mb-3 text-gray-300" />
        <p>Bugune ait platform satisi bulunamadi</p>
      </div>
    </div>

    <!-- Summary -->
    <div v-if="platforms.length > 0" class="bg-gray-50 rounded-lg p-4 mt-4">
      <div class="flex justify-between items-center">
        <span class="text-sm text-gray-600">Toplam Platform Cirosu</span>
        <span class="text-lg font-bold text-gray-900">{{ formatCurrency(totalPlatformSales) }}</span>
      </div>
      <div class="flex justify-between items-center mt-2 text-sm">
        <span class="text-gray-500">Onaylanan</span>
        <span :class="allConfirmed ? 'text-emerald-600' : 'text-amber-600'">
          {{ confirmedCount }}/{{ platforms.length }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { AlertTriangle, Globe } from 'lucide-vue-next'

interface PlatformItem {
  id: number
  name: string
  systemAmount: number
  confirmedAmount: number
  confirmed: boolean
}

interface Props {
  platforms: PlatformItem[]
  loading?: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:platforms': [value: PlatformItem[]]
}>()

function togglePlatform(id: number) {
  const updated = props.platforms.map(p =>
    p.id === id ? { ...p, confirmed: !p.confirmed } : p
  )
  emit('update:platforms', updated)
}

function updateAmount(id: number, event: Event) {
  const target = event.target as HTMLInputElement
  const value = parseFloat(target.value) || 0
  const updated = props.platforms.map(p =>
    p.id === id ? { ...p, confirmedAmount: value } : p
  )
  emit('update:platforms', updated)
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 2
  }).format(value)
}

const totalPlatformSales = computed(() =>
  props.platforms.reduce((sum, p) => sum + p.confirmedAmount, 0)
)

const confirmedCount = computed(() =>
  props.platforms.filter(p => p.confirmed).length
)

const allConfirmed = computed(() =>
  props.platforms.length > 0 && props.platforms.every(p => p.confirmed)
)
</script>
