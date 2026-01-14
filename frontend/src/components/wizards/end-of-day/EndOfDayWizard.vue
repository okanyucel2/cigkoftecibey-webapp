<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="show"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
        @click.self="handleClose"
      >
        <div class="bg-white rounded-xl shadow-xl w-full mx-4 max-w-lg max-h-[90vh] overflow-hidden flex flex-col">
          <!-- Header with Step Indicator -->
          <div class="p-4 border-b bg-white sticky top-0">
            <div class="flex justify-between items-start">
              <div>
                <h2 class="text-lg font-semibold text-gray-900">Gun Sonu</h2>
                <p class="text-sm text-gray-500">{{ stepTitles[currentStep] }}</p>
              </div>
              <button
                @click="handleClose"
                class="text-gray-400 hover:text-gray-600 text-2xl leading-none p-1 -mr-1"
                aria-label="Kapat"
              >
                &times;
              </button>
            </div>

            <!-- Step Indicator -->
            <div class="flex items-center gap-2 mt-4">
              <template v-for="(_, index) in steps" :key="index">
                <div
                  :class="[
                    'w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors',
                    index < currentStep
                      ? 'bg-emerald-500 text-white'
                      : index === currentStep
                        ? 'bg-emerald-100 text-emerald-700 ring-2 ring-emerald-500'
                        : 'bg-gray-100 text-gray-400'
                  ]"
                >
                  <Check v-if="index < currentStep" class="w-4 h-4" />
                  <span v-else>{{ index + 1 }}</span>
                </div>
                <div
                  v-if="index < steps.length - 1"
                  :class="[
                    'flex-1 h-0.5 transition-colors',
                    index < currentStep ? 'bg-emerald-500' : 'bg-gray-200'
                  ]"
                />
              </template>
            </div>
          </div>

          <!-- Step Content -->
          <div class="flex-1 overflow-auto p-4">
            <CashCountStep
              v-if="currentStep === 0"
              v-model:counted-amount="wizardData.countedAmount"
              :expected-amount="wizardData.expectedAmount"
              :difference="cashDifference"
            />

            <ExpenseConfirmStep
              v-if="currentStep === 1 && !showAddExpenseForm"
              v-model:expenses="wizardData.expenses"
              :loading="loadingExpenses"
              @add-expense="showAddExpenseForm = true"
            />

            <!-- Inline Add Expense Form -->
            <div v-if="currentStep === 1 && showAddExpenseForm" class="space-y-4">
              <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 class="font-medium text-blue-800 mb-1">Yeni Gider Ekle</h4>
                <p class="text-sm text-blue-600">Eksik gider bilgilerini girin</p>
              </div>

              <div class="space-y-3">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Aciklama
                  </label>
                  <input
                    v-model="newExpenseDescription"
                    type="text"
                    placeholder="Ornegin: Sebze Alimi"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Tutar (TL)
                  </label>
                  <input
                    v-model="newExpenseAmount"
                    type="number"
                    placeholder="0.00"
                    min="0"
                    step="0.01"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              <div class="flex gap-2 pt-2">
                <button
                  type="button"
                  class="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
                  @click="cancelAddExpense"
                >
                  Vazgec
                </button>
                <button
                  type="button"
                  class="flex-1 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
                  @click="addNewExpense"
                >
                  Ekle
                </button>
              </div>
            </div>

            <PlatformReconcileStep
              v-if="currentStep === 2"
              v-model:platforms="wizardData.platforms"
              :loading="loadingPlatforms"
            />

            <SummaryStep
              v-if="currentStep === 3"
              :wizard-data="wizardData"
              :cash-difference="cashDifference"
              v-model:difference-reason="wizardData.differenceReason"
              :require-reason="Math.abs(cashDifference) > 20"
            />
          </div>

          <!-- Footer Navigation -->
          <div class="p-4 border-t bg-gray-50 flex justify-between">
            <button
              v-if="currentStep > 0"
              type="button"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              @click="prevStep"
            >
              Geri
            </button>
            <div v-else />

            <button
              type="button"
              :disabled="!canProceed || saving"
              :class="[
                'px-4 py-2 text-sm font-medium rounded-lg transition-colors',
                currentStep === steps.length - 1
                  ? 'bg-emerald-600 text-white hover:bg-emerald-700 disabled:bg-emerald-300'
                  : 'bg-gray-900 text-white hover:bg-gray-800 disabled:bg-gray-300'
              ]"
              @click="currentStep === steps.length - 1 ? finishWizard() : nextStep()"
            >
              <span v-if="saving">Kaydediliyor...</span>
              <span v-else>{{ currentStep === steps.length - 1 ? 'Gunu Kapat' : 'Devam' }}</span>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Check } from 'lucide-vue-next'
import { useToast } from '@/composables/useToast'
import { expensesApi, onlineSalesApi } from '@/services/api'
import CashCountStep from './CashCountStep.vue'
import ExpenseConfirmStep from './ExpenseConfirmStep.vue'
import PlatformReconcileStep from './PlatformReconcileStep.vue'
import SummaryStep from './SummaryStep.vue'

export interface ExpenseItem {
  id: number
  description: string
  amount: number
  confirmed: boolean
}

export interface PlatformItem {
  id: number
  name: string
  systemAmount: number
  confirmedAmount: number
  confirmed: boolean
}

export interface WizardData {
  countedAmount: number | null
  expectedAmount: number
  expenses: ExpenseItem[]
  platforms: PlatformItem[]
  differenceReason: string
}

interface Props {
  show: boolean
}

defineProps<Props>()

const emit = defineEmits<{
  close: []
  complete: [data: WizardData]
}>()

const toast = useToast()

const steps = ['cash', 'expenses', 'platforms', 'summary'] as const
const stepTitles: Record<number, string> = {
  0: 'Kasa Sayimi',
  1: 'Giderleri Onayla',
  2: 'Platform Mutabakati',
  3: 'Ozet'
}

const currentStep = ref(0)
const saving = ref(false)
const loadingExpenses = ref(false)
const loadingPlatforms = ref(false)

// Add Expense Form State
const showAddExpenseForm = ref(false)
const newExpenseDescription = ref('')
const newExpenseAmount = ref('')

// Wizard data state
const wizardData = ref<WizardData>({
  countedAmount: null,
  expectedAmount: 0,
  expenses: [],
  platforms: [],
  differenceReason: ''
})

// Computed values
const cashDifference = computed(() => {
  if (wizardData.value.countedAmount === null) return 0
  return wizardData.value.countedAmount - wizardData.value.expectedAmount
})

const canProceed = computed(() => {
  switch (currentStep.value) {
    case 0: // Cash Count
      return wizardData.value.countedAmount !== null && wizardData.value.countedAmount >= 0
    case 1: // Expenses
      return wizardData.value.expenses.every(e => e.confirmed)
    case 2: // Platforms
      return wizardData.value.platforms.every(p => p.confirmed)
    case 3: // Summary
      // Require reason if difference > 20 TL
      if (Math.abs(cashDifference.value) > 20) {
        return wizardData.value.differenceReason.trim().length > 0
      }
      return true
    default:
      return true
  }
})

// Navigation
function nextStep() {
  if (currentStep.value < steps.length - 1) {
    currentStep.value++
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

function addNewExpense() {
  const description = newExpenseDescription.value.trim()
  const amount = parseFloat(newExpenseAmount.value) || 0

  if (!description || amount <= 0) {
    toast.warning('Aciklama ve tutar giriniz')
    return
  }

  // Add new expense to list (pre-confirmed since user just added it)
  const newExpense: ExpenseItem = {
    id: Date.now(), // Temporary ID
    description,
    amount,
    confirmed: true
  }

  wizardData.value.expenses.push(newExpense)

  // Reset form
  newExpenseDescription.value = ''
  newExpenseAmount.value = ''
  showAddExpenseForm.value = false

  toast.success('Gider eklendi')
}

function cancelAddExpense() {
  newExpenseDescription.value = ''
  newExpenseAmount.value = ''
  showAddExpenseForm.value = false
}

async function finishWizard() {
  saving.value = true

  try {
    // TODO: API call to save end of day data
    // await endOfDayApi.closeDay(wizardData.value)

    toast.success('Gun basariyla kapatildi')
    emit('complete', wizardData.value)
    resetWizard()
  } catch (error) {
    console.error('Error closing day:', error)
    toast.error('Gun kapatilirken hata olustu')
  } finally {
    saving.value = false
  }
}

function resetWizard() {
  currentStep.value = 0
  wizardData.value = {
    countedAmount: null,
    expectedAmount: 0,
    expenses: [],
    platforms: [],
    differenceReason: ''
  }
}

function handleClose() {
  if (currentStep.value > 0) {
    // Confirm before closing if user has progressed
    if (!confirm('Degisiklikler kaybolacak. Cikmak istediginize emin misiniz?')) {
      return
    }
  }
  resetWizard()
  emit('close')
}

// Load data when wizard opens
watch(() => currentStep.value, async (step) => {
  if (step === 1 && wizardData.value.expenses.length === 0) {
    await loadExpenses()
  }
  if (step === 2 && wizardData.value.platforms.length === 0) {
    await loadPlatforms()
  }
})

async function loadExpenses() {
  loadingExpenses.value = true
  try {
    // Fetch today's expenses from API
    const response = await expensesApi.getTodayExpenses()
    wizardData.value.expenses = response.data.map(exp => ({
      id: exp.id,
      description: exp.description || `Gider #${exp.id}`,
      amount: exp.amount,
      confirmed: false
    }))
  } catch (error) {
    console.error('Failed to load expenses:', error)
    // Fallback to empty array if API fails
    wizardData.value.expenses = []
    toast.warning('Giderler yuklenemedi')
  } finally {
    loadingExpenses.value = false
  }
}

async function loadPlatforms() {
  loadingPlatforms.value = true
  try {
    // Get today's date
    const today = new Date().toISOString().split('T')[0]
    // Fetch today's online sales by platform
    const response = await onlineSalesApi.getDailySales(today)
    wizardData.value.platforms = (response.data.entries || []).map(entry => ({
      id: entry.platform_id,
      name: entry.platform?.name || `Platform #${entry.platform_id}`,
      systemAmount: entry.amount,
      confirmedAmount: entry.amount,
      confirmed: false
    }))
  } catch (error) {
    console.error('Failed to load platforms:', error)
    // Fallback to empty array if API fails
    wizardData.value.platforms = []
    toast.warning('Platform verileri yuklenemedi')
  } finally {
    loadingPlatforms.value = false
  }
}

// Initialize expected amount when wizard opens
watch(() => currentStep.value, () => {
  if (currentStep.value === 0 && wizardData.value.expectedAmount === 0) {
    // TODO: Fetch from API - calculated cash balance
    wizardData.value.expectedAmount = 3250 // Mock value
  }
}, { immediate: true })
</script>
