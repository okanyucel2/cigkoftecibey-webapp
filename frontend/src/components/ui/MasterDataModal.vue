<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="modelValue"
        class="fixed inset-0 z-[60] overflow-y-auto"
      >
        <!-- Backdrop -->
        <div
          class="fixed inset-0 bg-gray-900/50 backdrop-blur-sm"
          @click="close"
        />

        <!-- Modal -->
        <div class="flex min-h-full items-center justify-center p-4">
          <Transition
            enter-active-class="transition ease-out duration-200"
            enter-from-class="opacity-0 scale-95"
            enter-to-class="opacity-100 scale-100"
            leave-active-class="transition ease-in duration-150"
            leave-from-class="opacity-100 scale-100"
            leave-to-class="opacity-0 scale-95"
          >
            <div
              v-if="modelValue"
              class="relative w-full max-w-md bg-white rounded-2xl shadow-xl"
            >
              <!-- Header -->
              <div class="px-6 py-4 border-b border-gray-100">
                <div class="flex items-center justify-between">
                  <h3 class="text-lg font-semibold text-gray-900">
                    {{ computedTitle }}
                  </h3>
                  <button
                    type="button"
                    class="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
                    @click="close"
                  >
                    <X class="w-5 h-5" />
                  </button>
                </div>
                <p v-if="subtitle" class="mt-1 text-sm text-gray-500">
                  {{ subtitle }}
                </p>
              </div>

              <!-- Content -->
              <form @submit.prevent="handleSubmit">
                <div class="px-6 py-4 space-y-4">
                  <!-- Supplier Form -->
                  <template v-if="type === 'supplier'">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">
                        Tedarikci Adi <span class="text-red-500">*</span>
                      </label>
                      <BaseInput
                        v-model="supplierForm.name"
                        placeholder="Tedarikci adi girin"
                        required
                      />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">
                        Telefon
                      </label>
                      <BaseInput
                        v-model="supplierForm.phone"
                        type="tel"
                        placeholder="0500 000 00 00"
                      />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">
                        Vergi No
                      </label>
                      <BaseInput
                        v-model="supplierForm.taxId"
                        placeholder="Vergi numarasi"
                      />
                    </div>
                  </template>

                  <!-- Expense Category Form -->
                  <template v-if="type === 'expense-category'">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">
                        Kategori Adi <span class="text-red-500">*</span>
                      </label>
                      <BaseInput
                        v-model="categoryForm.name"
                        placeholder="Kategori adi girin"
                        required
                      />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">
                        Ikon
                      </label>
                      <div class="flex flex-wrap gap-2">
                        <button
                          v-for="icon in iconOptions"
                          :key="icon.value"
                          type="button"
                          class="p-2 rounded-lg border transition-colors"
                          :class="categoryForm.icon === icon.value ? 'border-primary-500 bg-primary-50' : 'border-gray-200 hover:border-gray-300'"
                          @click="categoryForm.icon = icon.value"
                        >
                          <span class="text-lg">{{ icon.emoji }}</span>
                        </button>
                      </div>
                    </div>
                  </template>

                  <!-- Platform Form -->
                  <template v-if="type === 'platform'">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">
                        Platform Adi <span class="text-red-500">*</span>
                      </label>
                      <BaseInput
                        v-model="platformForm.name"
                        placeholder="Platform adi girin"
                        required
                      />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">
                        Komisyon Orani (%)
                      </label>
                      <BaseInput
                        v-model="platformForm.commissionRate"
                        type="number"
                        placeholder="0"
                        prefix="%"
                      />
                    </div>
                  </template>
                </div>

                <!-- Footer -->
                <div class="px-6 py-4 border-t border-gray-100 flex justify-end gap-3">
                  <button
                    type="button"
                    class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                    @click="close"
                  >
                    Iptal
                  </button>
                  <button
                    type="submit"
                    class="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors"
                    :disabled="!isValid || saving"
                  >
                    <span v-if="saving" class="flex items-center gap-2">
                      <Loader2 class="w-4 h-4 animate-spin" />
                      Kaydediliyor...
                    </span>
                    <span v-else>Kaydet</span>
                  </button>
                </div>
              </form>
            </div>
          </Transition>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { X, Loader2 } from 'lucide-vue-next'
import { BaseInput } from '@/components/ui'

export type MasterDataType = 'supplier' | 'expense-category' | 'platform'

export interface SupplierData {
  name: string
  phone: string
  taxId: string
}

export interface CategoryData {
  name: string
  icon: string
}

export interface PlatformData {
  name: string
  commissionRate: string
}

interface Props {
  modelValue: boolean
  type: MasterDataType
  title?: string
  subtitle?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Yeni Ekle'
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'save': [data: SupplierData | CategoryData | PlatformData]
}>()

const saving = ref(false)

// Form states
const supplierForm = ref<SupplierData>({
  name: '',
  phone: '',
  taxId: ''
})

const categoryForm = ref<CategoryData>({
  name: '',
  icon: ''
})

const platformForm = ref<PlatformData>({
  name: '',
  commissionRate: ''
})

// Icon options for expense categories
const iconOptions = [
  { value: 'shopping', emoji: '🛒' },
  { value: 'truck', emoji: '🚚' },
  { value: 'tools', emoji: '🔧' },
  { value: 'cleaning', emoji: '🧹' },
  { value: 'electric', emoji: '⚡' },
  { value: 'water', emoji: '💧' },
  { value: 'gas', emoji: '🔥' },
  { value: 'office', emoji: '📋' },
  { value: 'other', emoji: '📦' }
]

// Computed title based on type
const computedTitle = computed(() => {
  if (props.title !== 'Yeni Ekle') return props.title
  switch (props.type) {
    case 'supplier': return 'Yeni Tedarikci'
    case 'expense-category': return 'Yeni Kategori'
    case 'platform': return 'Yeni Platform'
    default: return 'Yeni Ekle'
  }
})

// Validation
const isValid = computed(() => {
  switch (props.type) {
    case 'supplier':
      return supplierForm.value.name.trim().length > 0
    case 'expense-category':
      return categoryForm.value.name.trim().length > 0
    case 'platform':
      return platformForm.value.name.trim().length > 0
    default:
      return false
  }
})

function close() {
  emit('update:modelValue', false)
}

function resetForms() {
  supplierForm.value = { name: '', phone: '', taxId: '' }
  categoryForm.value = { name: '', icon: '' }
  platformForm.value = { name: '', commissionRate: '' }
}

async function handleSubmit() {
  if (!isValid.value) return

  saving.value = true
  try {
    let data: SupplierData | CategoryData | PlatformData

    switch (props.type) {
      case 'supplier':
        data = { ...supplierForm.value }
        break
      case 'expense-category':
        data = { ...categoryForm.value }
        break
      case 'platform':
        data = { ...platformForm.value }
        break
      default:
        return
    }

    emit('save', data)
    close()
  } finally {
    saving.value = false
  }
}

// Reset forms when modal closes
watch(() => props.modelValue, (isOpen) => {
  if (!isOpen) {
    resetForms()
  }
})

// Handle Escape key
function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && props.modelValue) {
    close()
  }
}

watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    document.addEventListener('keydown', handleKeydown)
  } else {
    document.removeEventListener('keydown', handleKeydown)
  }
})
</script>
